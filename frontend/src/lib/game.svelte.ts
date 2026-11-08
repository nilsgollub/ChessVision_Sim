import { api, type GameSummary, type HistoryMove, type MoveInfo, type TopMove } from "./api";
import { START_FEN, normalizeFen, parseFen, rebuildFen, squareName, squareRC, type Grid } from "./chess";
import { pieceInfo, sanDe } from "./pieces";
import { play, soundLog } from "./sound";

export type Tab = "spielen" | "scannen" | "korrigieren" | "partien" | "mehr";
export type SaveState = "idle" | "saving" | "saved" | "error";
export type Tone = "neutral" | "busy" | "good" | "warn" | "bad";

class Game {
  fen = $state(START_FEN);
  tab = $state<Tab>("spielen");
  view = $state<"3d" | "2d">("3d");
  flipped = $state(false);
  selected = $state<string | null>(null);
  targets = $state<string[]>([]);
  lastMove = $state<MoveInfo | null>(null);
  topMoves = $state<TopMove[]>([]);
  evalCp = $state<number | null>(null);
  evalMate = $state<number | null>(null);
  analyzedFen = $state<string | null>(null);
  status = $state("Tippe eine Figur an.");
  tone = $state<Tone>("neutral");
  busy = $state(false);
  aiReplies = $state(false);
  level = $state(2);
  editPiece = $state<string>("P");
  /** Zähler, damit die Figurenplakette bei jeder neuen Auswahl hüpft. */
  plateBump = $state(0);

  // Gespeicherte Partie: Startstellung + Zugliste, auf dem Server abgelegt.
  gameId = $state<string | null>(null);
  gameName = $state("");
  startFen = $state(START_FEN);
  history = $state<HistoryMove[]>([]);
  saveState = $state<SaveState>("idle");
  saveError = $state("");
  savedGames = $state<GameSummary[]>([]);
  /** Effekt des letzten Zugs (nur bei echten Zügen, nicht beim Laden oder Zurücknehmen). */
  fx = $state<{ id: number; from: string; to: string; captured: string; capturedSq: string } | null>(null);
  private fxId = 0;
  private saveTimer: ReturnType<typeof setTimeout> | null = null;
  private saving: Promise<void> = Promise.resolve();

  parsed = $derived(parseFen(this.fen));
  grid: Grid = $derived(this.parsed.grid);
  turn = $derived(this.parsed.turn);
  hintsFresh = $derived(this.analyzedFen === this.fen);

  private legal: string[] = [];
  private legalFen = "";

  setStatus(text: string, tone: Tone = "neutral") {
    this.status = text;
    this.tone = tone;
  }

  /** Neue FEN vom Backend übernehmen (vollständig, inkl. Rochade, En passant, Zähler). */
  loadFen(fen: string, move: MoveInfo | null = null) {
    this.fx = null;
    if (move) {
      // Geschlagene Figur aus der Stellung vor dem Zug; en passant steht sie neben dem Zielfeld.
      let capturedSq = "", captured = "";
      if (move.capture) {
        capturedSq = this.pieceAt(move.to) ? move.to : move.to[0] + move.from[1];
        captured = this.pieceAt(capturedSq);
      }
      this.fx = { id: ++this.fxId, from: move.from, to: move.to, captured, capturedSq };
      this.history.push({ uci: move.uci, san: move.san, piece: move.piece, fen: normalizeFen(fen) });
      this.scheduleSave();
    }
    this.fen = normalizeFen(fen);
    this.lastMove = move;
    this.selected = null;
    this.targets = [];
    if (this.analyzedFen !== this.fen) this.topMoves = [];
  }

  /** Brett im Editor geändert oder Farbe umgeschaltet: FEN aus dem Grid neu aufbauen. */
  private rebuild(grid: Grid, turn: "w" | "b") {
    this.fen = rebuildFen(this.fen, grid, turn);
    // Nach einer Korrektur beginnt die Zugliste neu ab der korrigierten Stellung.
    this.startFen = this.fen;
    this.history = [];
    this.scheduleSave();
    this.lastMove = null;
    this.topMoves = [];
    this.selected = null;
    this.targets = [];
  }

  setTurn(turn: "w" | "b") {
    if (turn === this.turn) return;
    this.rebuild(this.grid.map((r) => [...r]), turn);
    this.setStatus(turn === "w" ? "Weiß ist am Zug." : "Schwarz ist am Zug.");
  }

  editSquare(sq: string) {
    const [r, c] = squareRC(sq);
    const grid = this.grid.map((row) => [...row]);
    const piece = this.editPiece === "ERASE" ? "" : this.editPiece;
    grid[r][c] = grid[r][c] === piece ? "" : piece;
    this.rebuild(grid, this.turn);
  }

  /** Neue Partie (Grundstellung, Scan oder leeres Brett): neuer Eintrag in der Partienliste. */
  newGame(fen = START_FEN, name = "") {
    this.loadFen(fen);
    this.startFen = this.fen;
    this.history = [];
    this.gameId = null;
    this.gameName = name;
    this.evalCp = null;
    this.evalMate = null;
    this.analyzedFen = null;
    this.setStatus(this.turn === "w" ? "Neue Partie. Weiß ist am Zug." : "Neue Partie. Schwarz ist am Zug.");
    this.scheduleSave(0);
  }

  // --- Speichern und Laden -------------------------------------------------

  scheduleSave(delay = 400) {
    if (this.saveTimer) clearTimeout(this.saveTimer);
    this.saveState = "saving";
    this.saveTimer = setTimeout(() => {
      this.saveTimer = null;
      // Speichervorgänge nacheinander, damit der erste die ID vergibt, bevor der nächste kommt.
      this.saving = this.saving.then(() => this.saveNow());
    }, delay);
  }

  private async saveNow() {
    const body = { name: this.gameName || undefined, start_fen: this.startFen, moves: this.history.map((m) => ({ uci: m.uci })), fen: this.fen };
    // Eine unberührte Grundstellung legt noch keinen Eintrag an.
    if (!this.gameId && !this.history.length && this.fen === START_FEN) {
      this.saveState = "idle";
      return;
    }
    try {
      let g;
      try {
        g = this.gameId ? await api.saveGame(this.gameId, body) : await api.createGame(body);
      } catch (e) {
        // Auf einem anderen Gerät gelöscht: als neue Partie ablegen.
        if (!this.gameId || !/gibt es nicht/.test((e as Error).message)) throw e;
        g = await api.createGame(body);
      }
      this.gameId = g.id;
      this.gameName = g.name;
      this.saveState = "saved";
      this.saveError = "";
    } catch (e) {
      this.saveState = "error";
      this.saveError = (e as Error).message;
    }
  }

  rename(name: string) {
    this.gameName = name.trim();
    if (this.gameName) this.scheduleSave(0);
  }

  async refreshGames() {
    try {
      this.savedGames = await api.listGames();
    } catch {
      /* Liste bleibt, wie sie war */
    }
  }

  async openGame(id: string, quiet = false) {
    try {
      const g = await api.getGame(id);
      this.gameId = g.id;
      this.gameName = g.name;
      this.startFen = normalizeFen(g.start_fen);
      this.history = g.moves.map((m) => ({ ...m, fen: normalizeFen(m.fen) }));
      const last = g.moves.at(-1);
      this.loadFen(g.fen, null);
      this.lastMove = last ? { uci: last.uci, san: last.san, from: last.uci.slice(0, 2), to: last.uci.slice(2, 4), piece: last.piece, capture: false } : null;
      this.evalCp = null;
      this.evalMate = null;
      this.analyzedFen = null;
      this.saveState = "saved";
      if (!quiet) this.setStatus(`„${g.name}“ ist offen. ${this.turn === "w" ? "Weiß" : "Schwarz"} ist am Zug.`, "good");
      else this.setStatus(`Weiter mit „${g.name}“. ${this.turn === "w" ? "Weiß" : "Schwarz"} ist am Zug.`);
    } catch (e) {
      this.setStatus((e as Error).message, "bad");
    }
  }

  async deleteGame(id: string) {
    try {
      await api.deleteGame(id);
      if (id === this.gameId) this.gameId = null;
      await this.refreshGames();
    } catch (e) {
      this.setStatus((e as Error).message, "bad");
    }
  }

  /** Beim Start: die zuletzt gespielte Partie öffnen, egal auf welchem Gerät sie gespielt wurde. */
  async resumeLatest() {
    await this.refreshGames();
    const latest = this.savedGames[0];
    if (latest) await this.openGame(latest.id, true);
  }

  undo() {
    if (this.busy || !this.history.length) return;
    const removed = this.history.pop()!;
    const prev = this.history.at(-1);
    this.fen = prev ? prev.fen : this.startFen;
    this.lastMove = prev ? { uci: prev.uci, san: prev.san, from: prev.uci.slice(0, 2), to: prev.uci.slice(2, 4), piece: prev.piece, capture: false } : null;
    this.selected = null;
    this.targets = [];
    this.topMoves = [];
    this.setStatus(`Zug ${sanDe(removed.san)} zurückgenommen.`);
    this.scheduleSave(0);
  }

  private async legalMoves(): Promise<string[]> {
    if (this.legalFen !== this.fen) {
      const fen = this.fen;
      try {
        const res = await api.legalMoves(fen);
        this.legal = res.moves;
        this.legalFen = fen;
      } catch {
        return [];
      }
    }
    return this.legal;
  }

  async tapSquare(sq: string) {
    if (this.busy) return;
    if (this.tab === "korrigieren") {
      this.editSquare(sq);
      return;
    }
    const [r, c] = squareRC(sq);
    const piece = this.grid[r][c];
    const own = piece && (piece === piece.toUpperCase() ? "w" : "b") === this.turn;

    if (this.selected && this.selected !== sq && !own) {
      await this.move(this.selected, sq);
      return;
    }
    if (this.selected === sq || !piece) {
      this.selected = null;
      this.targets = [];
      return;
    }
    this.selected = sq;
    this.plateBump++;
    if (!own) {
      this.targets = [];
      const info = pieceInfo(piece);
      this.setStatus(`${info.name} gehört zu ${info.white ? "Weiß" : "Schwarz"}. ${this.turn === "w" ? "Weiß" : "Schwarz"} ist dran.`, "warn");
      return;
    }
    const moves = await this.legalMoves();
    this.targets = moves.filter((m) => m.startsWith(sq)).map((m) => m.slice(2, 4));
    const info = pieceInfo(piece);
    this.setStatus(this.targets.length ? `${info.name} kann auf ${this.targets.length} ${this.targets.length === 1 ? "Feld" : "Felder"}.` : `${info.name} kann gerade nicht ziehen.`);
  }

  async move(from: string, to: string) {
    this.busy = true;
    try {
      const res = await api.makeMove(this.fen, from, to);
      if (!res.legal) {
        this.setStatus("So darf diese Figur nicht ziehen.", "warn");
        play("nope");
        this.selected = null;
        this.targets = [];
        return;
      }
      this.loadFen(res.fen, res.move ?? null);
      this.announce(res.move, res.is_check, res.is_game_over, res.result);
      if (this.aiReplies && !res.is_game_over) {
        this.busy = false;
        await this.aiMove();
      }
    } catch (e) {
      this.setStatus((e as Error).message, "bad");
    } finally {
      this.busy = false;
    }
  }

  private announce(move?: MoveInfo, check?: boolean, over?: boolean, result?: string | null) {
    play(over ? (result === "1/2-1/2" ? "draw" : "win") : check ? "check" : move?.capture ? "capture" : "move");
    if (over) {
      this.setStatus(result === "1/2-1/2" ? "Unentschieden!" : `Schachmatt! ${result === "1-0" ? "Weiß" : "Schwarz"} gewinnt.`, "good");
    } else if (check) {
      this.setStatus("Schach! Der König muss sich retten.", "warn");
    } else if (move) {
      const info = pieceInfo(move.piece);
      this.setStatus(`${info.name} zieht nach ${move.to}${move.capture ? " und schlägt" : ""}.`);
    }
  }

  async aiMove() {
    if (this.busy) return;
    this.busy = true;
    this.setStatus("Die KI überlegt …", "busy");
    try {
      const res = await api.play(this.fen, this.level);
      if (res.game_over) {
        this.setStatus("Die Partie ist schon zu Ende.", "good");
        return;
      }
      this.loadFen(res.fen, res.move ?? null);
      this.announce(res.move, res.is_check, res.is_game_over, res.result);
    } catch (e) {
      this.setStatus((e as Error).message, "bad");
    } finally {
      this.busy = false;
    }
  }

  async hint() {
    if (this.busy) return;
    this.busy = true;
    this.setStatus("Stockfish sucht die besten Züge …", "busy");
    const fen = this.fen;
    try {
      const res = await api.analyze(fen);
      if (fen !== this.fen) return;
      if (res.game_over) {
        this.topMoves = [];
        this.setStatus(res.checkmate ? "Schachmatt, die Partie ist vorbei." : "Die Partie ist vorbei.", "good");
        return;
      }
      this.topMoves = res.top_moves;
      this.evalCp = res.eval_cp;
      this.evalMate = res.mate;
      this.analyzedFen = fen;
      this.setStatus(`${res.top_moves.length} Ideen gefunden.`, "good");
    } catch (e) {
      this.setStatus((e as Error).message, "bad");
    } finally {
      this.busy = false;
    }
  }

  pieceAt(sq: string): string {
    const [r, c] = squareRC(sq);
    return this.grid[r][c];
  }

  /** Feldnamen in Darstellungsreihenfolge (oben links zuerst). */
  displaySquares(): string[] {
    const out: string[] = [];
    for (let i = 0; i < 8; i++)
      for (let j = 0; j < 8; j++) out.push(squareName(this.flipped ? 7 - i : i, this.flipped ? 7 - j : j));
    return out;
  }
}

export const game = new Game();

// Für Tests und zum Nachschauen in der Konsole.
(window as unknown as { brettfreunde: unknown }).brettfreunde = { getFen: () => game.fen, game, soundLog };
