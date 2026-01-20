<script lang="ts">
  import { invoke } from '@tauri-apps/api/tauri';
  import { fade, fly, slide } from 'svelte/transition';
  import { flip } from 'svelte/animate';
  import { cubicInOut } from 'svelte/easing';
  import { passwords, isLocked, status } from '../stores/vault';
  import AddPasswordModal from './AddPasswordModal.svelte';
  import Settings from './Settings.svelte';

  let showAddModal = false;
  let showSettings = false;
  let searchTerm = "";

  $: filteredPasswords = $passwords.filter(p => 
    p.service.toLowerCase().includes(searchTerm.toLowerCase()) ||
    p.username.toLowerCase().includes(searchTerm.toLowerCase())
  );

  async function handleType(id: string) {
    try {
      const res = await invoke('send_to_pico', { id });
      console.log(res);
    } catch (e: any) {
      alert("Error: " + e);
    }
  }

  function formatDate(timestamp: number) {
    return new Date(timestamp * 1000).toLocaleDateString(undefined, { 
      year: 'numeric', month: 'short', day: 'numeric' 
    });
  }
</script>

<div class="dashboard-root" in:fade={{ duration: 400 }}>
  <header class="glass top-nav" in:fly={{ y: -20, delay: 200 }}>
    <div class="brand">
      <span class="logo">🚀</span>
      <span>PicoPass</span>
    </div>
    
    <div class="nav-actions">
      <div class="status-badge { $status.includes('Connected') ? 'online' : '' }">
        <span class="pulse-dot"></span>
        { $status }
      </div>
      <div class="divider"></div>
      <button class="nav-btn" on:click={() => showSettings = true} aria-label="Settings">⚙️</button>
      <button class="nav-btn lock" on:click={() => $isLocked = true} aria-label="Lock Vault">🔒</button>
    </div>
  </header>

  <main class="main-container">
    <div class="action-bar" in:fade={{ delay: 400 }}>
      <div class="search-container">
        <span class="search-icon">🔍</span>
        <input 
          type="text" 
          placeholder="Search your vault..." 
          bind:value={searchTerm}
          aria-label="Search passwords"
        />
      </div>
      <button class="btn-primary" on:click={() => showAddModal = true}>
        <span class="icon">+</span>
        <span>Add Entry</span>
      </button>
    </div>

    <div class="entries-grid">
      {#each filteredPasswords as pw (pw.id)}
        <div 
          class="glass entry-card" 
          in:fly={{ y: 20, duration: 400 }}
          animate:flip={{ duration: 400, easing: cubicInOut }}
        >
          <div class="card-header">
            <div class="avatar">{pw.service.charAt(0).toUpperCase()}</div>
            <div class="info">
              <h3>{pw.service}</h3>
              <span class="username">{pw.username}</span>
            </div>
          </div>
          
          <div class="card-body">
             <div class="meta-info">
               <span class="label">ADDED</span>
               <span class="value">{formatDate(pw.created_at)}</span>
             </div>
          </div>

          <div class="card-actions">
            <button class="btn-ghost" on:click={() => handleType(pw.id)}>
              ⌨️ Auto-Type
            </button>
          </div>
        </div>
      {:else}
        <div class="empty-state" in:fade>
          <div class="empty-icon">📂</div>
          <h3>Vault is empty</h3>
          <p>Your secure passwords will appear here.</p>
        </div>
      {/each}
    </div>
  </main>

  {#if showAddModal}
    <AddPasswordModal on:close={() => showAddModal = false} />
  {/if}

  {#if showSettings}
    <Settings on:close={() => showSettings = false} />
  {/if}
</div>

<style>
  .dashboard-root {
    width: 100%;
    height: 100vh;
    display: flex;
    flex-direction: column;
    padding: 1.5rem;
  }

  .top-nav {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.8rem 2rem;
    margin-bottom: 2rem;
  }

  .brand {
    display: flex;
    align-items: center;
    gap: 0.8rem;
    font-size: 1.4rem;
    font-weight: 800;
  }

  .nav-actions {
    display: flex;
    align-items: center;
    gap: 1.2rem;
  }

  .status-badge {
    padding: 0.4rem 1rem;
    background: rgba(255, 255, 255, 0.05);
    border-radius: 100px;
    font-size: 0.8rem;
    color: var(--text-secondary);
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .status-badge.online { color: var(--text-success); }

  .pulse-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: #475569;
  }
  .online .pulse-dot { 
    background: var(--text-success);
    box-shadow: 0 0 8px var(--text-success);
    animation: pulse-light 2s infinite;
  }

  @keyframes pulse-light {
    0% { opacity: 0.5; }
    50% { opacity: 1; }
    100% { opacity: 0.5; }
  }

  .divider { width: 1px; height: 20px; background: rgba(255, 255, 255, 0.1); }

  .nav-btn {
    background: transparent;
    border: none;
    font-size: 1.2rem;
    cursor: pointer;
    opacity: 0.6;
    transition: var(--transition);
  }
  .nav-btn:hover { opacity: 1; transform: scale(1.1); }

  .main-container {
    flex: 1;
    max-width: 1200px;
    width: 100%;
    margin: 0 auto;
    overflow-y: auto;
    padding: 0 1rem 2rem;
  }

  .action-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 3rem;
    gap: 1.5rem;
  }

  .search-container {
    flex: 1;
    position: relative;
    display: flex;
    align-items: center;
  }

  .search-icon {
    position: absolute;
    left: 1.2rem;
    opacity: 0.4;
  }

  .search-container input {
    width: 100%;
    padding: 1rem 1rem 1rem 3rem;
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-md);
    color: #fff;
    outline: none;
    transition: var(--transition);
  }

  .search-container input:focus {
    background: rgba(255, 255, 255, 0.06);
    border-color: var(--primary);
  }

  .btn-primary {
    display: flex;
    align-items: center;
    gap: 0.8rem;
    padding: 1rem 2rem;
    background: var(--primary);
    border: none;
    border-radius: var(--radius-md);
    color: white;
    font-weight: 700;
    cursor: pointer;
    transition: var(--transition);
  }

  .btn-primary:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(99, 102, 241, 0.3);
  }

  .entries-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
    gap: 1.5rem;
  }

  .entry-card {
    padding: 1.8rem;
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
    transition: var(--transition);
  }

  .entry-card:hover {
    background: rgba(255, 255, 255, 0.05);
    border-color: var(--primary-glow);
    transform: scale(1.02);
  }

  .card-header {
    display: flex;
    align-items: center;
    gap: 1rem;
  }

  .avatar {
    width: 48px;
    height: 48px;
    background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
    border-radius: 14px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 800;
    font-size: 1.2rem;
  }

  .info h3 { margin: 0; font-size: 1.3rem; }
  .username { color: var(--text-secondary); font-size: 0.9rem; }

  .meta-info {
    display: flex;
    flex-direction: column;
    gap: 0.2rem;
  }

  .label { font-size: 0.65rem; font-weight: 800; color: #475569; letter-spacing: 0.05em; }
  .value { font-size: 0.85rem; color: #94a3b8; }

  .card-actions { margin-top: auto; }

  .btn-ghost {
    width: 100%;
    padding: 0.8rem;
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 10px;
    color: var(--text-primary);
    font-weight: 600;
    cursor: pointer;
    transition: var(--transition);
  }

  .btn-ghost:hover {
    background: var(--primary);
    border-color: var(--primary);
    color: white;
  }

  .empty-state {
    grid-column: 1 / -1;
    text-align: center;
    padding: 8rem 0;
    color: var(--text-secondary);
  }

  .empty-icon { font-size: 4rem; opacity: 0.2; margin-bottom: 1rem; }
</style>
