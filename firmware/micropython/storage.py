# firmware/micropython/storage.py

import json
import os
import binascii

class PasswordStorage:
    """Persistência de dados na Flash"""
    
    def __init__(self, filename="/picopass_data.json"):
        self.filename = filename
    
    def save(self, data):
        """Salva dados em JSON"""
        try:
            # Converter bytes para base64 para JSON
            serializable = self._make_serializable(data)
            
            with open(self.filename, 'w') as f:
                json.dump(serializable, f)
            
            return True
        except Exception as e:
            print(f"Save error: {e}")
            return False
    
    def load(self):
        """Carrega dados do JSON"""
        try:
            if not self.file_exists():
                return None
            
            with open(self.filename, 'r') as f:
                data = json.load(f)
            
            # Converter base64 de volta para bytes
            return self._deserialize(data)
        
        except Exception as e:
            print(f"Load error: {e}")
            return None
    
    def file_exists(self):
        """Verifica se arquivo existe"""
        try:
            os.stat(self.filename)
            return True
        except:
            return False
    
    def delete(self):
        """Deleta arquivo de dados"""
        try:
            if self.file_exists():
                os.remove(self.filename)
            return True
        except Exception as e:
            print(f"Delete error: {e}")
            return False
    
    def _make_serializable(self, data):
        """Converte dados para formato serializável"""
        result = {}
        
        for key, value in data.items():
            if key == 'slots':
                # Slots contêm dados criptografados (bytes)
                serialized_slots = []
                for slot in value:
                    if slot:
                        serialized_slots.append({
                            'iv': binascii.b2a_base64(slot['iv']).decode().strip(),
                            'data': binascii.b2a_base64(slot['data']).decode().strip()
                        })
                    else:
                        serialized_slots.append(None)
                result[key] = serialized_slots
            else:
                result[key] = value
        
        return result
    
    def _deserialize(self, data):
        """Converte dados de JSON para formato original"""
        result = {}
        
        for key, value in data.items():
            if key == 'slots':
                deserialized_slots = []
                for slot in value:
                    if slot:
                        # Defensive decoding
                        try:
                            iv = binascii.a2b_base64(slot['iv'])
                            d = binascii.a2b_base64(slot['data'])
                            deserialized_slots.append({'iv': iv, 'data': d})
                        except:
                            deserialized_slots.append(None)
                    else:
                        deserialized_slots.append(None)
                result[key] = deserialized_slots
            else:
                result[key] = value
        
        return result
