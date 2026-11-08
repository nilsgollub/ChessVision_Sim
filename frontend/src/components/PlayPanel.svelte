<script lang="ts">
  import { game } from "../lib/game.svelte";
  import Icon from "./Icon.svelte";
  import TopMoves from "./TopMoves.svelte";
  import CapturedTray from "./CapturedTray.svelte";

  const LEVELS = ["Anfänger", "Leicht", "Mittel", "Stark", "Profi"];
</script>

<div class="panel">
  <div class="actions">
    <button class="btn primary" onclick={() => game.hint()} disabled={game.busy}>
      <Icon name="bulb" /> Tipp holen
    </button>
    <button class="btn secondary" onclick={() => game.aiMove()} disabled={game.busy}>
      <Icon name="spark" /> KI zieht
    </button>
  </div>

  <button class="undo" onclick={() => game.undo()} disabled={game.busy || !game.history.length}>
    <Icon name="undo" size={20} /> Zug zurück
  </button>

  <TopMoves />

  <section class="opponent">
    <label class="switch">
      <input type="checkbox" bind:checked={game.aiReplies} />
      <span class="track" aria-hidden="true"><span class="knob"></span></span>
      <span>KI antwortet nach jedem Zug</span>
    </label>
    <fieldset class="levels">
      <legend>Wie stark spielt die KI?</legend>
      <div class="seg">
        {#each LEVELS as label, i}
          <label class:on={game.level === i + 1}>
            <input type="radio" name="level" value={i + 1} bind:group={game.level} />
            {label}
          </label>
        {/each}
      </div>
    </fieldset>
  </section>

  <CapturedTray />
</div>

<style>
  .panel { display: grid; gap: 14px; }
  .undo { justify-self: start; display: inline-flex; align-items: center; gap: 6px; min-height: 44px; padding: 0 14px; margin-top: -4px; border: 0; border-radius: 99px; background: transparent; color: var(--ink); font-weight: 700; }
  .undo:not(:disabled):hover { background: #fff; box-shadow: inset 0 0 0 2px var(--line-strong); }
  .actions { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
  .opponent { background: #fff; border-radius: 20px; padding: 12px 14px; display: grid; gap: 12px; box-shadow: inset 0 0 0 2px var(--line); }
  .switch { display: flex; align-items: center; gap: 12px; font-weight: 700; min-height: 44px; cursor: pointer; }
  .switch input { position: absolute; opacity: 0; width: 1px; height: 1px; }
  .track { width: 48px; height: 28px; border-radius: 99px; background: var(--line-strong); position: relative; transition: background 180ms; flex: none; }
  .knob { position: absolute; top: 3px; left: 3px; width: 22px; height: 22px; border-radius: 50%; background: #fff; box-shadow: 0 2px 4px rgba(42,47,90,.25); transition: transform 200ms cubic-bezier(.22,1,.36,1); }
  .switch input:checked + .track { background: var(--mint); }
  .switch input:checked + .track .knob { transform: translateX(20px); }
  .switch input:focus-visible + .track { outline: 3px solid var(--focus); outline-offset: 2px; }
  .levels { border: 0; padding: 0; margin: 0; min-width: 0; }
  legend { font-weight: 700; margin-bottom: 8px; padding: 0; }
  .seg { display: grid; grid-template-columns: repeat(5, 1fr); gap: 4px; background: var(--ground); padding: 4px; border-radius: 16px; }
  .seg label { position: relative; text-align: center; font-size: 0.82rem; font-weight: 700; padding: 10px 2px; border-radius: 12px; cursor: pointer; min-height: 40px; display: grid; place-items: center; color: var(--ink-soft); }
  .seg label.on { background: #fff; color: var(--ink); box-shadow: 0 2px 6px rgba(42,47,90,.12); }
  .seg input { position: absolute; opacity: 0; inset: 0; cursor: pointer; }
  .seg label:has(input:focus-visible) { outline: 3px solid var(--focus); }
  @container (max-width: 330px) {
    .actions { grid-template-columns: 1fr; }
    .seg { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  }
</style>
