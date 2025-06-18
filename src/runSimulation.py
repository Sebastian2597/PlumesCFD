import os
import sys
import subprocess
import configparser
import numpy as np

import editBoundaryFile
import editInitialCondition
import editBoundaryConditionT
import editDecomposeParDict
import quasi1DIsentropic
import monitorSimulation
import accretionRate
import updateGeometry
import createGmshGeoFile
import readWallFields
import setWallInteractionTerms

case = sys.argv[1]
os.chdir(case)

print(f"Starting Coupled Wall Interactions Simulation in {case}...\n", flush=True)

# ----------------- READ CONFIG -------------------
config = configparser.ConfigParser()
config.read("simulation_parameters.ini")

# Mesh
mesh_name = config.get("MESH", "name")
mesh_vertical_divisions = config.getint("MESH", "vertical_divisions")
mesh_horizontal_divisions = config.getint("MESH", "horizontal_divisions")
mesh_progression_vertical = config.getfloat("MESH", "progression_vertical")
mesh_progression_horizontal = config.getfloat("MESH", "progression_horizontal")
mesh_bump_horizontal = config.getfloat("MESH", "bump_horizontal")

# Simulation control
steady_state_simulation_end_time_limit = config.getfloat("SIMULATION", "steady_state_simulation_end_time_limit")
simulation_end_time = config.getfloat("SIMULATION", "simulation_end_time")
maximum_number_of_runs = config.getint("SIMULATION", "maximum_number_of_runs")
processors = config.getint("SIMULATION", "processors")

# Wall temperature BCs
wall_temperature_boundary_condition_type = config.get("WALL_TEMPERATURE", "boundary_condition_type")
wall_temperature_boundary_condition_start = config.getfloat("WALL_TEMPERATURE", "boundary_condition_start")
wall_temperature_boundary_condition_end = config.getfloat("WALL_TEMPERATURE", "boundary_condition_end")

# Time stepping
wall_evolution_threshold_percentage = config.getfloat("WALL_EVOLUTION", "threshold_percentage")
dt_max = config.getfloat("WALL_EVOLUTION", "dt_max")
dt_min = config.getfloat("WALL_EVOLUTION", "dt_min")
safety_factor = config.getfloat("WALL_EVOLUTION", "safety_factor")

# Convergence thresholds
convergence_thresholds = {
    'p': config.getfloat("CONVERGENCE_THRESHOLDS", "p"),
    'U': config.getfloat("CONVERGENCE_THRESHOLDS", "U"),
    'T': config.getfloat("CONVERGENCE_THRESHOLDS", "T"),
    'J': config.getfloat("CONVERGENCE_THRESHOLDS", "J"),
    'S_sat': config.getfloat("CONVERGENCE_THRESHOLDS", "S_sat"),
    'N': config.getfloat("CONVERGENCE_THRESHOLDS", "N"),
    'Y': config.getfloat("CONVERGENCE_THRESHOLDS", "Y")
}

# print configuration parameters
print("===========================================================", flush=True)
print("\t\tSIMULATION PARAMETERS", flush=True)  
print("===========================================================\n", flush=True)
print("[MESH]", flush=True)
print(f"Mesh name: {mesh_name}", flush=True)
print(f"Mesh vertical divisions: {mesh_vertical_divisions}", flush=True)
print(f"Mesh horizontal divisions: {mesh_horizontal_divisions}", flush=True)
print(f"Mesh progression vertical: {mesh_progression_vertical}", flush=True)
print(f"Mesh progression horizontal: {mesh_progression_horizontal}", flush=True)
print(f"Mesh bump horizontal: {mesh_bump_horizontal}", flush=True)
print("\n[SIMULATION]", flush=True)
print(f"Processors: {processors}", flush=True)
print(f"Steady state simulation end time limit: {steady_state_simulation_end_time_limit} s", flush=True)
print(f"Simulation end time: {simulation_end_time} s", flush=True)
print(f"Maximum number of runs: {maximum_number_of_runs}", flush=True)
print("\n[WALL TEMPERATURE]", flush=True)
print(f"Wall temperature boundary condition type: {wall_temperature_boundary_condition_type}", flush=True)
print(f"Wall temperature boundary condition start: {wall_temperature_boundary_condition_start} K", flush=True)
print(f"Wall temperature boundary condition end: {wall_temperature_boundary_condition_end} K", flush=True)
print("\n[WALL EVOLUTION]", flush=True)
print(f"Wall evolution threshold percentage: {wall_evolution_threshold_percentage * 100:.2f}%", flush=True)
print(f"dt max: {dt_max} s", flush=True)
print(f"dt min: {dt_min} s", flush=True)
print(f"Safety factor for dt: {safety_factor}", flush=True)
print("\n[CONVERGENCE]", flush=True)
for field, threshold in convergence_thresholds.items():
    print(f"{field} convergence threshold: {threshold:.3e}", flush=True)    
print("===========================================================\n", flush=True)

# --------------------------------------------------

# Run OpenFOAM commands in background
    
print("Creating Gmsh file from wall geometry...", flush=True)

gmsh_points = createGmshGeoFile.create('channel_data.csv', mesh_name, mesh_vertical_divisions, mesh_horizontal_divisions, mesh_progression_vertical, mesh_progression_horizontal, mesh_bump_horizontal)

print("Done.\n", flush=True)

number_of_runs = 0
simulation_time = 0

subprocess.run("rm -rf simulation_results", shell=True, check=True, stderr=subprocess.STDOUT)

while simulation_time < (simulation_end_time * 60) and number_of_runs <= maximum_number_of_runs:
    print("===========================================================", flush=True)
    print(f"\tRUNNING SIMULATION AT t = {simulation_time:2f}s...", flush=True)
    print("===========================================================\n", flush=True)

    log_file = open("OpenFOAM_simulation.log", "w")   

    print(f"Converting {mesh_name}.geo into a mesh file...", flush=True)
    
    subprocess.run(f"gmsh -3 {mesh_name}.geo -o {mesh_name}.msh -format msh2", shell=True, check=True, stdout=log_file, stderr=subprocess.STDOUT)   

    print(f"Successfuly converted {mesh_name}.geo into {mesh_name}.msh.\n", flush=True)
    
    print("Converting Gmsh msh file to Foam...", flush=True)

    subprocess.run(f"gmshToFoam {mesh_name}.msh", shell=True, check=True, stdout=log_file, stderr=subprocess.STDOUT)
    
    print("Successfuly converted Gmsh file to Foam.\n", flush=True)
    
    print("Editing boundary file & initial conditions for pressure, temperature, Mach number and velocity...", flush=True)
    
    editBoundaryFile.edit()
    
    checkMesh = subprocess.run("checkMesh | grep 'hex'", shell=True, stdout=subprocess.PIPE, universal_newlines=True)
    
    number_of_cells = int(checkMesh.stdout.strip()[15:])
    
    subprocess.run("postProcess -func writeCellCentres", shell=True, check=True, stdout=log_file, stderr=subprocess.STDOUT)

    cell_centers_x = editInitialCondition.read_cell_centers()
    
    wall_coordinates, outerwall, top_wall_indices = readWallFields.get_wall_cells("0/C", mesh_vertical_divisions)

    p_ini, T_ini, Mach_ini, U_ini = quasi1DIsentropic.compute_flow_variables(wall_coordinates[:,0], wall_coordinates[:,1], cell_centers_x)

    if simulation_time == 0:
        print("Initialising wall accretion & sublimation source terms for first steady state simulation...", flush=True)
        
        setWallInteractionTerms.initialise('mdot_a', number_of_cells)
        setWallInteractionTerms.initialise('mdot_s', number_of_cells)

        print("Done.\n", flush=True)
    
    editInitialCondition.edit('p', p_ini)
    editInitialCondition.edit('T', T_ini)
    editInitialCondition.edit('Ma', Mach_ini)
    editInitialCondition.edit('U', U_ini)
    
    editBoundaryConditionT.edit(wall_temperature_boundary_condition_type, len(wall_coordinates), wall_temperature_boundary_condition_start, wall_temperature_boundary_condition_end)
    
    monitorSimulation.update_control_dict(steady_state_simulation_end_time_limit)

    
    print("Decomposing the mesh for parallel simulations...", flush=True)
    
    subprocess.run("rm -rf proc*", shell=True, check=True, stdout=log_file, stderr=subprocess.STDOUT)

    subprocess.run("rm -rf 0.*", shell=True, check=True, stdout=log_file, stderr=subprocess.STDOUT)

    editDecomposeParDict.edit(processors)
    
    subprocess.run("decomposePar", shell=True, check=True, stdout=log_file, stderr=subprocess.STDOUT)
    
    print("Done.\n", flush=True)
            
    subprocess.Popen(f"nohup mpirun -np {processors} rhoCentralFoam_2ph -parallel >> OpenFOAM_simulation.log 2>&1 &", shell=True)
    
    # check for convergence
    monitorSimulation.check_rms(convergence_thresholds)

    print("Copying files to simulation results folder...", flush=True)
    
    subprocess.run(f"mkdir -p ./simulation_results/{simulation_time:.2f}", shell=True, check=True, stdout=log_file, stderr=subprocess.STDOUT)
        
    subprocess.run(f"cp -r 0 ./simulation_results/{simulation_time:.2f}", shell=True, check=True, stdout=log_file, stderr=subprocess.STDOUT)
            
    latestTime = subprocess.run("foamListTimes -latestTime", shell=True, stdout=subprocess.PIPE, universal_newlines=True)
    latestTime_str = latestTime.stdout.strip()

    subprocess.run(f"cp -r {latestTime_str} ./simulation_results/{simulation_time:.2f}", shell=True, check=True, stdout=log_file, stderr=subprocess.STDOUT)

    subprocess.run(f"cp -r constant ./simulation_results/{simulation_time:.2f}", shell=True, check=True, stdout=log_file, stderr=subprocess.STDOUT)

    subprocess.run(f"cp -r system ./simulation_results/{simulation_time:.2f}", shell=True, check=True, stdout=log_file, stderr=subprocess.STDOUT)
    
    subprocess.run(f"cp foam.foam ./simulation_results/{simulation_time:.2f}", shell=True, check=True, stdout=log_file, stderr=subprocess.STDOUT)
    
    subprocess.run(f"cp {mesh_name}.geo ./simulation_results/{simulation_time:.2f}", shell=True, check=True, stdout=log_file, stderr=subprocess.STDOUT)        

    print("Done.\n", flush=True)
    
    print("Evolving the change in wall height due to wall accretion & sublimation...", flush=True)
        
    
    # check if r at any cell on the boundary > local cell height: if true then stop dr/dt evolution
    
    with open(f"./simulation_results/{simulation_time:.2f}/wall_coordinates", 'w') as f:
        for value in wall_coordinates[:,1]:
            f.write(str(value) + '\n')
    
    wall_cell_lengths, wall_cell_heights = readWallFields.compute_wall_cell_sizes(wall_coordinates, outerwall)
            
    mdot_a = readWallFields.read_static_field(f'./{latestTime_str}/mdot_a', top_wall_indices)
    mdot_s = readWallFields.read_static_field(f'./{latestTime_str}/mdot_s', top_wall_indices)

    R_wall_threshold = wall_evolution_threshold_percentage * wall_coordinates[:,1] # a certain percentage of the local channel height

    dRw_a_dt = accretionRate.calculate(mdot_a)
    dRw_s_dt = accretionRate.calculate(mdot_s)
    
    dRw_dt_total = dRw_a_dt + dRw_s_dt
    
    dRw_total = np.zeros((len(dRw_dt_total)))
    
    simulation_time_temp = simulation_time
    wall_closed = False
    
    wall_coordinates_temp = wall_coordinates
    
    while np.all(dRw_total < R_wall_threshold) and not wall_closed:
        
        # Calculate how close we are to the threshold
        delta = np.abs(R_wall_threshold - dRw_total)
        max_delta = np.max(delta)
    
        # Dynamically adjust dt
        if max_delta > 0:
            dt = safety_factor * max_delta / np.max(np.abs(dRw_dt_total))
            dt = np.clip(dt, dt_min, dt_max)  # Keep dt between dt_min and dt_max
        else:
            dt = dt_min
        
        dRw = dRw_dt_total * dt
        dRw_total += dRw
        simulation_time += dt
    
        wall_coordinates_temp[:,1] -= dRw
        
        
        if np.any(wall_coordinates_temp[:,1] <= 0):
            print(f'Wall has fully closed at t = {simulation_time:.3f}s!', flush=True)
            subprocess.run(f"mkdir -p ./simulation_results/{simulation_time:.2f}_wall_closed", shell=True, check=True, stdout=log_file, stderr=subprocess.STDOUT)
            with open(f"./simulation_results/{simulation_time:.2f}_wall_closed", 'w') as f:
                for value in wall_coordinates_temp[:,1]:
                    f.write(str(value) + '\n')
            
            wall_closed = True 
            
    print("Done.\n", flush=True)

    print("Updating wall coordinates in Gmsh file...", flush=True)
    
    updated_wall_coordinates_Gmsh = updateGeometry.interpolateSpline(wall_coordinates, dRw_total, gmsh_points[:,0])
    
    updateGeometry.update(f'./{mesh_name}', updated_wall_coordinates_Gmsh, len(gmsh_points))
    
    print("Done.\n", flush=True)

    
    print("Removing old steady state results & old processor folders...", flush=True)
    
    subprocess.run("rm -r proc*", shell=True, check=True, stdout=log_file, stderr=subprocess.STDOUT)
    subprocess.run("rm -r 0.*", shell=True, check=True, stdout=log_file, stderr=subprocess.STDOUT)
    
    print("Done.\n", flush=True)
    
    if wall_closed:
        stop_simulation = True
    print("===========================================================", flush=True)
    print(f"\tSIMULATION AT t = {simulation_time_temp:2f} s COMPLETED!", flush=True)
    print("===========================================================\n", flush=True)
    log_file.close()
    simulation_time_temp = simulation_time
    number_of_runs += 1
    
print("===========================================================", flush=True)
print("\t\tALL SIMULATIONS COMPLETED!", flush=True)
print("===========================================================", flush=True)
