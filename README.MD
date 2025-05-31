# PlumesCFD

## Overview

- 'PlumesCFD' is a module that runs multiple consecutive steady state two-phase water CFD simulations based on an adapted version of the Wet Steam Model implemented in ESI OpenCFD OpenFOAM that accounts for wall accretion and wall sublimation that updates the mesh accordingly outside of the CFD simulation. 
- This module can be used to simulate the flow in the channels of icy moons that exhibit geyser phenomena such as Enceladus and Europa.
- 


## Assumptions
- Two-phase flow: pure water vapour & pure water ice
- 

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
- 

## How to change the simulation settings and the project-specific parameters

- 

## How to start the program

- To start the simulations run 'startSimulation.sh'. 

## How to properly stop the program

- If the simulations have been started with 'startSimulation.sh' then you can simply stop by running 'stopSimulations.sh'.
- If an OpenFOAM simulation is running in the background then use:
    ```
    $ pkill -2 -u "$USER" -x mpirun
    ```
and check whether there are any lingering processes:
    ```
    $ ps -u $USER -f | grep -Ei 'foam|controlDict|python|watch|tail|bash'
    ```



