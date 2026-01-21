# firmware/micropython/license.py
import machine
import binascii
import hashlib

class LicenseManager:
    def __init__(self):
        self.license_file = "license.key"
        self.board_id = self._get_board_id()
        self.board_type = self._get_board_type()

    def _get_board_id(self):
        """Obtém o ID único do hardware (Número de Série)."""
        try:
            # machine.unique_id() retorna o ID único do chip
            return binascii.hexlify(machine.unique_id()).decode()
        except:
            return "UNKNOWN_ID"

    def _get_board_type(self):
        """Identifica o tipo de placa baseado na plataforma e hardware."""
        import sys
        platform = sys.platform
        if "rp2" in platform:
            # Tenta diferenciar entre RP2040 e RP2350 se possível
            return "raspberry_pi_pico" # Simplificado para o exemplo
        elif "esp32" in platform:
            return "esp32_s3"
        return "generic_board"

    def generate_activation_request(self):
        """Gera uma string para solicitação de ativação."""
        return f"ACT_REQ:{self.board_id}|{self.board_type}"

    def verify_license(self):
        """Verifica se a licença atual é válida para este hardware."""
        try:
            with open(self.license_file, "r") as f:
                license_key = f.read().strip()
            
            # A licença é um hash do ID + Tipo + Salt Secreto
            expected = self._calculate_key(self.board_id, self.board_type)
            return license_key == expected
        except:
            return False

    def save_license(self, key):
        """Salva uma nova chave de licença."""
        with open(self.license_file, "w") as f:
            f.write(key)

    def _calculate_key(self, board_id, board_type):
        """Algoritmo de validação (deve ser o mesmo no App)."""
        secret_salt = "PicoPass_Secure_2026"
        data = f"{board_id}:{board_type}:{secret_salt}"
        hash_obj = hashlib.sha256(data.encode())
        return binascii.hexlify(hash_obj.digest()).decode()[:16] # Chave de 16 chars
