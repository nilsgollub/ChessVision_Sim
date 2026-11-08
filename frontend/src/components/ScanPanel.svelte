<script lang="ts">
  import { game } from "../lib/game.svelte";
  import { api } from "../lib/api";
  import Icon from "./Icon.svelte";

  type Pt = [number, number];
  const LABELS = ["a8", "h8", "h1", "a1"];

  let file = $state<File | null>(null);
  let imgUrl = $state("");
  let natural = $state({ w: 1, h: 1 });
  let corners = $state<Pt[]>([[0.15, 0.15], [0.85, 0.15], [0.85, 0.85], [0.15, 0.85]]);
  let phase = $state<"idle" | "finding" | "ready" | "scanning">("idle");
  let autoFound = $state(false);
  let warped = $state("");
  let error = $state("");
  let stage = $state<HTMLDivElement>();
  let drag = -1;

  async function pick(e: Event) {
    const f = (e.currentTarget as HTMLInputElement).files?.[0];
    if (!f) return;
    file = f;
    error = "";
    warped = "";
    if (imgUrl) URL.revokeObjectURL(imgUrl);
    imgUrl = URL.createObjectURL(f);
    phase = "finding";
    try {
      const res = await api.detectCorners(f);
      corners = res.corners_normalized;
      autoFound = res.auto_detected;
    } catch (err) {
      error = (err as Error).message;
    }
    phase = "ready";
  }

  function toNorm(e: PointerEvent): Pt {
    const r = stage!.getBoundingClientRect();
    return [Math.min(1, Math.max(0, (e.clientX - r.left) / r.width)), Math.min(1, Math.max(0, (e.clientY - r.top) / r.height))];
  }
  function down(i: number, e: PointerEvent) {
    drag = i;
    (e.currentTarget as Element).setPointerCapture(e.pointerId);
  }
  function move(e: PointerEvent) {
    if (drag < 0) return;
    corners[drag] = toNorm(e);
  }
  function nudge(i: number, e: KeyboardEvent) {
    const d = e.shiftKey ? 0.02 : 0.005;
    const k: Record<string, Pt> = { ArrowLeft: [-d, 0], ArrowRight: [d, 0], ArrowUp: [0, -d], ArrowDown: [0, d] };
    if (!k[e.key]) return;
    e.preventDefault();
    corners[i] = [Math.min(1, Math.max(0, corners[i][0] + k[e.key][0])), Math.min(1, Math.max(0, corners[i][1] + k[e.key][1]))];
  }

  async function scan() {
    if (!file) return;
    phase = "scanning";
    error = "";
    try {
      const res = await api.scan(file, corners, game.turn);
      warped = res.warped_image_b64;
      game.newGame(res.fen);
      game.setStatus(res.pieces_detected_count > 0
        ? `${res.pieces_detected_count} Figuren erkannt. Prüfe das Brett und korrigiere, was nicht stimmt.`
        : "Keine Figuren erkannt. Die Grundstellung ist geladen, du kannst sie korrigieren.", "good");
      game.tab = "korrigieren";
    } catch (err) {
      error = (err as Error).message;
    }
    phase = "ready";
  }

  const poly = $derived(corners.map(([x, y]) => `${x * 100},${y * 100}`).join(" "));
</script>

<div class="panel">
  {#if phase === "idle"}
    <div class="intro">
      <p>Fotografiere das echte Brett möglichst von oben, mit Weiß unten.</p>
    </div>
  {/if}

  <label class="btn primary upload">
    <Icon name="camera" /> {file ? "Neues Foto" : "Brett fotografieren"}
    <input type="file" accept="image/*" capture="environment" onchange={pick} />
  </label>

  {#if imgUrl}
    <p class="help">
      {#if phase === "finding"}Suche die Ecken …
      {:else if autoFound}Ecken gefunden. Zieh die Punkte auf die Ecken der <b>Spielfelder</b>, nicht auf den Rand.
      {:else}Ecken nicht sicher gefunden. Zieh die vier Punkte auf die Ecken der Spielfelder.{/if}
    </p>
    <div class="stage" role="application" aria-label="Foto mit vier Eckpunkten" bind:this={stage} style:aspect-ratio="{natural.w} / {natural.h}" onpointermove={move} onpointerup={() => (drag = -1)}>
      <img src={imgUrl} alt="Foto des Bretts" onload={(e) => (natural = { w: (e.currentTarget as HTMLImageElement).naturalWidth, h: (e.currentTarget as HTMLImageElement).naturalHeight })} />
      <svg viewBox="0 0 100 100" preserveAspectRatio="none" class="overlay" aria-hidden="true">
        <polygon points={poly} />
      </svg>
      {#each corners as [x, y], i}
        <button class="pin" style:left="{x * 100}%" style:top="{y * 100}%" aria-label="Ecke {LABELS[i]} verschieben (Pfeiltasten)"
          onpointerdown={(e) => down(i, e)} onkeydown={(e) => nudge(i, e)}>
          <span>{LABELS[i]}</span>
        </button>
      {/each}
    </div>
    <button class="btn primary" onclick={scan} disabled={phase !== "ready"}>
      <Icon name="check" /> {phase === "scanning" ? "Erkenne Figuren …" : "Figuren erkennen"}
    </button>
  {/if}

  {#if error}<p class="error" role="alert">{error}. Versuch es nochmal oder setz die Figuren im Bereich Korrigieren.</p>{/if}

  {#if warped}
    <figure class="warped">
      <img src={warped} alt="Entzerrtes Brett mit Gitter" />
      <figcaption>So sieht die Erkennung das Brett.</figcaption>
    </figure>
  {/if}
</div>

<style>
  .panel { display: grid; gap: 14px; }
  .intro p { margin: 0; }
  .upload { position: relative; }
  .upload input { position: absolute; inset: 0; opacity: 0; cursor: pointer; }
  .help { margin: 0; color: var(--ink-soft); }
  .stage { position: relative; width: 100%; border-radius: 18px; overflow: hidden; touch-action: none; background: var(--ink); }
  .stage img { width: 100%; height: 100%; display: block; object-fit: fill; user-select: none; -webkit-user-drag: none; }
  .overlay { position: absolute; inset: 0; width: 100%; height: 100%; pointer-events: none; }
  .overlay polygon { fill: color-mix(in srgb, var(--pink) 16%, transparent); stroke: var(--pink); stroke-width: 0.6; vector-effect: non-scaling-stroke; stroke-linejoin: round; }
  .pin {
    position: absolute; width: 44px; height: 44px; margin: -22px 0 0 -22px; border-radius: 50%; border: 3px solid #fff;
    background: var(--pink-deep); color: #fff; box-shadow: 0 3px 10px rgba(42, 47, 90, 0.35); padding: 0; touch-action: none; cursor: grab;
  }
  .pin span { font: 600 0.8rem var(--font-display); }
  .pin:active { cursor: grabbing; transform: scale(1.12); }
  .error { margin: 0; color: var(--bad); font-weight: 700; }
  .warped { margin: 0; display: grid; gap: 6px; }
  .warped img { width: 100%; border-radius: 18px; }
  figcaption { font-size: 0.85rem; color: var(--ink-soft); }
</style>
