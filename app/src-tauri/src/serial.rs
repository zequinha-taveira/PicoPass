use serialport;
use std::time::Duration;
use std::io::{Write, Read};
use serde::{Serialize, Deserialize};

#[derive(Serialize, Deserialize, Debug, Clone)]
pub struct DeviceInfo {
    pub port: String,
    pub board_type: String,
    pub name: String,
    pub serial_number: Option<String>,
    pub is_activated: bool,
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

            let mut device = DeviceInfo {
                port: p.port_name.clone(),
                board_type: board_type.to_string(),
                name: name.to_string(),
                serial_number: None,
                is_activated: false,
            };

            // Tenta obter informações adicionais via Serial
            if let Ok(mut port) = serialport::new(&p.port_name, 115_200)
                .timeout(Duration::from_millis(500))
                .open() 
            {
                let _ = port.write_all(b"PING\n");
                let mut buffer: [u8; 128] = [0; 128];
                if let Ok(t) = port.read(&mut buffer) {
                    let response = String::from_utf8_lossy(&buffer[..t]);
                    if response.contains("PONG") {
                        let parts: Vec<&str> = response.trim().split('|').collect();
                        if parts.len() >= 4 {
                            device.is_activated = parts[1] == "ACTIVATED";
                            device.serial_number = Some(parts[2].to_string());
                            // Opcional: atualizar board_type se o dispositivo reportar algo diferente
                        }
                    }
                }
            }

            // Se não estiver ativado mas tivermos o serial, tentamos ativar automaticamente
            if !device.is_activated && device.serial_number.is_some() {
                if let Some(key) = generate_license_key(device.serial_number.as_ref().unwrap(), &device.board_type) {
                    if let Ok(mut port) = serialport::new(&p.port_name, 115_200)
                        .timeout(Duration::from_millis(1000))
                        .open() 
                    {
                        let command = format!("ACTIVATE:{}\n", key);
                        let _ = port.write_all(command.as_bytes());
                        device.is_activated = true; // Assume sucesso para a UI, o firmware confirmará no próximo PING
                    }
                }
            }

            return Some(device);
        }
    }
    None
}

fn generate_license_key(serial: &str, board_type: &str) -> Option<String> {
    use sha2::{Sha256, Digest};
    let secret_salt = "PicoPass_Secure_2026";
    let data = format!("{}:{}:{}", serial, board_type, secret_salt);
    let mut hasher = Sha256::new();
    hasher.update(data.as_bytes());
    let result = hasher.finalize();
    Some(hex::encode(result)[..16].to_string())
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
