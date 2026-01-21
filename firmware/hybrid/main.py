# firmware/hybrid/main.py

import fast_crypto  # Compiled C module
import time
import machine

# Placeholder for full hybrid implementation
# The user specified loop would be here, utilizing fast_crypto

class HybridPicoPass:
    def __init__(self):
        print("Hybrid PicoPass Initialized")
        
    def hash_password(self, password):
        """Uses C module for performance"""
        # fast_crypto returns bytes, we want hex string usually
        h = fast_crypto.hash_sha256(password.encode())
        return h.hex()

def main():
    print("Starting Hybrid Firmware...")
    device = HybridPicoPass()
    
    # Test crypto speed
    start = time.ticks_ms()
    h = device.hash_password("test_password")
    end = time.ticks_ms()
    print(f"Hash in {time.ticks_diff(end, start)}ms: {h}")

if __name__ == "__main__":
    main()
