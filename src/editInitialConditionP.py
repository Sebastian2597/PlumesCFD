# -*- coding: utf-8 -*-
"""
Created on Wed Jan 29 16:42:07 2025

@author: sebas
"""

import numpy as np

def edit(number_of_cells, pressure_values):
    
    pressure_BC_file = "0/p"
    all_lines = []
    
    with open(pressure_BC_file, "r") as file:
        lines = file.readlines()
    
    # Modify the boundary types
    with open(pressure_BC_file, "w") as file:
        #number_of_cells = 18000
        first_lines = lines[:21]
        first_lines.append(str(number_of_cells) + '\n(\n')
        
        last_lines = lines[-34:]
        
        n_int = int(np.ceil(number_of_cells / len(pressure_values)))
        pressure_lines = []
        j = 0
        for i in range(1, number_of_cells + 1):
            pressure_lines.append(str(pressure_values[j]) + "\n")
            if i % n_int == 0:
                j+= 1
                
        all_lines = first_lines + pressure_lines + last_lines
        
        for line in all_lines:
            file.write(line)
        
    return


