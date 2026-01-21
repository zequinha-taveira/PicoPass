FROM ubuntu:22.04

# Install dependencies
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y \
    cmake \
    gcc-arm-none-eabi \
    libnewlib-arm-none-eabi \
    build-essential \
    python3 \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Pico SDK
WORKDIR /opt
RUN git clone https://github.com/raspberrypi/pico-sdk.git
ENV PICO_SDK_PATH=/opt/pico-sdk
WORKDIR /opt/pico-sdk
RUN git submodule update --init

# Set working directory for build
WORKDIR /workspace

# Default command to build
CMD ["/bin/bash", "-c", "cd firmware/c && mkdir -p build && cd build && cmake .. && make"]
