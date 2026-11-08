import os
import cv2
import numpy as np
from dataclasses import dataclass
from typing import List, Tuple, Optional

try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False


@dataclass
class DetectedPiece:
    label: str  # 'P', 'N', 'B', 'R', 'Q', 'K', 'p', 'n', 'b', 'r', 'q', 'k'
    bbox: Tuple[float, float, float, float]  # (x1, y1, x2, y2) im Originalbild
    confidence: float


# Mapping von gängigen YOLO-Schach-Datensätzen (Roboflow/Ultralytics) auf FEN-Zeichen
CLASS_TO_FEN = {
    "white-pawn": "P", "white-knight": "N", "white-bishop": "B",
    "white-rook": "R", "white-queen": "Q", "white-king": "K",
    "black-pawn": "p", "black-knight": "n", "black-bishop": "b",
    "black-rook": "r", "black-queen": "q", "black-king": "k",
    "wP": "P", "wN": "N", "wB": "B", "wR": "R", "wQ": "Q", "wK": "K",
    "bP": "p", "bN": "n", "bB": "b", "bR": "r", "bQ": "q", "bK": "k",
    "P": "P", "N": "N", "B": "B", "R": "R", "Q": "Q", "K": "K",
    "p": "p", "n": "n", "b": "b", "r": "r", "q": "q", "k": "k"
}


def castling_from_grid(grid: List[List[str]]) -> str:
    """Rochaderechte nur, wenn König und Turm auf ihren Ausgangsfeldern stehen.

    grid[0] ist die 8. Reihe, grid[7] die 1. Reihe; Spalte 0 = a, 7 = h.
    """
    rights = ""
    if grid[7][4] == "K":
        if grid[7][7] == "R":
            rights += "K"
        if grid[7][0] == "R":
            rights += "Q"
    if grid[0][4] == "k":
        if grid[0][7] == "r":
            rights += "k"
        if grid[0][0] == "r":
            rights += "q"
    return rights or "-"


class ChessVisionEngine:
    def __init__(self, model_path: str = "chess_yolov8n.pt", board_size_px: int = 800):
        self.board_size_px = board_size_px
        self.square_size_px = board_size_px / 8.0
        self.dst_corners = np.array([
            [0, 0],
            [board_size_px, 0],
            [board_size_px, board_size_px],
            [0, board_size_px]
        ], dtype=np.float32)

        self.model = None
        if YOLO_AVAILABLE and os.path.exists(model_path):
            self.model = YOLO(model_path)
            print(f"[INFO] YOLO-Modell geladen: {model_path}")
        else:
            print(f"[WARNUNG] Kein YOLO-Modell unter '{model_path}' gefunden. "
                  f"Eckenerkennung & Entzerrung aktiv, Figurenerkennung im Fallback-Modus.")

    @staticmethod
    def order_corner_points(pts: np.ndarray) -> np.ndarray:
        """
        Sortiert 4 Punkte zuverlässig in die Reihenfolge:
        [Oben-Links (TL), Oben-Rechts (TR), Unten-Rechts (BR), Unten-Links (BL)]
        """
        rect = np.zeros((4, 2), dtype=np.float32)
        s = pts.sum(axis=1)
        rect[0] = pts[np.argmin(s)]  # TL hat kleinste Summe (x + y)
        rect[2] = pts[np.argmax(s)]  # BR hat größte Summe (x + y)

        diff = np.diff(pts, axis=1)
        rect[1] = pts[np.argmin(diff)]  # TR hat kleinste Differenz (y - x)
        rect[3] = pts[np.argmax(diff)]  # BL hat größte Differenz (y - x)
        return rect

    def detect_board_corners(self, image: np.ndarray) -> Tuple[np.ndarray, bool]:
        """
        Automatische Erkennung der 4 äußeren Schachbrettecken.
        Nutzt mehrstufiges Kontur-Filtering + Minimum-Area-Bounding-Box als Fallback.
        Gibt (4x2 Array der Ecken, Erfolg_Bool) zurück.
        """
        h, w = image.shape[:2]
        img_area = float(h * w)

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.bilateralFilter(gray, 9, 75, 75)

        # Kombination aus adaptivem Thresholding und Canny für maximale Robustheit
        thresh = cv2.adaptiveThreshold(
            blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 15, 3
        )
        edges = cv2.Canny(blurred, 50, 150)
        combined = cv2.bitwise_or(thresh, edges)

        # Lücken in den Außenlinien schließen
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        closed = cv2.morphologyEx(combined, cv2.MORPH_CLOSE, kernel, iterations=2)

        contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours = sorted(contours, key=cv2.contourArea, reverse=True)

        for cnt in contours[:10]:
            area = cv2.contourArea(cnt)
            # Das Brett sollte mindestens 15% und maximal 98% des Bildes einnehmen
            if area < 0.15 * img_area or area > 0.98 * img_area:
                continue

            peri = cv2.arcLength(cnt, True)
            # Versuche verschiedene Epsilon-Toleranzen für die Polygon-Approximation
            for eps_factor in [0.02, 0.03, 0.04, 0.05]:
                approx = cv2.approxPolyDP(cnt, eps_factor * peri, True)
                if len(approx) == 4 and cv2.isContourConvex(approx):
                    pts = approx.reshape(4, 2).astype(np.float32)
                    return self.order_corner_points(pts), True

        # Zweite Stufe: Konvexe Hülle der größten Kontur in ein 4-Eck zwingen
        if contours and cv2.contourArea(contours[0]) > 0.15 * img_area:
            hull = cv2.convexHull(contours[0])
            peri = cv2.arcLength(hull, True)
            approx = cv2.approxPolyDP(hull, 0.04 * peri, True)
            if len(approx) == 4:
                pts = approx.reshape(4, 2).astype(np.float32)
                return self.order_corner_points(pts), True

            # Letzter geometrischer Fallback: Rotated Minimum Area Box
            rect = cv2.minAreaRect(hull)
            box = cv2.boxPoints(rect)
            return self.order_corner_points(box.astype(np.float32)), False

        # Standard-Fallback (zentriertes Quadrat mit 15% Rand), falls gar nichts erkannt wurde
        pad_x, pad_y = int(w * 0.15), int(h * 0.15)
        default_pts = np.array([
            [pad_x, pad_y],
            [w - pad_x, pad_y],
            [w - pad_x, h - pad_y],
            [pad_x, h - pad_y]
        ], dtype=np.float32)
        return default_pts, False

    def compute_homography(self, src_corners: np.ndarray) -> np.ndarray:
        ordered = self.order_corner_points(src_corners.astype(np.float32))
        return cv2.getPerspectiveTransform(ordered, self.dst_corners)

    def warp_board(self, image: np.ndarray, homography: np.ndarray) -> np.ndarray:
        return cv2.warpPerspective(image, homography, (self.board_size_px, self.board_size_px))

    def detect_pieces(self, image: np.ndarray, conf_threshold: float = 0.35) -> List[DetectedPiece]:
        if self.model is None:
            return []

        results = self.model.predict(image, conf=conf_threshold, verbose=False)
        detected: List[DetectedPiece] = []

        for r in results:
            names = r.names
            for box in r.boxes:
                cls_id = int(box.cls[0].item())
                raw_name = names.get(cls_id, "")
                if raw_name in CLASS_TO_FEN:
                    fen_char = CLASS_TO_FEN[raw_name]
                    x1, y1, x2, y2 = box.xyxy[0].tolist()
                    conf = float(box.conf[0].item())
                    detected.append(DetectedPiece(label=fen_char, bbox=(x1, y1, x2, y2), confidence=conf))

        return detected

    def map_pieces_to_grid(self, pieces: List[DetectedPiece], homography: np.ndarray) -> List[List[str]]:
        grid = [["" for _ in range(8)] for _ in range(8)]
        conf_grid = [[0.0 for _ in range(8)] for _ in range(8)]

        for p in pieces:
            x1, y1, x2, y2 = p.bbox
            # Fußpunkt: Horizontal mittig, vertikal bei 85% der Boxhöhe (Standfuß)
            foot_x = (x1 + x2) / 2.0
            foot_y = y1 + 0.85 * (y2 - y1)

            pt = np.array([[[foot_x, foot_y]]], dtype=np.float32)
            warped_pt = cv2.perspectiveTransform(pt, homography)[0][0]
            wx, wy = warped_pt[0], warped_pt[1]

            if 0 <= wx < self.board_size_px and 0 <= wy < self.board_size_px:
                col = int(wx // self.square_size_px)
                row = int(wy // self.square_size_px)
                if p.confidence > conf_grid[row][col]:
                    grid[row][col] = p.label
                    conf_grid[row][col] = p.confidence

        return grid

    @staticmethod
    def grid_to_fen(grid: List[List[str]], active_color: str = "w") -> str:
        fen_rows = []
        for row in grid:
            empty = 0
            row_str = ""
            for cell in row:
                if cell == "":
                    empty += 1
                else:
                    if empty > 0:
                        row_str += str(empty)
                        empty = 0
                    row_str += cell
            if empty > 0:
                row_str += str(empty)
            fen_rows.append(row_str)
        return f"{'/'.join(fen_rows)} {active_color} {castling_from_grid(grid)} - 0 1"
