# -*- coding: utf-8 -*-
"""
Created on Sun Apr 27 20:35:21 2025

@author: sebas
"""

def initialise(field_name, num_cells):
    header = f"""/*--------------------------------*- C++ -*----------------------------------*\\
| =========                 |                                                 |
| \\\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\\\    /   O peration     | Version:  v2012                                 |
|   \\\\  /    A nd           | Website:  www.openfoam.com                      |
|    \\\\/     M anipulation  |                                                 |
\\*---------------------------------------------------------------------------*/
FoamFile
{{
    version     2.0;
    format      ascii;
    class       volScalarField;
    location    "0";
    object      {field_name};
}}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

dimensions      [1 -3 -1 0 0 0 0];


internalField   nonuniform List<scalar> 
{num_cells}
(
"""
    boundary_field = """)
;
boundaryField
{
    inlet
    {
        type            fixedValue;
        value           uniform 0;
    }
    outlet				
    {
        type            fixedValue;
        value           uniform 0;
    }
    outerwall				
    {
        type            zeroGradient;
    }
    longitudinal_symmetry
    {
        type            symmetryPlane;
    }
    lateral_sides
    {
        type            empty;
    }
}
"""

    with open('./0/' + field_name, 'w') as f:
        f.write(header)
        for _ in range(num_cells):
            f.write('0\n')
        f.write(boundary_field)
        

def update(field_name, indices, new_values):
    # Read the whole file
    with open('./0/' + field_name, 'r') as f:
        lines = f.readlines()

    # Find the start and end of the internalField list
    try:
        start_index = next(i for i, line in enumerate(lines) if '(' in line and 'internalField' not in line) + 1
        end_index = next(i for i, line in enumerate(lines[start_index:], start=start_index) if ')' in line)
    except StopIteration:
        raise ValueError("Could not find internalField list in the file.")

    # Update the required indices
    for idx, val in zip(indices, new_values):
        if idx < 0 or idx >= (end_index - start_index):
            raise IndexError(f"Cell index {idx} out of range (0 to {end_index - start_index - 1}).")
        lines[start_index + idx] = f"{val}\n"

    # Write back to the file
    with open('./0/' + field_name, 'w') as f:
        f.writelines(lines)