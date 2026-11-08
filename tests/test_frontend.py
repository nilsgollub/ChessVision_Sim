"""Browser-Ablauf gegen den echten Server (Playwright + Chromium).

Überspringt sich, wenn Playwright oder ein Chromium fehlt.
Ein vorhandenes Chromium lässt sich mit CHROMIUM_PATH=/pfad/zu/chrome angeben.
"""
import os
import shutil
import socket
import json
import subprocess
import tempfile
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
    env = {**os.environ, "BRETT_DATA_DIR": tempfile.mkdtemp(prefix="brett-ui-")}
    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "backend:app", "--host", "127.0.0.1", "--port", str(port)],
        cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, env=env,
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
            # CHROMIUM_PATH erlaubt ein bereits installiertes Chromium anderer Revision;
            # SwiftShader liefert WebGL für das 3D-Brett auch ohne GPU.
            exe = os.getenv("CHROMIUM_PATH")
            args = ["--use-angle=swiftshader", "--enable-unsafe-swiftshader"]
            b = p.chromium.launch(executable_path=exe, args=args) if exe else p.chromium.launch(args=args)
        except Exception as e:  # kein passendes Chromium installiert
            pytest.skip(f"Chromium nicht startbar: {e}")
        yield b
        b.close()


def clear_games(url):
    games = json.load(urllib.request.urlopen(f"{url}/api/games"))
    for g in games:
        urllib.request.urlopen(urllib.request.Request(f"{url}/api/games/{g['id']}", method="DELETE"))


@pytest.fixture
def page(browser, server_url):
    clear_games(server_url)  # jede Prüfung beginnt ohne gespeicherte Partie
    pg = browser.new_page(viewport={"width": 390, "height": 844})
    pg.goto(server_url)
    pg.click("[data-testid=view-2d]")
    pg.wait_for_selector("[data-square=e2]")
    yield pg
    pg.close()


def fen(page):
    return page.evaluate("window.brettfreunde.getFen()")


def move(page, uci):
    before = fen(page)
    page.click(f"[data-square={uci[:2]}]")
    page.click(f"[data-square={uci[2:4]}]")
    page.wait_for_function("prev => window.brettfreunde.getFen() !== prev", arg=before)
    return fen(page)


def test_en_passant_and_counters_survive_moves(page):
    f = move(page, "e2e4")
    # Das En-passant-Feld schreibt python-chess nur, wenn der Schlag legal ist
    assert f.endswith(" b KQkq - 0 1")
    move(page, "a7a6")
    move(page, "e4e5")
    f = move(page, "d7d5")
    assert f.endswith(" w KQkq d6 0 3")
    # Schlag en passant ist nur mit der vollständigen FEN legal
    f = move(page, "e5d6")
    assert f == "rnbqkbnr/1pp1pppp/p2P4/8/8/8/PPPP1PPP/RNBQKBNR b KQkq - 0 3"


def test_castling_rights_after_castle(page):
    for uci in ["e2e4", "e7e5", "g1f3", "b8c6", "f1c4", "f8c5"]:
        move(page, uci)
    f = move(page, "e1g1")
    assert f == "r1bqk1nr/pppp1ppp/2n5/2b1p3/2B1P3/5N2/PPPP1PPP/RNBQ1RK1 b kq - 5 4"


def test_selecting_piece_shows_name_plate_and_targets(page):
    page.click("[data-square=g1]")
    assert "Fritzi" in page.inner_text(".plate")
    page.wait_for_selector("[data-square=f3] .target-dot")
    assert page.locator(".target-dot").count() == 2


def test_turn_toggle_and_editor_rebuild_from_grid(page):
    for uci in ["e2e4", "a7a6", "e4e5", "d7d5"]:
        move(page, uci)
    page.click("[data-tab=korrigieren]")
    # Farbe umschalten: En passant verfällt, Rechte und Zähler bleiben
    page.click("[data-testid=turn-b]")
    assert fen(page).endswith(" b KQkq - 0 3")
    page.click("[data-testid=turn-w]")
    # Editor: Turm h1 entfernen -> weißes Recht "K" fällt weg
    page.click("text=Feld leeren")
    page.click("[data-square=h1]")
    assert fen(page).split()[2] == "Qkq"
    # Turm zurücksetzen bringt das Recht nicht zurück
    page.click("[aria-label='Weißer Turm']")
    page.click("[data-square=h1]")
    assert fen(page).split()[2] == "Qkq"


def wait_saved(page):
    page.wait_for_function("window.brettfreunde.game.saveState === 'saved'")


def test_game_continues_on_second_device(page, browser, server_url):
    move(page, "e2e4")
    move(page, "e7e5")
    wait_saved(page)
    # Zweites Gerät (Tablet) öffnet die App und landet in derselben Partie
    tablet = browser.new_page(viewport={"width": 1024, "height": 768})
    tablet.goto(server_url)
    tablet.wait_for_function("window.brettfreunde.getFen().startsWith('rnbqkbnr/pppp1ppp/8/4p3/4P3')")
    tablet.click("[data-tab=partien]")
    assert "1." in tablet.inner_text("ol.moves") and "e5" in tablet.inner_text("ol.moves")
    # Dort weiterspielen, das Handy sieht den Stand nach dem Öffnen der Liste
    tablet.click("[data-tab=spielen]")
    tablet.click("[data-testid=view-2d]")
    move(tablet, "g1f3")
    wait_saved(tablet)
    tablet.close()
    page.reload()
    page.wait_for_function("window.brettfreunde.getFen().includes('5N2')")


def test_undo_and_switching_games(page, server_url):
    move(page, "d2d4")
    move(page, "d7d5")
    page.click("text=Zug zurück")
    assert fen(page) == "rnbqkbnr/pppppppp/8/8/3P4/8/PPP1PPPP/RNBQKBNR b KQkq - 0 1"
    wait_saved(page)
    page.click("[data-tab=partien]")
    page.fill(".name input", "Papa gegen Lea")
    page.press(".name input", "Enter")
    wait_saved(page)
    page.click("text=Neue Partie")
    move(page, "c2c4")
    wait_saved(page)
    page.click("[data-tab=partien]")
    page.wait_for_selector("text=Papa gegen Lea")
    page.click("[aria-label='Papa gegen Lea weiterspielen']")
    page.wait_for_function("window.brettfreunde.getFen().startsWith('rnbqkbnr/pppppppp/8/8/3P4')")


def test_capture_animation_in_2d_including_en_passant(page):
    for uci in ["e2e4", "d7d5"]:
        move(page, uci)
    move(page, "e4d5")
    ko = page.locator("svg.board .knockout")
    assert ko.count() == 1 and ko.locator(".bit").count() == 12
    assert page.evaluate("window.brettfreunde.game.fx.capturedSq") == "d5"
    # en passant: geschlagener Bauer steht neben dem Zielfeld
    page.evaluate("window.brettfreunde.game.newGame('rnbqkbnr/pp1p1ppp/8/2pPp3/8/8/PPP2PPP/RNBQKBNR w KQkq e6 0 4')")
    move(page, "d5e6")
    fx = page.evaluate("window.brettfreunde.game.fx")
    assert fx["capturedSq"] == "e5" and fx["captured"] == "p"
    # Normale Züge ohne Schlag: kein Effekt
    move(page, "a7a6")
    assert page.evaluate("window.brettfreunde.game.fx.captured") == ""


def test_capture_animation_in_3d(browser, server_url):
    clear_games(server_url)
    pg = browser.new_page(viewport={"width": 390, "height": 844})
    pg.goto(server_url)
    try:
        pg.wait_for_function("window.brett3d !== undefined", timeout=5000)
    except Exception:
        pytest.skip("kein WebGL in diesem Browser")
    pg.evaluate("window.brettfreunde.game.newGame('rnbqkbnr/ppp1pppp/8/3p4/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2')")
    pg.evaluate("window.brett3d.setSlowMotion(10)")
    pg.evaluate("window.brettfreunde.game.move('e4', 'd5')")
    pg.wait_for_function("window.brett3d.runningAnimations() >= 3")  # Zug, Umfallen, Zuckerperlen
    pg.evaluate("window.brett3d.setSlowMotion(1)")
    pg.wait_for_function("window.brett3d.runningAnimations() === 0", timeout=20000)
    pg.close()


@pytest.mark.parametrize("size", [(844, 390), (740, 360)])
def test_phone_landscape_layout(browser, server_url, size):
    clear_games(server_url)
    w, h = size
    pg = browser.new_page(viewport={"width": w, "height": h})
    pg.goto(server_url)
    pg.click("[data-testid=view-2d]")
    pg.wait_for_selector("[data-square=a1]")
    board = pg.locator(".board-frame").bounding_box()
    assert board["y"] >= 0 and board["y"] + board["height"] <= h + 1, "Brett muss ganz sichtbar sein"
    assert abs(board["width"] - board["height"]) < 2
    # Nichts in der Bedienspalte ragt über den Bildschirm hinaus, Knöpfe sind erreichbar
    overflow = pg.evaluate("""() => [...document.querySelectorAll('.side *')]
        .filter(el => el.getBoundingClientRect().right > innerWidth + 1).length""")
    assert overflow == 0
    pg.click("text=Tipp holen")
    pg.close()


def test_three_d_board_moves_by_tap(browser, server_url):
    clear_games(server_url)
    pg = browser.new_page(viewport={"width": 390, "height": 844})
    pg.goto(server_url)
    try:
        pg.wait_for_function("window.brett3d !== undefined", timeout=5000)
    except Exception:
        pytest.skip("kein WebGL in diesem Browser")
    pg.wait_for_timeout(500)
    for sq in ("e2", "e4"):
        pt = pg.evaluate(f"window.brett3d.squareToScreen('{sq}')")
        pg.mouse.click(pt["x"], pt["y"])
        pg.wait_for_timeout(300)
    pg.wait_for_function("window.brettfreunde.getFen().startsWith('rnbqkbnr/pppppppp/8/8/4P3')")
    pg.close()


@pytest.mark.skipif(shutil.which("stockfish") is None and not os.path.exists("/usr/games/stockfish"),
                    reason="Stockfish nicht installiert")
def test_hint_shows_three_ranked_moves_and_ai_plays(page):
    page.click("text=Tipp holen")
    page.wait_for_selector("ol.ranks li >> nth=2")
    assert page.locator("ol.ranks li").count() == 3
    assert page.locator("svg.board .arrows path").count() == 6
    before = fen(page)
    page.click("text=KI zieht")
    page.wait_for_function("prev => window.brettfreunde.getFen() !== prev", arg=before)
    assert fen(page).split()[1] == "b"
