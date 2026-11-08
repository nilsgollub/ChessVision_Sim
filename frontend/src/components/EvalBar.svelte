<script lang="ts">
  import { game } from "../lib/game.svelte";
  import { evalShare, evalWords } from "../lib/pieces";
  const known = $derived(game.evalCp !== null || game.evalMate !== null);
  const share = $derived(known ? evalShare(game.evalCp, game.evalMate) : 0.5);
  const words = $derived(known ? evalWords(game.evalCp, game.evalMate) : "Noch keine Bewertung");
</script>

<div class="bar" class:flipped={game.flipped} role="meter" aria-valuemin="0" aria-valuemax="100"
  aria-valuenow={Math.round(share * 100)} aria-label="Bewertung: {words}" title={words}>
  <div class="white" style="height: {share * 100}%"></div>
</div>

<style>
  .bar {
    width: 12px; height: 100%; border-radius: 99px; background: var(--black-piece);
    display: flex; flex-direction: column; justify-content: flex-end; overflow: hidden;
    box-shadow: inset 0 0 0 2px var(--ink);
  }
  .bar.flipped { flex-direction: column-reverse; justify-content: flex-end; }
  .white { background: #fff; box-shadow: inset 0 0 0 2px var(--ink); border-radius: 99px; transition: height 360ms cubic-bezier(.2, .9, .3, 1); }
</style>
