# PlumesCFD

## Overview

- `PlumesCFD` is a module that runs multiple consecutive steady state two-phase water CFD simulations based on an adapted version of the Wet Steam Model implemented in ESI OpenCFD OpenFOAM that accounts for wall accretion and wall sublimation that updates the mesh accordingly outside of the CFD simulation. 
- This module is essentially a Coupled Wall Interactions CFD framework and can be used to simulate the flow in dynamic channels of icy moons that exhibit geyser phenomena such as Enceladus and Europa.
- This framework is intended to be modular so that it can be extended and improved for future use. 


## Assumptions
- Two-phase flow: pure water vapour & pure water ice
- Classical Nucleation Theory (CNT) for the calculation for the nucleation rate taken from water vapour to liquid water & applied correction from Wölk and Strey 2001.
- Grain growth based on a kinetic limited model developed by Gyarmathy 1976 and modified by Young 1982 applicable for low pressures (high Knudsen number) flows.
- Grains are assumed to be perfectly spherical and infinitely stiff.
- Only homogeneous nucleation is present as the timescale needed for foreign nuclei to serve as condensation surfaces far exceeds that of the channel expansion process. 
- Grains are assumed to be small enough that they travel at the speed of the surrounding vapour and therefore no momentum exchange. 
- No grain agglomeration occurs which is valid for cases with low mass fractions. 
- Effect of graviational forces on the flow and the grains are assumed to be negligible. 
- Wall accretion and wall sublimation have no effect on the boundary conditions.

## How to construct the repository

- OpenFOAM is a linux software, therefore in Windows, it is best to set this repository in Windows Subsystem for Linux. 
    ```
    $ git clone git@github.com:Sebastian2597/PlumesCFD.git
    ```
- External Programs
  - Users should install OpenFOAM from the ESI OpenCFD group: https://www.openfoam.com/news/main-news/openfoam-v2412
  - Users should install Gmsh for creating the mesh: https://gmsh.info/
  - Users should install ParaView for a GUI of post-processing the results: https://www.paraview.org/
  - Users should install pip3, python3 with its associated packages as well as pyvista and scipy.

## Repository structure

- The repository is composed of three main directories: `cases`, `postProcessing` and `src`. The `cases` directory contains all of the cases folders that the user wants to simulate, the `postProcessing` folder contains all of the python plotting for post-processing the simulation data, and `src` contains the python source files for the Coupled Wall interactions Framework including the Two-Phase OpenFOAM C++ code in the `solver` folder. 

- `cases`
|  - `baseline`
|  - `wall_interactions`
- `postProcessing`
- `src`
|  - `solver`

## How to create a case and set the simulation settings and the project-specific parameters

- Create a folder in the `cases` directory
- Copy the contents in the `baseline` as a reference
- Edit the `simulation_parameters` to configure how the mesh is constructed, 

## How to start the program

- To start the simulations run `./startSimulations.sh cases/xxx` insert the name of the case folder in "xxx".
- The OpenFOAM steady state simulations and python framework will run completely in the background and will output print statements to a log file located in the `cases` folder of interest.

## How to properly stop the program

- If the simulations have been started with `./startSimulations.sh cases/xxx` then you can simply stop by running 'stopSimulations.sh'.
- Or if an OpenFOAM simulation is running in the background then use:
    ```
    $ pkill -2 -u "$USER" -x mpirun
    ```
and check whether there are any lingering processes:
    ```
    $ ps -u $USER -f | grep -Ei 'foam|controlDict|python|watch|tail|bash'
    ```



