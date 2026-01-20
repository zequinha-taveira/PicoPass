# firmware/micropython/rp2350_test.py
import machine
import utime
import rp2

# Default Pins for RP2350 USB Stick (Tenstar Robot)
LED_PIN = 25
BTN_PIN = 24  # Common on many RP2040/RP2350 sticks. Try 15 or 0 if this fails.

led = machine.Pin(LED_PIN, machine.Pin.OUT)
btn = machine.Pin(BTN_PIN, machine.Pin.IN, machine.Pin.PULL_UP)

print("Starting RP2350 Hardware Test...")
print(f"LED: GPIO {LED_PIN} | BTN: GPIO {BTN_PIN} (Pull-up) | BOOTSEL: Enabled")

try:
    while True:
        led.value(1)
        # Check either the external button or the BOOTSEL button
        if not btn.value() or rp2.bootsel_button():
            trigger = "External Button" if not btn.value() else "BOOTSEL Button"
            print(f"{trigger} Pressed!")
            led.value(0)
            utime.sleep(0.5)
        utime.sleep(0.1)
        led.value(0)
        utime.sleep(0.1)
except KeyboardInterrupt:
    print("Test stopped.")
