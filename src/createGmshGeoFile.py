# -*- coding: utf-8 -*-
"""
Created on Sun Apr 20 21:19:51 2025

@author: sebas
"""

import csv
import numpy as np


def create(csv_file, gmsh_file, vertical_divisions=86, horizontal_divisions=216):
    """
    Convert a CSV file of (x, y) coordinates into a Gmsh script with optimized transfinite mesh.

    Parameters:
    - csv_file: str, path to the input CSV file with x, y coordinates.
    - gmsh_file: str, path to the output Gmsh script file.
    - vertical_divisions: int, divisions for vertical lines.
    - horizontal_divisions: int, divisions for horizontal lines.
    """
    points = []

    # Read points from the CSV file
    with open(csv_file, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            try:
                x, y = map(float, row)
                points.append((x, y))
            except ValueError:
                print(f"Skipping invalid row: {row}")

    num_points = len(points)
    if num_points < 2:
        raise ValueError("At least 2 points are required to create lines.")
        


    # Calculate gradient changes to determine sections
    x_coords, y_coords = zip(*points)
    gradients = np.gradient(y_coords)
    section_boundaries = [0]  # Start at the first point

    for i in range(len(gradients) - 1):
        if np.sign(gradients[i + 1]) != np.sign(gradients[i]) and np.sign(gradients[i]) == -1:
            section_boundaries.append(i + 1)

    section_boundaries.append(num_points - 1)  # Include the last point
    num_sections = len(section_boundaries) - 1
  


    # Open Gmsh script file for writing
    with open(gmsh_file + '.geo', 'w') as file:
        
        file.write('SetFactory("OpenCASCADE");\n')
        
        # Write points from CSV
        for i, (x, y) in enumerate(points, start=1):
            file.write(f"Point({i}) = {{{x}, {y}, 0, 1.0}};\n")

        # Add symmetry points (horizontal base line points)
        symmetry_point_indices = []
        for i in range(num_sections + 1):
            symmetry_x = points[section_boundaries[i]][0]
            symmetry_point_index = num_points + 1 + i
            symmetry_point_indices.append(symmetry_point_index)
            file.write(f"Point({symmetry_point_index}) = {{{symmetry_x}, 0, 0, 1.0}};\n")

        # Create horizontal line segments through the data points
        horizontal_base_line_indices = []
        for i in range(num_sections):
            start_idx = section_boundaries[i] + 1
            end_idx = section_boundaries[i + 1] + 1
            line_idx = i + 1
            horizontal_base_line_indices.append(line_idx)
            file.write(f"Spline({line_idx}) = {{{start_idx}, {', '.join(map(str, range(start_idx + 1, end_idx + 1)))}}};\n")

        # Create vertical lines connecting symmetry points to data points
        vertical_line_indices = []
        for i, sym_idx in enumerate(symmetry_point_indices):
            if i == 0:
                vertical_line_idx = num_sections + i + 1
                vertical_line_indices.append(vertical_line_idx)
                file.write(f"Line({vertical_line_idx}) = {{{sym_idx}, 1}};\n")
            elif i == len(symmetry_point_indices) - 1:
                vertical_line_idx = num_sections + i + 1
                vertical_line_indices.append(vertical_line_idx)
                file.write(f"Line({vertical_line_idx}) = {{{sym_idx}, {num_points}}};\n")
            else:
                vertical_line_idx = num_sections + i + 1
                vertical_line_indices.append(vertical_line_idx)
                closest_point = section_boundaries[i] + 1
                file.write(f"Line({vertical_line_idx}) = {{{sym_idx}, {closest_point}}};\n")

        # Create horizontal lines connecting symmetry points
        horizontal_line_indices = []
        for i in range(len(symmetry_point_indices) - 1):
            line_idx = len(horizontal_base_line_indices) + len(vertical_line_indices) + i + 1
            horizontal_line_indices.append(line_idx)
            file.write(f"Line({line_idx}) = {{{symmetry_point_indices[i]}, {symmetry_point_indices[i + 1]}}};\n")

        # Create curve loops and surfaces for each section
        loop_index = 1
        surface_index = 1
        surface_indices = []  # Track surface indices for extrusion
        
        vertical_divisions_section = int(np.round(vertical_divisions / num_sections))

        for i in range(num_sections):
            
            curve_loop_lines = [
                horizontal_base_line_indices[i],
                -vertical_line_indices[i + 1],
                -horizontal_line_indices[i],
                vertical_line_indices[i],
            ]

            file.write(f"Curve Loop({loop_index}) = {{{', '.join(map(str, curve_loop_lines))}}};\n")
            file.write(f"Plane Surface({surface_index}) = {{{loop_index}}};\n")

            horizontal_divisions_section = int(np.round(horizontal_divisions * (section_boundaries[i + 1] - section_boundaries[i]) / (section_boundaries[-1])))
            
            
            # Assign progression to horizontal and vertical lines for each section
            progression_vertical = 0.935
            if i == 0:  # First section
                progression_horizontal = 0.995
                
                file.write(f"Transfinite Curve {{{horizontal_base_line_indices[i]}}} = {horizontal_divisions_section} Using Progression {progression_horizontal};\n")
                file.write(f"Transfinite Curve {{{horizontal_line_indices[i]}}} = {horizontal_divisions_section} Using Progression {progression_horizontal};\n")

            elif i == num_sections - 1:  # Last section
                progression_horizontal = 1.005
                
                file.write(f"Transfinite Curve {{{horizontal_base_line_indices[i]}}} = {horizontal_divisions_section} Using Progression {progression_horizontal};\n")
                file.write(f"Transfinite Curve {{{horizontal_line_indices[i]}}} = {horizontal_divisions_section} Using Progression {progression_horizontal};\n")
      
            else: 
                bump_horizontal = 0.93
                
                file.write(f"Transfinite Curve {{{horizontal_base_line_indices[i]}}} = {horizontal_divisions_section} Using Bump {bump_horizontal};\n")
                file.write(f"Transfinite Curve {{{horizontal_line_indices[i]}}} = {horizontal_divisions_section} Using Bump {bump_horizontal};\n")


            file.write(f"Transfinite Curve {{{vertical_line_indices[i + 1]}}} = {vertical_divisions_section} Using Progression {progression_vertical};\n")
            file.write(f"Transfinite Curve {{{vertical_line_indices[i]}}} = {vertical_divisions_section} Using Progression {progression_vertical};\n")
            file.write(f"Transfinite Surface {{{surface_index}}};\n")
            file.write(f"Recombine Surface {{{surface_index}}};\n")

            surface_indices.append(surface_index)
            loop_index += 1
            surface_index += 1


        # Extrude surfaces
        surface_indices_str = ", ".join(map(str, surface_indices))
        file.write(f"out[] = Extrude {{0, 0, 1}} {{Surface{{{surface_indices_str}}}; Layers{{1}}; Recombine;}};\n")

        # Write physical volumes and surfaces
        volume_entries = []
        outlet_entries = []
        outerwall_entries = []
        symmetry_entries = []
        lateral_entries = [f"{surface_indices[0]}"]  # Include original surface at front face

        for i in range(len(surface_indices)):
            base_idx = 6 * i
            if i == 0:
                volume_entries.append(f"out[{base_idx + 1}]")
            else:
                volume_entries.append(f"{i + 1}")

            # You can define the outlet as the top face of the last section
            if i == len(surface_indices) - 1:
                outlet_entries.append(f"out[{base_idx + 3}]")
            outerwall_entries.append(f"out[{base_idx + 2}]")
            symmetry_entries.append(f"out[{base_idx + 4}]")
            lateral_entries.append(f"out[{base_idx + 0}]")
            if i >= 1:
                lateral_entries.append(f"out[{base_idx + 1}]")


        file.write(f"Physical Volume(\"fluid\") = {{{', '.join(volume_entries)}}};\n")
        file.write("Physical Surface(\"inlet\") = {out[5]};\n")
        file.write(f"Physical Surface(\"outlet\") = {{{', '.join(outlet_entries)}}};\n")
        file.write(f"Physical Surface(\"outerwall\") = {{{', '.join(outerwall_entries)}}};\n")
        file.write(f"Physical Surface(\"longitudinal_symmetry\") = {{{', '.join(symmetry_entries)}}};\n")
        file.write(f"Physical Surface(\"lateral_sides\") = {{{', '.join(lateral_entries)}}};\n")

    return np.array(points)


