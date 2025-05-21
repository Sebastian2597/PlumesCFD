# -*- coding: utf-8 -*-
"""
Created on Wed Apr 30 14:58:21 2025

@author: sebas
"""

import numpy as np

def edit(boundary_condition_type, number_of_wall_points, temperature_inlet, temperature_outlet):
    temperature_BC_file = "./0/T"
    
    with open(temperature_BC_file, "r") as file:
        lines = file.readlines()

    new_lines = []
    inside_outerwall = False
    for i, line in enumerate(lines):
        if "outerwall" in line:
            new_lines.append(line)
            inside_outerwall = True
            if boundary_condition_type == 'fixedValue':
                new_lines.append("    {\n")
                new_lines.append("        type            fixedValue;\n")
                new_lines.append("        value           nonuniform List<scalar>\n")
                new_lines.append("        (\n")
                temperatures = np.linspace(temperature_inlet, temperature_outlet, number_of_wall_points)
                for t in temperatures:
                    new_lines.append(f"            {t:.6f}\n")
                new_lines.append("        );\n")
                new_lines.append("    }\n")
            elif boundary_condition_type == 'zeroGradient':
                new_lines.append("    {\n")
                new_lines.append("        type            zeroGradient;\n")
                new_lines.append("    }\n")
        elif inside_outerwall:
            if "}" in line:
                inside_outerwall = False
        else:
            new_lines.append(line)

    with open(temperature_BC_file, "w") as file:
        file.writelines(new_lines)

    return
