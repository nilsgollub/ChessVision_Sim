<script lang="ts">
  import { game } from "../lib/game.svelte";
  import { EMPTY_FEN, START_FEN } from "../lib/chess";
  import { pieceInfo } from "../lib/pieces";
  import PieceArt from "./PieceArt.svelte";
  import Icon from "./Icon.svelte";

  const WHITE = ["K", "Q", "R", "B", "N", "P"];
  const BLACK = ["k", "q", "r", "b", "n", "p"];
</script>

<div class="panel">
  <p class="help">Wähle eine Figur und tippe aufs Feld. Nochmal tippen nimmt sie weg.</p>

  <div class="palette" role="radiogroup" aria-label="Figur zum Setzen">
    {#each [WHITE, BLACK] as row}
      <div class="row">
        {#each row as p}
          {@const info = pieceInfo(p)}
          <button role="radio" aria-checked={game.editPiece === p} class="pal" class:on={game.editPiece === p}
            style:--ribbon={info.ribbon} style:--soft={info.soft} aria-label={info.label}
            onclick={() => (game.editPiece = p)}>
            <PieceArt piece={p} size={40} />
          </button>
        {/each}
      </div>
    {/each}
    <button role="radio" aria-checked={game.editPiece === "ERASE"} class="pal erase" class:on={game.editPiece === "ERASE"}
      onclick={() => (game.editPiece = "ERASE")}><Icon name="eraser" /> Feld leeren</button>
  </div>

  <fieldset class="turn">
    <legend>Wer ist am Zug?</legend>
    <div class="seg">
      <button class:on={game.turn === "w"} aria-pressed={game.turn === "w"} onclick={() => game.setTurn("w")} data-testid="turn-w">Weiß</button>
      <button class:on={game.turn === "b"} aria-pressed={game.turn === "b"} onclick={() => game.setTurn("b")} data-testid="turn-b">Schwarz</button>
    </div>
  </fieldset>

  <div class="actions">
    <button class="btn secondary" onclick={() => game.newGame(START_FEN)}><Icon name="reset" /> Grundstellung</button>
    <button class="btn secondary" onclick={() => game.newGame(EMPTY_FEN)}><Icon name="clear" /> Nur Könige</button>
  </div>
</div>

<style>
  .panel { display: grid; gap: 14px; }
  .help { margin: 0; color: var(--ink-soft); }
  .palette { display: grid; gap: 8px; background: #fff; border-radius: 20px; padding: 10px; box-shadow: inset 0 0 0 2px var(--line); }
  .row { display: grid; grid-template-columns: repeat(6, 1fr); gap: 6px; }
  .pal { display: grid; place-items: center; min-height: 52px; border-radius: 14px; border: 2px solid transparent; background: var(--soft, var(--ground)); padding: 2px; }
  .pal.on { border-color: var(--ribbon, var(--ink)); box-shadow: 0 0 0 2px #fff inset; }
  .erase { display: flex; gap: 8px; align-items: center; justify-content: center; font-weight: 700; background: var(--ground); }
  .turn { border: 0; margin: 0; padding: 0; min-width: 0; }
  legend { font-weight: 700; margin-bottom: 8px; padding: 0; }
  .seg { display: grid; grid-template-columns: 1fr 1fr; gap: 4px; background: #fff; padding: 4px; border-radius: 16px; box-shadow: inset 0 0 0 2px var(--line); }
  .seg button { min-height: 44px; border-radius: 12px; border: 0; background: transparent; font-weight: 700; color: var(--ink-soft); }
  .seg button.on { background: var(--ink); color: #fff; }
  .actions { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
  @container (max-width: 330px) {
    .actions { grid-template-columns: 1fr; }
    .row { grid-template-columns: repeat(3, 1fr); }
  }
</style>
