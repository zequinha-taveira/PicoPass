# firmware/micropython/hid_keyboard.py

import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode
import time

class USBKeyboard:
    """Controlador de teclado USB HID"""
    
    def __init__(self):
        try:
            self.keyboard = Keyboard(usb_hid.devices)
            self.enabled = True
        except:
            print("USB HID not available")
            self.enabled = False
            self.keyboard = None
        
        self.delay_between_keys = 0.01  # 10ms
    
    def type_string(self, text):
        """Digita uma string completa"""
        if not self.enabled: return
        
        for char in text:
            self.type_char(char)
            time.sleep(self.delay_between_keys)
    
    def type_char(self, char):
        """Digita um caractere"""
        if not self.enabled: return
        
        from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS
        
        # Simple fallback implementation if layout not fully available
        # or use specific keycodes
        if char == '\n':
            self.keyboard.send(Keycode.ENTER)
        elif char == '\t':
            self.keyboard.send(Keycode.TAB)
        else:
            try:
                # Use layout if possible, or basic write
                # Note: adafruit_hid usually needs Layout class for ASCII->Keycode
                # We'll assume a basic write method or create layout instance if needed
                # For this implementation, we assume `keyboard.write` isn't standard in adafruit_hid
                # but let's stick to the requested code which used `keyboard.write(char)` in the else block
                # The user's code had: self.keyboard.write(char)
                # adafruit_hid.keyboard.Keyboard has .write()? No, Layout has .write().
                # I will create a layout instance here to match standard usage.
                if not hasattr(self, 'layout'):
                   self.layout = KeyboardLayoutUS(self.keyboard)
                
                self.layout.write(char)
            except Exception as e:
                print(f"Key error: {e}")
    
    def press_key(self, keycode):
        """Pressiona uma tecla específica"""
        if not self.enabled: return
        self.keyboard.send(keycode)
    
    def press_combination(self, *keycodes):
        """Pressiona combinação de teclas (ex: Ctrl+C)"""
        if not self.enabled: return
        self.keyboard.send(*keycodes)
    
    def type_username_password(self, username, password, tab_between=True):
        """Digita usuário + senha (comum em logins)"""
        self.type_string(username)
        
        if tab_between:
            self.press_key(Keycode.TAB)
            time.sleep(0.05)
        
        self.type_string(password)
