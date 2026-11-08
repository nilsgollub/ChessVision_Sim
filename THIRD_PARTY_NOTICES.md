# Third-party notices

Brettfreunde (ChessVision Sim) is licensed under the GNU Affero General Public License v3.0, see [LICENSE](LICENSE).
It builds on the following third-party work.

## Bundled with the web app (`static/`) and the Android app (`app/www/`)

| Component | License | Notes |
|---|---|---|
| [Fredoka](https://github.com/hafontia/Fredoka-One) font, via Fontsource | SIL OFL 1.1 | Copyright 2016 The Fredoka Project Authors. Full text: [licenses/OFL-Fredoka.txt](licenses/OFL-Fredoka.txt) |
| [Nunito](https://github.com/googlefonts/nunito) font, via Fontsource | SIL OFL 1.1 | Copyright 2014 The Nunito Project Authors. Full text: [licenses/OFL-Nunito.txt](licenses/OFL-Nunito.txt) |
| [three.js](https://threejs.org) | MIT | 3D board |
| [Svelte](https://svelte.dev) | MIT | UI framework |
| [Capacitor](https://capacitorjs.com) | MIT | Android shell |

## Python backend (installed via `requirements.txt`, not bundled)

| Component | License |
|---|---|
| [python-chess](https://github.com/niklasf/python-chess) | GPL-3.0-or-later |
| [Ultralytics YOLO](https://github.com/ultralytics/ultralytics) (optional, piece detection) | AGPL-3.0 |
| [FastAPI](https://fastapi.tiangolo.com), [Uvicorn](https://www.uvicorn.org) | MIT / BSD-3-Clause |
| [OpenCV](https://opencv.org) (`opencv-python-headless`) | Apache-2.0 |
| [NumPy](https://numpy.org) | BSD-3-Clause |
| [Stockfish](https://stockfishchess.org) (separate program, called via UCI) | GPL-3.0 |

## Training data for the piece detector (`training/train_colab.py`)

The trained weights (`chess_yolov8n.pt`) are not part of this repository. The training script downloads:

- [dopaul/chess-pieces-merged](https://huggingface.co/datasets/dopaul/chess-pieces-merged), only the `chess_pieces_dominique` images, CC BY 4.0
- [Francesco/chess-pieces-mjzgj](https://huggingface.co/datasets/Francesco/chess-pieces-mjzgj) (Roboflow "Chess Pieces", part of RF100), CC BY 4.0

The scan screenshot in `docs/screenshots/` uses a photo from the `chess_pieces_dominique` set (CC BY 4.0).

## Original artwork

The chess piece characters (`frontend/src/lib/pieceArt.ts`), icons and app icons are original to this project and covered by its license.
