# -*- coding: utf-8 -*-
"""
Created on Fri Mar 14 14:14:45 2025

@author: sebas
"""

def edit():

    # Modify boundary file
    boundary_file = "constant/polyMesh/boundary"
    
    # Define the mapping of old patch names to new ones
    patch_types = {
        "lateral_sides": "empty",
        "outerwall": "wall",
        "longitudinal_symmetry": "symmetryPlane"
    }
    
    # Read the boundary file
    with open(boundary_file, "r") as file:
        lines = file.readlines()
    
    # Modify the boundary types
    with open(boundary_file, "w") as file:
        inside_patch = False
        current_patch = None
    
        for line in lines:
            stripped_line = line.strip()
    
            # Detect patch name
            if stripped_line in patch_types:
                inside_patch = True
                current_patch = stripped_line
    
            # Modify the type and physicalType fields if inside a known patch
            if inside_patch and ("type" in stripped_line):
                line = f"        type            {patch_types[current_patch]};\n"
                
            if inside_patch and ("physicalType" in stripped_line):
                line = f"        physicalType    {patch_types[current_patch]};\n        inGroups      1({patch_types[current_patch]});\n"
    
            # End patch section
            if stripped_line == "}":
                inside_patch = False
                current_patch = None
    
            file.write(line)
    
    print("Boundary file updated successfully!\n")
    
    return

