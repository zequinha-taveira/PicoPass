# firmware/micropython/main.py

import time
import machine
import sys
from machine import Pin
import gc
import binascii

# Imports dos módulos
from hid_keyboard import USBKeyboard
from led_controller import LEDController
from button_handler import ButtonHandler
from storage import PasswordStorage
from serial_protocol import SerialProtocol
from crypto import AESCrypto

# ============================================
# CONFIGURAÇÃO DE HARDWARE
# ============================================

# Versão do firmware
VERSION = "1.0.0"
try:
    BOARD_ID = binascii.hexlify(machine.unique_id()).decode().upper()
except:
    BOARD_ID = "UNKNOWN"

print(f"""
╔════════════════════════════════════════╗
║         PicoPass v{VERSION}            ║
║    Hardware Password Manager           ║
║    Board ID: {BOARD_ID[:16]}...        ║
╚════════════════════════════════════════╝
""")

# ============================================
# DEVICE STATE
# ============================================

class PicoPassDevice:
    """Gerenciador principal do PicoPass"""
    
    def __init__(self):
        print("Initializing hardware...")
        
        # Hardware components
        self.leds = LEDController()
        self.buttons = ButtonHandler()
        self.keyboard = USBKeyboard()
        self.storage = PasswordStorage()
        self.serial = SerialProtocol()
        self.crypto = AESCrypto(BOARD_ID)
        
        # State
        self.unlocked = False
        self.master_hash = None
        self.last_activity = 0
        self.auto_lock_timeout = 120  # 2 minutos
        
        # Password slots (4 slots)
        self.password_slots = [None, None, None, None]
        
        print("✓ Hardware initialized")
        
        # Boot sequence
        self.boot_sequence()
    
    def boot_sequence(self):
        """Animação de boot"""
        print("Running boot sequence...")
        
        # Animação de LEDs
        self.leds.boot_animation()
        
        # Carregar dados da flash
        self.load_from_flash()
        
        # Estado inicial: locked
        self.lock()
        
        print("✓ Boot complete - Device LOCKED")
    
    def load_from_flash(self):
        """Carrega dados persistentes da flash"""
        try:
            data = self.storage.load()
            
            if data:
                self.master_hash = data.get('master_hash')
                self.password_slots = data.get('slots', [None] * 4)
                self.auto_lock_timeout = data.get('timeout', 120)
                # Count valid slots
                count = len([s for s in self.password_slots if s])
                print(f"✓ Loaded {count} passwords")
            else:
                print("! No saved data found - first boot")
        
        except Exception as e:
            print(f"✗ Error loading data: {e}")
    
    def save_to_flash(self):
        """Salva dados na flash"""
        try:
            data = {
                'master_hash': self.master_hash,
                'slots': self.password_slots,
                'timeout': self.auto_lock_timeout,
            }
            self.storage.save(data)
            print("✓ Data saved to flash")
        except Exception as e:
            print(f"✗ Error saving: {e}")
    
    def unlock(self, master_password=None):
        """Desbloqueia o dispositivo"""
        # Se já configurado, verificar senha
        if self.master_hash:
            if not master_password:
                print("! Master password required")
                self.leds.error_blink(3)
                return False
            
            # Verificar hash
            # derive key first to use crypto
            self.crypto.derive_key(master_password)
            password_hash = self.crypto.hash_password(master_password)
            
            if password_hash != self.master_hash:
                print("✗ Wrong password!")
                self.leds.error_blink(5)
                # Clean key
                self.crypto.clear_key_cache()
                return False
        
        else:
            # Primeira vez - criar master password
            if master_password:
                self.crypto.derive_key(master_password)
                self.master_hash = self.crypto.hash_password(master_password)
                self.save_to_flash()
                print("✓ Master password set")
        
        self.unlocked = True
        self.last_activity = time.time()
        self.leds.set_status(True)
        self.leds.blink_status(2)
        
        print("✓ Device UNLOCKED")
        return True
    
    def lock(self):
        """Bloqueia o dispositivo"""
        self.unlocked = False
        self.leds.set_status(False)
        self.leds.set_error(True)
        # Clear crypto key
        self.crypto.clear_key_cache()
        
        # Limpar senhas da memória (segurança)
        gc.collect()
        
        print("✓ Device LOCKED")
    
    def type_password(self, slot):
        """Digita senha de um slot"""
        if not self.unlocked:
            print(f"! Device locked - cannot type slot {slot}")
            self.leds.error_blink(3)
            return
        
        if slot < 0 or slot >= len(self.password_slots):
            print(f"✗ Invalid slot: {slot}")
            self.leds.error_blink(2)
            return
        
        encrypted_data = self.password_slots[slot]
        
        if not encrypted_data:
            print(f"! Slot {slot} is empty")
            self.leds.error_blink(2)
            return
        
        try:
            # Descriptografar senha
            password = self.crypto.decrypt(encrypted_data)
            
            # Digitar via USB HID
            print(f"⌨ Typing password from slot {slot}...")
            self.leds.set_activity(True)
            
            self.keyboard.type_string(password)
            
            self.leds.set_activity(False)
            self.leds.blink_status(2)
            
            print("✓ Password typed!")
            
            # Atualizar last_activity
            self.last_activity = time.time()
            
            # Limpar senha da memória
            del password
            gc.collect()
        
        except Exception as e:
            print(f"✗ Error typing password: {e}")
            self.leds.error_blink(4)
    
    def add_password(self, slot, password):
        """Adiciona senha em um slot"""
        if not self.unlocked:
            print("! Device locked")
            return False
        
        if slot < 0 or slot >= len(self.password_slots):
            print(f"✗ Invalid slot: {slot}")
            return False
        
        try:
            # Criptografar senha
            encrypted_data = self.crypto.encrypt(password)
            
            # Salvar no slot
            self.password_slots[slot] = encrypted_data
            
            # Persistir na flash
            self.save_to_flash()
            
            print(f"✓ Password saved to slot {slot}")
            self.leds.blink_status(3)
            
            return True
        
        except Exception as e:
            print(f"✗ Error saving password: {e}")
            self.leds.error_blink(4)
            return False
    
    def delete_password(self, slot):
        """Remove senha de um slot"""
        if not self.unlocked:
            print("! Device locked")
            return False
        
        if slot < 0 or slot >= len(self.password_slots):
            return False
        
        self.password_slots[slot] = None
        self.save_to_flash()
        
        print(f"✓ Slot {slot} cleared")
        return True
    
    def check_auto_lock(self):
        """Verifica se deve auto-lock"""
        if self.unlocked:
            elapsed = time.time() - self.last_activity
            if elapsed > self.auto_lock_timeout:
                print(f"⏰ Auto-lock triggered after {int(elapsed)}s")
                self.lock()
    
    def handle_button_press(self, button_id):
        """Processa pressão de botão"""
        print(f"Button {button_id} pressed")
        self.last_activity = time.time() # Reset idle timer on interaction
        
        if button_id == 0:
            # Botão unlock (deve ser pressão longa)
            if self.buttons.is_long_press(button_id):
                if self.unlocked:
                    self.lock()
                else:
                    # Aguardar master password via serial
                    print("! Waiting for master password via serial...")
                    self.leds.waiting_pattern()
            else:
                 # Short press on lock button: maybe show status?
                 self.leds.pulse(self.leds.led_status if self.unlocked else self.leds.led_error, 0.5)
        
        elif button_id >= 1 and button_id <= 4:
            # Botões de senha (1-4) map to slots 0-3
            # But wait, buttons are 1-based in handler?
            # button_handler defines pin array index 0..4.
            # check_buttons returns index.
            # Button 0 is Pin 15 (Unlock).
            # Button 1 is Pin 14 (Slot 0).
            # So slot = button_id - 1 is correct.
            slot = button_id - 1
            self.type_password(slot)
    
    def handle_serial_command(self, command):
        """Processa comando serial do PC"""
        try:
            cmd_type = command.get('type')
            
            if cmd_type == 'PING':
                self.serial.send_response({'status': 'PONG', 'version': VERSION})
            
            elif cmd_type == 'GET_ID':
                self.serial.send_response({'board_id': BOARD_ID, 'version': VERSION})
            
            elif cmd_type == 'UNLOCK':
                password = command.get('password', '')
                success = self.unlock(password)
                self.serial.send_response({'status': 'ok' if success else 'error'})
            
            elif cmd_type == 'LOCK':
                self.lock()
                self.serial.send_response({'status': 'ok'})
            
            elif cmd_type == 'STATUS':
                self.serial.send_response({
                    'unlocked': self.unlocked,
                    'slots': [s is not None for s in self.password_slots],
                    'timeout': self.auto_lock_timeout
                })
            
            elif cmd_type == 'ADD_PASSWORD':
                slot = command.get('slot', -1)
                password = command.get('password', '')
                success = self.add_password(slot, password)
                self.serial.send_response({'status': 'ok' if success else 'error'})
            
            elif cmd_type == 'DELETE_PASSWORD':
                slot = command.get('slot', -1)
                success = self.delete_password(slot)
                self.serial.send_response({'status': 'ok' if success else 'error'})
            
            elif cmd_type == 'TYPE_PASSWORD':
                slot = command.get('slot', -1)
                self.type_password(slot)
                self.serial.send_response({'status': 'ok'})
            
            elif cmd_type == 'SET_TIMEOUT':
                timeout = command.get('timeout', 120)
                self.auto_lock_timeout = max(30, min(600, timeout))  # 30s - 10min
                self.save_to_flash()
                self.serial.send_response({'status': 'ok', 'timeout': self.auto_lock_timeout})
            
            else:
                self.serial.send_response({'status': 'error', 'message': 'Unknown command'})
        
        except Exception as e:
            print(f"✗ Command error: {e}")
            self.serial.send_response({'status': 'error', 'message': str(e)})

# ============================================
# MAIN LOOP
# ============================================

def main():
    """Loop principal"""
    print("Starting PicoPass...")
    
    try:
        device = PicoPassDevice()
        
        print("\n✓ PicoPass ready!")
        print("=" * 40)
        
        # Loop infinito
        while True:
            # Processar comandos serial
            command = device.serial.read_command()
            if command:
                device.handle_serial_command(command)
            
            # Verificar botões
            button = device.buttons.check_buttons()
            if button is not None:
                device.handle_button_press(button)
            
            # Verificar auto-lock
            device.check_auto_lock()
            
            # Sleep curto para não sobrecarregar CPU
            time.sleep(0.01)
    
    except KeyboardInterrupt:
        print("\n\n! Interrupted by user")
        try:
           device.leds.all_off()
        except:
           pass
    
    except Exception as e:
        print(f"\n\n✗ FATAL ERROR: {e}")
        # Piscar erro rapidamente
        try:
            from machine import Pin
            err_led = Pin(17, Pin.OUT)
            while True:
                err_led.toggle()
                time.sleep(0.1)
        except:
            pass

# Iniciar
if __name__ == "__main__":
    main()
