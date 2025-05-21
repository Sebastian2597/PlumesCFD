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

def saturation_curve():
    T_range = np.linspace(273.16, 280, 100)
    P_sat = 610.8 * np.exp(-5.1421*np.log(T_range/273.16) - 6828.77 * (1 / T_range - 1 / 273.16))
    return T_range, P_sat

def sublimation_curve():
    T_range = np.linspace(210, 273.16, 100)
    P_sat = np.exp((-2663.5 / T_range + 12.537) * np.log(10))
    return T_range, P_sat

def melting_curve():
    T_range = np.linspace(273.16, 280, 100)
    
    # Constants
    T_triple = 273.16      # K
    P_triple = 611.657     # Pa

    # Latent heat of fusion (J/kg)
    L_f = 333700           
    rho_ice = 917          # kg/m³
    rho_water = 1000       # kg/m³

    # Clausius-Clapeyron slope (approx.)
    dP_dT = L_f * (rho_water - rho_ice) / T_triple

    # Linear approximation around triple point
    P_sat = P_triple + dP_dT * (T_range - T_triple)

    # Ensure pressure doesn't fall below triple point
    P_sat = np.maximum(P_sat, P_triple)

    return T_range, P_sat

def plot_pressure_vs_temperature(simulation_results_path, pointa, pointb, resolution=1000, specific_time=None):
    all_time_folders = get_time_step_folders(simulation_results_path)
    if not all_time_folders:
        raise RuntimeError(f"No valid time-step folders found in {simulation_results_path}")

    latest_times = get_latest_time_for_folders(simulation_results_path, all_time_folders)
    print(f"Latest time values for each time folder: {latest_times}")
    
    time_values = [float(folder) for folder in all_time_folders]

    fig, ax = plt.subplots(figsize=(8, 6))
    
    if specific_time is not None:
        time_indices = [all_time_folders.index(t) for t in specific_time]
        time_folders = [all_time_folders[i] for i in time_indices]
    else:
        time_folders = all_time_folders

    norm = plt.Normalize(vmin=min(time_values), vmax=max(time_values))
    cmap = plt.cm.viridis
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([]) 

    for folder in time_folders:
        t = latest_times[folder]
        case_folder = os.path.join(simulation_results_path, folder)
        foam_file = os.path.join(case_folder, "foam.foam")

        if not os.path.isfile(foam_file):
            print(f"Warning: foam.foam not found in {case_folder}")
            continue

        reader = pv.OpenFOAMReader(foam_file)
        reader.set_active_time_value(t)
        mesh = reader.read()

        line = pv.Line(pointa, pointb, resolution=resolution)
        sampled = line.sample(mesh)

        if 'p' not in sampled.array_names or 'T' not in sampled.array_names:
            raise ValueError(f"'p' or 'T' not found in sampled data at time {t}.")

        T = sampled['T']
        p = sampled['p']

        color = cmap(norm(float(folder))) if specific_time is None else None
        if specific_time is not None:
            ax.plot(T, p, label=f"t={folder}s", color=color)
        else:
            ax.plot(T, p, color=color)
	

    # Phase diagram overlays
    T_sat, P_sat = saturation_curve()
    T_sub, P_sub = sublimation_curve()
    T_melt, P_melt = melting_curve()
    ax.plot(T_sat, P_sat, 'k--', label='Vapor-Liquid')
    ax.plot(T_sub, P_sub, 'k-', label='Vapor-Ice')
    ax.plot(T_melt, P_melt, 'k:', label='Liquid-Solid')
    ax.scatter([273.16], [611.657], color='k', label='Triple Point')

    ax.set_xlabel('Temperature [K]')
    ax.set_ylabel('Pressure [Pa]')
    ax.set_xlim(210, 280)
    ax.set_ylim(0, 1e3)
    ax.grid(True, linestyle='--', linewidth=0.5)

    if specific_time is not None:
        ax.legend()
    else:
        fig.colorbar(sm, ax=ax, label='Time [s]')
        ax.legend()

    ax.set_title('Pressure vs Temperature Along Line')
    plt.show()

# === USER CONFIGURATION ===
simulation_results_path = "../cases/wall_interactions/wall_accretion_backup/simulation_results/"
pointa = (0, 0, 0)
pointb = (1.5, 0, 0)
resolution = 1000
specific_time = None # or ['0.00', '15.58']

plot_pressure_vs_temperature(
    simulation_results_path,
    pointa,
    pointb,
    resolution,
    specific_time
)

