import pyvista as pv
import numpy as np
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import os

def get_time_step_folders(simulation_results_path):
    folders = []
    for name in os.listdir(simulation_results_path):
        path = os.path.join(simulation_results_path, name)
        if os.path.isdir(path):
            try:
                folders.append((float(name), name))
            except ValueError:
                continue
    return [name for _, name in sorted(folders)]

def get_latest_time_for_folders(simulation_results_path, all_time_folders):
    latest_times = {}
    for folder in all_time_folders:
        case_folder = os.path.join(simulation_results_path, folder)
        foam_file = os.path.join(case_folder, "foam.foam")
        if not os.path.isfile(foam_file):
            print(f"Warning: foam.foam not found in {case_folder}")
            continue
        reader = pv.OpenFOAMReader(foam_file)
        latest_time = max(reader.time_values)
        latest_times[folder] = latest_time
    return latest_times

def plot_fields_over_line_all_timesteps(simulation_results_path, pointa, pointb, resolution=1000, fields=None, specific_time=None, units=None):
    all_time_folders = get_time_step_folders(simulation_results_path)
    if not all_time_folders:
        raise RuntimeError(f"No valid time-step folders found in {simulation_results_path}")

    latest_times = get_latest_time_for_folders(simulation_results_path, all_time_folders)
    print(f"Latest time values for each time folder: {latest_times}")
    
    time_values = [float(time) for time in all_time_folders]
    field_data = {field: [] for field in fields}
    
    for folder in all_time_folders:
        case_folder = os.path.join(simulation_results_path, folder)
        foam_file = os.path.join(case_folder, "foam.foam")
        if not os.path.isfile(foam_file):
            print(f"Warning: foam.foam not found in {case_folder}")
            continue

        t = latest_times.get(folder)

        print(f"Processing: {foam_file} @ time {t}")
        reader = pv.OpenFOAMReader(foam_file)
        reader.set_active_time_value(t)
        mesh = reader.read()
        sampled = pv.Line(pointa, pointb, resolution=resolution).sample(mesh)

        for field in fields:
            if field not in sampled.array_names:
                raise ValueError(f"Field '{field}' not found in {foam_file} at time {t}.")
            field_data[field].append(sampled[field])   
    
    line = pv.Line(pointa, pointb, resolution=resolution)
    distances = np.linalg.norm(line.points - line.points[0], axis=1)
    distances = distances / distances[-1]

    n_fields = len(fields)
    
    # === NEW: Calculate grid layout ===
    n_cols = int(np.ceil(np.sqrt(n_fields)))
    n_rows = int(np.ceil(n_fields / n_cols))
    fig, axs = plt.subplots(n_rows, n_cols, figsize=(5 * n_cols, 4 * n_rows), constrained_layout=True)
    axs = axs.flatten()

    if specific_time is not None:
        for time in specific_time:
            idx = all_time_folders.index(time)
         
            for i, field in enumerate(fields):
                ax = axs[i]
                data_at_time = field_data[field][idx]
    
                if data_at_time.ndim == 2 and data_at_time.shape[1] == 3:
                    data_at_time = np.linalg.norm(data_at_time, axis=1)
                ax.plot(distances, data_at_time, label=f"t = {time}s")
                ax.set_xlabel('x/L [-]')
                ax.set_ylabel(units[field])
                ax.grid(True)
    
        for ax in axs[:n_fields]:
            ax.legend()

        # Hide unused subplots
        for j in range(n_fields, len(axs)):
            fig.delaxes(axs[j])

        #plt.tight_layout()
        plt.show()
        return

    # === MULTI-TIME HANDLING ===
    for i, field in enumerate(fields):
        ax = axs[i]
        field_array_list = field_data[field]

        if field_array_list[0].ndim == 2 and field_array_list[0].shape[1] == 3:
            field_array_list = [np.linalg.norm(arr, axis=1) for arr in field_array_list]

        lengths = [len(arr) for arr in field_array_list]
        if len(set(lengths)) != 1:
            raise ValueError(f"Inconsistent lengths for field {field}: {lengths}")

        
        norm = plt.Normalize(vmin=min(time_values), vmax=max(time_values))
        cmap = plt.cm.viridis
        sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
        sm.set_array([])

        for j, arr in enumerate(field_array_list):
            color = cmap(norm(time_values[j]))
            ax.plot(distances, arr, color=color)
            
        ax.set_xlabel('x/L [-]')
        ax.set_ylabel(units[field])
        ax.grid(True)
        fig.colorbar(sm, ax=ax, label="Time [s]")


    # Hide unused subplots
    for j in range(n_fields, len(axs)):
        fig.delaxes(axs[j])

    #plt.suptitle("Field vs Distance", fontsize=16)
    plt.show()

# === USER SETTINGS ===
simulation_results_path = "../cases/wall_interactions/wall_accretion_fixedT273/simulation_results/"
pointa = (0, 0, 0)
pointb = (1.5, 0, 0)
fields = ['p','T', 'rho', 'U', 'Mach', 'S_sat', 'J', 'N', 'Y']
specific_time = ['0.00','15.58']  # Use None to plot all time steps or ['27.44'] for selected time steps
#specific_time = None

units = {'p': r'P [Pa]',
         'T': r'T [K]',
         'rho': r'$\rho_{gas}$ [Pa]',
         'U': r'||$\vec{U}$|| [m/s]',
         'Mach': r'Mach [-]',
         'J': r'J [# m$^{-3}$s$^{-1}$]',
         'N': r'N [# kg$^{-1}$]',
         'S_sat': r'S$_{sat}$ [-]',
         'Y': r'f [-]',
         'drdt': r'dr/dt [m/s]',
         'r_droplet_actual': r'r$_{grain}$ [m]'
         }

# === RUN ===
plot_fields_over_line_all_timesteps(
    simulation_results_path,
    pointa,
    pointb,
    resolution=1000,
    fields=fields,
    specific_time=specific_time,
    units=units)