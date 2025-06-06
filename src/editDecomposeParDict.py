# -*- coding: utf-8 -*-
"""
Created on Fri Jun  6 16:13:24 2025

@author: sebas
"""

import re

def edit(n):
    filename = 'system/decomposeParDict'
    # Check if the file exists
    try:
        with open(filename, 'r') as file:
            pass
    except FileNotFoundError:
        print(f"File {filename} not found.")
        return
    with open(filename, 'r') as file:
        content = file.read()

    # Replace numberOfSubdomains
    content = re.sub(r'(numberOfSubdomains\s+)\d+;',
                 lambda m: f'{m.group(1)}{n};',
                 content)
                 
    # Factor and replace hierarchicalCoeffs n
    content = re.sub(r'n\s+\(\s*\d+\s+\d+\s+\d+\s*\);',
                     f'n               ({n} {1} {1});', content)

    with open(filename, 'w') as file:
        file.write(content)
