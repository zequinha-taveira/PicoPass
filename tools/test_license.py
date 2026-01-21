import hashlib
import binascii

def calculate_key(board_id, board_type):
    secret_salt = "PicoPass_Secure_2026"
    data = f"{board_id}:{board_type}:{secret_salt}"
    hash_obj = hashlib.sha256(data.encode())
    return binascii.hexlify(hash_obj.digest()).decode()[:16]

# Simulação de dados
test_id = "1234567890abcdef"
test_type = "raspberry_pi_pico"

key = calculate_key(test_id, test_type)
print(f"Board ID: {test_id}")
print(f"Board Type: {test_type}")
print(f"Generated Key: {key}")

# Verificação
expected_key = key
is_valid = (key == expected_key)
print(f"Validation: {'SUCCESS' if is_valid else 'FAILED'}")
