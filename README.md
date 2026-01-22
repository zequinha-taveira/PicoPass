# 🔐 PicoPass v1.0.0

> The open-source, hardware-backed secure password vault for Raspberry Pi Pico.

**Status:** ✅ Stable Release  
**License:** [MIT](LICENSE) | **Philosophy:** [Gratuita e Aberta - Sempre](MANIFESTO.md)

PicoPass is a high-security password manager that stores your encrypted vault on your PC but requires a physical Raspberry Pi Pico device to auto-type passwords with a button press. This prevents software-only attacks and provides a physical layer of security.

## 📋 Project Overview

- **Desktop App:** Tauri + Svelte + Rust (Supports firmware compilation and configuration)
- **Firmware:** Open-source MicroPython + C/C++ (Can be built and configured via the app)
- **Encryption:** AES-256-GCM
- **HID:** USB Auto-Type

## 📂 Project Structure

- `app/`: Desktop application (Tauri + Svelte)
- `firmware/`: Device firmware (MicroPython and C versions)
- `hardware/`: Schematics and hardware profiles
- `tools/`: Python helper scripts
- `docs/`: Project documentation
- `tests/`: End-to-end and integration tests

## 📚 Documentation
- [User Guide](docs/USER_GUIDE.md) - How to use PicoPass.
- [Flashing Guide](docs/FLASHING_GUIDE.md) - How to install firmware.
- [Developer Guide](docs/DEVELOPER_GUIDE.md) - How to contribute and build.
- [Hardware Setup](docs/HARDWARE_SETUP.md) - Wiring instructions.
- [API & Protocol](docs/API_DOCS.md) - Technical specifications.

## 🛠️ Development Plan

This project follows a 12-week development plan.

### Phase 1: Setup and Foundation (Weeks 1-2)
- Environment setup
- Project structure
- Initial prototypes (Hello World)
- Communication PoC (Serial, HID)

... (Full plan detailed in the user request)
