// license.rs - PicoPass Licensing System
// Per-device licensing with configuration schema generation

use serde::{Deserialize, Serialize};
use sha2::{Digest, Sha256};
use std::fs;
use std::path::PathBuf;

/// Pull mode for GPIO buttons
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub enum PullMode {
    Up,
    Down,
    None,
}

/// Display types supported
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum DisplayType {
    SSD1306,
    SH1106,
    ST7789,
    None,
}

/// Hardware profile for a specific board variant
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct BoardProfile {
    pub id: String,
    pub vendor: String,
    pub model: String,
    pub chip: String,
    pub led_gpio: u8,
    pub led_inverted: bool,
    pub button_gpio: u8,
    pub button_pull: PullMode,
    pub has_display: bool,
    pub display_type: Option<DisplayType>,
    pub display_sda: Option<u8>,
    pub display_scl: Option<u8>,
    pub notes: String,
}

impl BoardProfile {
    /// Get all predefined board profiles
    pub fn get_all_profiles() -> Vec<BoardProfile> {
        vec![
            // Raspberry Pi Official Boards
            BoardProfile {
                id: "raspberry_pi_pico".into(),
                vendor: "Raspberry Pi".into(),
                model: "Pico (RP2040)".into(),
                chip: "RP2040".into(),
                led_gpio: 25,
                led_inverted: false,
                button_gpio: 15,
                button_pull: PullMode::Up,
                has_display: false,
                display_type: None,
                display_sda: None,
                display_scl: None,
                notes: "⚠️ RP2040 not recommended for security keys".into(),
            },
            BoardProfile {
                id: "raspberry_pi_pico_w".into(),
                vendor: "Raspberry Pi".into(),
                model: "Pico W (RP2040)".into(),
                chip: "RP2040".into(),
                led_gpio: 0, // LED is on CYW43 chip, requires special handling
                led_inverted: false,
                button_gpio: 15,
                button_pull: PullMode::Up,
                has_display: false,
                display_type: None,
                display_sda: None,
                display_scl: None,
                notes: "⚠️ RP2040 not recommended. LED on WiFi chip.".into(),
            },
            BoardProfile {
                id: "raspberry_pi_pico2".into(),
                vendor: "Raspberry Pi".into(),
                model: "Pico 2 (RP2350)".into(),
                chip: "RP2350".into(),
                led_gpio: 25,
                led_inverted: false,
                button_gpio: 15,
                button_pull: PullMode::Up,
                has_display: false,
                display_type: None,
                display_sda: None,
                display_scl: None,
                notes: "✅ Recommended for security applications".into(),
            },
            // Waveshare Boards
            BoardProfile {
                id: "waveshare_rp2350_zero".into(),
                vendor: "Waveshare".into(),
                model: "RP2350-Zero".into(),
                chip: "RP2350".into(),
                led_gpio: 25,
                led_inverted: false,
                button_gpio: 15,
                button_pull: PullMode::Up,
                has_display: false,
                display_type: None,
                display_sda: None,
                display_scl: None,
                notes: "✅ Compact form factor, RP2350".into(),
            },
            BoardProfile {
                id: "waveshare_rp2350_one".into(),
                vendor: "Waveshare".into(),
                model: "RP2350-One".into(),
                chip: "RP2350".into(),
                led_gpio: 25,
                led_inverted: false,
                button_gpio: 15,
                button_pull: PullMode::Up,
                has_display: false,
                display_type: None,
                display_sda: None,
                display_scl: None,
                notes: "✅ More I/O, RP2350".into(),
            },
            BoardProfile {
                id: "waveshare_rp2350_plus".into(),
                vendor: "Waveshare".into(),
                model: "RP2350-Plus".into(),
                chip: "RP2350".into(),
                led_gpio: 25,
                led_inverted: false,
                button_gpio: 15,
                button_pull: PullMode::Up,
                has_display: false,
                display_type: None,
                display_sda: None,
                display_scl: None,
                notes: "✅ Extended features, RP2350".into(),
            },
            // ESP32 Boards
            BoardProfile {
                id: "esp32_s3".into(),
                vendor: "Espressif".into(),
                model: "ESP32-S3".into(),
                chip: "ESP32-S3".into(),
                led_gpio: 48,
                led_inverted: false,
                button_gpio: 0,
                button_pull: PullMode::Up,
                has_display: false,
                display_type: None,
                display_sda: None,
                display_scl: None,
                notes: "✅ Native WiFi/BLE support".into(),
            },
            // Custom/Generic
            BoardProfile {
                id: "custom".into(),
                vendor: "Custom".into(),
                model: "User Defined".into(),
                chip: "Unknown".into(),
                led_gpio: 25,
                led_inverted: false,
                button_gpio: 15,
                button_pull: PullMode::Up,
                has_display: false,
                display_type: None,
                display_sda: None,
                display_scl: None,
                notes: "⚙️ Manually configured board".into(),
            },
        ]
    }

    /// Find profile by ID
    pub fn find_by_id(id: &str) -> Option<BoardProfile> {
        Self::get_all_profiles().into_iter().find(|p| p.id == id)
    }

    /// Find profile by detected board type from USB
    pub fn find_by_detected_type(board_type: &str) -> Option<BoardProfile> {
        Self::get_all_profiles()
            .into_iter()
            .find(|p| p.id == board_type || p.model.to_lowercase().contains(&board_type.to_lowercase()))
    }
}

/// Device-specific configuration schema
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DeviceConfig {
    pub flash_offset: u32,
    pub flash_size: u32,
    pub led_gpio: u8,
    pub led_inverted: bool,
    pub led_brightness: u8,
    pub button_gpio: u8,
    pub button_pull: PullMode,
    pub button_debounce_ms: u16,
    pub serial_baud: u32,
    pub has_display: bool,
    pub display_sda: Option<u8>,
    pub display_scl: Option<u8>,
    // USB Identification
    pub usb_product_name: String,
    pub usb_manufacturer_name: String,
    pub use_custom_usb_id: bool,
    pub usb_vid: Option<u16>,
    pub usb_pid: Option<u16>,
}

impl DeviceConfig {
    /// Generate configuration from board profile
    pub fn from_profile(profile: &BoardProfile) -> Self {
        DeviceConfig {
            flash_offset: 0x10000000,
            flash_size: if profile.chip == "RP2350" { 4 * 1024 * 1024 } else { 2 * 1024 * 1024 },
            led_gpio: profile.led_gpio,
            led_inverted: profile.led_inverted,
            led_brightness: 100,
            button_gpio: profile.button_gpio,
            button_pull: profile.button_pull.clone(),
            button_debounce_ms: 50,
            serial_baud: 115200,
            has_display: profile.has_display,
            display_sda: profile.display_sda,
            display_scl: profile.display_scl,
            // Defaults for PicoPass
            usb_product_name: "PicoPass Security Key".to_string(),
            usb_manufacturer_name: "PicoPass".to_string(),
            use_custom_usb_id: false,
            usb_vid: None,
            usb_pid: None,
        }
    }
}

/// Registered device with its configuration
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RegisteredDevice {
    pub serial_number: String,
    pub board_type: String,
    pub profile_id: String,
    pub configuration: DeviceConfig,
    pub activated_at: u64,
    pub last_seen: u64,
    pub friendly_name: Option<String>,
}

/// License tier
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub enum LicenseTier {
    Free,
    Single,
    Multi { max_seats: u32 },
}

impl LicenseTier {
    pub fn max_devices(&self) -> u32 {
        match self {
            LicenseTier::Free => 0,
            LicenseTier::Single => 1,
            LicenseTier::Multi { max_seats } => *max_seats,
        }
    }
}

/// User license information
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct UserLicense {
    pub version: u32,
    pub license_key: String,
    pub user_id: String,
    pub tier: LicenseTier,
    pub registered_devices: Vec<RegisteredDevice>,
    pub created_at: u64,
    pub valid_until: Option<u64>,
}

impl UserLicense {
    /// Create a new empty license (free tier)
    pub fn new_free() -> Self {
        UserLicense {
            version: 2,
            license_key: String::new(),
            user_id: String::new(),
            tier: LicenseTier::Free,
            registered_devices: Vec::new(),
            created_at: crate::vault::get_now(),
            valid_until: None,
        }
    }

    /// Check if license can register more devices
    pub fn can_register_device(&self) -> bool {
        (self.registered_devices.len() as u32) < self.tier.max_devices()
    }

    /// Get remaining seats
    pub fn remaining_seats(&self) -> u32 {
        let max = self.tier.max_devices();
        let used = self.registered_devices.len() as u32;
        if max > used { max - used } else { 0 }
    }

    /// Find registered device by serial
    pub fn find_device(&self, serial: &str) -> Option<&RegisteredDevice> {
        self.registered_devices.iter().find(|d| d.serial_number == serial)
    }

    /// Check if device is already registered
    pub fn is_device_registered(&self, serial: &str) -> bool {
        self.find_device(serial).is_some()
    }
}

/// License validation result
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct LicenseValidation {
    pub is_valid: bool,
    pub tier: LicenseTier,
    pub max_devices: u32,
    pub error: Option<String>,
}

/// Activation result
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ActivationResult {
    pub success: bool,
    pub message: String,
    pub tier: Option<LicenseTier>,
    pub max_devices: Option<u32>,
}

/// Registration result
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RegistrationResult {
    pub success: bool,
    pub message: String,
    pub device: Option<RegisteredDevice>,
    pub activation_key: Option<String>,
}

/// License info for frontend
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct LicenseInfo {
    pub tier: String,
    pub max_devices: u32,
    pub used_devices: u32,
    pub remaining_seats: u32,
    pub is_valid: bool,
    pub valid_until: Option<u64>,
    pub registered_devices: Vec<DeviceSummary>,
}

/// Device summary for frontend
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DeviceSummary {
    pub serial_number: String,
    pub board_type: String,
    pub friendly_name: Option<String>,
    pub activated_at: u64,
    pub last_seen: u64,
}

impl From<&RegisteredDevice> for DeviceSummary {
    fn from(device: &RegisteredDevice) -> Self {
        DeviceSummary {
            serial_number: device.serial_number.clone(),
            board_type: device.board_type.clone(),
            friendly_name: device.friendly_name.clone(),
            activated_at: device.activated_at,
            last_seen: device.last_seen,
        }
    }
}

/// License Store - manages license persistence
pub struct LicenseStore {
    license_path: PathBuf,
    license: UserLicense,
}

impl LicenseStore {
    const SECRET_SALT: &'static str = "PicoPass_Device_Secure_2026";
    const LICENSE_VERSION: u32 = 2;

    /// Create or load license store
    pub fn new() -> Result<Self, String> {
        let license_path = Self::get_license_path()?;
        let license = Self::load_or_create(&license_path)?;
        
        Ok(LicenseStore {
            license_path,
            license,
        })
    }

    /// Get license file path
    fn get_license_path() -> Result<PathBuf, String> {
        let app_data = dirs::data_local_dir()
            .ok_or("Could not find app data directory")?;
        let picopass_dir = app_data.join("PicoPass");
        
        if !picopass_dir.exists() {
            fs::create_dir_all(&picopass_dir)
                .map_err(|e| format!("Failed to create PicoPass directory: {}", e))?;
        }
        
        Ok(picopass_dir.join("license.json"))
    }

    /// Load existing license or create new one
    fn load_or_create(path: &PathBuf) -> Result<UserLicense, String> {
        if path.exists() {
            let content = fs::read_to_string(path)
                .map_err(|e| format!("Failed to read license file: {}", e))?;
            serde_json::from_str(&content)
                .map_err(|e| format!("Failed to parse license file: {}", e))
        } else {
            Ok(UserLicense::new_free())
        }
    }

    /// Save license to disk
    pub fn save(&self) -> Result<(), String> {
        let content = serde_json::to_string_pretty(&self.license)
            .map_err(|e| format!("Failed to serialize license: {}", e))?;
        fs::write(&self.license_path, content)
            .map_err(|e| format!("Failed to write license file: {}", e))
    }

    /// Get current license info
    pub fn get_info(&self) -> LicenseInfo {
        LicenseInfo {
            tier: match &self.license.tier {
                LicenseTier::Free => "FREE".into(),
                LicenseTier::Single => "SINGLE".into(),
                LicenseTier::Multi { .. } => "MULTI".into(),
            },
            max_devices: self.license.tier.max_devices(),
            used_devices: self.license.registered_devices.len() as u32,
            remaining_seats: self.license.remaining_seats(),
            is_valid: self.license.tier != LicenseTier::Free,
            valid_until: self.license.valid_until,
            registered_devices: self.license.registered_devices.iter().map(|d| d.into()).collect(),
        }
    }

    /// Validate license key format and checksum
    pub fn validate_license_key(key: &str) -> LicenseValidation {
        // Format: PICO-XXXX-YYYY-ZZZZ-TTTT
        let parts: Vec<&str> = key.split('-').collect();
        
        if parts.len() != 5 || parts[0] != "PICO" {
            return LicenseValidation {
                is_valid: false,
                tier: LicenseTier::Free,
                max_devices: 0,
                error: Some("Invalid license key format".into()),
            };
        }

        // Decode tier from YYYY segment
        let tier_code = parts[2];
        let tier = match tier_code.chars().next() {
            Some('S') => LicenseTier::Single,
            Some('M') => {
                let seats = tier_code[1..].parse::<u32>().unwrap_or(3);
                LicenseTier::Multi { max_seats: seats }
            },
            _ => {
                return LicenseValidation {
                    is_valid: false,
                    tier: LicenseTier::Free,
                    max_devices: 0,
                    error: Some("Invalid tier code".into()),
                };
            }
        };

        // Verify checksum (TTTT)
        let data_to_hash = format!("{}-{}-{}-{}", parts[0], parts[1], parts[2], parts[3]);
        let mut hasher = Sha256::new();
        hasher.update(data_to_hash.as_bytes());
        hasher.update(Self::SECRET_SALT.as_bytes());
        let hash = hasher.finalize();
        let expected_checksum = hex::encode(&hash[..2]).to_uppercase();
        
        if parts[4] != expected_checksum {
            return LicenseValidation {
                is_valid: false,
                tier: LicenseTier::Free,
                max_devices: 0,
                error: Some("Invalid checksum".into()),
            };
        }

        LicenseValidation {
            is_valid: true,
            tier: tier.clone(),
            max_devices: tier.max_devices(),
            error: None,
        }
    }

    /// Activate a license key
    pub fn activate_license(&mut self, key: &str) -> ActivationResult {
        let validation = Self::validate_license_key(key);
        
        if !validation.is_valid {
            return ActivationResult {
                success: false,
                message: validation.error.unwrap_or("Invalid license key".into()),
                tier: None,
                max_devices: None,
            };
        }

        self.license.license_key = key.to_string();
        self.license.tier = validation.tier.clone();
        self.license.created_at = crate::vault::get_now();
        
        if let Err(e) = self.save() {
            return ActivationResult {
                success: false,
                message: format!("Failed to save license: {}", e),
                tier: None,
                max_devices: None,
            };
        }

        ActivationResult {
            success: true,
            message: "License activated successfully!".into(),
            tier: Some(validation.tier),
            max_devices: Some(validation.max_devices),
        }
    }

    /// Register a new device
    pub fn register_device(
        &mut self,
        serial_number: String,
        board_type: String,
        profile: &BoardProfile,
        friendly_name: Option<String>,
    ) -> RegistrationResult {
        // Check if already registered
        if self.license.is_device_registered(&serial_number) {
            let device = self.license.find_device(&serial_number).unwrap();
            let activation_key = self.calculate_activation_key(&serial_number, &board_type);
            return RegistrationResult {
                success: true,
                message: "Device already registered".into(),
                device: Some(device.clone()),
                activation_key: Some(activation_key),
            };
        }

        // Check if can register
        if !self.license.can_register_device() {
            return RegistrationResult {
                success: false,
                message: format!(
                    "License limit reached ({}/{}). Purchase additional seats.",
                    self.license.registered_devices.len(),
                    self.license.tier.max_devices()
                ),
                device: None,
                activation_key: None,
            };
        }

        // Create device configuration
        let config = DeviceConfig::from_profile(profile);
        let now = crate::vault::get_now();

        let device = RegisteredDevice {
            serial_number: serial_number.clone(),
            board_type: board_type.clone(),
            profile_id: profile.id.clone(),
            configuration: config,
            activated_at: now,
            last_seen: now,
            friendly_name,
        };

        self.license.registered_devices.push(device.clone());

        if let Err(e) = self.save() {
            // Rollback
            self.license.registered_devices.pop();
            return RegistrationResult {
                success: false,
                message: format!("Failed to save device: {}", e),
                device: None,
                activation_key: None,
            };
        }

        let activation_key = self.calculate_activation_key(&serial_number, &board_type);

        RegistrationResult {
            success: true,
            message: "Device registered successfully!".into(),
            device: Some(device),
            activation_key: Some(activation_key),
        }
    }

    /// Unregister a device (free up seat)
    pub fn unregister_device(&mut self, serial_number: &str) -> Result<(), String> {
        let initial_len = self.license.registered_devices.len();
        self.license.registered_devices.retain(|d| d.serial_number != serial_number);
        
        if self.license.registered_devices.len() == initial_len {
            return Err("Device not found".into());
        }

        self.save()?;
        Ok(())
    }

    /// Calculate activation key for firmware
    pub fn calculate_activation_key(&self, serial_number: &str, board_type: &str) -> String {
        let data = format!("{}:{}:{}", serial_number, board_type, Self::SECRET_SALT);
        let mut hasher = Sha256::new();
        hasher.update(data.as_bytes());
        let result = hasher.finalize();
        hex::encode(&result[..8])
    }

    /// Get device configuration for activation
    pub fn get_device_config(&self, serial_number: &str) -> Option<&DeviceConfig> {
        self.license
            .find_device(serial_number)
            .map(|d| &d.configuration)
    }

    /// Update last seen timestamp
    pub fn update_last_seen(&mut self, serial_number: &str) {
        if let Some(device) = self.license.registered_devices
            .iter_mut()
            .find(|d| d.serial_number == serial_number)
        {
            device.last_seen = crate::vault::get_now();
            let _ = self.save();
        }
    }

    /// Check if device is registered
    pub fn is_device_registered(&self, serial_number: &str) -> bool {
        self.license.is_device_registered(serial_number)
    }

    /// Get license reference
    pub fn get_license(&self) -> &UserLicense {
        &self.license
    }
}

/// Generate a demo license key for testing
pub fn generate_demo_license_key(tier: &str, seats: u32) -> String {
    let user_id = "DEMO";
    let tier_code = match tier {
        "single" => "S001".to_string(),
        "multi" => format!("M{:03}", seats),
        _ => "S001".to_string(),
    };
    let expiry = "LIFE"; // Lifetime

    let data_to_hash = format!("PICO-{}-{}-{}", user_id, tier_code, expiry);
    let mut hasher = Sha256::new();
    hasher.update(data_to_hash.as_bytes());
    hasher.update(LicenseStore::SECRET_SALT.as_bytes());
    let hash = hasher.finalize();
    let checksum = hex::encode(&hash[..2]).to_uppercase();

    format!("PICO-{}-{}-{}-{}", user_id, tier_code, expiry, checksum)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_license_key_generation() {
        let key = generate_demo_license_key("single", 1);
        assert!(key.starts_with("PICO-"));
        
        let validation = LicenseStore::validate_license_key(&key);
        assert!(validation.is_valid);
        assert_eq!(validation.tier, LicenseTier::Single);
    }

    #[test]
    fn test_multi_license_key() {
        let key = generate_demo_license_key("multi", 5);
        let validation = LicenseStore::validate_license_key(&key);
        assert!(validation.is_valid);
        assert_eq!(validation.max_devices, 5);
    }

    #[test]
    fn test_invalid_license_key() {
        let validation = LicenseStore::validate_license_key("INVALID-KEY");
        assert!(!validation.is_valid);
    }

    #[test]
    fn test_board_profiles() {
        let profiles = BoardProfile::get_all_profiles();
        assert!(profiles.len() > 0);
        
        let pico2 = BoardProfile::find_by_id("raspberry_pi_pico2");
        assert!(pico2.is_some());
        assert_eq!(pico2.unwrap().chip, "RP2350");
    }
}
