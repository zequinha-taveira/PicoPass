# 🛠️ PicoPass Hardware Setup Guide

If you are not using a custom PCB, you can easily build a PicoPass device on a breadboard.

## 📝 Bill of Materials
1. **Raspberry Pi Pico** (Standard or W).
2. **Push Button** (Tactile switch).
3. **LED** (Any color, e.g., Green or Blue).
4. **Resistor** (220Ω for LED).
5. **Breadboard and Jumper wires**.

## 🔌 Wiring Diagram

### 1. The "Action" Button
- Connect one leg of the button to **GPIO 15** (Pin 20).
- Connect the other leg of the button to any **GND** pin (e.g., Pin 18).
*Note: The firmware uses internal pull-up resistors, so no external resistor is needed for the button.*

### 2. Status LED (External)
- Connect the positive leg (longer) of the LED to **GPIO 16** (Pin 21).
- Connect the negative leg (shorter) to a **220Ω resistor**.
- Connect the other end of the resistor to **GND**.

### 3. Pin Mapping Reference
| Component | Pico Pin | GPIO | Function |
|-----------|----------|------|----------|
| Button | 20 | 15 | Trigger Auto-Type |
| LED (+) | 21 | 16 | Status/Ready Indicator |
### 4. RP2350 USB Stick (Tenstar Robot)
- **Built-in USB:** Plug directly into the PC.
- **BOOT Button:** This button has a dual function:
    - **Flash Mode:** Hold while plugging in to enters flash mode.
    - **Trigger Mode:** While the app is running, press it to trigger the **Auto-Type** function.
- **Internal LED:** GPIO 25.
- **Action Button (Optional):** GPIO 15 or 24 if you want an external switch.
*Note: Using the built-in BOOT button makes this hardware completely plug-and-play with zero extra wiring!*

## 🕹️ Advanced Modules (Experimental)

### 📺 1. OLED Display (I2C)
- **VCC:** 3.3V (Pin 36)
- **GND:** GND (Pin 38)
- **SDA:** GPIO 16 (Pin 21)
- **SCL:** GPIO 17 (Pin 22)
*Note: The app will automatically show the service name on the screen.*

### 📶 2. Bluetooth BLE (ESP32-S3 ONLY)
- No wiring needed. 
- Pair your smartphone with **"PicoPass-Pro"**.
- The device will type via USB and Bluetooth simultaneously.

## 🕹️ Firmware Modes
- **MicroPython:** Flash the Pico with MicroPython firmware and upload the `firmware/micropython/` files.
- **C/C++:** Preferred for performance. Flash the compiled `.uf2` file.
