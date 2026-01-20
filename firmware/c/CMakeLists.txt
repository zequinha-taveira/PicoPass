# == DO NOT EDIT THE FOLLOWING LINES for the Raspberry Pi Pico VS Code Extension to work ==
if(WIN32)
    set(USERHOME $ENV{USERPROFILE})
else()
    set(USERHOME $ENV{HOME})
endif()
set(sdkVersion 2.2.0)
set(toolchainVersion 14_2_Rel1)
set(picotoolVersion 2.2.0-a4)
set(picoVscode ${USERHOME}/.pico-sdk/cmake/pico-vscode.cmake)
if (EXISTS ${picoVscode})
    include(${picoVscode})
endif()
# ====================================================================================
set(PICO_BOARD pico CACHE STRING "Board type")

cmake_minimum_required(VERSION 3.13)

# Find the Pico SDK
include(pico_sdk_import.cmake)

project(picopass_firmware C CXX ASM)
set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 17)

# Initialize the SDK
pico_sdk_init()

add_executable(picopass
    main.c
    usb_descriptors.c
)

# Pull in common dependencies
target_link_libraries(picopass pico_stdlib tinyusb_device tinyusb_board)

# Enable USB and disable UART for stdio
pico_enable_stdio_usb(picopass 1)
pico_enable_stdio_uart(picopass 0)

# Create extra outputs (bin, hex, uf2)
pico_add_extra_outputs(picopass)
