# ⚡ PicoPass Flashing & Installation Guide

This guide will walk you through installing the PicoPass firmware on your hardware.

---

---

## � Method 3: Automated CLI (The "Pro" Way - No Thonny)

If you prefer the terminal or want something faster, use our automated deployer script.

1.  Open your terminal in the project root folder.
2.  Install dependencies (if you don't have them):
    ```bash
    pip install mpremote
    ```
3.  Run the deployer:
    ```bash
    python3 tools/deploy.py
    ```

**What this script does:**
- Automatically detects your Pico/RP2350.
- Uploads all firmware files and libraries.
- Resets the device to start the app.

---

This method allows you to use all the advanced features (OLED, BLE, RP2350 support).

### 1. Install MicroPython Firmware
1.  **Download the MicroPython UF2** for your board:
    - [Raspberry Pi Pico](https://micropython.org/download/RPI_PICO/)
    - [Raspberry Pi Pico W](https://micropython.org/download/RPI_PICO_W/)
    - [Raspberry Pi RP2350 (Pico 2)](https://micropython.org/download/RPI_PICO2/)
2.  Hold the **BOOTSEL** button on your board and plug it into your computer.
3.  A new drive named `RPI-RP2` (or similar) will appear.
4.  Drag and drop the downloaded `.uf2` file into this drive. The board will reboot automatically.

### 2. Upload PicoPass Files
You need to copy the files from the `firmware/micropython/` folder to the root of your device.

**Option A: Using Thonny IDE (Easiest for Beginners)**
1.  Download and install [Thonny IDE](https://thonny.org/).
2.  Open Thonny and go to **Run > Select Interpreter**. Select **MicroPython (Raspberry Pi Pico)**.
3.  In the "Files" pane, locate your `PicoPass/firmware/micropython/` folder.
4.  Select all files inside (including the `lib` folder), right-click, and choose **Upload to / **.
5.  Wait for the transfer to complete. Your Pico will automatically start PicoPass!

**Option B: Using Command Line (mpremote)**
If you have Python installed:
```bash
pip install mpremote
cd firmware/micropython
mpremote fs cp -r . :
mpremote reset
```

---

---

## 🛠️ Method 2: C/C++ Firmware (High Performance)

Use this method if you only need standard USB-HID functionality with minimum latency.

1.  Locate the compiled file: `firmware/c/build/picopass.uf2`.
2.  Hold the **BOOTSEL** button on your board and plug it into your computer.
3.  Drag and drop `picopass.uf2` into the `RPI-RP2` drive.
4.  The board will reboot and be ready to use immediately as a PicoPass device.

---

## 💻 Method 4: VS Code Extension (Visual & Professional)

Since you are using the official **Raspberry Pi Pico VS Code Extension**, here is how to flash the C/C++ version:

### 1. Project Setup
1.  Open the **Pico Side Bar** (the Raspberry logo icon).
2.  Click **Import Project**.
3.  **IMPORTANT:** When choosing the folder, do NOT select the root of the repo. Select the **`firmware/c`** folder specifically.
4.  Ensure the **SDK** and **Toolchain** have finished installing (check the bottom progress bars in your screenshot).

### 2. Compile & Flash
1.  In the side bar, click **Compile Project**.
2.  Put your device into **BOOTSEL** mode.
3.  Click **Run Project (USB)**. The extension will flash the firmware automatically.

*Note: This is the best way to develop and debug the **C/C++ firmware**.*

---

---

## ✅ How to Verify it worked
- **LED:** The onboard LED should blink 3 times on startup.
- **Serial:** Open the PicoPass Desktop App. It should show **"Connected: Raspberry Pi Pico"** (or RP2350) in the status bar.
- **Display (If attached):** The OLED should show the "PicoPass v1.1" welcome screen.

---
*Stuck? Check the [Hardware Setup](HARDWARE_SETUP.md) for pinout details.*
