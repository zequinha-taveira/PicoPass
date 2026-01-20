use serialport;
use std::time::Duration;
use std::io::{Write, Read};
use serde::{Serialize, Deserialize};

#[derive(Serialize, Deserialize, Debug, Clone)]
pub struct DeviceInfo {
    pub port: String,
    pub board_type: String,
    pub name: String,
}

pub fn find_pico() -> Option<DeviceInfo> {
    let ports = serialport::available_ports().ok()?;
    for p in ports {
        if let serialport::SerialPortType::UsbPort(info) = p.port_type {
            // Mapping VIDs to board types
            let (board_type, name) = match info.vid {
                0x2e8a => {
                if info.pid == 0x000f || info.pid == 0x0001 { // Common RP2350 PIDs
                    ("raspberry_pi_rp2350", "Raspberry Pi RP2350")
                } else {
                    ("raspberry_pi_pico", "Raspberry Pi Pico")
                }
            },
            0x303a => ("esp32_s3", "ESP32-S3"),
            0x2341 => ("arduino_hid", "Arduino HID"),
            _ => continue,
            };

            return Some(DeviceInfo {
                port: p.port_name,
                board_type: board_type.to_string(),
                name: name.to_string(),
            });
        }
    }
    None
}

pub fn send_password(port_name: &str, password: &str, service: &str) -> Result<(), String> {
    let mut port = serialport::new(port_name, 115_200)
        .timeout(Duration::from_millis(1000))
        .open()
        .map_err(|e| e.to_string())?;

    let command = format!("TYPE:{}|{}\n", password, service);
    port.write_all(command.as_bytes()).map_err(|e| e.to_string())?;
    
    // Wait for acknowledgment from Pico
    let mut buffer: [u8; 32] = [0; 32];
    match port.read(&mut buffer) {
        Ok(t) => {
            let response = String::from_utf8_lossy(&buffer[..t]);
            if response.contains("READY_TO_TYPE") {
                Ok(())
            } else {
                Err(format!("Pico responded with: {}", response))
            }
        }
        Err(e) => Err(format!("Failed to read from Pico: {}", e)),
    }
}
