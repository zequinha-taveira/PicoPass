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
echo "Compiling firmware for RP2350..."
# Mount the parent directory to /workspace so we match the structure expected by the Dockerfile CMD
cd ..
docker run --rm -v "$(pwd):/workspace" -e PICO_BOARD=pico2 -e PICO_PLATFORM=rp2350 picopass-builder
