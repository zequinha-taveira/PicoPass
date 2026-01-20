<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import { fade, fly } from 'svelte/transition';
  import { status, isLocked } from '../stores/vault';

  const dispatch = createEventDispatcher();
  
  let autoLockTimeout = 15;
  let theme = "dark";
</script>

<div class="modal-overlay" on:click|self={() => dispatch('close')} in:fade>
  <div class="glass-card settings-modal" in:fly={{ y: 20 }}>
    <header>
      <h2>Vault Settings</h2>
      <button class="icon-btn" on:click={() => dispatch('close')}>✕</button>
    </header>

    <div class="settings-content">
      <section>
        <h4>Security</h4>
        <div class="setting-item">
          <div class="text">
            <span>Auto-Lock Timeout</span>
            <p>Lock vault after inactivity (minutes)</p>
          </div>
          <select bind:value={autoLockTimeout}>
            <option value={5}>5m</option>
            <option value={15}>15m</option>
            <option value={30}>30m</option>
            <option value={0}>Never</option>
          </select>
        </div>
      </section>

      <section>
        <h4>Hardware</h4>
        <div class="setting-item">
          <div class="text">
            <span>Device Information</span>
            <p>{$status}</p>
          </div>
          <button class="type-btn small">Refresh</button>
        </div>
      </section>

      <section>
        <h4>Data Management</h4>
        <div class="setting-item">
          <div class="text">
            <span>Export to CSV</span>
            <p>Readable list of services and usernames</p>
          </div>
          <button class="type-btn small" on:click={() => invoke('export_vault_csv').then(alert)}>Export</button>
        </div>
        <div class="setting-item" style="margin-top: 1rem">
          <div class="text">
            <span>Create Backup</span>
            <p>Encrypted JSON copy of the vault</p>
          </div>
          <button class="type-btn small" on:click={() => invoke('perform_backup').then(() => alert('Backup created!'))}>Backup</button>
        </div>
      </section>

      <section>
        <h4>Account</h4>
        <button class="danger-btn" on:click={() => $isLocked = true}>
          Force Lock Vault
        </button>
      </section>
    </div>
  </div>
</div>

<style>
  .modal-overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0, 0, 0, 0.82); backdrop-filter: blur(8px); display: flex; align-items: center; justify-content: center; z-index: 2000; }
  .settings-modal { width: 95%; max-width: 500px; padding: 2rem; }
  
  header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem; }
  h2 { margin: 0; font-size: 1.5rem; }

  .settings-content { display: flex; flex-direction: column; gap: 2rem; }
  h4 { margin: 0 0 1rem 0; color: #6366f1; text-transform: uppercase; font-size: 0.75rem; letter-spacing: 1px; }

  .setting-item { display: flex; justify-content: space-between; align-items: center; gap: 1rem; }
  .text span { display: block; font-weight: 600; font-size: 0.95rem; }
  .text p { margin: 0; font-size: 0.8rem; color: #64748b; }

  select { background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); border-radius: 8px; color: white; padding: 0.4rem 0.8rem; cursor: pointer; }
  
  .type-btn.small { padding: 0.4rem 0.8rem; font-size: 0.75rem; }
  
  .danger-btn { width: 100%; padding: 0.8rem; background: rgba(244, 63, 94, 0.1); border: 1px solid rgba(244, 63, 94, 0.2); border-radius: 12px; color: #fb7185; cursor: pointer; transition: all 0.2s; font-weight: 600; }
  .danger-btn:hover { background: #f43f5e; color: white; }
</style>
