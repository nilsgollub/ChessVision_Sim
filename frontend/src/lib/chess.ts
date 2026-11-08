// FEN-Hilfen. Die vollständige FEN kommt vom Backend; aus dem Brett wird sie nur
// nach Editor-Änderungen oder dem Farbwechsel neu aufgebaut.

export type Grid = string[][]; // grid[0] = 8. Reihe, Spalte 0 = a
export const START_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1";
export const EMPTY_FEN = "4k3/8/8/8/8/8/8/4K3 w - - 0 1";

export function parseFen(fen: string) {
  const parts = fen.trim().split(/\s+/);
  const grid: Grid = Array.from({ length: 8 }, () => Array(8).fill(""));
  parts[0].split("/").forEach((row, r) => {
    let c = 0;
    for (const ch of row) {
      if (/\d/.test(ch)) c += Number(ch);
      else grid[r][c++] = ch;
    }
  });
  return {
    grid,
    turn: (parts[1] === "b" ? "b" : "w") as "w" | "b",
    castling: parts[2] || "-",
    ep: parts[3] || "-",
    halfmove: parts[4] || "0",
    fullmove: parts[5] || "1",
  };
}

export function normalizeFen(fen: string): string {
  const f = parseFen(fen);
  return [fen.trim().split(/\s+/)[0], f.turn, f.castling, f.ep, f.halfmove, f.fullmove].join(" ");
}

export function placementFromGrid(grid: Grid): string {
  return grid
    .map((row) => {
      let s = "", empty = 0;
      for (const cell of row) {
        if (!cell) empty++;
        else { if (empty) { s += empty; empty = 0; } s += cell; }
      }
      return empty ? s + empty : s;
    })
    .join("/");
}

/** Rochaderechte nur behalten, wenn König und Turm noch auf ihren Ausgangsfeldern stehen. */
export function filterCastling(rights: string, grid: Grid): string {
  const ok: Record<string, boolean> = {
    K: grid[7][4] === "K" && grid[7][7] === "R",
    Q: grid[7][4] === "K" && grid[7][0] === "R",
    k: grid[0][4] === "k" && grid[0][7] === "r",
    q: grid[0][4] === "k" && grid[0][0] === "r",
  };
  return "KQkq".split("").filter((ch) => rights.includes(ch) && ok[ch]).join("") || "-";
}

/** Neuaufbau nach manuellen Änderungen: Rechte gefiltert, En passant verfällt, Zähler bleiben. */
export function rebuildFen(prevFen: string, grid: Grid, turn: "w" | "b"): string {
  const prev = parseFen(prevFen);
  return `${placementFromGrid(grid)} ${turn} ${filterCastling(prev.castling, grid)} - ${prev.halfmove} ${prev.fullmove}`;
}

export function squareName(r: number, c: number): string {
  return String.fromCharCode(97 + c) + (8 - r);
}

export function squareRC(sq: string): [number, number] {
  return [8 - Number(sq[1]), sq.charCodeAt(0) - 97];
}

const START_COUNTS: Record<string, number> = { p: 8, n: 2, b: 2, r: 2, q: 1, k: 1 };

/** Geschlagene Figuren aus dem Materialvergleich mit der Grundstellung (ohne Umwandlungen exakt). */
export function capturedPieces(grid: Grid): string[] {
  const count: Record<string, number> = {};
  for (const row of grid) for (const p of row) if (p) count[p] = (count[p] || 0) + 1;
  const out: string[] = [];
  for (const t of ["q", "r", "b", "n", "p"]) {
    for (const p of [t.toUpperCase(), t]) {
      const missing = START_COUNTS[t] - (count[p] || 0);
      for (let i = 0; i < missing; i++) out.push(p);
    }
  }
  return out;
}

export function lichessUrl(fen: string): string {
  return "https://lichess.org/analysis/standard/" + fen.trim().replace(/\s+/g, "_");
}
