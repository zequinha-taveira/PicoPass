# firmware/micropython/test_hid.py
# Note: This requires Adafruit HID library or CircuitPython firmware
import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS
from adafruit_hid.keycode import Keycode
import time

# Initialize keyboard
kbd = Keyboard(usb_hid.devices)
layout = KeyboardLayoutUS(kbd)

def type_password(password):
    print(f"Typing password via HID...")
    time.sleep(2) # Give user time to focus input
    layout.write(password)
    kbd.press(Keycode.ENTER)
    kbd.release_all()
    print("✅ HID Typing Complete")

if __name__ == "__main__":
    type_password("PicoPass123_Secure!")
