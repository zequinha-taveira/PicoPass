# 🛡️ PicoPass Security Policy

PicoPass is designed with a "Physical-First" security model. This document outlines our technical security implementation and threat mitigations.

## 🔐 Encryption & Cryptography

### Vault Encryption
- **Algorithm:** AES-256-GCM (Galois/Counter Mode) for authenticated encryption.
- **Key Derivation (KDF):** Argon2id with a progressive salt.
- **Master Password:** Never stored on disk. It is used only to derive the master key in RAM.

### Hardware Communication
- **Protocol:** Serial CDC encrypted tunnel (Conceptual) / Raw Serial.
- **Physical Trigger:** No password can be typed via HID without a physical button press on the device.
- **Sensitive Data:** Decrypted passwords only stay in the device's RAM for the duration of the typing action.

## 🛡️ Security Hardening (v1.1+)

### 1. Memory Safety (Rust & MicroPython)
- **Zeroize:** All sensitive buffers (master key, intermediate plaintext) in the Rust backend are explicitly zeroed out in RAM using the `zeroize` crate immediately after use.
- **Firmware GC:** The MicroPython firmware explicitly clears the pending password buffer and triggers Garbage Collection (`gc.collect()`) after every `TYPING_DONE` event.

### 2. Brute-Force Protection
- **Progressive Lockout:** The desktop app implements a login lockout that doubles with every failed attempt (e.g., 4s, 8s, 16s...). This effectively mitigates high-speed automated attacks on the master password.

### 3. Physical Security
- **No Persistence:** The hardware device does not store passwords in its non-volatile memory (NVM/Flash). If the device is stolen, no data can be recovered from it.

## ⚠️ Reporting a Vulnerability
If you discover a security vulnerability, please do NOT open a public issue. Instead, contact the maintainers directly or follow the coordinated disclosure process.

---
*Note: This software is provided as-is. For maximum security, use a strong, unique master password.*
