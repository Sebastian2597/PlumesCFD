# -*- coding: utf-8 -*-
"""
Created on Mon Mar 17 15:12:58 2025

@author: sebas
"""

from scipy.interpolate import splrep, splev
import numpy as np

def interpolateSpline(wall_coordinates, mesh_points, sample_points):
    
    x = wall_coordinates[:,0]
    y = mesh_points

    s = 1e-4 * len(x) * np.var(y)

    # Fit a spline y(x)
    tck = splrep(x, y, s=s)

    # Evaluate spline
    interpolated_y = splev(sample_points, tck)

    return interpolated_y

def update(filename, R_wall, N):

    with open(filename + '.geo', 'r') as file:
        lines = file.readlines()
    
    with open(filename + '.geo', 'w') as file:
        point_index = 1  # Start with Point(1)
    
        # Loop through the original lines to find the Points section
        for line in lines:
            # Check if the line contains a Point definition
            if line.startswith('Point'):
                if point_index <= N:  # We update only the first N points
                    # Extract the existing x and z coordinates from the line
                    parts = line.strip().split('{')[1].split('}')[0].split(',')
                    x_coord = parts[0].strip()
                    y_coord = parts[1].strip()
                    z_coord = parts[2].strip()
                    
                    # Get the updated y-coordinate for the current point
                    updated_y = float(y_coord) - R_wall[point_index - 1]
                    
                    # Write the updated point with the new y-coordinate
                    file.write(f"Point({point_index}) = {{{x_coord}, {updated_y}, {z_coord}, 1.0}};\n")
                    point_index += 1
                else:
                    # If more than N points, just copy the original point data
                    file.write(line)
            else:
                # If not a point line, copy the line unchanged
                file.write(line)    
            
    return
