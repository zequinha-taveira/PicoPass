#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

mod vault;
mod serial;
mod license;
use vault::{Vault, PasswordEntry, get_now};
use serial::{find_pico, add_password as serial_add_password, type_password as serial_type_password, delete_password as serial_delete_password, DeviceInfo};
use license::{LicenseStore, LicenseInfo, ActivationResult, RegistrationResult, BoardProfile, DeviceSummary};
use std::sync::Mutex;
use std::path::PathBuf;
use tauri::State;

use zeroize::Zeroizing;

struct AppState {
    vault: Mutex<Vault>,
    master_key: Mutex<Option<Zeroizing<[u8; 32]>>>,
    failed_attempts: Mutex<u32>,
    lockout_until: Mutex<u64>,
    license_store: Mutex<LicenseStore>,
}

#[tauri::command]
fn list_serial_ports() -> Result<Vec<DeviceInfo>, String> {
    if let Some(device) = find_pico() {
        Ok(vec![device])
    } else {
        Err("Hardware not detected. Connect a supported device.".into())
    }
}

#[tauri::command]
fn unlock_vault(password: String, state: State<AppState>) -> Result<String, String> {
    let now = get_now();
    let mut lockout_guard = state.lockout_until.lock().unwrap();
    
    if now < *lockout_guard {
        let remaining = *lockout_guard - now;
        return Err(format!("Locked out for {} more seconds", remaining));
    }

    // In a real app, we would use a stored salt. For PoC, we use a fixed one.
    let salt = b"picopass_fixed_salt";
    let key = Vault::derive_key(&password, salt);
    
    // Try to load the vault
    let vault_path = PathBuf::from("vault.json");
    let loaded_vault = Vault::load(&vault_path)?;
    
    // Verify if key is correct (by trying to decrypt the first entry if exists, or a dummy)
    // For simplicity in this PoC, we assume if load succeeds and we have a key, it's correct.
    // However, we should implement a check.
    
    let mut failed_guard = state.failed_attempts.lock().unwrap();
    
    // Simulate verification (placeholder)
    let is_correct = password == "master123"; // Simplified check for demonstration
    
    if !is_correct {
        *failed_guard += 1;
        let delay = (2u64.pow(*failed_guard)) * 2; // Progressive delay: 4s, 8s, 16s...
        *lockout_guard = now + delay;
        return Err(format!("Invalid password. Lockout for {} seconds.", delay));
    }

    // Reset on success
    *failed_guard = 0;
    *lockout_guard = 0;

    let mut vault_guard = state.vault.lock().unwrap();
    let mut key_guard = state.master_key.lock().unwrap();
    
    *vault_guard = loaded_vault;
    *key_guard = Some(key);
    
    Ok("Vault unlocked successfully".into())
}

#[tauri::command]
fn add_password(
    service: String, 
    username: String, 
    password_text: String, 
    state: State<AppState>
) -> Result<String, String> {
    let key_guard = state.master_key.lock().unwrap();
    let key = key_guard.as_ref().ok_or("Vault is locked")?;
    
    let (encrypted, nonce) = Vault::encrypt_password(&password_text, &key)?;
    
    let entry = PasswordEntry {
        id: uuid::Uuid::new_v4().to_string(),
        service,
        username,
        encrypted_password: encrypted,
        nonce,
        created_at: get_now(),
        modified_at: get_now(),
    };
    
    let mut vault_guard = state.vault.lock().unwrap();
    vault_guard.add_entry(entry);
    vault_guard.save(&PathBuf::from("vault.json"))?;
    
    Ok("Password added successfully".into())
}

#[tauri::command]
fn list_passwords(state: State<AppState>) -> Result<Vec<vault::PasswordEntry>, String> {
    let vault_guard = state.vault.lock().unwrap();
    Ok(vault_guard.list_entries())
}

#[tauri::command]
fn send_to_pico(id: String, state: State<AppState>) -> Result<String, String> {
    let vault_guard = state.vault.lock().unwrap();
    let key_guard = state.master_key.lock().unwrap();
    let key = key_guard.as_ref().ok_or("Vault is locked")?;
    
    let entry = vault_guard.entries.iter().find(|e| e.id == id)
        .ok_or("Password not found")?;
        
    let decrypted = Vault::decrypt_password(&entry.encrypted_password, &entry.nonce, &key)?;
    
    // Real serial communication
    let device = find_pico().ok_or("Device disconnected. Check hardware.")?;
    
    // Use slot 3 as temporary scratchpad for typing
    let scratch_slot = 3;
    
    serial_add_password(&device.port, scratch_slot, &decrypted)
        .map_err(|e| format!("Failed to set temp password: {}", e))?;
        
    serial_type_password(&device.port, scratch_slot)
        .map_err(|e| format!("Failed to type: {}", e))?;
        
    // Cleanup
    let _ = serial_delete_password(&device.port, scratch_slot);
    
    Ok(format!("Successfully typed {} password!", entry.service))
}

#[tauri::command]
fn export_vault_csv(state: State<AppState>) -> Result<String, String> {
    let vault_guard = state.vault.lock().unwrap();
    vault_guard.export_to_csv()
}

#[tauri::command]
fn perform_backup(state: State<AppState>) -> Result<Vec<u8>, String> {
    let vault_guard = state.vault.lock().unwrap();
    vault_guard.create_backup()
}

// ============== LICENSE COMMANDS ==============

#[tauri::command]
fn get_license_info(state: State<AppState>) -> Result<LicenseInfo, String> {
    let license_guard = state.license_store.lock().unwrap();
    Ok(license_guard.get_info())
}

#[tauri::command]
fn activate_license(license_key: String, state: State<AppState>) -> Result<ActivationResult, String> {
    let mut license_guard = state.license_store.lock().unwrap();
    Ok(license_guard.activate_license(&license_key))
}

#[tauri::command]
fn register_current_device(
    serial_number: String,
    board_type: String,
    profile_id: String,
    friendly_name: Option<String>,
    state: State<AppState>,
) -> Result<RegistrationResult, String> {
    let mut license_guard = state.license_store.lock().unwrap();
    
    let profile = BoardProfile::find_by_id(&profile_id)
        .or_else(|| BoardProfile::find_by_detected_type(&board_type))
        .ok_or_else(|| format!("Unknown board profile: {}", profile_id))?;
    
    Ok(license_guard.register_device(serial_number, board_type, &profile, friendly_name))
}

#[tauri::command]
fn list_registered_devices(state: State<AppState>) -> Result<Vec<DeviceSummary>, String> {
    let license_guard = state.license_store.lock().unwrap();
    let info = license_guard.get_info();
    Ok(info.registered_devices)
}

#[tauri::command]
fn unregister_device(serial_number: String, state: State<AppState>) -> Result<String, String> {
    let mut license_guard = state.license_store.lock().unwrap();
    license_guard.unregister_device(&serial_number)?;
    Ok("Device unregistered successfully".into())
}

#[tauri::command]
fn get_board_profiles() -> Vec<BoardProfile> {
    BoardProfile::get_all_profiles()
}

#[tauri::command]
fn check_device_registration(serial_number: String, state: State<AppState>) -> Result<bool, String> {
    let license_guard = state.license_store.lock().unwrap();
    Ok(license_guard.is_device_registered(&serial_number))
}

#[tauri::command]
fn generate_demo_key(tier: String, seats: u32) -> String {
    license::generate_demo_license_key(&tier, seats)
}

fn main() {
    // Initialize license store
    let license_store = LicenseStore::new()
        .expect("Failed to initialize license store");

    tauri::Builder::default()
        .manage(AppState {
            vault: Mutex::new(Vault::new()),
            master_key: Mutex::new(None),
            failed_attempts: Mutex::new(0),
            lockout_until: Mutex::new(0),
            license_store: Mutex::new(license_store),
        })
        .invoke_handler(tauri::generate_handler![
            // Vault commands
            list_serial_ports, 
            unlock_vault, 
            add_password, 
            list_passwords,
            send_to_pico,
            export_vault_csv,
            perform_backup,
            // License commands
            get_license_info,
            activate_license,
            register_current_device,
            list_registered_devices,
            unregister_device,
            get_board_profiles,
            check_device_registration,
            generate_demo_key
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}

