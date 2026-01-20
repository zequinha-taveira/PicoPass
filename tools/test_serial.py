# tools/test_serial.py
import serial
import time
import sys

def test_communication(port):
    print(f"Connecting to {port}...")
    try:
        ser = serial.Serial(port, 115200, timeout=1)
        time.sleep(2) # Wait for Pico to reset
        
        # Enviar comando
        print("Sending PING...")
        ser.write(b'PING\n')
        
        # Receber resposta
        response = ser.readline().strip()
        print(f"Response: {response.decode()}")
        
        if response == b'PONG':
            print("✅ Communication OK!")
            return True
        else:
            print("❌ Unexpected response")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    port = "/dev/ttyACM0" if len(sys.argv) < 2 else sys.argv[1]
    test_communication(port)
