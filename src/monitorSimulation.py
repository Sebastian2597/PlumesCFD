import os
import time
import subprocess
import numpy as np

# PATHS & SETTINGS

processor0_path = './processor0'
control_dict_path = "./system/controlDict"
steady_count_required = 5
check_interval_seconds = 30
fields = ['p', 'U', 'T', 'J', 'S_sat', 'N', 'Y']  # Fields to monitor

convergence_thresholds = {
    'p': 2e-4,
    'U': 9e-5,
    'T': 9e-5,
    'J': 1e-2,      # Looser due to steep gradients / large magnitude
    'S_sat': 1e-3,
    'N': 5e-3,
    'Y': 5e-4
}

# ---------- RMS UTILS ----------
def reconstruct_last_two_time_steps():
    processor_count = 7  # processor0 through processor12
    all_time_steps = []

    # Find valid time steps from processor0
    try:
        all_time_steps = sorted([float(d) for d in os.listdir('processor0')
                                 if os.path.isdir(os.path.join('processor0', d))
                                 and d not in ['0', 'constant']])
    except FileNotFoundError:
        print("[ERROR] processor0 directory not found.")
        return None

    if len(all_time_steps) < 2:
        return None

    last_two = [all_time_steps[-2], all_time_steps[-1]]

    # Check if all processors have these time steps
    for proc_id in range(processor_count):
        proc_dir = f'processor{proc_id}'
        for ts in last_two:
            ts_path = os.path.join(proc_dir, f"{ts:.6g}")  # Avoid float rounding issues
            if not os.path.isdir(ts_path):
                print(f"[WAIT] {ts:.6g} not yet found in {proc_dir}. Skipping reconstruction.")
                return None

    # Proceed with reconstruction if all processor folders contain the time steps
    for ts in last_two:
        subprocess.run(['reconstructPar', '-time', str(ts)],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    print(f"Computing RMS errors from {last_two[0]} and {last_two[1]}..." )
    return last_two

def calculate_rms_scalar_field(field_file):
    with open(field_file, 'r') as f:
        lines = f.readlines()
    
    values = []
    start_reading = False
    inside_internal_field = False

    for line in lines:
        line = line.strip()
        if "internalField" in line:
            inside_internal_field = True
        if inside_internal_field and line.startswith("("):
            start_reading = True
            continue
        elif line.startswith(")"):
            start_reading = False
            inside_internal_field = False

        if start_reading:
            try:
                values.append(float(line))
            except ValueError:
                continue
                
    return np.sqrt(np.mean(np.square(values))) if values else float('nan')

def calculate_rms_vector_field(field_file):
    with open(field_file, 'r') as f:
        lines = f.readlines()

    values = []
    start_reading = False
    inside_internal_field = False

    for line in lines:
        line = line.strip()
        if "internalField" in line:
            inside_internal_field = True
        if inside_internal_field and "(" in line and not start_reading:
            start_reading = True
            continue
        if line == ");":
            start_reading = False
            inside_internal_field = False
            continue

        if start_reading:
            try:
                vec = np.array([float(n) for n in line.strip("() ").split()])
                if len(vec) == 3:
                    values.append(np.linalg.norm(vec))
            except ValueError:
                continue

    return np.sqrt(np.mean(np.square(values))) if values else float('nan')

def compute_rms_errors(time_steps):
    field_rms_values = []
    for time_step in time_steps:
        field_rms = {}
        time_path = str(time_step)
        for field in fields:
            field_file = os.path.join(time_path, field)
            if not os.path.exists(field_file):
                continue
            if field == 'U':
                rms = calculate_rms_vector_field(field_file)
            else:
                rms = calculate_rms_scalar_field(field_file)
            field_rms[field] = rms
        field_rms_values.append(field_rms)
    
    if len(field_rms_values) == 2:
        rms_errors = {}
        for field in fields:
            v1 = field_rms_values[0].get(field)
            v2 = field_rms_values[1].get(field)
            if v1 is not None and v2 is not None and v2 != 0:
                rms_errors[field] = abs(v2 - v1) / abs(v2)
        return rms_errors
    return {}

# ---------- SIMULATION MONITOR ----------
def update_control_dict(new_end_time):
    with open(control_dict_path, "r") as f:
        lines = f.readlines()

    with open(control_dict_path, "w") as f:
        for line in lines:
            if "endTime" in line and not "stopAt" in line:
                f.write(f"endTime         {new_end_time};\n")
            else:
                f.write(line)

def check_rms():
    print("Running simulation & monitoring convergence based on RMS error...")
    last_checked = set()
    steady_count = 0

    while True:
        try:
            time_dirs = [float(d) for d in os.listdir(processor0_path)
                         if os.path.isdir(os.path.join(processor0_path, d)) and d not in ['0', 'constant']]
            time_dirs = sorted(time_dirs)

            # Check if new time steps appeared
            new_dirs = set(time_dirs) - last_checked
            if len(time_dirs) >= 2 and new_dirs:
                print(f"\nNew time steps detected: {sorted(new_dirs)}")
                last_checked = set(time_dirs)

                last_two = reconstruct_last_two_time_steps()
                if last_two is not None:
                    rms_errors = compute_rms_errors(last_two)
                    print(f"RMS Errors: {rms_errors}")

                    # Check all fields against their individual convergence thresholds
                    converged_fields = []
                    unconverged_fields = []
                    
                    for field, error in rms_errors.items():
                        threshold = convergence_thresholds.get(field)
                        if error < threshold:
                            converged_fields.append(field)
                        else:
                            unconverged_fields.append((field, error, threshold))
                    
                    if len(unconverged_fields) == 0:
                        steady_count += 1
                        print(f"All fields below thresholds. Steady count: {steady_count}/{steady_count_required}")
                    else:
                        steady_count = 0
                        print("Unconverged fields:")
                        for field, err, thresh in unconverged_fields:
                            print(f"   - {field}: {err:.3e} > threshold {thresh:.3e}")


                    if steady_count >= steady_count_required:
                        print("\nSteady state reached based on RMS. Stopping simulation.\n")
                        update_control_dict(last_two[-1])  # Update endTime
                        break

            time.sleep(check_interval_seconds)

        except Exception as e:
            print(f"Error: {e}")
            time.sleep(check_interval_seconds)

