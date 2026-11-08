<script lang="ts">
  import { game } from "../lib/game.svelte";
  import { evalWords, pieceInfo, RANK_COLORS } from "../lib/pieces";
  import PieceArt from "./PieceArt.svelte";
</script>

{#if game.hintsFresh && game.topMoves.length}
  <ol class="ranks" aria-label="Die besten Züge">
    {#each game.topMoves as m (m.uci)}
      {@const info = pieceInfo(m.piece)}
      <li style:--rank={RANK_COLORS[m.rank - 1]} style:--soft={info.soft}>
        <span class="ribbon" aria-hidden="true">{m.rank}</span>
        <div class="art"><PieceArt piece={m.piece} size={46} /></div>
        <div class="what">
          <p class="line"><b>{info.name}</b> nach {m.to}{m.capture ? " und schlägt" : ""}</p>
          <p class="sub"><span class="san">{m.san}</span> · {evalWords(m.eval_cp, m.mate)}</p>
        </div>
        <button class="go" disabled={game.busy}
          onclick={() => game.move(m.from, m.to)} aria-label="{info.name} nach {m.to} ziehen">Ziehen</button>
      </li>
    {/each}
  </ol>
{:else if !game.busy}
  <p class="empty">Tippe auf <b>Tipp holen</b>: Stockfish zeigt dir die drei besten Züge als Pfeile, Nummer 1 ist der beste.</p>
{/if}

<style>
  .ranks { list-style: none; margin: 0; padding: 0; display: grid; gap: 10px; }
  li {
    position: relative; display: grid; grid-template-columns: auto 1fr auto; gap: 10px; align-items: center;
    background: var(--soft); border-radius: 20px; padding: 10px 12px 10px 30px;
    box-shadow: 0 4px 14px rgba(42, 47, 90, 0.08), inset 0 0 0 2px var(--line);
  }
  .ribbon {
    position: absolute; left: 8px; top: -4px; width: 26px; height: 34px; background: var(--rank); color: #fff;
    font: 600 1.05rem/30px var(--font-display); text-align: center;
    clip-path: polygon(0 0, 100% 0, 100% 100%, 50% 80%, 0 100%);
  }
  .art { background: #fff; border-radius: 14px; padding: 2px; margin-left: 10px; }
  .line { margin: 0; font-size: 1rem; }
  .line b { font-family: var(--font-display); font-weight: 700; }
  .sub { margin: 2px 0 0; font-size: 0.85rem; color: var(--ink-soft); }
  .san { font-variant-numeric: tabular-nums; font-weight: 700; color: var(--ink); }
  .go { min-height: 44px; padding: 0 14px; border-radius: 99px; border: 2px solid var(--rank); background: #fff; color: var(--ink); font-weight: 700; }
  .go:not(:disabled):hover { background: var(--rank); color: #fff; }
  .empty { margin: 0; color: var(--ink-soft); font-size: 0.95rem; line-height: 1.4; }
</style>
