# 🔌 PicoPass API & Protocol Documentation

## 🖥️ Tauri Commands (Rust ↔ JS)

The frontend communicates with the Rust backend using the following `invoke` calls:

| Command | Arguments | Description |
|---------|-----------|-------------|
| `unlock_vault` | `password` | Derives the master key and decrypts the vault. |
| `add_password` | `service, username, passwordText` | Encrypts and saves a new entry. |
| `list_passwords`| None | Returns the list of stored (decrypted info) entries. |
| `send_to_pico` | `id` | Decrypts a password and sends it via Serial to the Pico. |
| `list_serial_ports`| None | Returns a list of `DeviceInfo` for connected hardware. |
| `export_vault_csv`| None | Generates a CSV of services and users. |
| `perform_backup` | None | Returns the full encrypted vault as a byte array. |

---

## 🔌 Serial Protocol (PC ↔ Hardware)

Communication happens over USB Serial (CDC) at **115200 baud**.

### PC -> Hardware Commands
- `PING`: Request status.
- `TYPE:password_text|service_name`: Sends the password and service metadata to be displayed on OLED.
- `LOCK`: Commands the device to clear all buffers and show "LOCKED" on OLED.

### Hardware -> PC Responses
- `PONG`: Response to `PING`.
- `READY_TO_TYPE`: Confirmation that the password was received and the device is waiting for a button press.
- `TYPING_DONE`: Sent after the password has been typed via HID and buffers cleared.
- `LOCKED`: Confirmation of buffer clear.

---

## ⌨️ USB HID Specs
The device registers as a **Standard USB HID Keyboard**.
- **Report ID:** 1
- **Interface Protocol:** Keyboard
- **Typing Speed:** 10ms delay between keypresses (optimized for compatibility).
