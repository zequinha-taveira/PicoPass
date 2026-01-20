# firmware/micropython/serial_test.py
import uselect
import sys

def main():
    spoll = uselect.poll()
    spoll.register(sys.stdin, uselect.POLLIN)

    while True:
        if spoll.poll(100):
            line = sys.stdin.readline().strip()
            if line == "PING":
                print("PONG")

if __name__ == "__main__":
    main()
