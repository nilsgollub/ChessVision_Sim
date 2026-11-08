"""Gespeicherte Partien: eine JSON-Datei je Partie im Datenordner.

Kein Konto, keine Datenbank: alle Geräte im Heimnetz sehen dieselben Partien.
Die Zugliste wird beim Speichern von der Startstellung aus nachgespielt und
muss genau bei der gemeldeten Stellung ankommen; so kann ein Gerät keinen
kaputten Stand ablegen. Gleichzeitiges Speichern: der letzte Stand gewinnt.
"""
import json
import os
import re
import secrets
import tempfile
import time
from typing import List, Optional

import chess
from pydantic import BaseModel, Field

ID_RE = re.compile(r"^[a-z0-9]{8,32}$")


class StoredMove(BaseModel):
    uci: str
    san: str = ""
    piece: str = ""


class GameIn(BaseModel):
    name: Optional[str] = Field(default=None, max_length=80)
    start_fen: str = chess.STARTING_FEN
    moves: List[StoredMove] = []
    fen: Optional[str] = None


class GameStore:
    def __init__(self, directory: str):
        self.dir = directory
        os.makedirs(self.dir, exist_ok=True)

    def _path(self, game_id: str) -> str:
        if not ID_RE.match(game_id):
            raise KeyError(game_id)
        return os.path.join(self.dir, f"{game_id}.json")

    @staticmethod
    def replay(start_fen: str, moves: List[StoredMove]) -> tuple[chess.Board, List[dict]]:
        """Spielt die Züge nach. Wirft ValueError bei ungültiger Stellung oder illegalem Zug."""
        board = chess.Board(start_fen)
        out = []
        for i, m in enumerate(moves):
            try:
                move = chess.Move.from_uci(m.uci)
            except ValueError:
                raise ValueError(f"Zug {i + 1} ist kein gültiger Zug: {m.uci}")
            if move not in board.legal_moves:
                raise ValueError(f"Zug {i + 1} ({m.uci}) ist in dieser Stellung nicht erlaubt")
            piece = board.piece_at(move.from_square)
            entry = {"uci": move.uci(), "san": board.san(move), "piece": piece.symbol() if piece else ""}
            board.push(move)
            entry["fen"] = board.fen()
            out.append(entry)
        return board, out

    def _summary(self, g: dict) -> dict:
        board = chess.Board(g["fen"])
        return {
            "id": g["id"], "name": g["name"], "fen": g["fen"], "updated": g["updated"], "created": g["created"],
            "move_count": len(g["moves"]), "turn": "w" if board.turn else "b",
            "result": board.result() if board.is_game_over() else None,
        }

    def _write(self, g: dict) -> None:
        fd, tmp = tempfile.mkstemp(dir=self.dir, suffix=".tmp")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(g, f, ensure_ascii=False, indent=1)
        os.replace(tmp, self._path(g["id"]))

    def _build(self, data: GameIn, base: Optional[dict] = None) -> dict:
        board, moves = self.replay(data.start_fen, data.moves)
        if data.fen is not None and board.fen() != chess.Board(data.fen).fen():
            raise ValueError("Zugliste und Stellung passen nicht zusammen")
        now = time.time()
        name = (data.name or "").strip() or (base or {}).get("name") or time.strftime("Partie vom %d.%m., %H:%M", time.localtime(now))
        return {
            "id": (base or {}).get("id") or secrets.token_hex(6),
            "name": name,
            "created": (base or {}).get("created", now),
            "updated": now,
            "start_fen": chess.Board(data.start_fen).fen(),
            "moves": moves,
            "fen": board.fen(),
        }

    def list(self) -> List[dict]:
        games = []
        for fn in os.listdir(self.dir):
            if fn.endswith(".json"):
                try:
                    with open(os.path.join(self.dir, fn), encoding="utf-8") as f:
                        games.append(self._summary(json.load(f)))
                except (OSError, ValueError, KeyError):
                    continue  # kaputte Datei überspringen statt die ganze Liste zu verlieren
        return sorted(games, key=lambda g: g["updated"], reverse=True)

    def get(self, game_id: str) -> dict:
        try:
            with open(self._path(game_id), encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            raise KeyError(game_id)

    def create(self, data: GameIn) -> dict:
        g = self._build(data)
        self._write(g)
        return g

    def save(self, game_id: str, data: GameIn) -> dict:
        g = self._build(data, self.get(game_id))
        self._write(g)
        return g

    def delete(self, game_id: str) -> None:
        try:
            os.remove(self._path(game_id))
        except FileNotFoundError:
            raise KeyError(game_id)
