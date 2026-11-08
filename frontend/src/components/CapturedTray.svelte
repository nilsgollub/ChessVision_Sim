<script lang="ts">
  import { game } from "../lib/game.svelte";
  import { capturedPieces } from "../lib/chess";
  import PieceArt from "./PieceArt.svelte";
  const out = $derived(capturedPieces(game.grid));
  const white = $derived(out.filter((p) => p === p.toUpperCase()));
  const black = $derived(out.filter((p) => p === p.toLowerCase()));
</script>

{#if out.length}
  <section class="tray" aria-label="Geschlagene Figuren">
    <h3>Schon vom Brett</h3>
    {#each [[white, "Weiß"], [black, "Schwarz"]] as [list, who]}
      {#if (list as string[]).length}
        <div class="row" aria-label="{who}: {(list as string[]).length} Figuren">
          {#each list as p, i (p + i)}<span class="chip"><PieceArt piece={p} size={30} muted /></span>{/each}
        </div>
      {/if}
    {/each}
  </section>
{/if}

<style>
  .tray { background: #fff; border-radius: 20px; padding: 10px 12px; box-shadow: inset 0 0 0 2px var(--line); }
  h3 { margin: 0 0 6px; font: 600 0.95rem var(--font-display); color: var(--ink-soft); }
  .row { display: flex; flex-wrap: wrap; gap: 4px; }
  .row + .row { margin-top: 6px; }
  .chip { background: #F4F3F8; border-radius: 10px; padding: 2px; }
</style>
