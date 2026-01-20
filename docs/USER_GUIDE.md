# 📖 PicoPass User Guide

Welcome to **PicoPass**, your hardware-backed secure password manager!

## 🚀 Getting Started

### 1. Requirements
- A Raspberry Pi Pico (or supported board).
- A micro-USB cable.
- The PicoPass Desktop App (Windows, macOS, or Linux).

### 2. Physical Setup
- Connect your Pico to your computer via USB.
- The on-board LED will blink to indicate it's ready.

### 3. Initial Configuration
1. Open the PicoPass App.
2. Set your **Master Password**. *Caution: If you lose this, your data cannot be recovered.*
3. The app will detect your Pico automatically.

## 🔑 Using PicoPass

### Adding a Password
1. Click the **"+ Add Entry"** button.
2. Fill in the Service (e.g., GitHub), Username, and Password.
3. Click "Save Entry". Your data is now encrypted and stored.

### Auto-Typing a Password
1. Place your cursor in the login field of the service you want to use.
2. In the PicoPass app, find the entry and click **"⌨️ Auto-Type"**.
3. The Pico's LED will turn on, indicating it is "armed".
4. **Press the physical button** on your Pico device.
5. Watch as PicoPass types your password instantly!

## 🛡️ Security Best Practices
- **Auto-Lock:** Configure how long the vault stays open in the Settings menu.
- **Backups:** Regularly export an encrypted backup from the Settings menu.
- **Physical Safety:** Your passwords stay on your PC (encrypted), but require the Pico to be typed. Don't leave your Pico unattended!

## ❓ Troubleshooting
- **Pico Not Detected:** Reconnect the USB cable or check if the correct firmware is flashed.
- **Typing Errors:** Ensure your keyboard layout matches the one configured in the firmware (default is US).
