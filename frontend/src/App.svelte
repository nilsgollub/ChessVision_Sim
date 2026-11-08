<script lang="ts">
  import { game, type Tab } from "./lib/game.svelte";
  import Board2D from "./components/Board2D.svelte";
  import Board3D from "./components/Board3D.svelte";
  import EvalBar from "./components/EvalBar.svelte";
  import PiecePlate from "./components/PiecePlate.svelte";
  import PlayPanel from "./components/PlayPanel.svelte";
  import ScanPanel from "./components/ScanPanel.svelte";
  import EditorPanel from "./components/EditorPanel.svelte";
  import MorePanel from "./components/MorePanel.svelte";
  import Icon from "./components/Icon.svelte";
  import { evalWords } from "./lib/pieces";

  const TABS: { id: Tab; label: string; icon: string; color: string; soft: string }[] = [
    { id: "spielen", label: "Spielen", icon: "play", color: "var(--pink)", soft: "#FFE3EF" },
    { id: "scannen", label: "Scannen", icon: "camera", color: "var(--sky)", soft: "var(--sky-soft)" },
    { id: "korrigieren", label: "Korrigieren", icon: "pencil", color: "var(--mint)", soft: "var(--mint-soft)" },
    { id: "mehr", label: "Mehr", icon: "more", color: "var(--lilac)", soft: "var(--lilac-soft)" },
  ];

  const evalText = $derived(game.evalCp !== null || game.evalMate !== null ? evalWords(game.evalCp, game.evalMate) : "");

  function setTab(t: Tab) {
    game.tab = t;
    game.selected = null;
    game.targets = [];
    if (t === "korrigieren") game.view = "2d";
  }
</script>

<div class="app">
  <header class="top">
    <h1>Brettfreunde<svg class="sparkle" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 2l2.2 6.6L21 11l-6.8 2.4L12 20l-2.2-6.6L3 11l6.8-2.4z"/><path class="s2" d="M20 1l.9 2.3 2.1.9-2.1.8L20 7.4l-.9-2.4-2.1-.8 2.1-.9z"/></svg></h1>
    <p class="pill" data-tone={game.tone} aria-live="polite">{game.busy ? "rechnet …" : `Zug ${game.parsed.fullmove}`}</p>
  </header>

  <main class="main">
    <section class="board-area" aria-label="Brett">
      <div class="board-tools">
        <button class="icon-btn" onclick={() => (game.flipped = !game.flipped)} aria-label="Brett drehen"><Icon name="flip" /></button>
        <p class="eval-words">{evalText}</p>
        <div class="view-seg" role="group" aria-label="Ansicht">
          <button class:on={game.view === "3d"} aria-pressed={game.view === "3d"} onclick={() => (game.view = "3d")} data-testid="view-3d">3D</button>
          <button class:on={game.view === "2d"} aria-pressed={game.view === "2d"} onclick={() => (game.view = "2d")} data-testid="view-2d">2D</button>
        </div>
      </div>
      <div class="board-row">
        <EvalBar />
        <div class="board-frame" class:three={game.view === "3d"}>
          {#if game.view === "3d"}<Board3D />{:else}<Board2D />{/if}
        </div>
      </div>
    </section>

    <section class="side">
      {#if game.tab === "spielen" || game.tab === "korrigieren"}<PiecePlate />{/if}
      <div class="panel-body">
        {#if game.tab === "spielen"}<PlayPanel />
        {:else if game.tab === "scannen"}<ScanPanel />
        {:else if game.tab === "korrigieren"}<EditorPanel />
        {:else}<MorePanel />{/if}
      </div>
    </section>
  </main>

  <nav class="nav" aria-label="Bereiche">
    {#each TABS as t}
      <button class:on={game.tab === t.id} aria-current={game.tab === t.id ? "page" : undefined} onclick={() => setTab(t.id)} data-tab={t.id}
        style:--tab={t.color} style:--tab-soft={t.soft}>
        <span class="nav-icon"><Icon name={t.icon} size={24} /></span>
        <span>{t.label}</span>
      </button>
    {/each}
  </nav>
</div>

<style>
  .app { min-height: 100dvh; display: grid; grid-template-rows: auto 1fr auto; max-width: 1180px; margin: 0 auto; }
  .top { display: flex; align-items: center; justify-content: space-between; gap: 12px; padding: max(10px, env(safe-area-inset-top)) 16px 6px; }
  h1 { margin: 0; font: 700 2rem/1 var(--font-display); letter-spacing: -0.015em; color: var(--ink); display: flex; align-items: flex-start; gap: 2px; }
  .sparkle { width: 22px; height: 22px; fill: var(--butter); margin-top: -6px; }
  .sparkle .s2 { fill: var(--pink); }
  .pill { margin: 0; font-weight: 700; font-size: 0.85rem; background: #fff; border-radius: 99px; padding: 6px 12px; box-shadow: inset 0 0 0 2px var(--line); white-space: nowrap; }
  .pill[data-tone="busy"] { background: var(--butter-soft); }

  .main { display: grid; gap: 14px; padding: 4px 12px 96px; align-content: start; }
  .board-tools { display: flex; align-items: center; gap: 10px; margin-bottom: 8px; }
  .eval-words { margin: 0; flex: 1; font-weight: 700; font-size: 0.9rem; color: var(--ink-soft); text-align: center; }
  .view-seg { display: inline-grid; grid-template-columns: 1fr 1fr; background: #fff; border-radius: 99px; padding: 3px; box-shadow: inset 0 0 0 2px var(--line); }
  .view-seg button { min-width: 52px; min-height: 40px; border: 0; border-radius: 99px; background: transparent; font: 600 0.95rem var(--font-display); color: var(--ink-soft); }
  .view-seg button.on { background: var(--ink); color: #fff; }
  .icon-btn { width: 44px; height: 44px; border-radius: 50%; border: 0; background: #fff; color: var(--ink); display: grid; place-items: center; box-shadow: inset 0 0 0 2px var(--line); }

  .board-row { display: grid; grid-template-columns: 12px 1fr; gap: 8px; }
  .board-frame { aspect-ratio: 1; border-radius: 22px; background: var(--frame); padding: 8px; box-shadow: 0 10px 28px rgba(42, 47, 90, 0.16); }
  .board-frame.three { padding: 0; background: var(--sprinkle), radial-gradient(120% 90% at 50% 30%, #fff 0%, var(--ground-deep) 100%); background-size: 120px 120px, 120px 120px, 120px 120px, 120px 120px, 120px 120px, 120px 120px, auto; overflow: hidden; }

  .side { display: grid; gap: 12px; align-content: start; }

  .nav {
    position: fixed; left: 0; right: 0; bottom: 0; z-index: 5; display: grid; grid-template-columns: repeat(4, 1fr);
    background: #fff; padding: 6px 8px max(8px, env(safe-area-inset-bottom)); box-shadow: 0 -6px 20px rgba(42, 47, 90, 0.1);
    border-radius: 22px 22px 0 0;
  }
  .nav button { display: grid; justify-items: center; gap: 2px; border: 0; background: transparent; color: var(--ink-soft); font-weight: 700; font-size: 0.78rem; min-height: 56px; border-radius: 16px; padding: 6px 0; }
  .nav-icon { color: var(--tab); display: grid; place-items: center; width: 40px; height: 30px; border-radius: 99px; transition: background 180ms; }
  .nav button.on { color: var(--ink); }
  .nav button.on .nav-icon { background: var(--tab-soft); }

  @media (min-width: 960px) {
    .app { grid-template-columns: 112px 1fr; grid-template-rows: auto 1fr; column-gap: 12px; }
    .top { grid-column: 2; padding-top: 18px; }
    .main { grid-column: 2; grid-template-columns: minmax(0, 560px) minmax(340px, 1fr); gap: 28px; padding: 8px 24px 32px 0; align-items: start; }
    .side { position: sticky; top: 12px; }
    .nav {
      position: sticky; top: 16px; grid-column: 1; grid-row: 1 / 3; align-self: start; margin: 16px 0 0 16px;
      grid-template-columns: 1fr; gap: 6px; border-radius: 22px; padding: 10px 8px; box-shadow: 0 6px 20px rgba(42, 47, 90, 0.1);
    }
    .nav button { min-height: 72px; }
  }
</style>
