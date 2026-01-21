# firmware/c/CMakeLists.txt

cmake_minimum_required(VERSION 3.13)

# Include Pico SDK
include($ENV{PICO_SDK_PATH}/external/pico_sdk_import.cmake)

project(picopass C CXX ASM)
set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 17)

pico_sdk_init()

# Executable
add_executable(picopass
    src/main.c
    src/picopass.c
    src/crypto.c
    src/usb_hid.c
    src/led.c
    src/button.c
    src/flash_storage.c
    src/serial.c
    usb_descriptors.c
)

# Include directories
target_include_directories(picopass BEFORE PRIVATE
    ${CMAKE_SOURCE_DIR}/include
)

# Libraries
target_link_libraries(picopass
    pico_stdlib
    pico_unique_id
    hardware_flash
    hardware_sync
    hardware_pwm
    hardware_gpio
    hardware_adc
    tinyusb_device
    tinyusb_board
    pico_mbedtls
)

# USB output
pico_enable_stdio_usb(picopass 0)
pico_enable_stdio_uart(picopass 1)

# Create UF2
pico_add_extra_outputs(picopass)

# Set output name
set_target_properties(picopass PROPERTIES
    OUTPUT_NAME "picopass"
)
