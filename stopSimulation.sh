#!/bin/bash

pkill -f -u "$USER" runSimulation.py
pkill -2 -u "$USER" -x mpirun

echo "All simulation processes have been stopped."