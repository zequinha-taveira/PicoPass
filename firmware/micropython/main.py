# firmware/micropython/main.py
from device import PicoPassDevice

def main():
    try:
        app = PicoPassDevice()
        app.run()
    except Exception as e:
        # Emergency blink on crash
        import machine
        import utime
        led = machine.Pin(25, machine.Pin.OUT)
        while True:
            led.toggle()
            utime.sleep(0.1)

if __name__ == "__main__":
    main()
