import os
import shutil
import base64
import cv2
import numpy as np
import chess
import chess.engine
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List
import json

from vision_engine import ChessVisionEngine

app = FastAPI(title="Chess Vision & Sim Backend")

# Initialisiere Vision Engine
vision = ChessVisionEngine(model_path="chess_yolov8n.pt", board_size_px=800)

# Stockfish Pfad automatisch finden (Linux / Windows)
STOCKFISH_CANDIDATES = [
    "/usr/games/stockfish",
    "/usr/bin/stockfish",
    "/usr/local/bin/stockfish",
    "C:/stockfish/stockfish.exe",
]


def find_stockfish():
    """Sucht Stockfish: STOCKFISH_PATH, dann PATH, dann feste Kandidatenpfade.

    Gibt (Pfad oder None, Liste der durchsuchten Orte) zurück.
    """
    searched = []
    env_path = os.getenv("STOCKFISH_PATH")
    if env_path:
        searched.append(f"STOCKFISH_PATH={env_path}")
        if os.path.exists(env_path):
            return env_path, searched
    searched.append("PATH (shutil.which('stockfish'))")
    which_path = shutil.which("stockfish")
    if which_path:
        return which_path, searched
    for candidate in STOCKFISH_CANDIDATES:
        searched.append(candidate)
        if os.path.exists(candidate):
            return candidate, searched
    return None, searched


class EngineRequest(BaseModel):
    fen: str
    think_time_sec: float = 0.8
    multipv: int = 3


class PlayRequest(BaseModel):
    fen: str
    level: int = 3  # 1 (Anfänger) bis 5 (volle Stärke)


# Spielstärken für den KI-Gegner. UCI_Elo geht bei Stockfish erst ab 1320 los,
# darunter hilft nur "Skill Level" (0-20) plus kurze Bedenkzeit.
ENGINE_LEVELS = {
    1: {"label": "Anfänger", "options": {"Skill Level": 0}, "time": 0.05},
    2: {"label": "Leicht", "options": {"Skill Level": 4}, "time": 0.1},
    3: {"label": "Mittel", "options": {"UCI_LimitStrength": True, "UCI_Elo": 1500}, "time": 0.3},
    4: {"label": "Stark", "options": {"UCI_LimitStrength": True, "UCI_Elo": 2000}, "time": 0.5},
    5: {"label": "Profi", "options": {}, "time": 1.0},
}


class MoveRequest(BaseModel):
    fen: str
    from_sq: str
    to_sq: str
    promotion: str = "q"


def encode_image_base64(img: np.ndarray) -> str:
    _, buffer = cv2.imencode(".jpg", img, [int(cv2.IMWRITE_JPEG_QUALITY), 85])
    return "data:image/jpeg;base64," + base64.b64encode(buffer).decode("utf-8")


@app.post("/api/detect-corners")
async def api_detect_corners(file: UploadFile = File(...)):
    """Schritt 1: Nimmt das Kamerabild entgegen und liefert die 4 erkannten Brettecken."""
    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img is None:
        raise HTTPException(status_code=400, detail="Ungültiges Bildformat.")

    h, w = img.shape[:2]
    corners, auto_success = vision.detect_board_corners(img)

    # Normierte Koordinaten (0.0 bis 1.0) für einfaches Rendering auf jedem Smartphone-Screen
    normalized_corners = [[float(pt[0] / w), float(pt[1] / h)] for pt in corners]

    return {
        "auto_detected": auto_success,
        "image_width": w,
        "image_height": h,
        "corners_normalized": normalized_corners
    }


@app.post("/api/scan-board")
async def api_scan_board(
    file: UploadFile = File(...),
    corners_json: str = Form(...),
    active_color: str = Form("w")
):
    """
    Schritt 2: Nimmt das Bild und die (ggf. vom Nutzer verschobenen) 4 Ecken,
    entzerrt das Brett, führt die YOLO-Figurenerkennung aus und gibt den FEN-String zurück.
    """
    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img is None:
        raise HTTPException(status_code=400, detail="Bild konnte nicht gelesen werden.")

    h, w = img.shape[:2]
    norm_corners = json.loads(corners_json)
    src_corners = np.array([[pt[0] * w, pt[1] * h] for pt in norm_corners], dtype=np.float32)

    homography = vision.compute_homography(src_corners)
    warped_img = vision.warp_board(img, homography)

    # Gitterlinien zur visuellen Kontrolle in das entzerrte Bild einzeichnen
    debug_warped = warped_img.copy()
    step = int(vision.square_size_px)
    for i in range(1, 8):
        cv2.line(debug_warped, (i * step, 0), (i * step, 800), (0, 255, 0), 2)
        cv2.line(debug_warped, (0, i * step), (800, i * step), (0, 255, 0), 2)

    # Figurenerkennung ausführen
    pieces = vision.detect_pieces(img)
    if pieces:
        grid = vision.map_pieces_to_grid(pieces, homography)
        fen = vision.grid_to_fen(grid, active_color=active_color)
    else:
        # Falls noch kein YOLO-Modell im Ordner liegt: Startstellung als Basis laden
        fen = f"rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR {active_color} KQkq - 0 1"

    return {
        "fen": fen,
        "pieces_detected_count": len(pieces),
        "warped_image_b64": encode_image_base64(debug_warped)
    }


@app.post("/api/make-move")
async def api_make_move(req: MoveRequest):
    """Prüft und führt einen menschlichen Zug auf dem digitalen Brett aus."""
    try:
        board = chess.Board(req.fen)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Ungültige FEN-Stellung: {e}")

    uci_str = f"{req.from_sq}{req.to_sq}"
    move = chess.Move.from_uci(uci_str)
    promo_move = chess.Move.from_uci(uci_str + req.promotion)

    if promo_move in board.legal_moves:
        chosen = promo_move
    elif move in board.legal_moves:
        chosen = move
    else:
        return {"legal": False, "fen": req.fen, "message": "Illegaler Zug"}
    move_info = _move_fields(board, chosen)
    board.push(chosen)

    return {
        "legal": True,
        "move": move_info,
        "fen": board.fen(),
        "is_check": board.is_check(),
        "is_game_over": board.is_game_over(),
        "result": board.result() if board.is_game_over() else None
    }


def _require_stockfish() -> str:
    stockfish_path, searched = find_stockfish()
    if stockfish_path is None:
        raise HTTPException(
            status_code=500,
            detail="Stockfish wurde nicht gefunden. Gesucht in: "
                   + ", ".join(searched)
                   + ". Bitte installieren oder STOCKFISH_PATH setzen."
        )
    return stockfish_path


def _board_from_fen(fen: str) -> chess.Board:
    try:
        return chess.Board(fen)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Ungültiger FEN-String: {e}")


def _score_fields(score: chess.engine.PovScore) -> dict:
    white = score.white()
    mate = white.mate()
    cp = white.score(mate_score=100000)
    if mate is not None:
        eval_str = f"Matt in {abs(mate)}"
    else:
        eval_str = f"{(cp or 0) / 100.0:+.2f}"
    return {"eval_cp": cp, "mate": mate, "evaluation": eval_str}


def _move_fields(board: chess.Board, move: chess.Move) -> dict:
    return {
        "uci": move.uci(),
        "san": board.san(move),
        "from": chess.square_name(move.from_square),
        "to": chess.square_name(move.to_square),
        "piece": board.piece_at(move.from_square).symbol(),
        "capture": board.is_capture(move),
    }


def _game_over_fields(board: chess.Board) -> dict:
    return {
        "game_over": True,
        "fen": board.fen(),
        "best_move": None,
        "result": board.result(),
        "checkmate": board.is_checkmate(),
        "top_moves": [],
    }


@app.post("/api/engine-analyze")
async def api_engine_analyze(req: EngineRequest):
    """Fragt Stockfish nach den besten Zügen (MultiPV) und der Bewertung."""
    stockfish_path = _require_stockfish()
    board = _board_from_fen(req.fen)
    if not board.is_valid():
        raise HTTPException(status_code=400, detail="Diese Stellung ist nicht möglich (z.B. fehlt ein König).")

    if board.is_game_over():
        return _game_over_fields(board)

    multipv = max(1, min(5, req.multipv))
    try:
        with chess.engine.SimpleEngine.popen_uci(stockfish_path) as engine:
            infos = engine.analyse(board, chess.engine.Limit(time=req.think_time_sec), multipv=multipv)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Stockfish-Fehler: {str(e)}")
    if not isinstance(infos, list):
        infos = [infos]

    top_moves = []
    for rank, info in enumerate(infos, start=1):
        pv = info.get("pv") or []
        if not pv:
            continue
        top_moves.append({"rank": rank, **_move_fields(board, pv[0]), **_score_fields(info["score"])})

    best = top_moves[0] if top_moves else None
    board_after = board.copy()
    if best:
        board_after.push(chess.Move.from_uci(best["uci"]))

    return {
        "game_over": False,
        "best_move_uci": best["uci"] if best else None,
        "best_move_san": best["san"] if best else "",
        "from_sq": best["from"] if best else "",
        "to_sq": best["to"] if best else "",
        "evaluation": best["evaluation"] if best else "0.00",
        "eval_cp": best["eval_cp"] if best else 0,
        "mate": best["mate"] if best else None,
        "top_moves": top_moves,
        "fen_after_move": board_after.fen(),
    }


@app.post("/api/engine-play")
async def api_engine_play(req: PlayRequest):
    """Die KI zieht in der gewählten Spielstärke (1 = Anfänger bis 5 = Profi)."""
    stockfish_path = _require_stockfish()
    board = _board_from_fen(req.fen)
    if not board.is_valid():
        raise HTTPException(status_code=400, detail="Diese Stellung ist nicht möglich (z.B. fehlt ein König).")
    if board.is_game_over():
        return _game_over_fields(board)

    level = ENGINE_LEVELS.get(req.level, ENGINE_LEVELS[3])
    try:
        with chess.engine.SimpleEngine.popen_uci(stockfish_path) as engine:
            if level["options"]:
                engine.configure(level["options"])
            result = engine.play(board, chess.engine.Limit(time=level["time"]))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Stockfish-Fehler: {str(e)}")

    move_info = _move_fields(board, result.move)
    board.push(result.move)
    return {
        "game_over": False,
        "move": move_info,
        "level": req.level,
        "level_label": level["label"],
        "fen": board.fen(),
        "is_check": board.is_check(),
        "is_game_over": board.is_game_over(),
        "result": board.result() if board.is_game_over() else None,
    }


class FenRequest(BaseModel):
    fen: str


@app.post("/api/legal-moves")
async def api_legal_moves(req: FenRequest):
    """Alle legalen Züge der Stellung (UCI), für die Zielpunkte auf dem Brett."""
    board = _board_from_fen(req.fen)
    return {"moves": [m.uci() for m in board.legal_moves]}


@app.get("/api/engine-levels")
async def api_engine_levels():
    return [{"level": k, "label": v["label"]} for k, v in ENGINE_LEVELS.items()]


app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def index():
    return FileResponse("static/index.html")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend:app", host="0.0.0.0", port=8000, reload=True)
