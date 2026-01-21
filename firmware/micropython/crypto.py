# firmware/micropython/crypto.py

import hashlib
import os

try:
    from ucryptolib import aes
except ImportError:
    try:
        import aes
    except ImportError:
        aes = None
        print("Warning: No AES library found")

class AESCrypto:
    """Criptografia AES-256-CBC para senhas"""
    
    def __init__(self, board_id):
        self.board_id = board_id
        self.key_cache = None
    
    def derive_key(self, master_password):
        """Deriva chave AES-256 do master password + board ID"""
        if self.key_cache:
            return self.key_cache
        
        # Combinar master password + board ID como salt
        data = (master_password + self.board_id).encode()
        
        # SHA-256 para gerar chave de 32 bytes
        # digest() returns bytes
        hash_obj = hashlib.sha256(data)
        key = hash_obj.digest()
        
        self.key_cache = key
        return key
    
    def hash_password(self, password):
        """Hash SHA-256 de senha (para verificação)"""
        # hexdigest logic manually if needed, but hashlib usually supports it
        # RP2 hashlib might not support hexdigest directly in some versions?
        # Let's assume standard behavior or fallback
        h = hashlib.sha256(password.encode())
        # Try digest and hexlify
        import binascii
        return binascii.hexlify(h.digest()).decode()
    
    def encrypt(self, plaintext):
        """Criptografa texto com AES-256"""
        if not aes:
            raise Exception("AES not supported on this firmware")
            
        # Gerar IV aleatório (16 bytes)
        iv = os.urandom(16)
        
        # Padding PKCS7
        block_size = 16
        padding_length = block_size - (len(plaintext) % block_size)
        padded = plaintext + (chr(padding_length) * padding_length)
        
        # Criptografar (precisa de master key configurada antes)
        if not self.key_cache:
            raise Exception("Key not derived - unlock first")
        
        # aes(key, mode, IV). Mode 2 = CBC
        cipher = aes(self.key_cache, 2, iv)
        ciphertext = cipher.encrypt(padded.encode())
        
        # Retornar IV + ciphertext
        return {
            'iv': iv,
            'data': ciphertext
        }
    
    def decrypt(self, encrypted_data):
        """Descriptografa dados"""
        if not aes:
            raise Exception("AES not supported on this firmware")
            
        if not self.key_cache:
            raise Exception("Key not derived - unlock first")
        
        iv = encrypted_data['iv']
        ciphertext = encrypted_data['data']
        
        # Descriptografar
        cipher = aes(self.key_cache, 2, iv)
        padded = cipher.decrypt(ciphertext)
        
        # Remover padding PKCS7
        # padded is bytes
        if len(padded) == 0: return ""
        
        padding_length = padded[-1]
        if padding_length > 16: # Invalid padding
             return padded.decode()
             
        plaintext = padded[:-padding_length].decode()
        
        return plaintext
    
    def clear_key_cache(self):
        """Limpa chave da memória (ao fazer lock)"""
        self.key_cache = None
