# firmware/micropython/display_manager.py
from machine import I2C, Pin
from lib.ssd1306 import SSD1306_I2C
import utime

class PicoPassDisplay:
    def __init__(self, scl_pin=17, sda_pin=16, width=128, height=64):
        try:
            # Standard I2C for Pico (I2C0 or I2C1)
            self.i2c = I2C(0, scl=Pin(scl_pin), sda=Pin(sda_pin), freq=400000)
            self.oled = SSD1306_I2C(width, height, self.i2c)
            self.active = True
            self.show_welcome()
        except Exception as e:
            print(f"OLED Init Error: {e}")
            self.active = False

    def clear(self):
        if self.active:
            self.oled.fill(0)
            self.oled.show()

    def show_welcome(self):
        if not self.active: return
        self.oled.fill(0)
        self.oled.text("PicoPass v1.0", 10, 10)
        self.oled.text("Ready to secure", 5, 30)
        self.oled.show()

    def _draw_lock_icon(self, x, y, size=10):
        # Draw a simple padlock
        self.oled.rect(x+2, y+size//2, size-4, size-size//2, 1) # Body
        self.oled.rect(x+3, y, size-6, size//2, 1) # Shackle
        self.oled.pixel(x+size//2, y+size//2+2, 0) # Keyhole

    def show_status(self, header, status, service=""):
        if not self.active: return
        self.oled.fill(0)
        
        # Header with background
        self.oled.fill_rect(0, 0, 128, 16, 1)
        self.oled.text(header, 5, 4, 0)
        
        # Lock icon in corner if relevant
        if header == "READY":
            self._draw_lock_icon(110, 3)
        
        # Service Info
        if service:
            self.oled.text("SERVICE:", 5, 24)
            self.oled.text(f"> {service[:14]}", 5, 36)
            self.oled.text(f"[{status}]", 5, 54)
        else:
            self.oled.text(status, 15, 34)
            
        self.oled.show()

    def show_locking(self):
        if not self.active: return
        self.oled.fill(0)
        self._draw_lock_icon(59, 20, 15)
        self.oled.text("VAULT LOCKED", 16, 42)
        self.oled.show()
