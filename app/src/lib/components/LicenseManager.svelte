<script lang="ts">
    import { createEventDispatcher, onMount } from "svelte";
    import { invoke } from "@tauri-apps/api/tauri";
    import { fade, fly, slide } from "svelte/transition";
    import {
        licenseInfo,
        registeredDevices,
        currentDevice,
    } from "../stores/vault";

    const dispatch = createEventDispatcher();

    // State
    let licenseKey = "";
    let activating = false;
    let registering = false;
    let error = "";
    let success = "";
    let friendlyName = "";
    let showActivateForm = false;
    let boardProfiles: any[] = [];

    interface LicenseInfo {
        tier: string;
        max_devices: number;
        used_devices: number;
        remaining_seats: number;
        is_valid: boolean;
        valid_until: number | null;
        registered_devices: DeviceSummary[];
    }

    interface DeviceSummary {
        serial_number: string;
        board_type: string;
        friendly_name: string | null;
        activated_at: number;
        last_seen: number;
    }

    interface BoardProfile {
        id: string;
        vendor: string;
        model: string;
        chip: string;
        notes: string;
    }

    onMount(async () => {
        await loadLicenseInfo();
        await loadBoardProfiles();
    });

    async function loadLicenseInfo() {
        try {
            const info: LicenseInfo = await invoke("get_license_info");
            licenseInfo.set(info);
            registeredDevices.set(info.registered_devices);
        } catch (e: any) {
            error = e.toString();
        }
    }

    async function loadBoardProfiles() {
        try {
            boardProfiles = await invoke("get_board_profiles");
        } catch (e: any) {
            console.error("Failed to load board profiles:", e);
        }
    }

    async function handleActivate() {
        if (!licenseKey.trim()) {
            error = "Please enter a license key";
            return;
        }

        activating = true;
        error = "";
        success = "";

        try {
            const result: any = await invoke("activate_license", {
                licenseKey: licenseKey.trim(),
            });

            if (result.success) {
                success = result.message;
                licenseKey = "";
                showActivateForm = false;
                await loadLicenseInfo();
            } else {
                error = result.message;
            }
        } catch (e: any) {
            error = e.toString();
        } finally {
            activating = false;
        }
    }

    async function handleRegisterDevice() {
        const device = $currentDevice;
        if (!device?.serial_number) {
            error = "No device connected or serial number not available";
            return;
        }

        registering = true;
        error = "";
        success = "";

        try {
            const result: any = await invoke("register_current_device", {
                serialNumber: device.serial_number,
                boardType: device.board_type,
                profileId: device.board_type,
                friendlyName: friendlyName.trim() || null,
            });

            if (result.success) {
                success = result.message;
                friendlyName = "";
                await loadLicenseInfo();

                // Update current device status
                currentDevice.update((d) =>
                    d
                        ? {
                              ...d,
                              is_registered: true,
                              needs_configuration: false,
                          }
                        : null,
                );
            } else {
                error = result.message;
            }
        } catch (e: any) {
            error = e.toString();
        } finally {
            registering = false;
        }
    }

    async function handleUnregister(serialNumber: string) {
        if (
            !confirm(
                "Are you sure you want to unregister this device? This will free up a license seat.",
            )
        ) {
            return;
        }

        try {
            await invoke("unregister_device", { serialNumber });
            success = "Device unregistered successfully";
            await loadLicenseInfo();
        } catch (e: any) {
            error = e.toString();
        }
    }

    async function generateDemoKey() {
        try {
            const key: string = await invoke("generate_demo_key", {
                tier: "single",
                seats: 1,
            });
            licenseKey = key;
            success = "Demo key generated! This is for testing only.";
        } catch (e: any) {
            error = e.toString();
        }
    }

    function formatDate(timestamp: number): string {
        return new Date(timestamp * 1000).toLocaleDateString(undefined, {
            year: "numeric",
            month: "short",
            day: "numeric",
            hour: "2-digit",
            minute: "2-digit",
        });
    }

    function getTierColor(tier: string): string {
        switch (tier) {
            case "MULTI":
                return "var(--primary)";
            case "SINGLE":
                return "#10b981";
            case "FREE":
                return "#6b7280";
            default:
                return "#6b7280";
        }
    }

    function close() {
        dispatch("close");
    }
</script>

<div class="modal-overlay" on:click|self={close} in:fade>
    <div class="glass-card license-modal" in:fly={{ y: 20 }}>
        <header>
            <h2>🔐 License Manager</h2>
            <button class="icon-btn" on:click={close}>✕</button>
        </header>

        <!-- Error/Success Messages -->
        {#if error}
            <div class="alert error" in:slide>
                <span>⚠️</span>
                {error}
                <button class="dismiss" on:click={() => (error = "")}>×</button>
            </div>
        {/if}

        {#if success}
            <div class="alert success" in:slide>
                <span>✓</span>
                {success}
                <button class="dismiss" on:click={() => (success = "")}
                    >×</button
                >
            </div>
        {/if}

        <div class="content">
            <!-- License Status Section -->
            <section class="status-section">
                <div class="status-card glass">
                    <div class="tier-display">
                        <span
                            class="tier-badge"
                            style="background: {getTierColor(
                                $licenseInfo?.tier || 'FREE',
                            )}"
                        >
                            {$licenseInfo?.tier || "FREE"}
                        </span>
                        {#if $licenseInfo?.is_valid}
                            <span class="valid-badge">✓ Active</span>
                        {:else}
                            <span class="invalid-badge">Not Activated</span>
                        {/if}
                    </div>

                    <div class="seats-info">
                        <div class="seats-bar">
                            <div
                                class="seats-used"
                                style="width: {$licenseInfo
                                    ? ($licenseInfo.used_devices /
                                          Math.max(
                                              $licenseInfo.max_devices,
                                              1,
                                          )) *
                                      100
                                    : 0}%"
                            ></div>
                        </div>
                        <span class="seats-text">
                            {$licenseInfo?.used_devices || 0} / {$licenseInfo?.max_devices ||
                                0} devices
                        </span>
                    </div>

                    {#if !$licenseInfo?.is_valid}
                        <button
                            class="btn-primary"
                            on:click={() =>
                                (showActivateForm = !showActivateForm)}
                        >
                            {showActivateForm
                                ? "Cancel"
                                : "🔑 Activate License"}
                        </button>
                    {/if}
                </div>

                <!-- Activation Form -->
                {#if showActivateForm}
                    <div class="activation-form glass" in:slide>
                        <h4>Enter License Key</h4>
                        <input
                            type="text"
                            bind:value={licenseKey}
                            placeholder="PICO-XXXX-XXXX-XXXX-XXXX"
                            class="license-input"
                        />
                        <div class="form-actions">
                            <button
                                class="btn-ghost"
                                on:click={generateDemoKey}
                            >
                                🧪 Generate Demo Key
                            </button>
                            <button
                                class="btn-primary"
                                on:click={handleActivate}
                                disabled={activating}
                            >
                                {activating ? "Activating..." : "Activate"}
                            </button>
                        </div>
                    </div>
                {/if}
            </section>

            <!-- Current Device Section -->
            {#if $currentDevice}
                <section class="device-section">
                    <h3>📟 Connected Device</h3>
                    <div class="device-card glass">
                        <div class="device-header">
                            <div class="device-icon">
                                {#if $currentDevice.board_type.includes("rp2350") || $currentDevice.board_type.includes("pico2")}
                                    🟢
                                {:else if $currentDevice.board_type.includes("esp32")}
                                    🔵
                                {:else}
                                    🟡
                                {/if}
                            </div>
                            <div class="device-info">
                                <span class="device-name"
                                    >{$currentDevice.name}</span
                                >
                                <code class="device-serial"
                                    >{$currentDevice.serial_number ||
                                        "Unknown"}</code
                                >
                                <span class="device-type"
                                    >{$currentDevice.board_type}</span
                                >
                            </div>
                            <div class="device-status">
                                {#if $currentDevice.is_registered}
                                    <span class="status-badge registered"
                                        >✓ Registered</span
                                    >
                                {:else}
                                    <span class="status-badge pending"
                                        >⏳ Not Registered</span
                                    >
                                {/if}
                            </div>
                        </div>

                        {#if !$currentDevice.is_registered && $licenseInfo?.is_valid}
                            <div class="register-form" in:slide>
                                <input
                                    type="text"
                                    bind:value={friendlyName}
                                    placeholder="Friendly name (optional)"
                                    class="name-input"
                                />
                                <button
                                    class="btn-primary"
                                    on:click={handleRegisterDevice}
                                    disabled={registering ||
                                        $licenseInfo.remaining_seats === 0}
                                >
                                    {registering
                                        ? "Registering..."
                                        : "📝 Register This Device"}
                                </button>
                                {#if $licenseInfo.remaining_seats === 0}
                                    <p class="warning-text">
                                        No available seats. Purchase additional
                                        seats to register more devices.
                                    </p>
                                {/if}
                            </div>
                        {:else if !$currentDevice.is_registered && !$licenseInfo?.is_valid}
                            <p class="info-text">
                                Activate a license to register this device.
                            </p>
                        {/if}
                    </div>
                </section>
            {:else}
                <section class="device-section">
                    <h3>📟 Connected Device</h3>
                    <div class="empty-device glass">
                        <span class="empty-icon">🔌</span>
                        <p>No device connected</p>
                        <span class="hint"
                            >Connect a PicoPass device via USB</span
                        >
                    </div>
                </section>
            {/if}

            <!-- Registered Devices Section -->
            <section class="devices-list-section">
                <h3>
                    📋 Registered Devices ({$registeredDevices?.length || 0})
                </h3>

                {#if $registeredDevices && $registeredDevices.length > 0}
                    <div class="devices-list">
                        {#each $registeredDevices as device (device.serial_number)}
                            <div class="device-row glass" in:fly={{ y: 10 }}>
                                <div class="row-main">
                                    <div class="row-icon">
                                        {#if device.board_type.includes("rp2350") || device.board_type.includes("pico2")}
                                            🟢
                                        {:else if device.board_type.includes("esp32")}
                                            🔵
                                        {:else}
                                            🟡
                                        {/if}
                                    </div>
                                    <div class="row-info">
                                        <span class="row-name"
                                            >{device.friendly_name ||
                                                device.board_type}</span
                                        >
                                        <code class="row-serial"
                                            >{device.serial_number}</code
                                        >
                                    </div>
                                </div>
                                <div class="row-meta">
                                    <span class="row-date"
                                        >Registered: {formatDate(
                                            device.activated_at,
                                        )}</span
                                    >
                                </div>
                                <button
                                    class="btn-danger-sm"
                                    on:click={() =>
                                        handleUnregister(device.serial_number)}
                                    title="Unregister device"
                                >
                                    🗑️
                                </button>
                            </div>
                        {/each}
                    </div>
                {:else}
                    <div class="empty-list glass">
                        <span class="empty-icon">📭</span>
                        <p>No registered devices</p>
                    </div>
                {/if}
            </section>

            <!-- Supported Boards Section -->
            <section class="boards-section">
                <h3>🔧 Supported Hardware</h3>
                <div class="boards-grid">
                    {#each boardProfiles.slice(0, 6) as profile}
                        <div
                            class="board-chip"
                            class:recommended={profile.notes?.includes("✅")}
                        >
                            <span class="chip-name">{profile.model}</span>
                            <span class="chip-vendor">{profile.vendor}</span>
                        </div>
                    {/each}
                </div>
            </section>
        </div>
    </div>
</div>

<style>
    .modal-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.85);
        backdrop-filter: blur(10px);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 2000;
    }

    .license-modal {
        width: 95%;
        max-width: 600px;
        max-height: 85vh;
        overflow-y: auto;
        padding: 2rem;
    }

    header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1.5rem;
    }

    h2 {
        margin: 0;
        font-size: 1.5rem;
    }

    h3 {
        margin: 0 0 1rem 0;
        font-size: 1rem;
        color: var(--text-secondary);
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    h4 {
        margin: 0 0 1rem 0;
        font-size: 0.95rem;
    }

    .content {
        display: flex;
        flex-direction: column;
        gap: 2rem;
    }

    /* Alerts */
    .alert {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.8rem 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        font-size: 0.85rem;
    }

    .alert.error {
        background: rgba(239, 68, 68, 0.1);
        border: 1px solid rgba(239, 68, 68, 0.3);
        color: #fca5a5;
    }

    .alert.success {
        background: rgba(34, 197, 94, 0.1);
        border: 1px solid rgba(34, 197, 94, 0.3);
        color: #86efac;
    }

    .alert .dismiss {
        margin-left: auto;
        background: none;
        border: none;
        color: inherit;
        cursor: pointer;
        font-size: 1.2rem;
        opacity: 0.6;
    }

    /* Status Section */
    .status-card {
        padding: 1.5rem;
        display: flex;
        flex-direction: column;
        gap: 1rem;
    }

    .tier-display {
        display: flex;
        align-items: center;
        gap: 0.8rem;
    }

    .tier-badge {
        padding: 0.3rem 0.8rem;
        border-radius: 6px;
        font-weight: 800;
        font-size: 0.75rem;
        letter-spacing: 0.5px;
        color: white;
    }

    .valid-badge {
        color: #22c55e;
        font-size: 0.8rem;
    }

    .invalid-badge {
        color: #6b7280;
        font-size: 0.8rem;
    }

    .seats-info {
        display: flex;
        flex-direction: column;
        gap: 0.4rem;
    }

    .seats-bar {
        height: 6px;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 3px;
        overflow: hidden;
    }

    .seats-used {
        height: 100%;
        background: var(--primary);
        border-radius: 3px;
        transition: width 0.3s ease;
    }

    .seats-text {
        font-size: 0.8rem;
        color: var(--text-secondary);
    }

    /* Activation Form */
    .activation-form {
        padding: 1.5rem;
        margin-top: 1rem;
    }

    .license-input {
        width: 100%;
        padding: 0.8rem 1rem;
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid var(--border-color);
        border-radius: 8px;
        color: #fff;
        font-family: monospace;
        font-size: 0.95rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 1rem;
    }

    .license-input:focus {
        outline: none;
        border-color: var(--primary);
    }

    .form-actions {
        display: flex;
        justify-content: space-between;
        gap: 1rem;
    }

    /* Device Section */
    .device-card {
        padding: 1.5rem;
    }

    .device-header {
        display: flex;
        align-items: center;
        gap: 1rem;
    }

    .device-icon {
        font-size: 2rem;
    }

    .device-info {
        flex: 1;
        display: flex;
        flex-direction: column;
        gap: 0.2rem;
    }

    .device-name {
        font-weight: 700;
        font-size: 1.1rem;
    }

    .device-serial {
        font-size: 0.75rem;
        color: var(--text-secondary);
        background: rgba(255, 255, 255, 0.05);
        padding: 0.2rem 0.5rem;
        border-radius: 4px;
        width: fit-content;
    }

    .device-type {
        font-size: 0.8rem;
        color: var(--text-secondary);
    }

    .status-badge {
        padding: 0.3rem 0.6rem;
        border-radius: 6px;
        font-size: 0.7rem;
        font-weight: 600;
    }

    .status-badge.registered {
        background: rgba(34, 197, 94, 0.15);
        color: #22c55e;
    }

    .status-badge.pending {
        background: rgba(234, 179, 8, 0.15);
        color: #eab308;
    }

    .register-form {
        margin-top: 1.5rem;
        padding-top: 1.5rem;
        border-top: 1px solid var(--border-color);
        display: flex;
        flex-direction: column;
        gap: 0.8rem;
    }

    .name-input {
        padding: 0.6rem 1rem;
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid var(--border-color);
        border-radius: 8px;
        color: #fff;
    }

    .name-input:focus {
        outline: none;
        border-color: var(--primary);
    }

    .info-text,
    .warning-text {
        font-size: 0.8rem;
        color: var(--text-secondary);
        margin: 0.5rem 0 0;
    }

    .warning-text {
        color: #f59e0b;
    }

    /* Empty States */
    .empty-device,
    .empty-list {
        padding: 2rem;
        text-align: center;
        color: var(--text-secondary);
    }

    .empty-icon {
        font-size: 2.5rem;
        opacity: 0.3;
        display: block;
        margin-bottom: 0.5rem;
    }

    .empty-device p,
    .empty-list p {
        margin: 0;
        font-size: 0.95rem;
    }

    .hint {
        font-size: 0.8rem;
        opacity: 0.6;
    }

    /* Devices List */
    .devices-list {
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
    }

    .device-row {
        padding: 1rem;
        display: flex;
        align-items: center;
        gap: 1rem;
    }

    .row-main {
        display: flex;
        align-items: center;
        gap: 0.8rem;
        flex: 1;
    }

    .row-icon {
        font-size: 1.2rem;
    }

    .row-info {
        display: flex;
        flex-direction: column;
        gap: 0.1rem;
    }

    .row-name {
        font-weight: 600;
        font-size: 0.9rem;
    }

    .row-serial {
        font-size: 0.7rem;
        color: var(--text-secondary);
    }

    .row-meta {
        text-align: right;
    }

    .row-date {
        font-size: 0.7rem;
        color: var(--text-secondary);
    }

    /* Boards Section */
    .boards-grid {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
    }

    .board-chip {
        padding: 0.5rem 0.8rem;
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid var(--border-color);
        border-radius: 8px;
        display: flex;
        flex-direction: column;
        gap: 0.2rem;
    }

    .board-chip.recommended {
        border-color: rgba(34, 197, 94, 0.3);
        background: rgba(34, 197, 94, 0.05);
    }

    .chip-name {
        font-size: 0.8rem;
        font-weight: 600;
    }

    .chip-vendor {
        font-size: 0.7rem;
        color: var(--text-secondary);
    }

    /* Buttons */
    .btn-primary {
        padding: 0.7rem 1.5rem;
        background: var(--primary);
        border: none;
        border-radius: 8px;
        color: white;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.2s;
    }

    .btn-primary:hover:not(:disabled) {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
    }

    .btn-primary:disabled {
        opacity: 0.5;
        cursor: not-allowed;
    }

    .btn-ghost {
        padding: 0.7rem 1.5rem;
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid var(--border-color);
        border-radius: 8px;
        color: var(--text-primary);
        font-weight: 600;
        cursor: pointer;
        transition: all 0.2s;
    }

    .btn-ghost:hover {
        background: rgba(255, 255, 255, 0.1);
    }

    .btn-danger-sm {
        padding: 0.4rem 0.6rem;
        background: rgba(239, 68, 68, 0.1);
        border: 1px solid rgba(239, 68, 68, 0.2);
        border-radius: 6px;
        color: #f87171;
        cursor: pointer;
        transition: all 0.2s;
    }

    .btn-danger-sm:hover {
        background: rgba(239, 68, 68, 0.2);
    }

    .icon-btn {
        background: transparent;
        border: none;
        font-size: 1.2rem;
        cursor: pointer;
        opacity: 0.6;
        transition: opacity 0.2s;
    }

    .icon-btn:hover {
        opacity: 1;
    }

    /* Glass effect */
    .glass {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
    }

    .glass-card {
        background: rgba(20, 20, 30, 0.95);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        backdrop-filter: blur(20px);
    }
</style>
