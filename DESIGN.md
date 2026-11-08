---
name: Brettfreunde
description: Echtes Schachbrett fotografieren, Stellung prüfen, mit Tipps weiterspielen; die Figuren sind Freunde mit Namen.
colors:
  ground: "#F1EEFF"
  ground-deep: "#E2DBFF"
  ink: "#2A2F5A"
  ink-soft: "#565B85"
  line: "#E4DFFA"
  line-strong: "#CBC4EE"
  pink: "#F2559A"
  pink-deep: "#C6457E"
  pink-soft: "#FFE3EF"
  lilac: "#8E6BE3"
  lilac-soft: "#ECE5FF"
  sky: "#3D93E8"
  sky-soft: "#DFEFFF"
  mint: "#1FAA7E"
  mint-soft: "#DDF6EC"
  butter: "#F5C24B"
  butter-soft: "#FFF3D1"
  ribbon-king: "#E9A92A"
  honey-deep: "#976D1B"
  lilac-deep: "#8161CE"
  sky-deep: "#3177BB"
  mint-deep: "#188462"
  coral-deep: "#B65B38"
  coral: "#F0784A"
  coral-soft: "#FFE7DC"
  bad: "#C2264B"
  bad-soft: "#FFE1E7"
  focus: "#3D93E8"
  sq-light: "#FFFFFF"
  sq-light-3d: "#E9E2FF"
  sq-dark: "#B7A9EE"
  sq-dark-ink: "#7C6BC8"
  frame: "#8E7AD9"
  frame-ink: "#FFFFFF"
  black-piece: "#353A6E"
  white-piece: "#FFFDFB"
  vinyl-white-3d: "#F6ECDF"
  last-move-light: "#FFEDB0"
  last-move-dark: "#F1CF6E"
  muted-ribbon: "#B9B7C9"
  muted-ink: "#8C8AA0"
  muted-body: "#F2F1F6"
  card: "#FFFFFF"
typography:
  display:
    fontFamily: "Fredoka, ui-rounded, system-ui, sans-serif"
    fontSize: "2rem"
    fontWeight: 700
    lineHeight: 1
    letterSpacing: "-0.015em"
  headline:
    fontFamily: "Fredoka, ui-rounded, system-ui, sans-serif"
    fontSize: "1.2rem"
    fontWeight: 700
    lineHeight: 1.2
  title:
    fontFamily: "Fredoka, ui-rounded, system-ui, sans-serif"
    fontSize: "1.05rem"
    fontWeight: 600
  body:
    fontFamily: "Nunito, ui-rounded, system-ui, sans-serif"
    fontSize: "1rem"
    fontWeight: 400
    lineHeight: 1.45
  label:
    fontFamily: "Nunito, ui-rounded, system-ui, sans-serif"
    fontSize: "0.85rem"
    fontWeight: 700
  mono:
    fontFamily: "ui-monospace, SF Mono, Menlo, monospace"
    fontSize: "0.85rem"
    fontWeight: 600
    lineHeight: 1.4
rounded:
  pill: "99px"
  frame: "22px"
  card: "20px"
  portrait: "18px"
  seg: "16px"
  tile: "14px"
  seg-item: "12px"
spacing:
  hair: "4px"
  tight: "8px"
  row: "10px"
  gutter: "12px"
  panel: "14px"
  gutter-desktop: "24px"
  column-gap-desktop: "28px"
components:
  button-primary:
    backgroundColor: "{colors.pink-deep}"
    textColor: "{colors.card}"
    typography: "{typography.title}"
    rounded: "{rounded.pill}"
    padding: "0 18px"
    height: "52px"
  button-primary-hover:
    backgroundColor: "#B23C71"
  button-secondary:
    backgroundColor: "{colors.card}"
    textColor: "{colors.ink}"
    typography: "{typography.title}"
    rounded: "{rounded.pill}"
    padding: "0 18px"
    height: "52px"
  icon-button:
    backgroundColor: "{colors.card}"
    textColor: "{colors.ink}"
    rounded: "{rounded.pill}"
    size: "44px"
  segment-on:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.card}"
    rounded: "{rounded.pill}"
    height: "40px"
  status-pill:
    backgroundColor: "{colors.card}"
    textColor: "{colors.ink}"
    typography: "{typography.label}"
    rounded: "{rounded.pill}"
    padding: "6px 12px"
  card:
    backgroundColor: "{colors.card}"
    textColor: "{colors.ink}"
    rounded: "{rounded.card}"
    padding: "12px 14px"
  name-plate:
    textColor: "{colors.ink}"
    rounded: "{rounded.frame}"
    padding: "10px 14px 10px 10px"
  name-tag:
    textColor: "{colors.card}"
    typography: "{typography.headline}"
    rounded: "{rounded.pill}"
    padding: "2px 12px"
  rank-card:
    textColor: "{colors.ink}"
    rounded: "{rounded.card}"
    padding: "10px 12px 10px 30px"
  rank-ribbon:
    textColor: "{colors.card}"
    typography: "{typography.title}"
    width: "26px"
    height: "34px"
  rank-go:
    backgroundColor: "{colors.card}"
    textColor: "{colors.ink}"
    rounded: "{rounded.pill}"
    padding: "0 14px"
    height: "44px"
  nav-item:
    textColor: "{colors.ink-soft}"
    typography: "{typography.label}"
    rounded: "{rounded.seg}"
    height: "56px"
  nav-item-active:
    textColor: "{colors.ink}"
  board-frame:
    backgroundColor: "{colors.frame}"
    rounded: "{rounded.frame}"
    padding: "8px"
  captured-chip:
    backgroundColor: "#F4F3F8"
    rounded: "10px"
    padding: "2px"
---

# Design System: Brettfreunde

## Overview

**Creative North Star: "Der Figurenkatalog im Spielzimmer"**

Brettfreunde ist ein Werkzeug-Bildschirm (Scannen, Korrigieren, Tipp holen) im Kleid eines Sammelfiguren-Katalogs. Jede Figur ist ein Charakter mit Namen, Gesicht und einem Bändchen in der Farbe ihres Typs; die Oberfläche drumherum ist ein lila getönter Grund mit weißen, rundum weichen Karten, Pillen und Plaketten. Das Brett ist die Bühne: im 3D-Modus glänzende Vinyl-Figuren auf einem Pastellbrett vor einem Konfetti-Hintergrund aus Zuckerperlen, im 2D-Modus dieselben Charaktere als gezeichnete Aufkleber.

Die Dichte ist die eines Handy-Werkzeugs: eine Spalte, große Tippziele (Knöpfe 52 px, Navigation 56 px, Symbolknöpfe 44 px), ein rosa Hauptknopf pro Schritt. Farbe kommt aus einer festen Familie von sechs Bonbon-Tönen, jeder mit einem hellen Partner-Ton; Grau bedeutet ausschließlich „geschlagen“. Bewegung ist sparsam bis auf eine Signatur: den kleinen Hüpfer, wenn eine Figur gewählt wird.

Abgelehnt ist der Kategorie-Standard von Schach-Apps: dunkle Oberfläche, grün-beiges Brett, Zahlenkolonnen. Bewertungen erscheinen in Worten („Weiß steht etwas besser“), Züge als Sätze über Figuren mit Namen.

**Key Characteristics:**
- Lila Grund, weiße Karten mit innenliegender 2-px-Kontur, Tinte statt Schwarz.
- Sechs Bändchenfarben je Figurtyp, jeweils mit hellem Partner-Ton als Flächenfarbe.
- Text auf Farbflächen immer auf der tiefen Stufe des Tons (mindestens 4.5:1 gegen Weiß).
- Zwei runde Schriften: Fredoka für Namen, Überschriften und Knöpfe; Nunito für alles andere.
- Alles Bedienbare ist eine Pille oder eine stark gerundete Karte.
- Top 3 als nummerierte Bändchen-Karten in fester Rangfarbe (Pink, Lila, Himmel), passend zu den Pfeilen auf dem Brett.
- Eine Signaturbewegung: der Hüpfer bei Auswahl.

## Colors

Bonbon-Pastell auf lila Grund: sechs gesättigte Töne mit je einem hellen Partner, getragen von einer tiefen Indigo-Tinte.

### Primary
- **Kaugummi-Pink** (pink): Rang-1-Pfeil und Ring des Ziehen-Knopfs, Damen-Bändchen, Symbol des Spielen-Tabs, Umriss des Eckvierecks beim Scannen (Fläche als 16-%-Mischung), Textauswahl. Partner **Pink-Hauch** (pink-soft) als Fläche hinter Damen-Karten und aktivem Spielen-Tab.
- **Himbeere** (pink-deep): die tiefe Stufe von Pink, überall wo Pink Schrift trägt: Hauptknopf („Tipp holen“, „Foto wählen“, „Scannen“, Hover #B23C71), Eckpins beim Scannen, Namensschild der Dame, Rang-1-Fähnchen.

### Secondary
- **Flieder** (lilac): Rang 2, Läufer-Bändchen, Mehr-Tab. Partner **Flieder-Hauch** (lilac-soft) für Läufer-Flächen und den „rechnet“-Zustand der Plakette.
- **Himmel** (sky): Rang 3, Turm-Bändchen, Scannen-Tab. Derselbe Wert dient als Fokusring (focus). Partner **Himmel-Hauch** (sky-soft).

### Tertiary
- **Minze** (mint): Springer-Bändchen, Korrigieren-Tab, eingeschalteter Schalter. Partner **Minz-Hauch** (mint-soft) als Fläche für Springer-Karten und den Zustand „gut“.
- **Butter** (butter): Sternchen der Wortmarke, Markierung des letzten Zugs im 3D-Brett. Das Königs-Bändchen nutzt ein dunkleres **Honig** (ribbon-king). Partner **Butter-Hauch** (butter-soft) hinter dem Zug-Satz der Plakette und im Status „warnen“/„rechnet“.
- **Koralle** (coral): Bauern-Bändchen. Partner **Koralle-Hauch** (coral-soft).

### Neutral
- **Lila Grund** (ground): Seitenhintergrund, Spur von Segmenten, FEN-Feld. Auch `theme-color`.
- **Tiefer Lila Grund** (ground-deep): Außenrand des radialen Bühnenverlaufs hinter dem 3D-Brett.
- **Indigo-Tinte** (ink): Text, aktiver Segment-Knopf, „ist dran“-Pille, Auswahlrahmen, Ziel-Punkte (mit 32–40 % Deckkraft), Augen der weißen Figuren, Hintergrund der Foto-Bühne.
- **Gedämpfte Tinte** (ink-soft): Nebentext, inaktive Tabs und Segmente.
- **Kontur** (line) und **starke Kontur** (line-strong): innenliegende Ringe von Karten, Pillen, sekundären Knöpfen; Schalter-Spur aus.
- **Kartenweiß** (card): jede Karte, Pille und Porträtfläche auf dem lila Grund.
- **Brett:** helle Felder Weiß (sq-light, 2D) bzw. Lila-Weiß (sq-light-3d), dunkle Felder Lavendel (sq-dark), Rahmen Violett (frame) mit weißen Koordinaten (frame-ink); Koordinaten auf hellen 2D-Feldern in sq-dark-ink. Letzter Zug: last-move-light / last-move-dark.
- **Figurenkörper:** weiß (white-piece, 2D), cremiges Vinyl (vinyl-white-3d, 3D), schwarz Indigo (black-piece, auch dunkle Hälfte des Bewertungsbalkens).
- **Geschlagen-Grau:** muted-ribbon, muted-ink, muted-body. Nur für Figuren im Fach „Schon vom Brett“.
- **Fehler** (bad / bad-soft): Fehlermeldungen und Plakette im Fehlerzustand.

### Tiefe Stufen
- **Honig tief** (honey-deep), **Himbeere** (pink-deep), **Himmel tief** (sky-deep), **Flieder tief** (lilac-deep), **Minze tief** (mint-deep), **Koralle tief** (coral-deep): je Figurtyp die Fläche des Namensschilds mit weißer Schrift; Himbeere, Flieder tief und Himmel tief zugleich die Rang-Fähnchen 1-2-3. Alle liegen bei 4.6:1 bis 4.7:1 gegen Weiß.

### Named Rules
**The Ribbon Rule.** Jeder Figurtyp besitzt drei Stufen: Bändchenfarbe, tiefe Stufe und hellen Partner. König Honig, Dame Pink, Turm Himmel, Läufer Flieder, Springer Minze, Bauer Koralle. Die Bändchenfarbe trägt alles ohne Text (Bändchen am Fuß, Porträtring, Palettenkachel, Mähne des Springers, 3D-Bändchen, Pfeile), die tiefe Stufe trägt das Namensschild, und die Fläche dahinter ist immer der Partner-Ton.

**The Deep Step Rule.** Schrift auf einer Farbfläche steht immer auf der tiefen Stufe des Tons, nie auf der Bändchenfarbe: weiße Schrift braucht mindestens 4.5:1. Die hellen Bändchentöne (2.1:1 bis 3.9:1 gegen Weiß) bleiben textfrei.

**The Rank Order Rule.** Rang 1 ist Pink, Rang 2 Flieder, Rang 3 Himmel, auf Karte und Pfeil gleich. Pfeilstärke fällt mit dem Rang (17 / 12 / 9 Einheiten auf 100er-Feldern), Deckkraft 0,9 für Rang 1, sonst 0,78. Die Ziffer im Fähnchen steht auf der tiefen Stufe der Rangfarbe.

**The Grey Means Gone Rule.** Grau gibt es nur für geschlagene Figuren; sie verlieren dabei Gesicht und Bändchenfarbe. Kein anderes Element wird grau eingefärbt, auch deaktivierte Knöpfe nicht (die werden auf 55 % Deckkraft gesetzt).

**The Lilac Ground Rule.** Der Seitengrund ist immer Lila, nie Weiß und nie dunkel. Weiß ist für Karten reserviert, Indigo für Text und kleine aktive Zustände.

## Typography

**Display Font:** Fredoka (mit ui-rounded, system-ui)
**Body Font:** Nunito (mit ui-rounded, system-ui)
**Label/Mono Font:** ui-monospace, nur für die FEN

**Character:** Zwei runde Groteske, eine verspielte und eine ruhige. Fredoka gibt Namen und Knöpfen den Spielzeug-Ton, Nunito hält Hinweise und Status leserlich. Beide sind lokal mitgeliefert (@fontsource), kein CDN.

### Hierarchy
- **Display** (Fredoka 700, 2rem, 1, -0.015em): nur die Wortmarke „Brettfreunde“ in der Kopfzeile, mit zweifarbigem Funkel-SVG (Butter, Pink) oben rechts.
- **Headline** (Fredoka 700, 1.2rem, 1.2): Namensschild der Figur auf der Plakette („Fritzi“, „Schwarz ist dran“). Figurennamen im Fließtext („**Flocke** nach f6“) ebenfalls Fredoka 700 in Fließtextgröße.
- **Title** (Fredoka 600, 1.05rem): Knopfbeschriftungen, Kartenüberschriften, Rangnummern im Bändchen. Kleinere Überschriften (Fach „Schon vom Brett“, Segment 3D/2D) 0.95rem.
- **Body** (Nunito 400, 1rem, 1.45): Hilfetexte, Zug-Satz auf der Plakette (0.98rem, 1.35), Rang-Zeilen.
- **Label** (Nunito 700, 0.78–0.9rem): Tab-Beschriftungen (0.78rem), Status-Pille und Figurenart (0.8–0.85rem), Bewertung in Worten (0.9rem), Stufen der KI (0.82rem). Kein Versal-Satz, keine Sperrung.
- **Mono** (ui-monospace 600, 0.85rem, 1.4): ausschließlich die FEN-Zeile, komplett markierbar.

### Named Rules
**The Two Rounds Rule.** Fredoka spricht für die Figuren (Namen, Überschriften, Knöpfe, Zahlen auf Bändchen), Nunito für alles Erklärende. Eine dritte Schrift gibt es nur als Monospace für die FEN.

**The Words First Rule.** Bewertungen stehen als Satz in Label-Stärke über dem Brett; Notation (SAN) erscheint nur klein, mit Tabellenziffern, als Nebenzeile.

## Layout

Handy zuerst, eine Spalte: Kopfzeile (Wortmarke links, Status-Pille rechts), Werkzeugzeile (Drehen, Bewertung in Worten, 3D/2D-Segment), dann das quadratische Brett mit 12 px breitem Bewertungsbalken links (8 px Abstand), darunter Plakette und Panel des gewählten Bereichs. Die Navigation ist eine feste Leiste unten mit vier gleich breiten Tabs; der Inhalt hält 96 px unten frei.

Rhythmus: Seitenrand 12 px, Abstand zwischen Hauptblöcken 14 px, innerhalb von Panels 14 px, zwischen Zeilen und Knöpfen 10 px, in Segmenten und Fächern 4–8 px. Zwei gleichwertige Knöpfe stehen in einem 1fr/1fr-Raster nebeneinander. Sichere Bereiche (`env(safe-area-inset-*)`) werden oben und unten eingerechnet.

Ab 960 px: Navigation wird eine 112 px breite, klebende Spalte links (Tabs 72 px hoch), Hauptbereich zweispaltig (Brett bis 560 px, Seitenspalte ab 340 px, 28 px Abstand), Seitenspalte klebt oben. Gesamtbreite höchstens 1180 px, zentriert.

## Elevation & Depth

Hybrid: Ruhende Container sind flach und werden über eine innenliegende 2-px-Kontur (line) vom Grund abgesetzt. Weiche, indigo-getönte Schatten heben nur, was schwebt oder Bühne ist: Brettrahmen, Plakette, Rangkarten, Navigationsleiste und der Hauptknopf (mit pinkem Schimmer). Echte Tiefe gibt es nur auf der 3D-Bühne: Himmelslicht (Weiß über Lavendel #8F80D6), eine Sonne mit weichem Schattenwurf und ein fliederfarbenes Gegenlicht (#B9A8FF), das die Umrisse heller Figuren nachzeichnet; schwarze Figuren glänzen mit starkem Klarlack, weiße sind matter.

### Shadow Vocabulary
- **Kontur** (`box-shadow: inset 0 0 0 2px var(--line)`): Karten, Pillen, Segmente, Fach, Symbolknöpfe in Ruhe.
- **Bühne** (`box-shadow: 0 10px 28px rgba(42, 47, 90, 0.16)`): nur der Brettrahmen.
- **Plakette** (`box-shadow: 0 6px 18px rgba(42, 47, 90, 0.1)`): Namensplakette.
- **Rangkarte** (`box-shadow: 0 4px 14px rgba(42, 47, 90, 0.08), inset 0 0 0 2px var(--line)`): Top-3-Karten.
- **Leiste** (`box-shadow: 0 -6px 20px rgba(42, 47, 90, 0.1)`): Navigation unten (am Desktop `0 6px 20px`).
- **Bonbon-Schimmer** (`box-shadow: 0 6px 14px rgba(198, 69, 126, 0.32)`): nur der primäre Knopf.
- **Gewählt im Segment** (`box-shadow: 0 2px 6px rgba(42, 47, 90, 0.12)`): aktive Stufe im Weiß-auf-Lila-Segment.

### Named Rules
**The Inset Contour Rule.** Konturen liegen innen (inset box-shadow), nicht als Rahmen. Ein Schatten nach außen bedeutet „schwebt“ und bleibt Brett, Plakette, Rangkarten, Leiste und Hauptknopf vorbehalten. Schatten sind immer weich und indigo-getönt, nie hart versetzt.

**The Sprinkle Stage Rule.** Hinter dem 3D-Brett liegt immer die Zuckerperlen-Fläche (`--sprinkle`, sechs Perlen in den sechs Bändchentönen, Kachel 120 px) über einem radialen Verlauf von Weiß zu ground-deep. Das Konfetti gehört zur Bühne, nicht zu Karten oder Panels.

## Shapes

Alles ist weich. Bedienbares ist eine volle Pille (99px): Knöpfe, Status, Namensschild, Segmente, Tab-Symbolhintergrund, Schalter. Container sind stark gerundete Rechtecke: Brettrahmen, Plakette und Leiste 22px, Karten und Rangkarten 20px, Porträt und Fotobühne 18px, Segment-Spur 16px, Palettenkacheln und Figurenporträts in Karten 14px, Segment-Knöpfe 12px. Einzige Kante mit Ecke ist das Rang-Bändchen: ein senkrechtes Fähnchen mit Schwalbenschwanz-Kerbe (`clip-path: polygon(0 0, 100% 0, 100% 100%, 50% 80%, 0 100%)`), das 4 px über den Kartenrand hinausragt.

Die Figuren haben eine eigene Formsprache: klare Schach-Silhouetten auf einem 100er-Raster, 3,4er Indigo-Kontur mit rundem Stoß, ein weißer 9er Aufkleber-Rand rundherum, ein Bändchen am Fuß, Gesicht mit zwei Augen samt Glanzpunkt, rosa Wangen und Lächeln (Springer im Profil). Symbole sind eigene Strich-SVGs auf 24er-Raster, Strich 2, runde Enden.

## Components

### Buttons
Satt, rund und ein bisschen federnd.
- **Shape:** volle Pille (99px), mindestens 52 px hoch, 18 px seitlich, Symbol plus Wort mit 8 px Abstand.
- **Primary:** Himbeere (pink-deep) mit weißer Fredoka-600-Schrift und Bonbon-Schimmer; Hover #B23C71. Einer pro Schritt.
- **Secondary:** Weiß mit Tinte und innenliegender 2-px-Kontur (line-strong); Hover zieht die Kontur auf Tinte.
- **Press:** `translateY(1px) scale(0.98)`, Übergänge 140 ms ease-out. Deaktiviert: 55 % Deckkraft.
- **Symbolknopf:** weißer Kreis 44 px mit Kontur (Brett drehen).
- **Ziehen (in Rangkarte):** weiße Pille 44 px mit 2-px-Rand in Rangfarbe, Schrift Tinte.

### Chips
- **Status-Pille:** weiß, Kontur, Nunito 700 0.85rem; im Zustand „rechnet“ Butter-Hauch.
- **Segmente (3D/2D, Weiß/Schwarz):** weiße Spur mit Kontur, aktiver Teil Tinte mit weißer Schrift. **KI-Stufen:** lila Spur, aktive Stufe weiß mit kleinem Schatten.
- **Figurenart-Pille:** weiß mit minzgrüner Innenkontur (#BDEBD9) und dunkelgrüner Schrift (#11664B), bei allen Figurtypen gleich.

### Cards / Containers
- **Corner Style:** 20px.
- **Background:** Kartenweiß auf lila Grund; Rangkarten und Plakette tragen stattdessen den Partner-Ton der jeweiligen Figur.
- **Shadow Strategy:** Kontur in Ruhe, siehe Elevation.
- **Internal Padding:** 12px 14px (Karten), 10–12 px (Fach, Palette).

### Inputs / Fields
- **Schalter:** Spur 48×28 px, aus line-strong, an Minze; weißer Knopf 22 px mit kleinem Schatten, gleitet in 200 ms `cubic-bezier(.22,1,.36,1)`.
- **Datei-Upload:** ein unsichtbares Eingabefeld über einem primären Knopf.
- **Eckpins:** Kreise 44 px in Himbeere (pink-deep) mit weißer Ziffer, mit 3 px weißem Rand und Schatten, Viereck dazwischen pink umrandet; beim Ziehen `scale(1.12)`.
- **Focus:** überall 3 px Himmel-Umriss mit 2 px Abstand.

### Navigation
Vier Tabs (Spielen, Scannen, Korrigieren, Mehr), jeder mit eigener Farbe (Pink, Himmel, Minze, Flieder) für das Symbol. Inaktiv: Symbol farbig, Wort ink-soft. Aktiv: Wort Tinte, Symbol sitzt in einer 40×30-px-Pille im Partner-Ton (Übergang 180 ms). Mobil feste Leiste unten mit oben gerundeten Ecken (22px), am Desktop klebende Spalte links.

### Namensplakette (Signatur)
Die Karte unter dem Brett zeigt die gewählte Figur: links ein weißes Porträt (18px Ecken) mit 3-px-Ring in Bändchenfarbe, rechts ein Pillen-Stapel aus Namensschild (tiefe Stufe des Figurtyps, weiße Fredoka 700 1.2rem), Figurenart-Pille und dem Zug-Satz auf Butter-Hauch (14px Ecken). Fläche: Partner-Ton der Figur, 2-px-Rand in Weiß, Mindesthöhe 88 px. Ohne Auswahl zeigt sie „Weiß/Schwarz ist dran“ mit Tinten-Schild und Tinten-Ring und färbt sich nach Zustand (gut, warnen, Fehler, rechnet). Bei jeder Auswahl springt sie leicht ein (`bump`, 380 ms, `cubic-bezier(.3,1.5,.5,1)`, von 6 px tiefer und 98 %).

### Top-3-Rangkarten
Liste aus bis zu drei Karten im Partner-Ton der ziehenden Figur, links das Rang-Fähnchen in der tiefen Stufe der Rangfarbe mit weißer Ziffer, daneben Figurenporträt (46 px auf Weiß), Satz „**Name** nach Feld“ und Nebenzeile mit SAN und Bewertung in Worten, rechts „Ziehen“. Auf dem Brett dieselben Ränge als Pfeile, Rang 1 obenauf.

### Brett
2D: SVG mit weißen und lavendelfarbenen Feldern im violetten Rahmen (22px, 8 px Innenabstand); Auswahl als Tinten-Rahmen mit 16er Rundung, Zielfelder als Tintenpunkte bzw. gestrichelte Ringe. 3D: abgerundeter Rahmenblock, Figuren als gedrechselte Vinyl-Körper mit Gesicht und Bändchen-Torus, Konfetti-Bühne dahinter. Figurenzüge gleiten 380 ms in einem Bogen (Springer höher).

### Signaturbewegung: der Hüpfer
**The One Hop Rule.** Die einzige ausdrucksstarke Bewegung ist der Hüpfer der gewählten Figur: in 2D 14 px hoch in 420 ms mit `cubic-bezier(.3,1.6,.5,1)`, in 3D derselbe Bogen über 420 ms, dazu das Einspringen der Plakette. Alles andere bewegt sich kurz und still (140–200 ms, ease-out). Bei `prefers-reduced-motion` entfallen alle Animationen.

### Fach „Schon vom Brett“
Weiße Karte mit Kontur, darin geschlagene Figuren als 30-px-Grauversion auf hellgrauen Kacheln (10px Ecken), getrennt nach Farbe.

## Do's and Don'ts

### Do:
- **Do** jede neue figurbezogene Fläche aus Bändchenfarbe, tiefer Stufe und Partner-Ton des Figurtyps bauen (The Ribbon Rule).
- **Do** Schrift auf Farbflächen immer auf die tiefe Stufe setzen (The Deep Step Rule).
- **Do** Rangfarben in der Reihenfolge Pink, Flieder, Himmel halten und Karte und Pfeil gleich färben.
- **Do** Karten weiß auf lila Grund mit `inset 0 0 0 2px var(--line)` absetzen; Außenschatten nur weich und indigo-getönt.
- **Do** Bedienbares als Pille (99px) mit mindestens 44 px, Hauptaktionen 52 px hoch.
- **Do** Figuren mit Namen ansprechen und Bewertungen in Worten zeigen; Notation nur als Nebenzeile.
- **Do** Fredoka für Namen, Überschriften und Knöpfe, Nunito für alles andere.
- **Do** Bewegung auf den Hüpfer bei Auswahl konzentrieren und `prefers-reduced-motion` respektieren.

### Don't:
- **Don't** dunkle Seitengründe, grün-beige Bretter oder Zahlenkolonnen verwenden.
- **Don't** Grau für irgendetwas anderes als geschlagene Figuren einsetzen.
- **Don't** neue Akzentfarben außerhalb der sechs Bändchentöne einführen.
- **Don't** harte, versetzte Schatten oder Rahmenlinien statt innenliegender Konturen verwenden.
- **Don't** Emoji oder Symbolschriften nutzen; Symbole sind eigene Strich-SVGs (24er Raster, Strich 2).
- **Don't** Schrift auf die hellen Bändchentöne setzen; Text auf Farbe gehört auf die tiefe Stufe.
