<script lang="ts">
  import { game } from "../lib/game.svelte";
  import { squareRC } from "../lib/chess";
  import { pieceSvg } from "../lib/pieceArt";
  import { pieceInfo, RANK_COLORS } from "../lib/pieces";

  const squares = $derived(game.displaySquares());

  function pos(sq: string): [number, number] {
    const [r, c] = squareRC(sq);
    const row = game.flipped ? 7 - r : r;
    const col = game.flipped ? 7 - c : c;
    return [col * 100, row * 100];
  }

  function arrow(from: string, to: string, rank: number) {
    const [x1, y1] = pos(from).map((v) => v + 50);
    const [x2, y2] = pos(to).map((v) => v + 50);
    const len = Math.hypot(x2 - x1, y2 - y1);
    const ux = (x2 - x1) / len, uy = (y2 - y1) / len;
    const w = [17, 12, 9][rank - 1] ?? 9;
    const head = w * 2.3;
    const ex = x2 - ux * head * 0.9, ey = y2 - uy * head * 0.9;
    const px = -uy, py = ux;
    return {
      line: `M${x1 + ux * 22} ${y1 + uy * 22} L${ex} ${ey}`,
      head: `M${x2} ${y2} L${ex + px * head * 0.62} ${ey + py * head * 0.62} L${ex - px * head * 0.62} ${ey - py * head * 0.62} Z`,
      w,
    };
  }

  // Zuckerperlen für den Schlag: Richtung und Farbe je Perle
  const BITS = Array.from({ length: 12 }, (_, i) => {
    const a = (i / 12) * Math.PI * 2 + (i % 2 ? 0.25 : 0);
    const d = 46 + (i % 3) * 14;
    return { tx: Math.cos(a) * d, ty: Math.sin(a) * d - 18, color: ["#F2559A", "#1FAA7E", "#F5C24B", "#8E6BE3", "#3D93E8", "#F0784A"][i % 6], r: 5 + (i % 3) };
  });

  function arrival(sq: string) {
    const fx = game.fx;
    if (!fx || fx.to !== sq) return null;
    const [fx0, fy0] = pos(fx.from);
    const [tx0, ty0] = pos(fx.to);
    return { dx: fx0 - tx0, dy: fy0 - ty0 };
  }

  function label(sq: string) {
    const p = game.pieceAt(sq);
    return p ? `${sq}, ${pieceInfo(p).label}` : `${sq}, leer`;
  }
</script>

<svg class="board" viewBox="0 0 800 800" role="grid" aria-label="Schachbrett">
  {#each squares as sq, i (sq)}
    {@const [x, y] = pos(sq)}
    {@const [r, c] = squareRC(sq)}
    {@const dark = (r + c) % 2 === 1}
    {@const piece = game.pieceAt(sq)}
    <g
      class="sq"
      data-square={sq}
      role="gridcell"
      tabindex={i === 0 ? 0 : -1}
      aria-label={label(sq)}
      aria-selected={game.selected === sq}
      onclick={() => game.tapSquare(sq)}
      onkeydown={(e) => (e.key === "Enter" || e.key === " ") && game.tapSquare(sq)}
    >
      <rect {x} {y} width="100" height="100" class={dark ? "dark" : "light"} />
      {#if game.lastMove && (game.lastMove.from === sq || game.lastMove.to === sq)}
        <rect {x} {y} width="100" height="100" class={dark ? "last-dark" : "last-light"} />
      {/if}
      {#if game.selected === sq}
        <rect x={x + 4} y={y + 4} width="92" height="92" rx="16" class="sel" />
      {/if}
      {#if (game.flipped ? r === 0 : r === 7)}
        <text x={x + 92} y={y + 92} class="coord" class:on-dark={dark} text-anchor="end">{sq[0]}</text>
      {/if}
      {#if (game.flipped ? c === 7 : c === 0)}
        <text x={x + 8} y={y + 22} class="coord" class:on-dark={dark}>{sq[1]}</text>
      {/if}
      {#if piece}
        {@const arr = arrival(sq)}
        {#key `${game.selected === sq ? game.plateBump : -1}/${arr ? game.fx?.id : 0}`}
          <g class="piece" class:hop={game.selected === sq} class:arrive={!!arr}
            style={arr ? `--dx: ${arr.dx}px; --dy: ${arr.dy}px` : undefined}
            transform="translate({x + 6} {y + 4}) scale(.88)">
            {@html pieceSvg(piece)}
          </g>
        {/key}
      {/if}
      {#if game.targets.includes(sq)}
        {#if piece}
          <rect x={x + 5} y={y + 5} width="90" height="90" rx="18" class="target-ring" />
        {:else}
          <circle cx={x + 50} cy={y + 50} r="14" class="target-dot" />
        {/if}
      {/if}
    </g>
  {/each}

  {#if game.fx?.captured}
    {#key game.fx.id}
      {@const [cx, cy] = pos(game.fx.capturedSq)}
      <g class="knockout" transform="translate({cx} {cy})" pointer-events="none" aria-hidden="true">
        {#each BITS as b}
          <circle class="bit" cx="50" cy="56" r={b.r} fill={b.color} style="--tx: {b.tx}px; --ty: {b.ty}px" />
        {/each}
        <g class="gone">{@html pieceSvg(game.fx.captured)}</g>
      </g>
    {/key}
  {/if}

  {#if game.hintsFresh}
    <g class="arrows" pointer-events="none">
      {#each [...game.topMoves].reverse() as m (m.uci)}
        {@const a = arrow(m.from, m.to, m.rank)}
        <g fill={RANK_COLORS[m.rank - 1]} stroke={RANK_COLORS[m.rank - 1]} opacity={m.rank === 1 ? 0.9 : 0.78}>
          <path d={a.line} stroke-width={a.w} stroke-linecap="round" fill="none" />
          <path d={a.head} stroke-width="4" stroke-linejoin="round" />
        </g>
      {/each}
    </g>
  {/if}
</svg>

<style>
  .board { width: 100%; height: 100%; display: block; border-radius: 18px; touch-action: manipulation; }
  .sq { cursor: pointer; outline: none; }
  .sq:focus-visible rect:first-child { stroke: var(--ink); stroke-width: 6; }
  .light { fill: var(--sq-light); }
  .dark { fill: var(--sq-dark); }
  .last-light { fill: #FFEDB0; }
  .last-dark { fill: #F1CF6E; }
  .sel { fill: none; stroke: var(--ink); stroke-width: 5; }
  .coord { font: 700 17px var(--font-ui); fill: var(--sq-dark-ink); }
  .coord.on-dark { fill: #fff; }
  .target-dot { fill: var(--ink); opacity: 0.32; }
  .target-ring { fill: none; stroke: var(--ink); stroke-width: 5; opacity: 0.4; stroke-dasharray: 10 8; }
  .piece { transform-box: fill-box; }
  .hop { animation: hop 420ms cubic-bezier(.3, 1.6, .5, 1); transform-origin: 50% 100%; }
  @keyframes hop {
    0% { translate: 0 0; }
    40% { translate: 0 -14px; }
    100% { translate: 0 0; }
  }
  /* Zug: die Figur gleitet vom Startfeld heran */
  .arrive { animation: arrive 300ms cubic-bezier(.22, 1, .36, 1); }
  @keyframes arrive { from { translate: var(--dx) var(--dy); } to { translate: 0 0; } }
  /* Schlag: geschlagene Figur hopst, kippt und schrumpft weg, Zuckerperlen sprühen */
  .gone { transform-origin: 50px 92px; animation: gone 440ms 170ms cubic-bezier(.4, 0, .7, 1) both; }
  @keyframes gone {
    0% { transform: translate(6px, 4px) scale(.88); opacity: 1; }
    30% { transform: translate(6px, -16px) scale(.92) rotate(-10deg); opacity: 1; }
    100% { transform: translate(6px, 12px) scale(0) rotate(50deg); opacity: 0; }
  }
  .bit { opacity: 0; animation: bit 560ms 230ms cubic-bezier(.2, .8, .4, 1) forwards; }
  @keyframes bit {
    0% { opacity: 1; translate: 0 0; scale: 1; }
    70% { opacity: 1; }
    100% { opacity: 0; translate: var(--tx) var(--ty); scale: .5; }
  }
  @media (prefers-reduced-motion: reduce) { .hop, .arrive { animation: none; } .gone, .bit { display: none; } }
</style>
