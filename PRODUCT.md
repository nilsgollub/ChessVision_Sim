# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Stack

Vite mit Framework (vom Nutzer gewählt am 2026-11-08). Framework delegiert: Svelte 5 mit TypeScript, weil es kleine Bundles für ältere Android-Handys liefert und gut neben einer imperativen Three.js-Szene läuft. Backend bleibt FastAPI (`backend.py`), das das gebaute Frontend ausliefert. Selbst gehostet im Heimnetz; Laufzeit-Abhängigkeiten werden lokal mitgeliefert, kein CDN.

## Users

Familie mit Kindern. Am echten Schachbrett zu Hause: eine Stellung fotografieren, auf dem Handy prüfen und korrigieren, dann gegen die KI weiterspielen, sich Tipps zeigen lassen oder zusammen eine Stellung verstehen. Kinder spielen mit, Erwachsene helfen beim Scannen und Korrigieren.

## Product Purpose

Brücke zwischen echtem Brett und Engine: Foto rein, Stellung raus, weiterspielen oder lernen. Erfolg heißt, dass eine Stellung vom Foto bis zum ersten Tipp in unter einer Minute auf dem Handy steht und ein Kind die Tipps versteht.

## Positioning

Selbst gehostet, ohne Konto und ohne Cloud: Foto, Figurenerkennung (eigenes YOLO-Modell) und Stockfish laufen auf dem eigenen Server im Heimnetz.

## Operating Context

- Android-Handy im Hochformat, Chrome, als Startbildschirm-App installiert, im Heim-WLAN oder über Tailscale.
- Ablauf: Brett fotografieren → 4 Ecken prüfen/verschieben → Scan → Stellung korrigieren (Editor) → Farbe am Zug wählen → Tipp (Top-3-Züge) oder gegen die KI spielen (Spielstärke wählbar).
- Ausgang zu Lichess (Analysebrett) und FEN kopieren.

## Capabilities and Constraints

- Backend-Endpunkte: `/api/detect-corners`, `/api/scan-board`, `/api/make-move`, `/api/engine-analyze`.
- Die vollständige FEN (Rochaderechte, En passant, Zugzähler) kommt vom Backend und wird unverändert weitergegeben; nur Editor-Änderungen und der Farbwechsel bauen sie aus dem Brett neu auf.
- Figurenerkennung: `chess_yolov8n.pt` (Startmodell aus öffentlichen Datensätzen, auf dem eigenen Brett noch nicht nachtrainiert). Automatische Eckenerkennung ist unzuverlässig, manuelles Verschieben der Pins bleibt Pflicht-Fallback.
- Ansicht: 3D-Brett als Standard, Umschalter auf 2D (gezeichnete Figuren) für Editor und schnelles Korrigieren.
- Funktionen laut Konzept: Eval-Balken, Pfeile für die besten Züge, Top-3-Kandidatenzüge, KI-Gegner mit einstellbarer Spielstärke, Lichess-Export, FEN kopieren, PWA-Manifest.
- Server läuft per HTTP im Heimnetz: Service Worker und Offline-Modus sind ohne HTTPS nicht verfügbar.

## Brand Commitments

Name ist nicht fest; „ChessVision Sim“ ist ein Arbeitstitel und darf ersetzt werden. Keine Logos oder Markenvorgaben.

## Evidence on Hand

Keine echten Fotos des eigenen Bretts im Repo. Testbilder stammen aus öffentlichen Datensätzen (`training/`). Keine Nutzerzitate, Zahlen oder Screenshots, die zitiert werden dürfen.

## Product Principles

1. Ein Kind muss den nächsten Schritt ohne Erklärung finden: große Tippziele, kurze Wörter, ein Hauptknopf pro Schritt.
2. Das Brett ist die Bühne; Bedienelemente treten zurück, bis sie gebraucht werden.
3. Scan-Fehler sind normal: Korrigieren muss schneller gehen als Neufotografieren.
4. Alles bleibt im Heimnetz; nichts verlässt den Server ohne ausdrücklichen Knopf (Lichess).

## Accessibility & Inclusion

Kinder als Mitnutzer: Tippziele mindestens 48 px, Figuren und Farben eindeutig unterscheidbar (nicht nur über Farbe), Texte ohne Fachjargon, Zahlen wie die Bewertung zusätzlich in Worten („Weiß steht besser“).
