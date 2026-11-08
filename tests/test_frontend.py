"""Browser-Ablauf gegen den echten Server (Playwright + Chromium).

Überspringt sich, wenn Playwright oder ein Chromium fehlt.
Ein vorhandenes Chromium lässt sich mit CHROMIUM_PATH=/pfad/zu/chrome angeben.
"""
import os
import socket
import subprocess
import sys
import time
import urllib.request

import pytest

sync_api = pytest.importorskip("playwright.sync_api")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture(scope="module")
def server_url():
    port = _free_port()
    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "backend:app", "--host", "127.0.0.1", "--port", str(port)],
        cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    url = f"http://127.0.0.1:{port}"
    for _ in range(100):
        try:
            urllib.request.urlopen(url, timeout=0.5)
            break
        except OSError:
            time.sleep(0.1)
    else:
        proc.kill()
        pytest.fail("Server startet nicht")
    yield url
    proc.terminate()
    proc.wait(timeout=10)


@pytest.fixture(scope="module")
def browser():
    with sync_api.sync_playwright() as p:
        try:
            # CHROMIUM_PATH erlaubt ein bereits installiertes Chromium anderer Revision
            exe = os.getenv("CHROMIUM_PATH")
            b = p.chromium.launch(executable_path=exe) if exe else p.chromium.launch()
        except Exception as e:  # kein passendes Chromium installiert
            pytest.skip(f"Chromium nicht startbar: {e}")
        yield b
        b.close()


@pytest.fixture
def page(browser, server_url):
    pg = browser.new_page()
    pg.goto(server_url)
    pg.wait_for_selector("#chessboard .square")
    yield pg
    pg.close()


def square(page, name):
    # Ungedrehtes Brett: Index = (8 - Reihe) * 8 + Linie
    c = ord(name[0]) - 97
    r = 8 - int(name[1])
    return page.locator("#chessboard .square").nth(r * 8 + c)


def move(page, uci):
    before = page.evaluate("currentFen")
    square(page, uci[:2]).click()
    square(page, uci[2:4]).click()
    page.wait_for_function("prev => currentFen !== prev", arg=before)
    return page.evaluate("currentFen")


def test_en_passant_and_counters_survive_moves(page):
    fen = move(page, "e2e4")
    # Das En-passant-Feld schreibt python-chess nur, wenn der Schlag legal ist
    assert fen.endswith(" b KQkq - 0 1")
    move(page, "a7a6")
    move(page, "e4e5")
    fen = move(page, "d7d5")
    assert fen.endswith(" w KQkq d6 0 3")
    assert page.locator("#fen-display").inner_text() == fen
    # Schlag en passant ist nur mit der vollständigen FEN legal
    fen = move(page, "e5d6")
    assert fen == "rnbqkbnr/1pp1pppp/p2P4/8/8/8/PPPP1PPP/RNBQKBNR b KQkq - 0 3"


def test_castling_rights_after_castle(page):
    for uci in ["e2e4", "e7e5", "g1f3", "b8c6", "f1c4", "f8c5"]:
        move(page, uci)
    fen = move(page, "e1g1")
    assert fen == "r1bqk1nr/pppp1ppp/2n5/2b1p3/2B1P3/5N2/PPPP1PPP/RNBQ1RK1 b kq - 5 4"


def test_turn_toggle_and_editor_rebuild_from_grid(page):
    for uci in ["e2e4", "a7a6", "e4e5", "d7d5"]:
        move(page, uci)
    # Farbe umschalten: En-passant verfällt, Rechte und Zähler bleiben
    page.click("#btn-turn")
    assert page.evaluate("currentFen").endswith(" b KQkq - 0 3")
    page.click("#btn-turn")
    # Editor: Turm h1 entfernen -> weißes Recht "K" fällt weg
    page.locator(".palette-btn", has_text="🗑️").click()
    square(page, "h1").click()
    assert page.evaluate("currentFen").split()[2] == "Qkq"
    # Turm zurücksetzen bringt das Recht nicht zurück
    page.locator(".palette-btn", has_text="♖").click()
    square(page, "h1").click()
    assert page.evaluate("currentFen").split()[2] == "Qkq"
