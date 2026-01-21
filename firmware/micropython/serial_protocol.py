# firmware/micropython/serial_protocol.py

import sys
import json
import uselect

class SerialProtocol:
    """Protocolo de comunicação serial com PC"""
    
    def __init__(self):
        self.buffer = ""
        self.poll = uselect.poll()
        self.poll.register(sys.stdin, uselect.POLLIN)
    
    def read_command(self):
        """Lê comando do PC (JSON)"""
        # Ler da UART/USB
        while self.poll.poll(0):
            try:
                char = sys.stdin.read(1)
            except:
                break
                
            if not char:
                break
            
            if char == '\n':
                # Comando completo recebido
                cmd_str = self.buffer.strip()
                self.buffer = ""
                if not cmd_str: return None
                
                try:
                    command = json.loads(cmd_str)
                    return command
                except:
                    # Parse error, just ignore or print error if debug enabled
                    # print("JSON Parse Error")
                    return None
            else:
                self.buffer += char
        
        return None
    
    def send_response(self, data):
        """Envia resposta para PC (JSON)"""
        try:
            response = json.dumps(data)
            print(response)  # Envia via stdout
        except Exception as e:
            # Fallback error
            print('{"status":"error","message":"serialization error"}')
