# -*- coding: utf-8 -*-
"""
Created on Tue Apr 22 23:11:02 2025

@author: sebas
"""

import numpy as np
import matplotlib.pyplot as plt
import re

  
def extract_internal_field_vectors(file_path):
    with open(file_path, 'r') as f:
        content = f.read()

    # Match internalField block
    internal_match = re.search(
        r'internalField\s+nonuniform\s+List<vector>\s+(\d+)\s*\((.*?)\)\s*;',
        content, re.DOTALL
    )

    if not internal_match:
        raise ValueError("No internalField block found.")

    vector_data = internal_match.group(2).strip()
    vector_lines = vector_data.split('\n')

    vectors = []
    for line in vector_lines:
        line = line.strip()
        if line.startswith('(') and line.endswith(')'):
            vector = tuple(map(float, line[1:-1].split()))
            vectors.append(vector)

    return np.array(vectors)


def extract_outerwall_vectors(file_path):
    with open(file_path, 'r') as f:
        content = f.read()

  
    outerwall_match = re.search(r'outerwall\s*\{(.*?)\}', content, re.DOTALL)
    if not outerwall_match:
        raise ValueError("No outerwall patch found.")

    outerwall_block = outerwall_match.group(1)

    value_match = re.search(r'value\s+(uniform|nonuniform)\s+(List<vector>\s+\d+\s*)?\((.*?)\)\s*;', outerwall_block, re.DOTALL)
    if not value_match:
        simple_match = re.search(r'value\s+uniform\s+\(([^)]+)\)\s*;', outerwall_block)
        if simple_match:
            vector = tuple(map(float, simple_match.group(1).split()))
            return np.array([vector])
        else:
            raise ValueError("No vector values found in outerwall patch.")

    vector_data = value_match.group(3).strip()
    vector_lines = vector_data.split('\n')

    vectors = []
    for line in vector_lines:
        line = line.strip()
        if line.startswith('(') and line.endswith(')'):
            vector = tuple(map(float, line[1:-1].split()))
            vectors.append(vector)

    return np.array(vectors)


def get_wall_cells(c_file_path, points_per_column):
    outerwall_vectors = extract_outerwall_vectors(c_file_path)
    internal_vectors = extract_internal_field_vectors(c_file_path)

    # Sort internal vectors by x then y
    sorted_indices = np.lexsort((internal_vectors[:, 1], internal_vectors[:, 0]))
    internal_sorted = internal_vectors[sorted_indices]

    x = internal_sorted[:, 0]

    top_wall_indices_in_original = []

    # Group into vertical slices
    for i in range(0, len(x), points_per_column - 1):
        col_indices = sorted_indices[i:i + points_per_column - 1]
        col_vectors = internal_vectors[col_indices]
        sorted_col_idx = np.argsort(col_vectors[:, 1])
        top_idx_in_col = col_indices[sorted_col_idx[-1]]  # Index of top-most point in original array
        top_wall_indices_in_original.append(top_idx_in_col)

    top_wall_indices = np.array(top_wall_indices_in_original)
    top_wall_cells = internal_vectors[top_wall_indices_in_original]

    return np.array(top_wall_cells), np.array(outerwall_vectors), np.array(top_wall_indices)

def compute_wall_cell_sizes(top_wall_cells, outerwall_vectors):
    # Cell height = vertical distance from outerwall point to top wall cell
    cell_heights = outerwall_vectors[:, 1] - top_wall_cells[:, 1]

    # Cell length = average horizontal spacing between adjacent top wall + outerwall cells
    cell_lengths = np.zeros(len(top_wall_cells))
    for i in range(len(top_wall_cells)):
        if i == 0:
            cell_lengths_top = np.linalg.norm(top_wall_cells[i + 1] - top_wall_cells[i])
            cell_lengths_outerwall = np.linalg.norm(outerwall_vectors[i + 1] - outerwall_vectors[i])
        elif i == len(top_wall_cells) - 1:
            cell_lengths_top = np.linalg.norm(top_wall_cells[i] - top_wall_cells[i - 1])
            cell_lengths_outerwall = np.linalg.norm(outerwall_vectors[i] - outerwall_vectors[i - 1])
        else:
            left_top = np.linalg.norm(top_wall_cells[i] - top_wall_cells[i - 1])
            right_top = np.linalg.norm(top_wall_cells[i + 1] - top_wall_cells[i])
            cell_lengths_top = 0.5 * (left_top + right_top)

            left_outerwall = np.linalg.norm(outerwall_vectors[i] - outerwall_vectors[i - 1])
            right_outerwall = np.linalg.norm(outerwall_vectors[i + 1] - outerwall_vectors[i])
            cell_lengths_outerwall = 0.5 * (left_outerwall + right_outerwall)

        # Final averaged cell length
        cell_lengths[i] = 0.5 * (cell_lengths_top + cell_lengths_outerwall)

    return cell_lengths, cell_heights

def read_static_field(field_file, top_wall_indices):
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
                
    return np.array(values)[top_wall_indices] if values else float('nan')


def read_vector_field(field_file, top_wall_indices):
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
    
    return np.array(values)[top_wall_indices] if values else float('nan')


# def compute_smooth_wall_normals(points, num_eval_points=1000000):
#     from scipy.interpolate import splprep, splev
#     x = points[:, 0]
#     y = points[:, 1]

#     # Fit a parametric B-spline (x(t), y(t))
#     tck, _ = splprep([x, y], s=0)

#     u = np.linspace(0, 1, num_eval_points)

#     # Evaluate spline and its derivative
#     x_spline, y_spline = splev(u, tck)
#     dx, dy = splev(u, tck, der=1)

#     # Normalize tangents and compute normals
#     tangents = np.vstack((dx, dy)).T
#     tangents /= np.linalg.norm(tangents, axis=1)[:, np.newaxis]

#     normals = np.column_stack([-tangents[:, 1], tangents[:, 0]])  # Rotate CCW

#     wall_coords = np.column_stack((x_spline, y_spline))

#     return wall_coords, normals





    
# top_wall_cells, internal, outerwall, top_wall_indices = get_top_wall_cells("C", points_per_column=43)

# cell_lengths, cell_heights = compute_top_cell_sizes(top_wall_cells, outerwall)

# # plt.figure(figsize=(10, 6))

# # plt.scatter(outerwall[:, 0], outerwall[:, 1], label='Outerwall Patch')
# # plt.scatter(top_wall_cells[:, 0], top_wall_cells[:, 1], label='Top Wall Cells')
# # plt.scatter(internal[top_wall_indices,0], internal[top_wall_indices,1], s=12)
# # plt.scatter(internal[:, 0], internal[:, 1], s=2, label='Internal Cells')
# # plt.xlabel("x")
# # plt.ylabel("y")
# # plt.title("Top Wall Cell Detection")
# # plt.legend()
# # plt.grid(True)
# # plt.show()

# # Overlay rectangles representing each top cell
# for i in range(len(top_wall_cells)):
#     x_center = top_wall_cells[i, 0]
#     y_top = top_wall_cells[i, 1] * 100
#     height = cell_heights[i] * 100
#     length = cell_lengths[i]

#     # Rectangle centered at x_center, y_top - height
#     x_left = x_center - length / 2
#     y_bottom = y_top
#     rect = plt.Rectangle((x_left, y_bottom), length, height,
#                          linewidth=1, edgecolor='red', facecolor='none')
#     plt.gca().add_patch(rect)

# # Redraw the plot with rectangles
# #plt.figure(figsize=(10, 6))
# plt.scatter(outerwall[:, 0], outerwall[:, 1]  * 100, label='Outerwall Patch')
# #plt.plot(outerwall[:, 0], outerwall[:, 1])
# plt.scatter(top_wall_cells[:, 0], top_wall_cells[:, 1]  * 100, label='Top Wall Cells')
# plt.scatter(internal[top_wall_indices, 0], internal[top_wall_indices, 1]  * 100, s=12)
# plt.scatter(internal[:, 0], internal[:, 1]  * 100, s=2, label='Internal Cells')
# plt.xlabel("x")
# plt.ylabel("y")
# plt.title("Top Wall Cells with Cell Size Rectangles")
# plt.legend()
# plt.grid(True)

# # Add cell rectangles
# for i in range(len(top_wall_cells)):
#     x_center = top_wall_cells[i, 0]
#     y_top = top_wall_cells[i, 1]
#     height = cell_heights[i]
#     length = cell_lengths[i]

#     x_left = x_center - length / 2
#     y_bottom = y_top
#     rect = plt.Rectangle((x_left, y_bottom), length, height,
#                          linewidth=1, edgecolor='red', facecolor='none')
#     plt.gca().add_patch(rect)

# plt.show()

# wall_coords, normals = compute_smooth_wall_normals(outerwall)


# wall_coords = wall_coords[::1000]
# normals = normals[::1000]

# plt.plot(wall_coords[:,0], wall_coords[:,1] * 100, marker = 'o', markersize = 4, color = 'purple')

# plt.quiver(wall_coords[:, 0], wall_coords[:, 1] * 100,
#             normals[:, 0], normals[:, 1],
#             color='blue', scale=300, width = 0.0001, label='Wall Normals', units ='xy', angles = 'xy')
# scale = 0.01  # Adjust the scale for visual clarity
# for (x, y), (nx, ny) in zip(wall_coords, normals):
#     plt.plot([x, x + nx * scale], [(y) * 100, (y * 100+ ny * scale)], color='black')

# plt.xlabel("x")
# plt.ylabel("y")
# plt.title("Outerwall Normals")
# plt.legend()
# #plt.axis('equal')
# plt.grid(True)
# plt.show()

