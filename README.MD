# PlumesCFD

## Overview

- `S2E-AOBC-EXAMPLE` is an example of a project-specific repository of `S2E-AOBC`.
- Users can refer this repository to make their own simulation environment.
  - **NOTE**: Please rewrite words like `example` to suit your project and remove unnecessary descriptions in this document after you copy the repository.
- For other detailed descriptions, please also see README of [s2e-aobc](https://github.com/ut-issl/s2e-aobc)

## How to construct the repository

- `git submodule`
  - This repository includes the [s2e-aobc](https://github.com/ut-issl/s2e-aobc) with the `git submodule`. And the `s2e-aobc` also includes [s2e-core](https://github.com/ut-issl/s2e-core) as a submodule. Please use the following command to clone the repository recursively.
    ```
    $ git clone --recursive git@github.com:ut-issl/s2e-aobc-example.git
    ```
- External Libraries
  - Users can use `s2e-aobc-example/s2e-aobc/s2e-core/ExtLibraries/CMakeLists.txt` to download the external libraries.
  - Please find how to download the `ExtLibraries` in the [s2e-document](https://github.com/ut-issl/s2e-documents).
    - [How to build and execute with Visual Studio](https://github.com/ut-issl/s2e-documents/blob/develop/General/HowToCompileWithVisualStudio.md)
    - [How to compile with Ubuntu in Docker](https://github.com/ut-issl/s2e-documents/blob/develop/General/HowToCompileWithUbuntuInDocker.md)

## How to properly stop the program

- pkill -f -u "$USER" runSimulation.py
- pkill -2 -u "$USER" -x mpirun
- Run $ ps -u $USER -f | grep -Ei 'foam|controlDict|python|watch|tail|bash' to confirm that all processes have been successfully terminated. 



## How to change the simulation settings and the project-specific parameters

- In the `data/initialize_files` directory, there are `ini` files to define the simulation settings and the project-specific parameters.
- Please find the information of these parameters in the [s2e-document](https://github.com/ut-issl/s2e-documents).
  - [Getting Started](https://github.com/ut-issl/s2e-documents/blob/develop/Tutorials/GettingStarted.md)