<script lang="ts">
  import { game } from "../lib/game.svelte";
  import { lichessUrl } from "../lib/chess";
  import Icon from "./Icon.svelte";

  let copied = $state(false);
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
    <h3>Stellung als FEN</h3>
    <code data-testid="fen">{game.fen}</code>
    <div class="actions">
      <button class="btn secondary" onclick={copyFen}><Icon name={copied ? "check" : "copy"} /> {copied ? "Kopiert" : "FEN kopieren"}</button>
      <a class="btn secondary" href={lichessUrl(game.fen)} target="_blank" rel="noopener"><Icon name="link" /> In Lichess öffnen</a>
    </div>
    <p class="note">Lichess ist der einzige Knopf, der die Stellung ins Internet schickt.</p>
  </section>

  <section class="card">
    <h3>Als App aufs Handy</h3>
    <p class="note">In Chrome oben rechts das Menü öffnen und „Zum Startbildschirm hinzufügen“ wählen. Brettfreunde startet dann im Vollbild.</p>
  </section>
</div>

<style>
  .panel { display: grid; gap: 14px; }
  .card { background: #fff; border-radius: 20px; padding: 12px 14px; box-shadow: inset 0 0 0 2px var(--line); display: grid; gap: 10px; }
  h3 { margin: 0; font: 600 1.05rem var(--font-display); }
  code { font: 600 0.85rem/1.4 ui-monospace, "SF Mono", Menlo, monospace; background: var(--ground); border-radius: 12px; padding: 8px 10px; word-break: break-all; user-select: all; }
  .actions { display: grid; grid-template-columns: repeat(auto-fit, minmax(190px, 1fr)); gap: 10px; }
  .note { margin: 0; font-size: 0.9rem; color: var(--ink-soft); line-height: 1.4; }
</style>
