<script lang="ts">
  import { isLocked } from './lib/stores/vault';
  import UnlockScreen from './lib/components/UnlockScreen.svelte';
  import Dashboard from './lib/components/Dashboard.svelte';
</script>

<main>
  <!-- Improved Dynamic Background -->
  <div class="scene">
    <div class="overlay"></div>
    <div class="blobs">
      <div class="blob b1"></div>
      <div class="blob b2"></div>
      <div class="blob b3"></div>
    </div>
  </div>

  <div class="content-wrapper">
    {#if $isLocked}
      <UnlockScreen />
    {:else}
      <Dashboard />
    {/if}
  </div>
</main>

<style>
  :global(body) {
    margin: 0;
    padding: 0;
    background: #020408;
    color: #fff;
  }

  main {
    height: 100vh;
    width: 100vw;
    position: relative;
    display: flex;
    align-items: center;
    justify-content: center;
    overflow: hidden;
  }

  .scene {
    position: absolute;
    inset: 0;
    z-index: 0;
  }

  .overlay {
    position: absolute;
    inset: 0;
    background: radial-gradient(circle at 50% 50%, transparent 0%, rgba(2, 4, 8, 0.8) 100%);
    z-index: 2;
  }

  .blobs {
    position: absolute;
    inset: 0;
    filter: blur(80px);
    z-index: 1;
    opacity: 0.25;
  }

  .blob {
    position: absolute;
    border-radius: 50%;
    animation: move 30s infinite alternate ease-in-out;
  }

  .b1 { width: 600px; height: 600px; background: var(--primary); top: -200px; left: -100px; }
  .b2 { width: 500px; height: 500px; background: var(--secondary); bottom: -100px; right: -50px; animation-duration: 35s; }
  .b3 { width: 400px; height: 400px; background: var(--accent); top: 30%; left: 40%; animation-duration: 25s; opacity: 0.4; }

  @keyframes move {
    0% { transform: translate(0, 0) rotate(0deg) scale(1); }
    100% { transform: translate(100px, 50px) rotate(90deg) scale(1.1); }
  }

  .content-wrapper {
    position: relative;
    z-index: 10;
    width: 100%;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
  }
</style>
