import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Set the path to the parent directory containing all the folders
parent_dir = "./test/simulation_results"
animate = True  # Set this to True to enable animation
repeat_animation = True

# Dictionary to store wall coordinates for each folder
wall_coords_by_folder = {}

# Loop through each item in the parent directory
for folder_name in sorted(os.listdir(parent_dir), key=float):  # ensure ordered by time
    folder_path = os.path.join(parent_dir, folder_name)
    
    if os.path.isdir(folder_path):
        file_path = os.path.join(folder_path, "wall_coordinates")
        if os.path.isfile(file_path):
            data = np.loadtxt(file_path)
            wall_coords_by_folder[folder_name] = data
        else:
            print(f"File 'wall_coordinates' not found in {folder_name}")

# Setup common variables
L = 1.5  # m 
x = np.linspace(0, L, 300)

with open("./test/simulation_results/test/wall_coordinates", 'w') as f:
    f.write('test')

wall_first_coordinate = list(wall_coords_by_folder.values())[0][0]
wall_last_coordinate = list(wall_coords_by_folder.values())[0][-1]
bounding_box_coordinate = 1.1 * max(wall_first_coordinate, wall_last_coordinate)

original_wall_colour = 'deepskyblue'
updated_wall_colour = 'cyan'

# Animation or static
if not animate:
    plt.figure(1)
    for time, wall_coordinates in wall_coords_by_folder.items():
        if float(time) == 0:
            plt.plot(x, wall_coordinates, color=original_wall_colour)
            plt.plot(x, -wall_coordinates, color=original_wall_colour)
            plt.fill_between(x, wall_coordinates, bounding_box_coordinate, color=original_wall_colour, alpha=1.0)
            plt.fill_between(x, -wall_coordinates, -bounding_box_coordinate, color=original_wall_colour, alpha=1.0)
            wall_coordinates_prev = wall_coordinates
        else:
            plt.fill_between(x, wall_coordinates_prev, wall_coordinates, color=updated_wall_colour, alpha=1.0)
            plt.fill_between(x, -wall_coordinates_prev, -wall_coordinates, color=updated_wall_colour, alpha=1.0)
            wall_coordinates_prev = wall_coordinates

    plt.plot(x, np.zeros(len(x)), 'k--')
    plt.xlim(0, L)
    plt.ylim(-bounding_box_coordinate, bounding_box_coordinate)
    plt.title("Wall Evolution (Static)")
    plt.xlabel("x [m]")
    plt.ylabel("Wall coordinate [m]")
    plt.show()

else:
    def animate_wall_evolution(wall_data):
        fig, ax = plt.subplots(figsize=(8, 5))
    
        # Initial plot setup
        ax.set_xlim(0, L)
        ax.set_ylim(-bounding_box_coordinate, bounding_box_coordinate)
        ax.set_title("Wall Evolution (Animated)")
        ax.set_xlabel("x [m]")
        ax.set_ylabel("Wall coordinate [m]")

        # Initial fills at t=0
        wall_coordinates_0 = wall_data[0]
        ax.plot(x, wall_coordinates_0, color=original_wall_colour)
        ax.plot(x, -wall_coordinates_0, color=original_wall_colour)
        ax.fill_between(x, wall_coordinates_0, bounding_box_coordinate, color=original_wall_colour, alpha=1.0)
        ax.fill_between(x, -wall_coordinates_0, -bounding_box_coordinate, color=original_wall_colour, alpha=1.0)
        ax.plot(x, np.zeros(len(x)), 'k--')
    
        current_fills = []  # List to track the current fill objects
    
        def update(frame):
            nonlocal current_fills
    
            # Remove previous fills before redrawing
            for fill in current_fills:
                fill.remove()
            current_fills.clear()  # Reset the fills list
    
            if frame == 0:  # At t=0, reset the plot to its initial state
                # Redraw initial state at t=0
                wall_coordinates_0 = wall_data[0]
                ax.plot(x, wall_coordinates_0, color=original_wall_colour)
                ax.plot(x, -wall_coordinates_0, color=original_wall_colour)
                ax.fill_between(x, wall_coordinates_0, bounding_box_coordinate, color=original_wall_colour, alpha=1.0)
                ax.fill_between(x, -wall_coordinates_0, -bounding_box_coordinate, color=original_wall_colour, alpha=1.0)
                ax.plot(x, np.zeros(len(x)), 'k--')
            else:
                # For subsequent frames, fill between the previous and current states
                wall_prev = wall_data[frame - 1]
                wall_next = wall_data[frame]
    
                fill1 = ax.fill_between(x, wall_prev, wall_next, color=updated_wall_colour, alpha=1.0)
                fill2 = ax.fill_between(x, -wall_prev, -wall_next, color=updated_wall_colour, alpha=1.0)
    
                # Add the new fills to the list
                current_fills.extend([fill1, fill2])
    
            return current_fills
    
        # Create the animation
        ani = FuncAnimation(fig, update, frames=len(wall_data), interval=500, blit=False, repeat=repeat_animation)
        plt.show()
        
        return ani
    

    # Call animation function with your data
    ani = animate_wall_evolution(list(wall_coords_by_folder.values()))
    ani.save('wall_evolution_animation.gif', fps=2, dpi=150)

