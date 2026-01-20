# firmware/micropython/keyboard.py
import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS
from adafruit_hid.keycode import Keycode
import time

class PicoPassHID:
    def __init__(self):
        try:
            self.kbd = Keyboard(usb_hid.devices)
            self.layout = KeyboardLayoutUS(self.kbd)
            self.active = True
        except Exception as e:
            print(f"HID Init Error: {e}")
            self.active = False

    def type_text(self, text, press_enter=True):
        if not self.active:
            print("HID not active")
            return
        
        # Small delay to ensure host is ready
        time.sleep(0.5)
        
        try:
            self.layout.write(text)
            if press_enter:
                self.kbd.press(Keycode.ENTER)
                self.kbd.release_all()
        except Exception as e:
            print(f"Typing Error: {e}")

    def press_sequence(self, keys):
        """Press a sequence of keycodes (e.g. [Keycode.CONTROL, Keycode.ALT, Keycode.DELETE])"""
        try:
            for key in keys:
                self.kbd.press(key)
            self.kbd.release_all()
        except Exception as e:
            print(f"Sequence Error: {e}")
