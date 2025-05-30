# -*- coding: utf-8 -*-
"""
Created on Wed Jan 29 16:42:07 2025

@author: sebas
"""

import numpy as np
import re

def read_cell_centers():
    filepath = "0/C"
    with open(filepath, 'r') as f:
        lines = f.readlines()

    # Find the start of the internalField list
    for i, line in enumerate(lines):
        if 'internalField' in line and 'nonuniform' in line:
            size_line_index = i + 1
            break
    else:
        raise ValueError("No nonuniform internalField found in file.")

    # Read number of entries
    size = int(lines[size_line_index].strip())

    # Find start and end of vector list
    data_start = size_line_index + 2
    data_end = data_start + size

    # Read the vector data
    vector_data = []
    for line in lines[data_start:data_end]:
        vec_str = line.strip().strip('()')
        vec = tuple(map(float, vec_str.split()))
        vector_data.append(vec)
        
    cell_centers_x = np.array(vector_data)[:,0]

    return cell_centers_x

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




def edit(field, field_values):
    BC_file = "0/" + field

    with open(BC_file, "r") as f:
        content = f.read()

    # Patterns for replacing internalField
    pattern_uniform = r'internalField\s+uniform\s+\([^\)]+\);' if field == 'U' else r'internalField\s+uniform\s+[\d\.Ee+-]+;'
    pattern_nonuniform = (
        r'internalField\s+nonuniform\s+List<vector>\s+\d+\s*\(.*?\)\s*;'
        if field == 'U' else
        r'internalField\s+nonuniform\s+List<scalar>\s+\d+\s*\(.*?\)\s*;'
    )

    # Construct replacement block
    if field == 'U':
        values_str = '\n'.join(f"({v} 0 0)" for v in field_values)
        new_internal = (
            f"internalField   nonuniform List<vector>\n"
            f"{len(field_values)}\n(\n{values_str}\n);\n"
        )
    else:
        values_str = '\n'.join(str(v) for v in field_values)
        new_internal = (
            f"internalField   nonuniform List<scalar>\n"
            f"{len(field_values)}\n(\n{values_str}\n);\n"
        )

    # Replace nonuniform if present
    new_content, n_subs = re.subn(pattern_nonuniform, new_internal, content, flags=re.DOTALL)
    
    # If not found, try replacing uniform
    if n_subs == 0:
        new_content, n_subs = re.subn(pattern_uniform, new_internal, content)

    # Write back only if replacement succeeded
    if n_subs > 0:
        with open(BC_file, "w") as f:
            f.write(new_content)
    else:
        raise ValueError("Failed to locate and replace internalField block.")


