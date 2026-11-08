export interface MoveInfo { uci: string; san: string; from: string; to: string; piece: string; capture: boolean }
export interface TopMove extends MoveInfo { rank: number; eval_cp: number | null; mate: number | null; evaluation: string }

export interface HistoryMove { uci: string; san: string; piece: string; fen: string }
export interface SavedGame { id: string; name: string; start_fen: string; moves: HistoryMove[]; fen: string; created: number; updated: number }
export interface GameSummary { id: string; name: string; fen: string; updated: number; created: number; move_count: number; turn: "w" | "b"; result: string | null }

async function req<T>(method: string, url: string, body?: unknown): Promise<T> {
  const res = await fetch(url, { method, headers: body ? { "Content-Type": "application/json" } : {}, body: body ? JSON.stringify(body) : undefined });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error((data as { detail?: string }).detail || `Fehler ${res.status}`);
  return data as T;
}

async function post<T>(url: string, body: unknown): Promise<T> {
  const res = await fetch(url, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error((data as { detail?: string }).detail || `Fehler ${res.status}`);
  return data as T;
}

export const api = {
  makeMove: (fen: string, from: string, to: string) =>
    post<{ legal: boolean; fen: string; move?: MoveInfo; is_check?: boolean; is_game_over?: boolean; result?: string | null }>(
      "/api/make-move", { fen, from_sq: from, to_sq: to }),
  analyze: (fen: string) =>
    post<{ game_over: boolean; result?: string; checkmate?: boolean; top_moves: TopMove[]; eval_cp: number | null; mate: number | null }>(
      "/api/engine-analyze", { fen, think_time_sec: 0.6, multipv: 3 }),
  play: (fen: string, level: number) =>
    post<{ game_over: boolean; result?: string | null; move?: MoveInfo; fen: string; is_check?: boolean; is_game_over?: boolean }>(
      "/api/engine-play", { fen, level }),
  listGames: () => req<GameSummary[]>("GET", "/api/games"),
  getGame: (id: string) => req<SavedGame>("GET", `/api/games/${id}`),
  createGame: (g: { name?: string; start_fen: string; moves: { uci: string }[]; fen: string }) => req<SavedGame>("POST", "/api/games", g),
  saveGame: (id: string, g: { name?: string; start_fen: string; moves: { uci: string }[]; fen: string }) => req<SavedGame>("PUT", `/api/games/${id}`, g),
  deleteGame: (id: string) => req<{ deleted: string }>("DELETE", `/api/games/${id}`),
  legalMoves: (fen: string) => post<{ moves: string[] }>("/api/legal-moves", { fen }),
  async detectCorners(file: File) {
    const fd = new FormData();
    fd.append("file", file);
    const res = await fetch("/api/detect-corners", { method: "POST", body: fd });
    if (!res.ok) throw new Error("Ecken konnten nicht gesucht werden");
    return (await res.json()) as { auto_detected: boolean; corners_normalized: [number, number][] };
  },
  async scan(file: File, corners: [number, number][], turn: "w" | "b") {
    const fd = new FormData();
    fd.append("file", file);
    fd.append("corners_json", JSON.stringify(corners));
    fd.append("active_color", turn);
    const res = await fetch("/api/scan-board", { method: "POST", body: fd });
    if (!res.ok) throw new Error("Scan fehlgeschlagen");
    return (await res.json()) as { fen: string; pieces_detected_count: number; warped_image_b64: string };
  },
};
