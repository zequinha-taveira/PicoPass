# firmware/micropython/device.py
import machine
import utime
import sys
import uselect
import rp2
import gc
from ble_hid import BLEKeyboard
from display_manager import PicoPassDisplay
from license import LicenseManager

class PicoPassDevice:
    def __init__(self, led_pin=25, btn_pin=15, sda_pin=16, scl_pin=17):
        # Hardware Configuration
        self.pins = {
            "led": led_pin,
            "btn": btn_pin,
            "sda": sda_pin,
            "scl": scl_pin
        }

        # GPIO Initialization
        self.led = machine.Pin(self.pins["led"], machine.Pin.OUT)
        self.btn_action = machine.Pin(self.pins["btn"], machine.Pin.IN, machine.Pin.PULL_UP)
        
        # Components
        self.hid = PicoPassHID()
        self.display = PicoPassDisplay(scl_pin=self.pins["scl"], sda_pin=self.pins["sda"])
        self.ble = BLEKeyboard(name="PicoPass-Pro")
        self.license = LicenseManager()
        
        # State
        self.activated = self.license.verify_license()
        self.locked = True
        self.pending_password = None
        
        # Serial Polling
        self.poll = uselect.poll()
        self.poll.register(sys.stdin, uselect.POLLIN)

    def blink(self, times=1, delay=0.1):
        for _ in range(times):
            self.led.value(1)
            utime.sleep(delay)
            self.led.value(0)
            utime.sleep(delay)

    def handle_serial(self):
        if self.poll.poll(0):
            line = sys.stdin.readline().strip()
            if not line: return
            
            if line == "PING":
                status = "ACTIVATED" if self.activated else "NOT_ACTIVATED"
                print(f"PONG|{status}|{self.license.board_id}|{self.license.board_type}")
            elif line.startswith("ACTIVATE:"):
                key = line[9:].strip()
                if self.license._calculate_key(self.license.board_id, self.license.board_type) == key:
                    self.license.save_license(key)
                    self.activated = True
                    print("ACTIVATION_SUCCESS")
                    self.display.show_status("SUCCESS", "Activated!")
                else:
                    print("ACTIVATION_FAILED")
                    self.display.show_status("ERROR", "Invalid Key")
            elif line.startswith("TYPE:"):
                if not self.activated:
                    print("ERROR_NOT_ACTIVATED")
                    self.display.show_status("LOCKED", "Activate First")
                    return
                # Protocol: TYPE:password_content|service_name
                parts = line[5:].split('|')
                self.pending_password = parts[0]
                service_name = parts[1] if len(parts) > 1 else "External"
                
                self.display.show_status("READY", "Press Button", service_name)
                self.blink(2)
                print("READY_TO_TYPE")
            elif line == "LOCK":
                self.locked = True
                self.display.show_locking()
                print("LOCKED")

    def run(self):
        print("PicoPass Pro v1.1 Starting...")
        self.blink(3)
        self.display.show_status("PicoPass Pro", "System Ready")
        
        while True:
            self.handle_serial()
            
            # Check button press for typing (External OR BOOTSEL)
            if not self.btn_action.value() or rp2.bootsel_button(): 
                if self.pending_password:
                    self.display.show_status("TYPING", "Processing...")
                    self.blink(1, 0.5)
                    
                    # Hybrid Mode: Try USB HID first, then BLE if connected
                    self.hid.type_text(self.pending_password)
                    if self.ble.is_connected():
                        self.ble.type_text(self.pending_password)
                    
                    # Security: Zero out the password buffer and trigger GC
                    self.pending_password = None
                    gc.collect() 
                    
                    self.display.show_status("SUCCESS", "Vault Secure")
                    print("TYPING_DONE")
                    utime.sleep(2)
                    self.display.show_welcome()
                else:
                    # Blink error if no password pending
                    self.display.show_status("ERROR", "No Password")
                    self.blink(5, 0.05)
                    utime.sleep(1)
                    self.display.show_welcome()
                
                # Debounce: wait for release of both buttons
                while not self.btn_action.value() or rp2.bootsel_button():
                    utime.sleep(0.01)

            # Check BLE connectivity changes for visual feedback
            # (Future: can add a small BLE icon to display)

            utime.sleep(0.01)

if __name__ == "__main__":
    device = PicoPassDevice()
    device.run()
