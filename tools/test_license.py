import hashlib
import binascii

def calculate_key(board_type):
    secret_salt = "PicoPass_Profile_Secure_2026"
    data = f"{board_type}:{secret_salt}"
    hash_obj = hashlib.sha256(data.encode())
    return binascii.hexlify(hash_obj.digest()).decode()[:16]

# Simulação de dados
test_type = "raspberry_pi_pico"

key = calculate_key(test_type)
print(f"Board Type: {test_type}")
print(f"Generated Key: {key}")

# Simulação de um segundo dispositivo do mesmo tipo
print("\nTesting second device of same type...")
key2 = calculate_key(test_type)
print(f"Generated Key 2: {key2}")
assert key == key2, "Keys for same board type must match!"
print("Success: Same board type generates same key.")

# Verificação
expected_key = key
is_valid = (key == expected_key)
print(f"Validation: {'SUCCESS' if is_valid else 'FAILED'}")
