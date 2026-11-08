<script lang="ts">
  import { game } from "../lib/game.svelte";
  import { lichessUrl } from "../lib/chess";
  import Icon from "./Icon.svelte";
  import { setSoundEnabled, soundEnabled } from "../lib/sound";

  // In der Android-App (Capacitor hängt das an den User-Agent an) gibt es statt des PWA-Hinweises den Serverwechsel.
  const inApp = navigator.userAgent.includes("Brettfreunde-App");
  let copied = $state(false);
  let sound = $state(soundEnabled());
  function toggleSound() {
    sound = !sound;
    setSoundEnabled(sound);
  }
  async function copyFen() {
    try {
      await navigator.clipboard.writeText(game.fen);
    } catch {
      const ta = document.createElement("textarea");
      ta.value = game.fen; document.body.append(ta); ta.select(); document.execCommand("copy"); ta.remove();
    }
    copied = true;
    setTimeout(() => (copied = false), 1600);
  }
</script>

<div class="panel">
  <section class="card">
    <div class="row">
      <div>
        <h3>Geräusche</h3>
        <p class="note">Leises Klopfen beim Ziehen, ein Plopp beim Schlagen, kleine Melodien bei Schach und Partieende.</p>
      </div>
      <button class="switch" role="switch" aria-checked={sound} aria-label="Geräusche" data-testid="sound-toggle" onclick={toggleSound}><span></span></button>
    </div>
  </section>

  <section class="card">
    <h3>Stellung als FEN</h3>
    <code data-testid="fen">{game.fen}</code>
    <div class="actions">
      <button class="btn secondary" onclick={copyFen}><Icon name={copied ? "check" : "copy"} /> {copied ? "Kopiert" : "FEN kopieren"}</button>
      <a class="btn secondary" href={lichessUrl(game.fen)} target="_blank" rel="noopener"><Icon name="link" /> In Lichess öffnen</a>
    </div>
    <p class="note">Lichess ist der einzige Knopf, der die Stellung ins Internet schickt.</p>
  </section>

  {#if inApp}
    <section class="card">
      <h3>Server</h3>
      <p class="note">Verbunden mit {location.host}. Unterwegs über Tailscale oder zuhause im WLAN: hier wechselst du die Adresse.</p>
      <a class="btn secondary" href="http://localhost/?wechseln" data-testid="server-wechseln"><Icon name="link" /> Server wechseln</a>
    </section>
  {:else}
    <section class="card">
      <h3>Als App aufs Handy</h3>
      <p class="note">Am besten die Android-App „Brettfreunde“ aus dem F-Droid-Repo Homelab-Apps installieren. Oder in Chrome oben rechts das Menü öffnen und „Zum Startbildschirm hinzufügen“ wählen.</p>
    </section>
  {/if}
</div>

<style>
  .panel { display: grid; gap: 14px; }
  .card { background: #fff; border-radius: 20px; padding: 12px 14px; box-shadow: inset 0 0 0 2px var(--line); display: grid; gap: 10px; }
  h3 { margin: 0; font: 600 1.05rem var(--font-display); }
  code { font: 600 0.85rem/1.4 ui-monospace, "SF Mono", Menlo, monospace; background: var(--ground); border-radius: 12px; padding: 8px 10px; word-break: break-all; user-select: all; }
  .actions { display: grid; grid-template-columns: repeat(auto-fit, minmax(190px, 1fr)); gap: 10px; }
  .row { display: flex; align-items: center; justify-content: space-between; gap: 14px; }
  .row > div { display: grid; gap: 4px; }
  .switch { flex: none; width: 60px; height: 36px; border-radius: 18px; border: 0; padding: 4px; background: var(--line-strong); cursor: pointer; transition: background 0.2s; }
  .switch span { display: block; width: 28px; height: 28px; border-radius: 50%; background: #fff; box-shadow: 0 1px 3px rgb(0 0 0 / 0.2); transition: transform 0.2s; }
  .switch[aria-checked="true"] { background: var(--ink); }
  .switch[aria-checked="true"] span { transform: translateX(24px); }
  .switch:focus-visible { outline: 3px solid var(--focus); outline-offset: 2px; }
  .note { margin: 0; font-size: 0.9rem; color: var(--ink-soft); line-height: 1.4; }
</style>
