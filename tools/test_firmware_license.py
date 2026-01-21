import sys
from unittest.mock import MagicMock

# Mocking machine and other MicroPython modules
sys.modules['machine'] = MagicMock()
sys.modules['utime'] = MagicMock()
sys.modules['uselect'] = MagicMock()
sys.modules['rp2'] = MagicMock()
sys.modules['keyboard'] = MagicMock()
sys.modules['display_manager'] = MagicMock()
sys.modules['ble_hid'] = MagicMock()

# Import the license manager
sys.path.append('PicoPass/firmware/micropython')
from license import LicenseManager

def test_license_manager():
    lm = LicenseManager()
    board_id = lm.board_id
    board_type = lm.board_type
    
    print(f"Detected Board ID: {board_id}")
    print(f"Detected Board Type: {board_type}")
    
    # Generate a key
    key = lm._calculate_key(board_id, board_type)
    print(f"Calculated Key: {key}")
    
    # Save and verify
    lm.save_license(key)
    is_valid = lm.verify_license()
    print(f"License Verification: {'SUCCESS' if is_valid else 'FAILED'}")
    
    assert is_valid == True

if __name__ == "__main__":
    try:
        test_license_manager()
        print("Firmware License Logic Test Passed!")
    except Exception as e:
        print(f"Test Failed: {e}")
        sys.exit(1)
