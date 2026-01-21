# firmware/micropython/license.py
# PicoPass License Manager - Per-Device Licensing
# Validation based on serial_number + board_type

import machine
import binascii
import hashlib
import json

class LicenseManager:
    """Manages device licensing and configuration."""
    
    SECRET_SALT = "PicoPass_Device_Secure_2026"
    
    def __init__(self):
        self.license_file = "license.key"
        self.config_file = "device.cfg"
        self.board_id = self._get_board_id()
        self.board_type = self._get_board_type()
        self.config = self._load_config()
        self._activated = None  # Cache

    def _get_board_id(self):
        """Get unique hardware ID (Serial Number)."""
        try:
            # machine.unique_id() returns chip's unique ID
            return binascii.hexlify(machine.unique_id()).decode()
        except:
            return "UNKNOWN_ID"

    def _get_board_type(self):
        """Identify board type based on platform and hardware."""
        import sys
        platform = sys.platform
        
        if "rp2" in platform:
            # Try to detect RP2350 vs RP2040
            try:
                import rp2
                # Check for RP2350-specific features
                if hasattr(rp2, 'bootsel_button'):
                    # Both have this, but we can check memory
                    import gc
                    mem_free = gc.mem_free()
                    # RP2350 has more RAM
                    if mem_free > 200000:
                        return "raspberry_pi_pico2"
                return "raspberry_pi_pico"
            except:
                return "raspberry_pi_pico"
        elif "esp32" in platform:
            return "esp32_s3"
        
        return "generic_board"

    def _load_config(self):
        """Load device configuration if exists."""
        try:
            with open(self.config_file, "r") as f:
                return json.load(f)
        except:
            return None

    def _save_config(self, config):
        """Save configuration received from app."""
        try:
            with open(self.config_file, "w") as f:
                json.dump(config, f)
            self.config = config
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False

    def verify_license(self):
        """Verify if license + config are valid for this device."""
        if self._activated is not None:
            return self._activated
            
        try:
            with open(self.license_file, "r") as f:
                license_key = f.read().strip()
            
            # Validation: key must match serial + board_type
            expected = self._calculate_key(self.board_id, self.board_type)
            self._activated = (license_key == expected) and (self.config is not None)
            return self._activated
        except:
            self._activated = False
            return False

    def save_license(self, key):
        """Save new license key."""
        try:
            with open(self.license_file, "w") as f:
                f.write(key)
            self._activated = None  # Reset cache
            return True
        except Exception as e:
            print(f"Error saving license: {e}")
            return False

    def _calculate_key(self, board_id, board_type):
        """Calculate activation key from serial + board_type."""
        data = f"{board_id}:{board_type}:{self.SECRET_SALT}"
        hash_obj = hashlib.sha256(data.encode())
        return binascii.hexlify(hash_obj.digest()).decode()[:16]

    def validate_activation_key(self, key):
        """Validate activation key from app."""
        expected = self._calculate_key(self.board_id, self.board_type)
        return key == expected

    def activate(self, activation_key, config=None):
        """Activate device with key and optional config."""
        if not self.validate_activation_key(activation_key):
            return False, "Invalid activation key"
        
        # Save license
        if not self.save_license(activation_key):
            return False, "Failed to save license"
        
        # Save config if provided
        if config:
            if not self._save_config(config):
                return False, "Failed to save config"
        
        self._activated = True
        return True, "Activation successful"

    def apply_config(self):
        """Get hardware configuration values."""
        if not self.config:
            # Return defaults
            return {
                "led_gpio": 25,
                "led_inverted": False,
                "led_brightness": 100,
                "btn_gpio": 15,
                "btn_pull": "UP",
                "has_display": False,
                "usb_product_name": "PicoPass Security Key",
                "usb_manufacturer_name": "PicoPass",
            }
        
        return {
            "led_gpio": self.config.get("led_gpio", 25),
            "led_inverted": self.config.get("led_inverted", False),
            "led_brightness": self.config.get("led_brightness", 100),
            "btn_gpio": self.config.get("button_gpio", 15),
            "btn_pull": self.config.get("button_pull", "UP"),
            "has_display": self.config.get("has_display", False),
            "display_sda": self.config.get("display_sda"),
            "display_scl": self.config.get("display_scl"),
            "usb_product_name": self.config.get("usb_product_name", "PicoPass Security Key"),
            "usb_manufacturer_name": self.config.get("usb_manufacturer_name", "PicoPass"),
            "use_custom_usb_id": self.config.get("use_custom_usb_id", False),
            "usb_vid": self.config.get("usb_vid"),
            "usb_pid": self.config.get("usb_pid"),
        }

    def generate_activation_request(self):
        """Generate string for activation request."""
        return f"ACT_REQ:{self.board_id}|{self.board_type}"

    def get_status_response(self):
        """Generate PONG response with device info."""
        status = "ACTIVATED" if self.verify_license() else "NOT_ACTIVATED"
        has_config = "CONFIGURED" if self.config else "NO_CONFIG"
        return f"PONG|{status}|{self.board_id}|{self.board_type}|{has_config}"

    def get_info(self):
        """Get comprehensive device info."""
        return {
            "board_id": self.board_id,
            "board_type": self.board_type,
            "activated": self.verify_license(),
            "has_config": self.config is not None,
            "config": self.config,
        }

    def reset(self):
        """Reset license and config (factory reset)."""
        import os
        try:
            os.remove(self.license_file)
        except:
            pass
        try:
            os.remove(self.config_file)
        except:
            pass
        self._activated = None
        self.config = None
        return True
