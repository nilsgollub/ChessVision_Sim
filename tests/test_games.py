import os

from fastapi.testclient import TestClient

import backend

client = TestClient(backend.app)
START = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"


def test_data_dir_is_temporary():
    assert "brett-test-" in backend.games.dir


def test_create_save_load_list_delete():
    g = client.post("/api/games", json={"start_fen": START, "moves": [{"uci": "e2e4"}],
                                        "fen": "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1"}).json()
    assert g["name"].startswith("Partie vom ")
    assert g["moves"][0] == {"uci": "e2e4", "san": "e4", "piece": "P",
                             "fen": "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1"}
    saved = client.put(f"/api/games/{g['id']}", json={"name": "Sonntagspartie", "start_fen": START,
                                                      "moves": [{"uci": "e2e4"}, {"uci": "e7e5"}]}).json()
    assert saved["name"] == "Sonntagspartie" and saved["created"] == g["created"]
    assert client.get(f"/api/games/{g['id']}").json()["fen"].startswith("rnbqkbnr/pppp1ppp/8/4p3/4P3")
    summary = next(x for x in client.get("/api/games").json() if x["id"] == g["id"])
    assert summary["move_count"] == 2 and summary["turn"] == "w"
    # Name bleibt beim nächsten Speichern ohne Namen erhalten
    again = client.put(f"/api/games/{g['id']}", json={"start_fen": START, "moves": []}).json()
    assert again["name"] == "Sonntagspartie"
    assert client.delete(f"/api/games/{g['id']}").status_code == 200
    assert client.get(f"/api/games/{g['id']}").status_code == 404


def test_list_newest_first():
    a = client.post("/api/games", json={"name": "A", "start_fen": START}).json()
    b = client.post("/api/games", json={"name": "B", "start_fen": START}).json()
    ids = [x["id"] for x in client.get("/api/games").json()]
    assert ids.index(b["id"]) < ids.index(a["id"])


def test_rejects_illegal_moves_and_mismatching_fen():
    res = client.post("/api/games", json={"start_fen": START, "moves": [{"uci": "e2e5"}]})
    assert res.status_code == 400 and "nicht erlaubt" in res.json()["detail"]
    res = client.post("/api/games", json={"start_fen": START, "moves": [{"uci": "e2e4"}], "fen": START})
    assert res.status_code == 400
    res = client.post("/api/games", json={"start_fen": "kaputt"})
    assert res.status_code == 400


def test_scanned_start_position_with_black_to_move():
    fen = "r3k2r/8/8/8/8/8/8/R3K2R b KQkq - 0 1"
    g = client.post("/api/games", json={"start_fen": fen, "moves": [{"uci": "e8g8"}]}).json()
    assert g["fen"] == "r4rk1/8/8/8/8/8/8/R3K2R w KQ - 1 2"


def test_ids_cannot_escape_data_dir():
    for bad in ["..%2F..%2Fbackend", "UPPER12345", "a.json"]:
        assert client.get(f"/api/games/{bad}").status_code == 404
        assert client.delete(f"/api/games/{bad}").status_code == 404
    assert os.path.exists("backend.py")


def test_name_length_limited():
    res = client.post("/api/games", json={"name": "x" * 81, "start_fen": START})
    assert res.status_code == 422
