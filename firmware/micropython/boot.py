# firmware/micropython/boot.py
# Boot configuration for PicoPass
# Handles USB configuration if supported by firmware/platform

import machine
import json
import os

CONF_FILE = "device.cfg"
LED_PIN = 25

def blink_error():
    led = machine.Pin(LED_PIN, machine.Pin.OUT)
    for _ in range(3):
        led.value(1)
        machine.delay(100)
        led.value(0)
        machine.delay(100)

def load_config():
    try:
        with open(CONF_FILE, "r") as f:
            return json.load(f)
    except:
        return None

# Try to configure USB if running on CircuitPython or custom MicroPython
# This is platform-dependent
try:
    import usb_cdc
    import usb_hid
    import storage
    
    # Check if we should customize USB
    config = load_config()
    if config:
        # Disable drive if configured (security feature)
        # storage.disable_usb_drive() 
        
        # Configure USB HID Name if supported
        # Note: Standard CircuitPython mostly relies on compile-time or 'usb_hid' module enables
        pass
        
    print("Boot configuration applied")
    
except ImportError:
    # Standard MicroPython
    pass
