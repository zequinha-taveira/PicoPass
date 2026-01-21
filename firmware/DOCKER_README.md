# Docker Build Instructions

This directory contains a Docker-based build system for the PicoPass firmware. This allows you to compile the C/C++ firmware without manually installing the ARM toolchain or Pico SDK.

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop) installed and running.

## Usage

### Windows (PowerShell)

1. Open PowerShell and navigate to the `firmware` directory.
2. Run the build script:
   ```powershell
   .\build_docker.ps1
   ```

### Linux / WSL / macOS

1. Open a terminal and navigate to the `firmware` directory.
2. Make the script executable (only needed once):
   ```bash
   chmod +x build_docker.sh
   ```
3. Run the build script:
   ```bash
   ./build_docker.sh
   ```

## Output

After a successful build, the compiled `.uf2` binary will be located in:
`firmware/c/build/picopass.uf2` (or similar name depending on CMake configuration).

## Customizing the Build

The `Dockerfile` installs:
- `cmake`
- `gcc-arm-none-eabi`
- `pico-sdk` (latest master)

If you need additional libraries or tools, you can modify the `Dockerfile` and re-run the build script. The image will be rebuilt automatically if it doesn't exist, or you can manually rebuild it with `docker build -t picopass-builder .`.
