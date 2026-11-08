<script lang="ts">
  import { pieceSvg } from "../lib/pieceArt";
  let { piece, size = 48, muted = false }: { piece: string; size?: number; muted?: boolean } = $props();
</script>

<svg width={size} height={size} viewBox="0 0 100 100" aria-hidden="true" class="art">{@html pieceSvg(piece, muted)}</svg>

<style>
  .art { display: block; overflow: visible; }
</style>
