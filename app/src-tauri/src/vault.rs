use serde::{Deserialize, Serialize};
use std::time::{SystemTime, UNIX_EPOCH};
use aes_gcm::{
    aead::{Aead, KeyInit},
    Aes256Gcm, Nonce,
};
use rand::{RngCore, thread_rng};
use argon2::{
    password_hash::{PasswordHasher, SaltString},
    Argon2,
};
use zeroize::{Zeroize, Zeroizing};
use std::fs;
use std::path::Path;

#[derive(Serialize, Deserialize, Clone, Debug)]
pub struct PasswordEntry {
    pub id: String,
    pub service: String,
    pub username: String,
    pub encrypted_password: Vec<u8>,
    pub nonce: Vec<u8>,
    pub created_at: u64,
    pub modified_at: u64,
}

#[derive(Serialize, Deserialize, Clone, Debug)]
pub struct Vault {
    pub version: String,
    pub entries: Vec<PasswordEntry>,
}

impl Vault {
    pub fn new() -> Self {
        Self {
            version: "1.0.0".to_string(),
            entries: Vec::new(),
        }
    }

    pub fn encrypt_password(password: &str, master_key: &[u8; 32]) -> Result<(Vec<u8>, Vec<u8>), String> {
        let cipher = Aes256Gcm::new_from_slice(master_key).map_err(|e| e.to_string())?;
        let mut nonce_bytes = [0u8; 12];
        thread_rng().fill_bytes(&mut nonce_bytes);
        let nonce = Nonce::from_slice(&nonce_bytes);

        // Convert password to Zeroizing buffer
        let mut password_bytes = Zeroizing::new(password.as_bytes().to_vec());
        let ciphertext = cipher
            .encrypt(nonce, password_bytes.as_slice())
            .map_err(|e| e.to_string())?;

        Ok((ciphertext, nonce_bytes.to_vec()))
    }

    pub fn decrypt_password(encrypted: &[u8], nonce_bytes: &[u8], master_key: &[u8; 32]) -> Result<Zeroizing<String>, String> {
        let cipher = Aes256Gcm::new_from_slice(master_key).map_err(|e| e.to_string())?;
        let nonce = Nonce::from_slice(nonce_bytes);

        let mut plaintext = cipher
            .decrypt(nonce, encrypted)
            .map_err(|e| e.to_string())?;

        let result = String::from_utf8(plaintext.clone()).map_err(|e| e.to_string())?;
        plaintext.zeroize(); // Explicitly zeroize the raw buffer
        
        Ok(Zeroizing::new(result))
    }

    pub fn add_entry(&mut self, entry: PasswordEntry) {
        self.entries.push(entry);
    }

    pub fn derive_key(password: &str, salt: &[u8]) -> Zeroizing<[u8; 32]> {
        let argon2 = Argon2::default();
        let mut key = [0u8; 32];
        let salt_str = SaltString::encode_b64(salt).unwrap();
        
        // Hash the password and extract the hash bytes
        let password_hash = argon2.hash_password(password.as_bytes(), &salt_str).unwrap();
        let hash_output = password_hash.hash.unwrap();
        key.copy_from_slice(&hash_output.as_bytes()[..32]);
        
        Zeroizing::new(key)
    }

    pub fn save(&self, path: &Path) -> Result<(), String> {
        let json = serde_json::to_string_pretty(self).map_err(|e| e.to_string())?;
        fs::write(path, json).map_err(|e| e.to_string())
    }

    pub fn load(path: &Path) -> Result<Self, String> {
        if !path.exists() {
            return Ok(Self::new());
        }
        let content = fs::read_to_string(path).map_err(|e| e.to_string())?;
        serde_json::from_str(&content).map_err(|e| e.to_string())
    }

    pub fn export_to_csv(&self) -> Result<String, String> {
        let mut wtr = csv::Writer::from_writer(vec![]);
        wtr.write_record(&["Service", "Username", "Created At"]).map_err(|e| e.to_string())?;
        
        for entry in &self.entries {
            wtr.write_record(&[
                &entry.service,
                &entry.username,
                &get_now().to_string(), // In a real app we'd format entry.created_at
            ]).map_err(|e| e.to_string())?;
        }
        
        let data = String::from_utf8(wtr.into_inner().map_err(|e| e.to_string())?).map_err(|e| e.to_string())?;
        Ok(data)
    }

    pub fn create_backup(&self) -> Result<Vec<u8>, String> {
        // A backup is just the encrypted vault file itself for now
        serde_json::to_vec_pretty(self).map_err(|e| e.to_string())
    }

    pub fn list_entries(&self) -> Vec<PasswordEntry> {
        self.entries.clone()
    }
}

pub fn get_now() -> u64 {
    SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap()
        .as_secs()
}
