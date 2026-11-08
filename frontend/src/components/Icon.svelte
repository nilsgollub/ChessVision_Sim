<script lang="ts">
  // Eigene Strichsymbole, 24er-Raster, Strich 2.
  let { name, size = 22 }: { name: string; size?: number } = $props();
  const P: Record<string, string> = {
    play: "M7 4.5v15l12-7.5z",
    camera: "M4 8h3l2-3h6l2 3h3v11H4zM12 11a3.2 3.2 0 1 0 0 6.4 3.2 3.2 0 0 0 0-6.4z",
    pencil: "M15 4.5l4.5 4.5L9 19.5H4.5V15zM12.5 7l4.5 4.5",
    more: "M5 12h.01M12 12h.01M19 12h.01",
    flip: "M4 9a8 8 0 0 1 14-3l2 2M20 4v4h-4M20 15a8 8 0 0 1-14 3l-2-2M4 20v-4h4",
    bulb: "M9 18h6M10 21h4M12 3a6 6 0 0 0-3.5 10.9c.6.5 1 1.2 1 2V16h5v-.1c0-.8.4-1.5 1-2A6 6 0 0 0 12 3z",
    spark: "M12 3l1.8 5.2L19 10l-5.2 1.8L12 17l-1.8-5.2L5 10l5.2-1.8zM19 16l.8 2.2L22 19l-2.2.8L19 22l-.8-2.2L16 19l2.2-.8z",
    copy: "M9 9h10v10H9zM5 15V5h10",
    link: "M14 4h6v6M20 4l-9 9M18 14v6H4V6h6",
    eraser: "M8 20h12M5.5 14.5l8-8 5 5-6.5 6.5H9z",
    reset: "M4 12a8 8 0 1 0 2.3-5.7L4 8.5M4 4v4.5h4.5",
    clear: "M5 5l14 14M19 5L5 19",
    check: "M5 12.5l4.5 4.5L19 7",
    upload: "M12 16V4M7 9l5-5 5 5M5 20h14",
  };
  const filled = $derived(name === "play");
</script>

<svg width={size} height={size} viewBox="0 0 24 24" aria-hidden="true" fill={filled ? "currentColor" : "none"}
  stroke="currentColor" stroke-width={name === "more" ? 3.2 : 2} stroke-linecap="round" stroke-linejoin="round">
  <path d={P[name]} />
</svg>
