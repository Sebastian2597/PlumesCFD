 bo#!/bin/bash

# Define the source folder explicitly
SOURCE="./src/rhoCentralFoam_2ph_new"

# Check if source directory exists
if [ ! -d "$SOURCE" ]; then
    echo "Error: Source folder does not exist."
    exit 1
fi

# Set destination path
DEST="/usr/lib/openfoam/openfoam2406/applications/solvers/compressible/rhoCentralFoam_2ph"

# Remove existing folder if it exists
if [ -d "$DEST" ]; then
    echo "Removing existing folder: $DEST"
    rm -rf "$DEST"
fi

# Copy the folder recursively
cp -r "$SOURCE" "$DEST"

# Check if copy was successful
if [ "$?" -eq 0 ]; then
    echo "New folder copied successfully to $DEST"
else
    echo "Error: Failed to copy new folder."
    exit 1
fi

chmod -R +x "$DEST"

echo "Running Allwmake"
/usr/lib/openfoam/openfoam2406/applications/solvers/compressible/rhoCentralFoam_2ph/Allwclean
/usr/lib/openfoam/openfoam2406/applications/solvers/compressible/rhoCentralFoam_2ph/Allwmake

