#!/bin/bash

pkill -f -u "$USER" runSimulation.py
pkill -2 -u "$USER" -x mpirun
