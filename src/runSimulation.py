import os
import subprocess
import numpy as np

import editBoundaryFile
import editInitialCondition
import editBoundaryConditionT
import quasi1DIsentropic
import monitorSimulation
import accretionRate
import updateGeometry
import createGmshGeoFile
import readWallFields
import setWallInteractionTerms
import matplotlib.pyplot as plt


case = "./cases/test/"
original_mesh_name = 'channel_mesh'
current_mesh_name = original_mesh_name

steady_state_simulation_end_time = 0.5
simulation_end_time = 1440 # minutes
maximum_number_of_runs = 100

wall_temperature_boundary_condition_type = 'zeroGradient' # fixedValue or zeroGradient
wall_temperature_boundary_condition_start = 273 # [K]
wall_temperature_boundary_condition_end = 273 # [K]

os.chdir(case)

# Run OpenFOAM commands in background
with open("OpenFOAM_simulation_log", "w") as log_file:
    
    print("Creating Gmsh file from wall geometry...", flush=True)
    
    gmsh_points, vertical_divisions_section = createGmshGeoFile.create('channel_data.csv', current_mesh_name)
    subprocess.run(f"cp {current_mesh_name}.geo {current_mesh_name}_original.geo", shell=True, check=True, stderr=subprocess.STDOUT)
    
    print("Done.\n", flush=True)
    
    number_of_runs = 0
    simulation_time = 0
    
    while simulation_time < (simulation_end_time * 60) and number_of_runs <= maximum_number_of_runs:
        print("===========================================================", flush=True)
        print(f"\tRUNNING SIMULATION AT t = {simulation_time:2f}s...", flush=True)
        print("===========================================================\n", flush=True)
    
        print(f"Converting {current_mesh_name}.geo into a mesh file...", flush=True)
        
        subprocess.run(f"gmsh -3 {current_mesh_name}.geo -o {current_mesh_name}.msh -format msh2", shell=True, check=True, stdout=log_file, stderr=subprocess.STDOUT)   

        print(f"Successfuly converted {current_mesh_name}.geo into {current_mesh_name}.msh.\n", flush=True)
        
        print("Converting Gmsh msh file to Foam...", flush=True)

        subprocess.run(f"gmshToFoam {current_mesh_name}.msh", shell=True, check=True, stdout=log_file, stderr=subprocess.STDOUT)
        
        print("Successfuly converted Gmsh file to Foam.\n", flush=True)
        
        print("Editing boundary file & initial conditions for pressure, temperature, Mach number and velocity...", flush=True)
        
        editBoundaryFile.edit()
        
        checkMesh = subprocess.run("checkMesh | grep 'hex'", shell=True, stdout=subprocess.PIPE, universal_newlines=True)
        
        number_of_cells = int(checkMesh.stdout.strip()[15:])
        
        subprocess.run("postProcess -func writeCellCentres", shell=True, check=True, stdout=log_file, stderr=subprocess.STDOUT)

        cell_centers_x = editInitialCondition.read_cell_centers()
        
        wall_coordinates, outerwall, top_wall_indices = readWallFields.get_wall_cells("0/C", vertical_divisions_section)

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
        
        monitorSimulation.update_control_dict(steady_state_simulation_end_time)

        
        print("Decomposing the mesh for parallel simulations...", flush=True)
        
        subprocess.run("rm -rf proc*", shell=True, check=True, stdout=log_file, stderr=subprocess.STDOUT)

        subprocess.run("rm -rf 0.*", shell=True, check=True, stdout=log_file, stderr=subprocess.STDOUT)
        
        subprocess.run("decomposePar", shell=True, check=True, stdout=log_file, stderr=subprocess.STDOUT)
        
        print("Done.\n", flush=True)
                
        subprocess.Popen("nohup mpirun -np 7 rhoCentralFoam_2ph -parallel >> OpenFOAM_simulation_log 2>&1 &", shell=True)
        
        # check for convergence
        monitorSimulation.check_rms()
   
        print("Copying files to simulation results folder...", flush=True)
        
        subprocess.run(f"mkdir -p ./simulation_results/{simulation_time:.2f}", shell=True, check=True, stdout=log_file, stderr=subprocess.STDOUT)
            
        subprocess.run(f"cp -r 0 ./simulation_results/{simulation_time:.2f}", shell=True, check=True, stdout=log_file, stderr=subprocess.STDOUT)
                
        latestTime = subprocess.run("foamListTimes -latestTime", shell=True, stdout=subprocess.PIPE, universal_newlines=True)
        latestTime_str = latestTime.stdout.strip()

        subprocess.run(f"cp -r {latestTime_str} ./simulation_results/{simulation_time:.2f}", shell=True, check=True, stdout=log_file, stderr=subprocess.STDOUT)

        subprocess.run(f"cp -r constant ./simulation_results/{simulation_time:.2f}", shell=True, check=True, stdout=log_file, stderr=subprocess.STDOUT)
        
        subprocess.run(f"cp foam.foam ./simulation_results/{simulation_time:.2f}", shell=True, check=True, stdout=log_file, stderr=subprocess.STDOUT)
        
        subprocess.run(f"cp {current_mesh_name}.geo ./simulation_results/{simulation_time:.2f}", shell=True, check=True, stdout=log_file, stderr=subprocess.STDOUT)        

        print("Done.\n", flush=True)
        
        print("Evolving the change in wall height due to wall accretion & sublimation...", flush=True)
            
        
        # check if r at any cell on the boundary > local cell height: if true then stop dr/dt evolution
        
        with open(f"./simulation_results/{simulation_time:.2f}/wall_coordinates", 'w') as f:
            for value in wall_coordinates[:,1]:
                f.write(str(value) + '\n')
        
        wall_cell_lengths, wall_cell_heights = readWallFields.compute_wall_cell_sizes(wall_coordinates, outerwall)
                
        mdot_a = readWallFields.read_static_field(f'./{latestTime_str}/mdot_a', top_wall_indices)
        mdot_s = readWallFields.read_static_field(f'./{latestTime_str}/mdot_a', top_wall_indices)

        R_wall_threshold = 0.05 * wall_coordinates[:,1] # 5% of the local channel height

        dRw_a_dt = accretionRate.calculate(mdot_a)
        dRw_s_dt = accretionRate.calculate(mdot_s)
        
        dRw_dt_total = dRw_a_dt + dRw_s_dt
        
        dRw_total = np.zeros((len(dRw_dt_total)))
        
        simulation_time_temp = simulation_time
        wall_closed = False
        
        # Base time step
        dt_max = 3600  # Maximum allowed dt [s] (1 hour)
        dt_min = 1e-4  # Minimum allowed dt [s]
        safety_factor = 0.2  # So we don't overshoot the threshold
        
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
        
        
        updated_wall_coordinates_Gmsh = updateGeometry.interpolateSpline(wall_coordinates, dRw_total, gmsh_points[:,0])
        
        updateGeometry.update(f'./{current_mesh_name}', updated_wall_coordinates_Gmsh, len(gmsh_points))
        
        print("Done.\n", flush=True)
    
        
        print("Removing steady state results & processor folders...", flush=True)
        
        subprocess.run("rm -r proc*", shell=True, check=True, stdout=log_file, stderr=subprocess.STDOUT)
        subprocess.run("rm -r 0.*", shell=True, check=True, stdout=log_file, stderr=subprocess.STDOUT)
        
        print("Done.\n", flush=True)
        
        if wall_closed:
            stop_simulation = True
        print("===========================================================", flush=True)
        print(f"\tSIMULATION AT t = {simulation_time_temp:2f} s COMPLETED!", flush=True)
        print("===========================================================\n", flush=True)
        simulation_time_temp = simulation_time
        number_of_runs += 1
    
print("===========================================================", flush=True)
print("\t\tALL SIMULATIONS COMPLETED!", flush=True)
print("===========================================================", flush=True)
