// serial.rs - PicoPass Serial Communication
// Updated for JSON Firmware Protocol (v2)

use serialport;
use std::time::Duration;
use std::io::{Write, Read};
use serde::{Serialize, Deserialize};
// use sha2::{Sha256, Digest}; // Crypto now on firmware

use crate::license::DeviceConfig;

/// Extended device info with state
#[derive(Serialize, Deserialize, Debug, Clone)]
pub struct DeviceInfo {
    pub port: String,
    pub board_id: String, // from firmware
    pub version: String,
    pub unlocked: bool,
    pub slots_status: Vec<bool>, // true if occupied
    
    // Legacy/Computed fields for frontend compatibility
    pub board_type: String, 
    pub name: String,
    pub is_registered: bool, // Checked against local DB
    pub needs_configuration: bool,
}

impl DeviceInfo {
    pub fn get_profile_id(&self) -> String {
        // Simplified mapping or reuse board_type logic if needed
        "pico_pass_v1".to_string()
    }
}

// -- Protocol Structs --

#[derive(Serialize)]
struct Command<'a> {
    #[serde(rename = "type")]
    cmd_type: &'a str,
    #[serde(skip_serializing_if = "Option::is_none")]
    password: Option<&'a str>,
    #[serde(skip_serializing_if = "Option::is_none")]
    slot: Option<u8>,
    #[serde(skip_serializing_if = "Option::is_none")]
    timeout: Option<u32>,
}

#[derive(Deserialize, Debug)]
#[serde(untagged)]
enum FirmwareResponse {
    Status { status: String, version: Option<String>, message: Option<String>, timeout: Option<u32> },
    Id { board_id: String, version: String },
    State { unlocked: bool, slots: Vec<bool>, timeout: u32 },
}

/// Helper to send JSON command and parse response
fn send_command<T: for<'de> Deserialize<'de>>(port_name: &str, cmd: &Command) -> Result<T, String> {
    let mut port = serialport::new(port_name, 115_200)
        .timeout(Duration::from_millis(1000))
        .open()
        .map_err(|e| format!("Failed to open port: {}", e))?;

    let json = serde_json::to_string(cmd).map_err(|e| e.to_string())?;
    let json_cmd = format!("{}\n", json);
    
    // Clear buffer
    let _ = port.clear(serialport::ClearBuffer::All);
    
    port.write_all(json_cmd.as_bytes())
        .map_err(|e| format!("Write failed: {}", e))?;

    std::thread::sleep(Duration::from_millis(50));

    let mut serial_buf: Vec<u8> = vec![0; 1024];
    let t = port.read(&mut serial_buf).map_err(|e| format!("Read failed: {}", e))?;
    let response_str = String::from_utf8_lossy(&serial_buf[..t]);
    
    // Clean up response (trim whitespace)
    let clean = response_str.trim();
    
    serde_json::from_str(clean).map_err(|e| format!("Parse error: {} in '{}'", e, clean))
}

/// Find connected PicoPass device
pub fn find_pico() -> Option<DeviceInfo> {
    let ports = serialport::available_ports().ok()?;
    
    for p in ports {
        if let serialport::SerialPortType::UsbPort(_) = p.port_type {
            // Optimistic check: try to GET_ID
            let cmd = Command { cmd_type: "GET_ID", password: None, slot: None, timeout: None };
            
            if let Ok(FirmwareResponse::Id { board_id, version }) = send_command::<FirmwareResponse>(&p.port_name, &cmd) {
                
                // Also get STATUS
                let mut unlocked = false;
                let mut slots = vec![];
                
                let status_cmd = Command { cmd_type: "STATUS", password: None, slot: None, timeout: None };
                if let Ok(FirmwareResponse::State { unlocked: u, slots: s, .. }) = send_command::<FirmwareResponse>(&p.port_name, &status_cmd) {
                     unlocked = u;
                     slots = s;
                }

                return Some(DeviceInfo {
                    port: p.port_name,
                    board_id: board_id,
                    version: version,
                    unlocked: unlocked,
                    slots_status: slots,
                    board_type: "picopass_hw".to_string(),
                    name: "PicoPass Device".to_string(),
                    is_registered: false, // Updated by caller (Main) checking DB
                    needs_configuration: false, // Firmware manages config now
                });
            }
        }
    }
    None
}

// -- Commands --

pub fn unlock_device(port: &str, password: &str) -> Result<bool, String> {
    let cmd = Command { cmd_type: "UNLOCK", password: Some(password), slot: None, timeout: None };
    match send_command::<FirmwareResponse>(port, &cmd)? {
        FirmwareResponse::Status { status, .. } => Ok(status == "ok"),
        _ => Err("Invalid response".into())
    }
}

pub fn lock_device(port: &str) -> Result<(), String> {
    let cmd = Command { cmd_type: "LOCK", password: None, slot: None, timeout: None };
    let _ = send_command::<serde_json::Value>(port, &cmd); // Ignore response content, just check success
    Ok(())
}

pub fn add_password(port: &str, slot: u8, password: &str) -> Result<bool, String> {
    let cmd = Command { cmd_type: "ADD_PASSWORD", password: Some(password), slot: Some(slot), timeout: None };
    match send_command::<FirmwareResponse>(port, &cmd)? {
        FirmwareResponse::Status { status, .. } => Ok(status == "ok"),
        _ => Err("Invalid response".into())
    }
}

pub fn delete_password(port: &str, slot: u8) -> Result<bool, String> {
    let cmd = Command { cmd_type: "DELETE_PASSWORD", password: None, slot: Some(slot), timeout: None };
    match send_command::<FirmwareResponse>(port, &cmd)? {
        FirmwareResponse::Status { status, .. } => Ok(status == "ok"),
        _ => Err("Invalid response".into())
    }
}

pub fn type_password(port: &str, slot: u8) -> Result<(), String> {
    let cmd = Command { cmd_type: "TYPE_PASSWORD", password: None, slot: Some(slot), timeout: None };
    let _ = send_command::<serde_json::Value>(port, &cmd)?;
    Ok(())
}

// -- Legacy/Compatibility Wrappers --

/// Legacy activate: maps to Unlocking (setting master password) if needed
pub fn activate_device(port_name: &str, activation_key: &str, _config: &DeviceConfig) -> Result<(), String> {
    // In new firmware, "Activation" is setting the master password.
    // Use the provided key as the master password?
    // Or just fail if not Unlocking?
    
    // For compatibility with LicenseManager which generates a key,
    // we can use that key as the master password.
    unlock_device(port_name, activation_key).map(|_| ())
}

// Port helpers
pub fn list_available_ports() -> Vec<String> {
    serialport::available_ports()
        .map(|ports| ports.into_iter().map(|p| p.port_name).collect())
        .unwrap_or_default()
}
