import { defineConfig } from "vite";
import { svelte } from "@sveltejs/vite-plugin-svelte";

// Das gebaute Frontend landet in ../static, von dort liefert backend.py es aus.
export default defineConfig({
  plugins: [svelte()],
  base: "/static/",
  build: { outDir: "../static", emptyOutDir: true, chunkSizeWarningLimit: 900 },
  server: { proxy: { "/api": "http://127.0.0.1:8000" } },
});
