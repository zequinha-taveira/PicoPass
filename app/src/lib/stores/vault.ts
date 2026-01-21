import { writable } from 'svelte/store';

// ============== VAULT TYPES ==============

export interface PasswordEntry {
    id: string;
    service: string;
    username: string;
    created_at: number;
    modified_at: number;
}

// ============== LICENSE TYPES ==============

export interface LicenseInfo {
    tier: string;  // 'FREE' | 'SINGLE' | 'MULTI' from backend
    max_devices: number;
    used_devices: number;
    remaining_seats: number;
    is_valid: boolean;
    valid_until: number | null;
    registered_devices: DeviceSummary[];
}

export interface DeviceSummary {
    serial_number: string;
    board_type: string;
    friendly_name: string | null;
    activated_at: number;
    last_seen: number;
}

export interface CurrentDevice {
    port: string;
    serial_number: string | null;
    board_type: string;
    name: string;
    is_registered: boolean;
    is_activated: boolean;
    needs_configuration: boolean;
    vendor_id: number;
    product_id: number;
}

// ============== VAULT STORES ==============

export const isLocked = writable(true);
export const passwords = writable<PasswordEntry[]>([]);
export const masterPassword = writable("");
export const loading = writable(false);

// ============== DEVICE STORES ==============

export const status = writable("Device: Disconnected");
export const isActivated = writable(false);
export const currentDevice = writable<CurrentDevice | null>(null);

// ============== LICENSE STORES ==============

export const licenseInfo = writable<LicenseInfo | null>(null);
export const registeredDevices = writable<DeviceSummary[]>([]);

// ============== HELPER FUNCTIONS ==============

export function updateDeviceStatus(device: CurrentDevice | null) {
    if (device) {
        currentDevice.set(device);
        isActivated.set(device.is_activated);

        let statusText = `Device: ${device.name}`;
        if (device.is_registered) {
            statusText += ' (Registered)';
        } else if (device.serial_number) {
            statusText += ' (Not Registered)';
        }
        status.set(statusText);
    } else {
        currentDevice.set(null);
        isActivated.set(false);
        status.set("Device: Disconnected");
    }
}

export function clearVault() {
    passwords.set([]);
    masterPassword.set("");
    isLocked.set(true);
}
