# firmware/micropython/device.py
# PicoPass Device Controller
# Dynamic configuration from license manager

import machine
import utime
import sys
import uselect
import gc
import json

try:
    import rp2
    HAS_RP2 = True
except:
    HAS_RP2 = False

from license import LicenseManager

# Optional imports - fail gracefully if not available
try:
    from ble_hid import BLEKeyboard
    HAS_BLE = True
except:
    HAS_BLE = False
    BLEKeyboard = None

try:
    from display_manager import PicoPassDisplay
    HAS_DISPLAY = True
except:
    HAS_DISPLAY = False
    PicoPassDisplay = None


class PicoPassHID:
    """USB HID Keyboard emulation."""
    
    def __init__(self):
        self.enabled = False
        try:
            import usb_hid
            from adafruit_hid.keyboard import Keyboard
            from adafruit_hid.keycode import Keycode
            self.kbd = Keyboard(usb_hid.devices)
            self.Keycode = Keycode
            self.enabled = True
        except:
            self.kbd = None
            self.Keycode = None

    def type_text(self, text):
        """Type text character by character."""
        if not self.enabled or not self.kbd:
            print("HID not available, simulating type")
            return
        
        from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS
        layout = KeyboardLayoutUS(self.kbd)
        
        for char in text:
            try:
                layout.write(char)
                utime.sleep(0.02)  # Small delay between chars
            except Exception as e:
                print(f"HID error: {e}")


class PicoPassDevice:
    """Main PicoPass device controller."""
    
    VERSION = "2.0.0"
    
    def __init__(self):
        # Initialize license manager first
        self.license = LicenseManager()
        
        # Get hardware configuration
        hw_config = self.license.apply_config()
        
        # Store config for reference
        self.hw_config = hw_config
        
        # GPIO Initialization with dynamic config
        led_gpio = hw_config.get("led_gpio", 25)
        self.led_inverted = hw_config.get("led_inverted", False)
        self.led = machine.Pin(led_gpio, machine.Pin.OUT)
        
        btn_gpio = hw_config.get("btn_gpio", 15)
        btn_pull_str = hw_config.get("btn_pull", "UP")
        if btn_pull_str == "UP":
            pull_mode = machine.Pin.PULL_UP
        elif btn_pull_str == "DOWN":
            pull_mode = machine.Pin.PULL_DOWN
        else:
            pull_mode = None
        
        self.btn_action = machine.Pin(btn_gpio, machine.Pin.IN, pull_mode)
        
        # Components
        self.hid = PicoPassHID()
        
        # Optional display
        if HAS_DISPLAY and hw_config.get("has_display", False):
            sda = hw_config.get("display_sda", 16)
            scl = hw_config.get("display_scl", 17)
            self.display = PicoPassDisplay(scl_pin=scl, sda_pin=sda)
        else:
            self.display = None
        
        # Optional BLE
        if HAS_BLE:
            self.ble = BLEKeyboard(name="PicoPass-Pro")
        else:
            self.ble = None
        
        # State
        self.activated = self.license.verify_license()
        self.locked = True
        self.pending_password = None
        self.pending_service = None
        
        # Serial Polling
        self.poll = uselect.poll()
        self.poll.register(sys.stdin, uselect.POLLIN)

    def led_on(self):
        """Turn LED on (respects polarity)."""
        self.led.value(0 if self.led_inverted else 1)

    def led_off(self):
        """Turn LED off (respects polarity)."""
        self.led.value(1 if self.led_inverted else 0)

    def blink(self, times=1, delay=0.1):
        """Blink LED n times."""
        for _ in range(times):
            self.led_on()
            utime.sleep(delay)
            self.led_off()
            utime.sleep(delay)

    def show_status(self, title, message, extra=None):
        """Show status on display if available."""
        if self.display:
            self.display.show_status(title, message, extra)
        print(f"[{title}] {message}" + (f" ({extra})" if extra else ""))

    def handle_serial(self):
        """Process incoming serial commands."""
        if not self.poll.poll(0):
            return
        
        try:
            line = sys.stdin.readline().strip()
        except:
            return
        
        if not line:
            return
        
        # PING - Device discovery
        if line == "PING":
            response = self.license.get_status_response()
            print(response)
        
        # ACTIVATE:key - Activate with license key
        elif line.startswith("ACTIVATE:"):
            key = line[9:].strip()
            if self.license.validate_activation_key(key):
                self.license.save_license(key)
                self.activated = True
                print("OK|ACTIVATION_SUCCESS")
                self.show_status("SUCCESS", "Device Activated")
            else:
                print("ERROR|INVALID_KEY")
                self.show_status("ERROR", "Invalid Key")
        
        # CONFIG:json - Receive configuration
        elif line.startswith("CONFIG:"):
            try:
                config_json = line[7:]
                config = json.loads(config_json)
                if self.license._save_config(config):
                    print("OK|CONFIG_SAVED")
                    self.show_status("SUCCESS", "Config Saved")
                    # Note: Config changes require restart to apply
                else:
                    print("ERROR|CONFIG_SAVE_FAILED")
            except Exception as e:
                print(f"ERROR|CONFIG_PARSE_FAILED|{e}")
        
        # TYPE:password|service - Prepare password for typing
        elif line.startswith("TYPE:"):
            if not self.activated:
                print("ERROR|NOT_ACTIVATED")
                self.show_status("LOCKED", "Activate First")
                return
            
            # Protocol: TYPE:password_content|service_name
            content = line[5:]
            if '|' in content:
                parts = content.split('|', 1)
                self.pending_password = parts[0]
                self.pending_service = parts[1] if len(parts) > 1 else "External"
            else:
                self.pending_password = content
                self.pending_service = "External"
            
            self.show_status("READY", "Press Button", self.pending_service)
            self.blink(2)
            print("OK|READY_TO_TYPE")
        
        # LOCK - Lock the device
        elif line == "LOCK":
            self.locked = True
            self.pending_password = None
            self.pending_service = None
            self.show_status("LOCKED", "Device Locked")
            print("OK|LOCKED")
        
        # INFO - Get device info
        elif line == "INFO":
            info = self.license.get_info()
            print(f"INFO|{json.dumps(info)}")
        
        # RESET - Factory reset
        elif line == "RESET":
            self.license.reset()
            self.activated = False
            print("OK|RESET_COMPLETE")
            self.show_status("RESET", "Factory Reset")
        
        # VERSION - Get firmware version
        elif line == "VERSION":
            print(f"VERSION|{self.VERSION}")
        
        else:
            print(f"ERROR|UNKNOWN_COMMAND|{line}")

    def check_button(self):
        """Check if action button is pressed."""
        # Check external button (active low for PULL_UP)
        pull = self.hw_config.get("btn_pull", "UP")
        if pull == "UP":
            button_pressed = not self.btn_action.value()
        else:
            button_pressed = self.btn_action.value()
        
        # Also check BOOTSEL button on RP2 boards
        bootsel_pressed = False
        if HAS_RP2:
            try:
                bootsel_pressed = rp2.bootsel_button()
            except:
                pass
        
        return button_pressed or bootsel_pressed

    def wait_button_release(self):
        """Wait for button release (debounce)."""
        while self.check_button():
            utime.sleep(0.01)

    def type_password(self):
        """Type the pending password."""
        if not self.pending_password:
            return False
        
        self.show_status("TYPING", "Processing...")
        self.blink(1, 0.3)
        
        # USB HID first
        if self.hid.enabled:
            self.hid.type_text(self.pending_password)
        
        # BLE if connected
        if self.ble and self.ble.is_connected():
            self.ble.type_text(self.pending_password)
        
        # Security: Clear password
        service = self.pending_service
        self.pending_password = None
        self.pending_service = None
        gc.collect()
        
        self.show_status("SUCCESS", "Typed!", service)
        print("OK|TYPING_DONE")
        
        utime.sleep(1.5)
        return True

    def run(self):
        """Main loop."""
        print(f"PicoPass v{self.VERSION} Starting...")
        print(f"Board: {self.license.board_type}")
        print(f"Serial: {self.license.board_id}")
        print(f"Activated: {self.activated}")
        
        self.blink(3)
        self.show_status("PicoPass", "System Ready")
        
        while True:
            # Handle serial commands
            self.handle_serial()
            
            # Check button press
            if self.check_button():
                if self.pending_password:
                    self.type_password()
                else:
                    # Blink error - no password pending
                    self.show_status("ERROR", "No Password")
                    self.blink(5, 0.05)
                    utime.sleep(0.5)
                    self.show_status("PicoPass", "Ready")
                
                # Debounce
                self.wait_button_release()
            
            # Small delay
            utime.sleep(0.01)


if __name__ == "__main__":
    device = PicoPassDevice()
    device.run()
