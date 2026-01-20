<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import { fade, scale } from 'svelte/transition';
  import { invoke } from '@tauri-apps/api/tauri';
  import { passwords } from '../stores/vault';

  const dispatch = createEventDispatcher();
  
  let service = "";
  let username = "";
  let password = "";
  let loading = false;

  async function handleSave() {
    if (!service || !username || !password) return alert("All fields are required");
    loading = true;
    try {
      await invoke('add_password', { 
        service, 
        username, 
        passwordText: password 
      });
      $passwords = await invoke('list_passwords');
      dispatch('close');
    } catch (e: any) {
      alert("Error: " + e);
    } finally {
      loading = false;
    }
  }

  function generatePassword() {
    const chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*()_+";
    let generated = "";
    for (let i = 0; i < 16; i++) {
      generated += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    password = generated;
  }
</script>

<div class="modal-overlay" on:click|self={() => dispatch('close')} in:fade={{ duration: 200 }}>
  <div class="glass-card modal-content" in:scale={{ start: 0.95, duration: 200 }}>
    <h2>Add Secure Entry</h2>
    <p class="modal-desc">Store a new encrypted password in your vault.</p>

    <div class="form">
      <div class="field">
        <label for="service">Service</label>
        <input id="service" type="text" placeholder="e.g. GitHub" bind:value={service} />
      </div>
      
      <div class="field">
        <label for="username">Username or Email</label>
        <input id="username" type="text" placeholder="user@example.com" bind:value={username} />
      </div>
      
      <div class="field">
        <label for="password">Password</label>
        <div class="password-input-group">
          <input id="password" type="password" placeholder="••••••••••••" bind:value={password} />
          <button class="gen-btn" on:click={generatePassword} title="Generate Strong Password">⚡</button>
        </div>
      </div>
    </div>

    <div class="modal-actions">
      <button class="secondary-btn" on:click={() => dispatch('close')}>Cancel</button>
      <button class="primary-btn" on:click={handleSave} disabled={loading}>
        {#if loading} Saving... {:else} Save Entry {/if}
      </button>
    </div>
  </div>
</div>

<style>
  .modal-overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0, 0, 0, 0.7); backdrop-filter: blur(4px); display: flex; align-items: center; justify-content: center; z-index: 1000; }
  .modal-content { width: 90%; max-width: 480px; padding: 2.5rem; }
  
  h2 { margin: 0; font-size: 1.8rem; }
  .modal-desc { color: #94a3b8; font-size: 0.95rem; margin-bottom: 2rem; }

  .form { display: flex; flex-direction: column; gap: 1.2rem; }
  .field { display: flex; flex-direction: column; gap: 0.5rem; }
  label { font-size: 0.85rem; font-weight: 600; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.5px; }
  
  input { padding: 0.9rem 1.1rem; background: rgba(255, 255, 255, 0.04); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 12px; color: white; font-size: 1rem; transition: all 0.2s; }
  input:focus { outline: none; border-color: #6366f1; background: rgba(255, 255, 255, 0.08); }

  .password-input-group { position: relative; display: flex; align-items: center; }
  .password-input-group input { flex: 1; padding-right: 3.5rem; }
  .gen-btn { position: absolute; right: 8px; height: 36px; width: 36px; background: rgba(99, 102, 241, 0.1); border: 1px solid rgba(99, 102, 241, 0.2); border-radius: 8px; color: #818cf8; cursor: pointer; transition: all 0.2s; }
  .gen-btn:hover { background: #6366f1; color: white; }

  .modal-actions { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-top: 2.5rem; }
  
  button { padding: 0.9rem; border-radius: 12px; font-weight: 600; cursor: pointer; transition: all 0.2s; border: none; }
  .primary-btn { background: #6366f1; color: white; }
  .primary-btn:hover { background: #4f46e5; }
  .primary-btn:disabled { opacity: 0.5; cursor: not-allowed; }
  
  .secondary-btn { background: rgba(255, 255, 255, 0.05); color: #94a3b8; }
  .secondary-btn:hover { background: rgba(255, 255, 255, 0.1); color: white; }
</style>
