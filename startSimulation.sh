#!/bin/bash

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <case_directory>"
    exit 1
fi

CASE_DIR="$1"

if [ ! -d "$CASE_DIR" ]; then
    echo "Error: Directory '$CASE_DIR' does not exist."
    exit 1
fi

mkdir -p "${CASE_DIR%/}/logs"

LOGFILE="${CASE_DIR%/}/logs/simulation_$(date +%Y%m%d_%H%M%S).log"

echo "Starting simulation in background for case directory: $CASE_DIR"
echo "Logging output to: $LOGFILE"

# Pass the case path into Python and redirect all stdout+stderr from Python to the log file
nohup python3 src/runSimulation.py "$CASE_DIR" > "$LOGFILE" 2>&1 &
