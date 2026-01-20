# 🛠️ PicoPass Developer Guide

This guide is for developers who want to contribute to the PicoPass project.

## 🏗️ Architecture Overview

PicoPass consists of three main parts:
1. **Frontend (Svelte + TypeScript):** A modern, reactive UI for managing passwords.
2. **Backend (Rust + Tauri):** Handles cryptography (AES-256-GCM), key derivation (Argon2), and serial communication with the Pico.
3. **Firmware (MicroPython or C):** Acts as a USB HID Keyboard and handles the physical "type" button.

## 💻 Environment Setup

### 1. Prerequisites
- **Rust:** `curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh`
- **Node.js (18+):** Recommended to use `nvm`.
- **Python 3:** For scripts and MicroPython tooling.
- **Pico SDK (Optional):** Required only for building the C firmware.

### 2. Repository Structure
- `/app`: Tauri/Svelte source code.
- `/firmware`: MicroPython and C firmware versions.
- `/tools`: Utility scripts for building and testing.

## 🔨 Building and Running

### Run the App in Dev Mode
```bash
cd app
npm install
npm run tauri dev
```

### Build the App for Production
```bash
cd app
npm run tauri build
```

### Build the Firmware (MicroPython)
Simply use the tool:
```bash
python3 firmware/build.py
```

## 🔐 Cryptography Notes
- **Vault Format:** JSON file (`vault.json`).
- **Encryption:** AES-256-GCM from the `aes-gcm` crate.
- **Key Derivation:** Argon2id with a salt.
- **Data Flow:** The app never sends the raw master password to the device. It only sends the decrypted password for a single entry when the user clicks "Auto-Type".

## 🤝 Contributing
1. Fork the repo.
2. Create a feature branch.
3. Commit your changes.
4. Open a Pull Request.
