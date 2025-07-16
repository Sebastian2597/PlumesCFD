import os
import re
import subprocess

def sync(simulate_wall_accretion: bool, simulate_wall_sublimation: bool):
    """
    Synchronizes wall_accretion and wall_sublimation flags in the header file
    and calls rebuild script if changes were made.

    Parameters:
    - simulate_wall_accretion (bool): Desired value for wall_accretion.
    - simulate_wall_sublimation (bool): Desired value for wall_sublimation.
    """
    # Full path to the header file inside solver/
    file_path = "./rhoCentralFoam_2ph_old/phaseChangeThermodynamics/constantsForEmpiricalEqns.H"

    # Regex patterns
    pattern_accretion = re.compile(r'const bool wall_accretion\s*=\s*(true|false);')
    pattern_sublimation = re.compile(r'const bool wall_sublimation\s*=\s*(true|false);')

    # Read current lines
    with open(file_path, 'r') as file:
        lines = file.readlines()

    changed = False

    # Update lines if needed
    for i, line in enumerate(lines):
        match_acc = pattern_accretion.search(line)
        if match_acc:
            current_value = match_acc.group(1) == 'true'
            if current_value != simulate_wall_accretion:
                lines[i] = f'const bool wall_accretion = {"true" if simulate_wall_accretion else "false"}; // Set to false if you do not want to model\n'
                changed = True

        match_sub = pattern_sublimation.search(line)
        if match_sub:
            current_value = match_sub.group(1) == 'true'
            if current_value != simulate_wall_sublimation:
                lines[i] = f'const bool wall_sublimation = {"true" if simulate_wall_sublimation else "false"}; // Set to false if you do not want to model\n'
                changed = True

    # Write and rebuild if changed
    if changed:
        with open(file_path, 'w') as file:
            file.writelines(lines)

        print("Wall Accretion and Wall Sublimation flags updated. Recompiling rhoCentralFoam_2ph...", flush=True)

        try:
            subprocess.run("./copyOldRhoCentralFoam_2ph.sh", shell=True, check=True)
        except subprocess.CalledProcessError as e:
            print("Error running rebuild script.")
            print(f"Command: {e.cmd}")
            print(f"Return code: {e.returncode}")
    else:
        print("Wall Accretion and Wall Sublimation flags match.", flush=True)

