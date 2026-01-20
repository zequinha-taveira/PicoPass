# 📜 Changelog

All notable changes to this project will be documented in this file.

## [1.0.0] - 2026-01-20

### 🚀 Added
- **Desktop App:** Initial release of the Tauri + Svelte + Rust application.
- **Cryptography:** AES-256-GCM encryption with Argon2 key derivation.
- **Firmware:** MicroPython and C/C++ firmware versions for Raspberry Pi Pico.
- **USB HID:** Auto-typing functionality via physical button trigger.
- **Multi-Hardware:** Detection support for Pico, Pico W, and ESP32-S3.
- **Data Management:** CSV Export and encrypted JSON Backup/Restore.
- **Premium UI:** Modern Glassmorphism design with hardware status indicators.
- **Documentation:** Full User Guide, Developer Guide, and Hardware Setup instructions.

### 🔧 Changed
- Modularized frontend components for better maintenance.
- Optimized serial communication protocol for reliability.

### 🛡️ Security
- Implemented state-locked memory management for decrypted keys.
- Physical button confirmation required for all HID typing operations.
