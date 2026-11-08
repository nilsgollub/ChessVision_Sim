<script lang="ts">
  import { game } from "../lib/game.svelte";
  import { parseFen, START_FEN } from "../lib/chess";
  import { pieceSvg } from "../lib/pieceArt";
  import Icon from "./Icon.svelte";
  import { sanDe } from "../lib/pieces";

  let confirmDelete = $state<string | null>(null);
  let nameDraft = $state(game.gameName);
  $effect(() => { nameDraft = game.gameName; });

  const pairs = $derived.by(() => {
    // Zugpaare ab der Startstellung; beginnt Schwarz, bleibt das erste Weiß-Feld leer.
    const start = parseFen(game.startFen);
    let num = Number(start.fullmove) || 1;
    const rows: { num: number; w?: string; b?: string }[] = [];
    let row: { num: number; w?: string; b?: string } | null = null;
    let color = start.turn;
    for (const m of game.history) {
      if (color === "w" || !row) { row = { num }; rows.push(row); }
      if (color === "w") row.w = m.san;
      else { row.b = m.san; num++; }
      color = color === "w" ? "b" : "w";
    }
    return rows;
  });

  const others = $derived(game.savedGames.filter((g) => g.id !== game.gameId));

  function ago(ts: number) {
    const s = Math.max(0, Date.now() / 1000 - ts);
    if (s < 60) return "gerade eben";
    if (s < 3600) return `vor ${Math.round(s / 60)} Min.`;
    if (s < 86400) return `vor ${Math.round(s / 3600)} Std.`;
    return new Date(ts * 1000).toLocaleDateString("de-CH", { day: "numeric", month: "long" });
  }

  function mini(fen: string) {
    const { grid } = parseFen(fen);
    let out = "";
    grid.forEach((row, r) => row.forEach((p, c) => {
      out += `<rect x="${c * 100}" y="${r * 100}" width="100" height="100" fill="${(r + c) % 2 ? "var(--sq-dark)" : "var(--sq-light)"}"/>`;
      if (p) out += `<g transform="translate(${c * 100 + 4} ${r * 100 + 2}) scale(.92)">${pieceSvg(p)}</g>`;
    }));
    return out;
  }

  async function open(id: string) {
    await game.openGame(id);
    game.tab = "spielen";
  }

  function fresh() {
    game.newGame(START_FEN);
    game.tab = "spielen";
  }

  const saveText = $derived(
    game.saveState === "saving" ? "Wird gespeichert …"
      : game.saveState === "saved" ? "Gespeichert, auch auf deinen anderen Geräten"
      : game.saveState === "error" ? `Nicht gespeichert: ${game.saveError}`
      : "Wird nach dem ersten Zug gespeichert",
  );
</script>

<div class="panel">
  <section class="current" aria-label="Aktuelle Partie">
    <label class="name">
      <span>Name der Partie</span>
      <input type="text" maxlength="80" bind:value={nameDraft} placeholder="z.B. Sonntagspartie"
        onchange={() => game.rename(nameDraft)} onkeydown={(e) => e.key === "Enter" && (e.currentTarget as HTMLInputElement).blur()} />
    </label>
    <p class="save" data-state={game.saveState} aria-live="polite">{saveText}</p>

    {#if pairs.length}
      <ol class="moves" aria-label="Zugliste">
        {#each pairs as p}
          <li><span class="num">{p.num}.</span><span class="san">{p.w ? sanDe(p.w) : "…"}</span><span class="san">{p.b ? sanDe(p.b) : ""}</span></li>
        {/each}
      </ol>
    {:else}
      <p class="empty">Noch keine Züge. Jeder Zug landet hier und wird gespeichert.</p>
    {/if}

    <div class="actions">
      <button class="btn secondary" onclick={() => game.undo()} disabled={game.busy || !game.history.length}><Icon name="undo" /> Zug zurück</button>
      <button class="btn secondary" onclick={fresh}><Icon name="plus" /> Neue Partie</button>
    </div>
  </section>

  <section aria-label="Gespeicherte Partien">
    <h3>Weitere Partien</h3>
    {#if others.length}
      <ul class="list">
        {#each others as g (g.id)}
          <li>
            <svg class="thumb" viewBox="0 0 800 800" aria-hidden="true">{@html mini(g.fen)}</svg>
            <div class="info">
              <p class="gname">{g.name}</p>
              <p class="meta">{g.result ? `Ende: ${g.result}` : `${g.turn === "w" ? "Weiß" : "Schwarz"} am Zug`} · {g.move_count} {g.move_count === 1 ? "Zug" : "Züge"} · {ago(g.updated)}</p>
              <div class="row">
                {#if confirmDelete === g.id}
                  <button class="small danger" onclick={() => { game.deleteGame(g.id); confirmDelete = null; }}>Ja, löschen</button>
                  <button class="small" onclick={() => (confirmDelete = null)}>Behalten</button>
                {:else}
                  <button class="small go" onclick={() => open(g.id)} aria-label="{g.name} weiterspielen">Weiterspielen</button>
                  <button class="small icon" onclick={() => (confirmDelete = g.id)} aria-label="{g.name} löschen"><Icon name="trash" size={18} /></button>
                {/if}
              </div>
            </div>
          </li>
        {/each}
      </ul>
    {:else}
      <p class="empty">Hier erscheinen deine anderen Partien. Was du am Handy spielst oder scannst, kannst du am PC oder Tablet hier weiterspielen.</p>
    {/if}
  </section>
</div>

<style>
  .panel { display: grid; gap: 16px; }
  .current { background: #fff; border-radius: 20px; padding: 12px 14px; box-shadow: inset 0 0 0 2px var(--line); display: grid; gap: 10px; }
  .name { display: grid; gap: 4px; font-weight: 700; font-size: 0.85rem; color: var(--ink-soft); }
  .name input { min-height: 48px; border-radius: 14px; border: 2px solid var(--line-strong); padding: 0 12px; font: 600 1.1rem var(--font-display); color: var(--ink); background: var(--ground); }
  .name input:focus { outline: none; border-color: var(--focus); background: #fff; }
  .save { margin: 0; font-size: 0.85rem; font-weight: 700; color: var(--ink-soft); }
  .save[data-state="saved"] { color: #11664B; }
  .save[data-state="error"] { color: var(--bad); }
  .moves { list-style: none; margin: 0; padding: 8px; display: grid; grid-template-columns: repeat(auto-fill, minmax(132px, 1fr)); gap: 2px 10px; background: var(--ground); border-radius: 14px; max-height: 180px; overflow-y: auto; }
  .moves li { display: grid; grid-template-columns: 2.4em 1fr 1fr; font-variant-numeric: tabular-nums; font-size: 0.92rem; }
  .num { color: var(--ink-soft); }
  .san { font-weight: 700; }
  .actions { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
  h3 { margin: 0 0 8px; font: 600 1.05rem var(--font-display); }
  .list { list-style: none; margin: 0; padding: 0; display: grid; gap: 10px; }
  .list li { display: grid; grid-template-columns: 76px 1fr; gap: 12px; align-items: center; background: var(--coral-soft); border-radius: 20px; padding: 10px; }
  .thumb { width: 76px; height: 76px; border-radius: 10px; box-shadow: 0 0 0 3px #fff; }
  .gname { margin: 0; font: 700 1.05rem var(--font-display); overflow-wrap: anywhere; }
  .meta { margin: 2px 0 8px; font-size: 0.82rem; color: var(--ink-soft); }
  .row { display: flex; gap: 8px; flex-wrap: wrap; }
  .small { min-height: 40px; padding: 0 14px; border-radius: 99px; border: 0; background: #fff; font-weight: 700; color: var(--ink); box-shadow: inset 0 0 0 2px var(--line-strong); }
  .small.go { background: var(--coral-deep); color: #fff; box-shadow: none; }
  .small.icon { width: 40px; padding: 0; display: grid; place-items: center; }
  .small.danger { background: var(--bad); color: #fff; box-shadow: none; }
  .empty { margin: 0; color: var(--ink-soft); font-size: 0.95rem; line-height: 1.4; }
  @container (max-width: 330px) {
    .actions { grid-template-columns: 1fr; }
    .list li { grid-template-columns: 56px 1fr; }
    .thumb { width: 56px; height: 56px; }
  }
</style>
