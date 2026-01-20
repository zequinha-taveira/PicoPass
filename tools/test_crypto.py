# tools/test_crypto.py
import os
try:
    from cryptography.hazmat.primitives.ciphers.aead import AesGcm
except ImportError:
    print("Please install cryptography: pip install cryptography")
    exit(1)

def test_aes_gcm():
    password = b"secret_password_32bytes_long_123" # Must be 16, 24, or 32 bytes
    aesgcm = AesGcm(password)
    nonce = os.urandom(12)
    data = b"my secret password"
    aad = b"authenticated but unencrypted data"
    
    # Encrypt
    ct = aesgcm.encrypt(nonce, data, aad)
    print(f"Encrypted: {ct.hex()}")
    
    # Decrypt
    pt = aesgcm.decrypt(nonce, ct, aad)
    print(f"Decrypted: {pt.decode()}")
    
    assert pt == data
    print("✅ Crypto PoC OK!")

if __name__ == "__main__":
    test_aes_gcm()
