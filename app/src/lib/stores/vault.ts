import { writable } from 'svelte/store';

export interface PasswordEntry {
    id: string;
    service: string;
    username: string;
    created_at: number;
    modified_at: number;
}

export const isLocked = writable(true);
export const passwords = writable<PasswordEntry[]>([]);
export const status = writable("Device: Disconnected");
export const masterPassword = writable("");
export const loading = writable(false);
