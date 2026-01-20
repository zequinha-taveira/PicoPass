<script lang="ts">
  import { fade, fly, scale } from 'svelte/transition';
  import { cubicOut } from 'svelte/easing';
  import { invoke } from '@tauri-apps/api/tauri';
  import { isLocked, passwords, status, masterPassword, loading } from '../stores/vault';

  let lockoutRemaining = 0;
  let lockoutInterval: any;

  async function handleUnlock() {
    if (!$masterPassword) return;
    $loading = true;
    try {
      await invoke('unlock_vault', { password: $masterPassword });
      $passwords = await invoke('list_passwords');
      
      const devices = await invoke('list_serial_ports') as any[];
      if (devices.length > 0) {
        $status = `Connected: ${devices[0].name}`;
      } else {
        $status = "Vault Unlocked (No Hardware)";
      }
      
      $isLocked = false;
    } catch (e: any) {
      if (e.includes("Locked out")) {
        // Extract remaining seconds if possible or just show error
        $status = "⚠️ Security Lockout: " + e;
        startLockoutTimer();
      } else {
        $status = "❌ " + e;
      }
    } finally {
      $loading = false;
    }
  }

  function startLockoutTimer() {
    // Basic lockout UI feedback
    $masterPassword = ""; // Clear password on failure
  }
</script>

<div 
  class="auth-container" 
  in:scale={{ duration: 600, start: 0.9, easing: cubicOut }}
>
  <div class="glass auth-card">
    <div class="header">
      <div class="icon-wrapper animate-pulse">
        <span class="icon">🔐</span>
      </div>
      <h1>PicoPass</h1>
      <p class="subtitle">Hardware-Backed Security Vault</p>
    </div>
    
    <div class="form" role="form" aria-label="Unlock Vault">
      <div class="input-field">
        <input 
          type="password" 
          placeholder="Master Password" 
          bind:value={$masterPassword}
          on:keydown={(e) => e.key === 'Enter' && handleUnlock()}
          aria-label="Enter master password"
          autocomplete="current-password"
        />
        <div class="glow"></div>
      </div>

      <button 
        class="primary-btn-large" 
        on:click={handleUnlock} 
        disabled={$loading}
        aria-busy={$loading}
      >
        {#if $loading}
          <div class="loader"></div>
        {:else}
          Unlock Vault
        {/if}
      </button>
    </div>
    
    <div class="footer">
      <div class="pico-status {$status.includes('Connected') ? 'success' : 'warning'}">
        <span class="dot"></span>
        {$status}
      </div>
    </div>
  </div>
</div>

<style>
  .auth-container {
    width: 100%;
    max-width: 440px;
    z-index: 10;
  }

  .auth-card {
    padding: 3.5rem;
    text-align: center;
    box-shadow: var(--shadow-premium);
  }

  .icon-wrapper {
    width: 80px;
    height: 80px;
    background: rgba(99, 102, 241, 0.1);
    border-radius: 20px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto 1.5rem;
    font-size: 2.5rem;
    border: 1px solid rgba(99, 102, 241, 0.2);
  }

  h1 {
    font-size: 3rem;
    margin: 0;
    line-height: 1;
    background: linear-gradient(135deg, #fff 0%, #94a3b8 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
  }

  .subtitle {
    color: var(--text-secondary);
    font-weight: 300;
    margin-top: 0.5rem;
    margin-bottom: 3rem;
  }

  .input-field {
    position: relative;
    margin-bottom: 1.5rem;
  }

  input {
    width: 100%;
    padding: 1.2rem;
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: var(--radius-md);
    color: #fff;
    font-size: 1.1rem;
    transition: var(--transition);
    outline: none;
  }

  input:focus {
    background: rgba(255, 255, 255, 0.07);
    border-color: var(--primary);
    box-shadow: 0 0 20px rgba(99, 102, 241, 0.15);
  }

  .primary-btn-large {
    width: 100%;
    padding: 1.2rem;
    background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
    border: none;
    border-radius: var(--radius-md);
    color: white;
    font-size: 1.1rem;
    font-weight: 700;
    cursor: pointer;
    transition: var(--transition);
    box-shadow: 0 10px 25px rgba(99, 102, 241, 0.2);
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .primary-btn-large:hover:not(:disabled) {
    transform: translateY(-2px);
    box-shadow: 0 15px 30px rgba(99, 102, 241, 0.3);
  }

  .primary-btn-large:active {
    transform: translateY(0);
  }

  .primary-btn-large:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  .footer {
    margin-top: 2.5rem;
  }

  .pico-status {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.6rem;
    font-size: 0.85rem;
    color: var(--text-secondary);
  }

  .dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #475569;
  }

  .success .dot { background: var(--text-success); box-shadow: 0 0 10px var(--text-success); }
  .warning .dot { background: #f59e0b; }

  .loader {
    width: 24px;
    height: 24px;
    border: 3px solid rgba(255, 255, 255, 0.3);
    border-top-color: #fff;
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
  }

  @keyframes spin { to { transform: rotate(360deg); } }
</style>
