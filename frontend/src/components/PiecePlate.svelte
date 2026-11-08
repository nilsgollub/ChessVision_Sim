<script lang="ts">
  import { game } from "../lib/game.svelte";
  import { pieceInfo } from "../lib/pieces";
  import PieceArt from "./PieceArt.svelte";

  const piece = $derived(game.selected ? game.pieceAt(game.selected) : "");
  const info = $derived(piece ? pieceInfo(piece) : null);
  const TONE_BG: Record<string, string> = { good: "var(--mint-soft)", warn: "var(--butter-soft)", bad: "var(--bad-soft)", busy: "var(--lilac-soft)", neutral: "#fff" };
</script>

{#key game.plateBump}
  <section class="plate" class:bump={!!info} aria-live="polite" style:--soft={info?.soft ?? TONE_BG[game.tone]} style:--ribbon={info?.ribbon ?? "var(--ink)"} style:--deep={info?.deep ?? "var(--ink)"}>
    {#if info}
      <div class="portrait"><PieceArt {piece} size={64} /></div>
      <div class="text">
        <p class="name"><span class="tag">{info.name}</span><span class="kind">{info.label} · {game.selected}</span></p>
        <p class="note pill-note">{info.note}</p>
      </div>
    {:else}
      <div class="portrait turn"><PieceArt piece={game.turn === "w" ? "K" : "k"} size={56} /></div>
      <div class="text">
        <p class="name"><span class="tag turn-tag">{game.turn === "w" ? "Weiß" : "Schwarz"} ist dran</span></p>
        <p class="note" class:bad={game.tone === "bad"}>{game.status}</p>
      </div>
    {/if}
  </section>
{/key}

<style>
  .plate {
    display: grid; grid-template-columns: auto 1fr; gap: 12px; align-items: center;
    background: var(--soft); border: 2px solid #fff; border-radius: 22px; padding: 10px 14px 10px 10px;
    box-shadow: 0 6px 18px rgba(42, 47, 90, 0.1); min-height: 88px;
  }
  .bump { animation: bump 380ms cubic-bezier(.3, 1.5, .5, 1); }
  @keyframes bump { 0% { transform: translateY(6px) scale(.98); } 100% { transform: none; } }
  .portrait { background: #fff; border-radius: 18px; padding: 4px; box-shadow: 0 0 0 3px var(--ribbon); }
  .portrait.turn { box-shadow: 0 0 0 3px var(--ink); }
  .name { display: flex; flex-wrap: wrap; align-items: baseline; gap: 4px 10px; margin: 0 0 4px; }
  .tag { font: 700 1.2rem/1.2 var(--font-display); background: var(--deep); color: #fff; border-radius: 99px; padding: 2px 12px; }
  .turn-tag { background: var(--ink); }
  .kind { font-size: 0.8rem; font-weight: 700; color: #11664B; background: #fff; box-shadow: inset 0 0 0 2px #BDEBD9; border-radius: 99px; padding: 2px 10px; }
  .pill-note { background: var(--butter-soft); border-radius: 14px; padding: 6px 10px; }
  .note { margin: 0; font-size: 0.98rem; line-height: 1.35; }
  .note.bad { color: var(--bad); font-weight: 700; }
  @media (prefers-reduced-motion: reduce) { .bump { animation: none; } }
</style>
