import { api, type MoveInfo, type TopMove } from "./api";
import { START_FEN, normalizeFen, parseFen, rebuildFen, squareName, squareRC, type Grid } from "./chess";
import { pieceInfo } from "./pieces";

export type Tab = "spielen" | "scannen" | "korrigieren" | "mehr";
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
    this.fen = normalizeFen(fen);
    this.lastMove = move;
    this.selected = null;
    this.targets = [];
    if (this.analyzedFen !== this.fen) this.topMoves = [];
  }

  /** Brett im Editor geändert oder Farbe umgeschaltet: FEN aus dem Grid neu aufbauen. */
  private rebuild(grid: Grid, turn: "w" | "b") {
    this.fen = rebuildFen(this.fen, grid, turn);
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

  newGame(fen = START_FEN) {
    this.loadFen(fen);
    this.evalCp = null;
    this.evalMate = null;
    this.analyzedFen = null;
    this.setStatus("Neue Partie. Weiß fängt an.");
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
(window as unknown as { brettfreunde: unknown }).brettfreunde = { getFen: () => game.fen, game };
