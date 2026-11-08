# ♟️ Brettfreunde (ChessVision Sim) – Projektdokumentation

Lokales Computer-Vision- und Schach-Simulationssystem (FastAPI + OpenCV + YOLOv8 + Stockfish) mit mobiler Android Web-App (PWA). Ermöglicht das Fotografieren eines echten Schachbretts, automatische Eckenerkennung & Perspektiventzerrung, Figurenerkennung sowie nahtloses Weiterspielen oder Zugtipps via Stockfish.

---

## 1. Systemarchitektur & Dateistruktur

```
ChessVision_Sim/
├── backend.py          # FastAPI Server, REST-Endpunkte, python-chess & Stockfish-Anbindung
├── games_store.py    # Gespeicherte Partien (JSON-Dateien in data/games/)
├── vision_engine.py    # OpenCV Auto-Corner-Detection, Homographie-Entzerrung, YOLO Fußpunkt-Mapping
├── chess_yolov8n.pt    # (Optional) Trainiertes YOLOv8-Gewichtsmodell für die 12 Figurenklassen
├── frontend/           # Web-App (Vite + Svelte 5 + Three.js), Quellcode
├── PRODUCT.md          # Produktkontext (Nutzer, Zweck, Grundsätze)
├── requirements.txt
├── requirements-dev.txt  # Test-Abhängigkeiten (pytest, httpx, playwright)
├── tests/              # pytest: API-Tests (TestClient) und Browser-Ablauf (Playwright)
└── static/             # Gebaute Web-App (erzeugt von `npm run build` in frontend/, nicht von Hand ändern)
```


---

## 2. Funktionsweise der Pipeline

### A. Automatische Brettecken-Erkennung (`detect_board_corners`)

1. **Vorverarbeitung:** Das Kamerabild wird in Graustufen konvertiert und mit einem kantenbewahrenden Bilateralfilter (`cv2.bilateralFilter`) entrauscht.  
2. **Kanten- & Konturextraktion:** Kombination aus adaptivem Gauß-Thresholding (`cv2.adaptiveThreshold`) und Canny-Edge-Detection (`cv2.Canny`), gefolgt von morphologischem Schließen (`cv2.MORPH_CLOSE`), um unterbrochene Außenlinien des Schachbretts zu verbinden.  
3. **Polygon-Approximation:** Die größten Konturen (15 % bis 98 % der Bildfläche) werden über `cv2.approxPolyDP` mit adaptiven Epsilon-Toleranzen auf ein konvexes Viereck geprüft. Falls ein Störelement die Kontur ausbeult, wird die konvexe Hülle (`cv2.convexHull`) bzw. die minimale rotierte Bounding Box (`cv2.minAreaRect`) als geometrischer Fallback herangezogen.  
4. **Punkt-Sortierung (`order_corner_points`):** Die 4 Ecken werden mathematisch über Koordinatensummen ($x+y$) und Differenzen ($y-x$) deterministisch in die Reihenfolge `[TL (a8), TR (h8), BR (h1), BL (a1)]` gebracht.

### B. Homographie & 3D-Fußpunkt-Projektion (`map_pieces_to_grid`)

* Aus den 4 Ecken (ggf. nach Feinjustierung per Touch im UI) wird mittels `cv2.getPerspectiveTransform` die $3 \times 3$ Homographie-Matrix $H$ für ein normiertes $800 \times 800\,\text{px}$ Zielbild ($100 \times 100\,\text{px}$ pro Schachfeld) berechnet.  
* **Lösung des 3D-Parallaxe-Problems:** Da echte Schachfiguren bei schrägem Kamerawinkel nach oben in benachbarte Felder ragen, wird **nicht** der Mittelpunkt der YOLO-Bounding-Box verwendet, sondern der **Standfuß der Figur**: $$x_{\text{foot}} = \frac{x_1 + x_2}{2}, \quad y_{\text{foot}} = y_1 + 0.85 \cdot (y_2 - y_1)$$  
* Dieser Punkt wird über `cv2.perspectiveTransform` mit $H$ in das entzerrte 2D-Koordinatensystem projiziert und eindeutig der Spalte (`col = int(wx // 100)`) und Reihe (`row = int(wy // 100)`) zugeordnet.

### C. Spiel- & Engine-Logik (`backend.py`)

* Das Frontend speichert die vollständige FEN aus `/api/make-move`, `/api/engine-analyze` und `/api/scan-board` (Rochaderechte, En-passant-Feld, Zugzähler) und schickt sie unverändert zurück. Nur nach Änderungen im Editor oder beim Umschalten der Farbe am Zug wird sie aus dem Brett neu aufgebaut: Rochaderechte bleiben nur, wenn König und Turm noch auf ihren Ausgangsfeldern stehen, das En-passant-Feld wird `-`, die Zugzähler bleiben. Beim Scan leitet `grid_to_fen` die Rochaderechte ebenso aus der Stellung ab.
* Nutzt `python-chess` zur Validierung legaler Züge, Schach-/Matt-Erkennung und FEN-Verwaltung.  
* Kommuniziert über das UCI-Protokoll (`chess.engine.SimpleEngine.popen_uci`) mit einer lokalen **Stockfish**-Instanz, liefert Stellungsbewertungen in Centipawns bzw. Matt-Zügen und berechnet entweder einen visuellen Tipp oder führt den besten KI-Zug direkt aus.

---

## 3. Installation & Setup (Linux / WSL2 / Raspberry Pi / Windows)

### 1. Abhängigkeiten installieren

```sh
pip install fastapi uvicorn python-multipart opencv-python-headless numpy chess ultralytics
```

### 2. Stockfish installieren

* **Ubuntu / Debian / WSL2 / Raspberry Pi:**

```sh
sudo apt update && sudo apt install stockfish -y
```

* **Windows:** Stockfish-Binary von `stockfishchess.org` herunterladen und den Pfad in der Umgebungsvariable `STOCKFISH_PATH` setzen (oder nach `C:/stockfish/stockfish.exe` legen).

Das Backend sucht Stockfish in dieser Reihenfolge: Umgebungsvariable `STOCKFISH_PATH`, `stockfish` im `PATH`, dann `/usr/games/stockfish`, `/usr/bin/stockfish`, `/usr/local/bin/stockfish`, `C:/stockfish/stockfish.exe`. Wird nichts gefunden, nennt die Fehlermeldung alle durchsuchten Orte.

### 3. Server starten

```sh
python backend.py
```

Der Server läuft standardmäßig auf `0.0.0.0:8000`.

### 4. Web-App bauen (nur nach Änderungen in `frontend/`)

Die gebaute App liegt fertig in `static/`, für den normalen Betrieb reicht `python backend.py`. Nach Änderungen am Frontend:

```sh
cd frontend
npm install
npm run build      # schreibt nach ../static
npm run dev        # Entwicklungsserver mit Live-Reload, leitet /api an Port 8000 weiter
```

Die App heißt **Brettfreunde**: Figuren sind Charaktere mit Namen und einem Satz, wie sie ziehen. Standard ist ein 3D-Brett (Three.js, mit dem Finger drehbar), daneben eine 2D-Ansicht für Editor und schnelles Korrigieren. Dazu Bewertungsbalken, Pfeile und Karten für die drei besten Züge, ein KI-Gegner in fünf Stufen (Anfänger bis Profi), Lichess-Export, FEN kopieren und ein Manifest für „Zum Startbildschirm hinzufügen“. Ein Service Worker fehlt bewusst: Ohne HTTPS im Heimnetz würde ihn Chrome nicht zulassen.

**Partien speichern:** Jede Partie wird nach jedem Zug automatisch auf dem Server gesichert, als JSON-Datei in `data/games/` (anderer Ort über die Umgebungsvariable `BRETT_DATA_DIR`). Beim Öffnen landet jedes Gerät in der zuletzt gespielten Partie: am Handy fotografieren, am PC oder Tablet weiterspielen. Im Bereich „Partien“ stehen der Name, die Zugliste in deutscher Notation, „Zug zurück“, „Neue Partie“ und alle anderen Partien mit Mini-Brett. Beim Speichern spielt der Server die Zugliste nach und lehnt Stände ab, die nicht zur gemeldeten Stellung passen. Spielen zwei Geräte gleichzeitig dieselbe Partie, gilt der zuletzt gespeicherte Stand. Nach einer Korrektur im Editor beginnt die Zugliste neu ab der korrigierten Stellung.

API-Endpunkte: `/api/games` (GET Liste, POST neu), `/api/games/{id}` (GET, PUT, DELETE), `/api/detect-corners`, `/api/scan-board`, `/api/make-move`, `/api/legal-moves`, `/api/engine-analyze` (Top-3 per MultiPV), `/api/engine-play` (Stufen 1–5; Stufe 1 und 2 über Stockfishs `Skill Level`, weil `UCI_Elo` erst bei 1320 beginnt), `/api/engine-levels`.

### 5. Tests

```sh
pip install -r requirements-dev.txt
pytest
```

Der Stockfish-Test wird übersprungen, wenn kein Stockfish gefunden wird; die Browser-Tests (`tests/test_frontend.py`), wenn Playwright oder Chromium fehlen. Ein bereits installiertes Chromium anderer Revision lässt sich mit `CHROMIUM_PATH=/pfad/zu/chrome pytest` verwenden, sonst `playwright install chromium`.

---

## 4. Nutzung auf dem Android-Smartphone

1. Verbinde dein Smartphone mit demselben WLAN wie der Server/PC.  
2. Öffne Chrome auf dem Smartphone und rufe `http://<IP-DES-SERVERS>:8000` auf (über das Chrome-Menü *„Zum Startbildschirm hinzufügen“* lässt sich die Web-App wie eine native App im Vollbild nutzen).  
3. **Ablauf im Spiel:**  
   * Tippe auf **„📷 Foto aufnehmen“** und fotografiere das echte Brett (Orientierung idealerweise aus Sicht von Weiß, sodass `a8` oben links liegt).  
   * Prüfe kurz die **4 grünen Eck-Pins** (lassen sich bei Bedarf per Finger verschieben) und tippe auf **„⚡ Brett entzerren & Scannen“**.  
   * Kontrolliere das 2D-Brett (über die Editor-Leiste unten lassen sich verdeckte Figuren mit einem Tap korrigieren oder das Brett drehen).  
   * Tippe auf **„💡 Tipp (Stockfish)“**, um den besten Zug blau markiert zu bekommen, oder auf **„🤖 KI-Zug ausführen“**, um die Partie direkt gegen die Engine fortzusetzen.

---

## 5. Eigenes YOLOv8-Modell einbinden / feintunen

### Fertiges Startmodell (Stand 2026-11-08)

`training/train_colab.py` trainiert `chess_yolov8n.pt` auf öffentlichen Datensätzen (beide CC-BY-4.0):

* [dopaul/chess-pieces-merged](https://huggingface.co/datasets/dopaul/chess-pieces-merged), nur die Bilder aus `chess_pieces_dominique`. Die Roboflow-Bilder darin haben keine Labels, bei den Formaten 960×1280 und 4032×3024 passen die Labels nicht zum Bild. Beides filtert das Skript heraus.
* [Francesco/chess-pieces-mjzgj](https://huggingface.co/datasets/Francesco/chess-pieces-mjzgj) (Roboflow „Chess Pieces“ aus RF100).

Ergebnis des ersten Laufs (422 Trainingsbilder, YOLOv8n, 640 px, Colab L4, etwa 5 Minuten): mAP50 0,98 auf Validierung und 0,97 auf Test, Details in `training/metrics.json`. Das Modell (6,5 MB) liegt wegen `*.pt` in `.gitignore` nicht im Repo. Neu erzeugen:

```sh
pip install ultralytics huggingface_hub pandas pillow
python training/train_colab.py --epochs 100 --data-dir ./dataset --out ./out
cp out/chess_yolov8n.pt .
```

Lokal reicht für die Erkennung PyTorch für die CPU (etwa 1 GB statt mehrerer GB mit CUDA):

```sh
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
pip install ultralytics
```

Die Datensätze zeigen andere Bretter als deines. Für zuverlässige Ergebnisse auf dem eigenen Brett das Modell wie unten beschrieben mit eigenen Fotos nachtrainieren. Die Ultralytics-Gewichte stehen unter AGPL-3.0.

**Bekannte Grenze der Eckenerkennung:** Bei Brettmatten mit breitem Rand findet `detect_board_corners` oft den Mattenrand statt der 8×8 Felder, das Gitter liegt dann versetzt. Die Pins im UI vor dem Scan auf die Ecken der Spielfelder schieben.

### Eigenes Brett

Sobald eine Datei `chess_yolov8n.pt` im Projektverzeichnis liegt, lädt `vision_engine.py` diese automatisch beim Start. Unterstützt werden alle Standard-Klassenbezeichnungen (`wP, wN, wB, wR, wQ, wK, bP, bN, bB, bR, bQ, bK` sowie `white-pawn`, `black-king` etc.).

Um ein Modell exakt auf dein eigenes Holz-/Kunststoffbrett zu trainieren:

1. 30–50 Fotos deines Bretts aus verschiedenen Winkeln aufnehmen.  
2. Auf Roboflow oder CVAT die 12 Figurenklassen labeln.  
3. Mit Ultralytics trainieren:

```sh
yolo detect train data=dataset.yaml model=yolov8n.pt epochs=80 imgsz=640
```

4. Die erzeugte `best.pt` als `chess_yolov8n.pt` in das Hauptverzeichnis kopieren.