import pytest
from fastapi.testclient import TestClient

import backend
from vision_engine import ChessVisionEngine

client = TestClient(backend.app)

START = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"


# --- Stockfish-Suche ---------------------------------------------------------

def test_find_stockfish_prefers_env(monkeypatch, tmp_path):
    exe = tmp_path / "sf"
    exe.write_text("")
    monkeypatch.setenv("STOCKFISH_PATH", str(exe))
    monkeypatch.setattr(backend.shutil, "which", lambda name: "/should/not/be/used")
    assert backend.find_stockfish()[0] == str(exe)


def test_find_stockfish_uses_which(monkeypatch):
    monkeypatch.delenv("STOCKFISH_PATH", raising=False)
    monkeypatch.setattr(backend.shutil, "which", lambda name: "/opt/bin/stockfish")
    assert backend.find_stockfish()[0] == "/opt/bin/stockfish"


def test_find_stockfish_checks_candidates_in_order(monkeypatch, tmp_path):
    second = tmp_path / "stockfish.exe"
    second.write_text("")
    monkeypatch.delenv("STOCKFISH_PATH", raising=False)
    monkeypatch.setattr(backend.shutil, "which", lambda name: None)
    monkeypatch.setattr(backend, "STOCKFISH_CANDIDATES",
                        [str(tmp_path / "missing"), str(second)])
    path, searched = backend.find_stockfish()
    assert path == str(second)
    assert str(tmp_path / "missing") in searched


def test_engine_error_names_searched_locations(monkeypatch):
    monkeypatch.setenv("STOCKFISH_PATH", "/nope/stockfish")
    monkeypatch.setattr(backend.shutil, "which", lambda name: None)
    monkeypatch.setattr(backend, "STOCKFISH_CANDIDATES", ["/also/missing", "C:/stockfish/stockfish.exe"])
    res = client.post("/api/engine-analyze", json={"fen": START})
    assert res.status_code == 500
    detail = res.json()["detail"]
    for loc in ["/nope/stockfish", "PATH", "/also/missing", "C:/stockfish/stockfish.exe"]:
        assert loc in detail


# --- make-move: vollständige FEN ---------------------------------------------

def play(fen, *moves):
    for uci in moves:
        res = client.post("/api/make-move", json={"fen": fen, "from_sq": uci[:2], "to_sq": uci[2:4]})
        data = res.json()
        assert data["legal"], (fen, uci)
        fen = data["fen"]
    return fen


def test_make_move_keeps_counters_and_en_passant():
    fen = play(START, "e2e4")
    # python-chess schreibt das En-passant-Feld nur, wenn der Schlag legal ist
    assert fen.endswith(" b KQkq - 0 1")
    fen = play(fen, "a7a6", "e4e5", "d7d5")
    assert fen.endswith(" w KQkq d6 0 3")
    fen = play(fen, "e5d6")  # en passant nur mit korrekter FEN legal
    assert fen.split()[0] == "rnbqkbnr/1pp1pppp/p2P4/8/8/8/PPPP1PPP/RNBQKBNR"


def test_make_move_castling_updates_rights():
    fen = play(START, "e2e4", "e7e5", "g1f3", "b8c6", "f1c4", "f8c5", "e1g1")
    assert fen.split()[2] == "kq"
    assert fen.endswith(" b kq - 5 4")


# --- engine-analyze ------------------------------------------------------------

@pytest.mark.skipif(backend.find_stockfish()[0] is None, reason="Stockfish nicht installiert")
def test_engine_analyze_returns_full_fen():
    fen = "r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 4 20"
    res = client.post("/api/engine-analyze", json={"fen": fen, "think_time_sec": 0.1})
    assert res.status_code == 200, res.text
    data = res.json()
    assert data["best_move_uci"]
    parts = data["fen_after_move"].split()
    assert parts[1] == "b"
    assert parts[5] == "20"


# --- grid_to_fen ---------------------------------------------------------------

def grid_from_placement(placement):
    grid = []
    for row in placement.split("/"):
        cells = []
        for ch in row:
            cells.extend([""] * int(ch) if ch.isdigit() else [ch])
        grid.append(cells)
    return grid


@pytest.mark.parametrize("placement,rights", [
    ("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR", "KQkq"),
    ("r3k3/8/8/8/8/8/8/4K2R", "Kq"),
    ("4k2r/8/8/8/8/8/8/R4K1R", "k"),
    ("8/8/8/4k3/8/8/8/4K3", "-"),
])
def test_grid_to_fen_castling(placement, rights):
    fen = ChessVisionEngine.grid_to_fen(grid_from_placement(placement), active_color="b")
    assert fen == f"{placement} b {rights} - 0 1"


def test_scan_board_without_model_returns_start_position():
    import cv2
    import numpy as np
    _, img = cv2.imencode(".jpg", np.zeros((100, 100, 3), dtype=np.uint8))
    res = client.post(
        "/api/scan-board",
        files={"file": ("b.jpg", img.tobytes(), "image/jpeg")},
        data={"corners_json": "[[0,0],[1,0],[1,1],[0,1]]", "active_color": "w"},
    )
    assert res.status_code == 200
    assert res.json()["fen"] == START
