#!/bin/bash

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "Error: Docker is not running."
    exit 1
fi

# Build the Docker image
echo "Building Docker image..."
docker build -t picopass-builder .

# Run the container to build the firmware
echo "Compiling firmware..."
# Mount the parent directory to /workspace so we match the structure expected by the Dockerfile CMD
# The Dockerfile CMD expects `firmware/c`, so if we mount `firmware` to `/workspace/firmware`, it works.
# But we are inside `firmware/`.
# Let's mount the repo root.
PARENT_DIR=$(dirname $(pwd))
REPO_ROOT=$(basename $PARENT_DIR)

# Wait, simpler: mount current dir's parent (repo root) to /workspace
# The CMD is `cd firmware/c ...`
# So if we mount `c:\PicoPass` (repo root) to `/workspace`, then `firmware/c` exists.

cd ..
docker run --rm -v "$(pwd):/workspace" picopass-builder
