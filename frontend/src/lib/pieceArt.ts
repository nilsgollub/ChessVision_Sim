// Gezeichnete Schachfiguren als Charaktere, 100x100. Klare Silhouetten (Kinder sollen die echten
// Figuren erkennen), dazu ein Gesicht und ein Bändchen in der Farbe des Figurentyps.
// Wird von der 2D-Ansicht, den Karten und der Palette benutzt; der Springer-Umriss auch für 3D.

import { PIECES, type PieceType } from "./pieces";

export const INK = "#2A2F5A";
const WHITE_BODY = "#FFFDFB";
const BLACK_BODY = "#353A6E";

export const KNIGHT_PATH =
  "M31 75 C31 66 34 61 39 57 C32 57 24 55 21 49 C18 43 22 37 28 35 C32 29 37 23 42 20 L43 10 L50 17 C63 17 73 28 73 43 C73 56 69 64 69 75 Z";

type Shape = { body: string; face: { x: number; y: number; profile?: boolean } };

const BASE = `<rect x="20" y="80" width="60" height="12" rx="6"/>`;

const SHAPES: Record<PieceType, Shape> = {
  p: {
    body: `<path d="M33 76 C34 61 39 53 44 50 L56 50 C61 53 66 61 67 76 Z"/><circle cx="50" cy="37" r="16"/>`,
    face: { x: 50, y: 38 },
  },
  r: {
    body: `<path d="M31 76 L33 44 L67 44 L69 76 Z"/><path d="M26 22 Q26 18 30 18 L36 18 Q39 18 39 22 L39 26 L45 26 L45 22 Q45 18 49 18 L51 18 Q55 18 55 22 L55 26 L61 26 L61 22 Q61 18 64 18 L70 18 Q74 18 74 22 L74 42 Q74 46 70 46 L30 46 Q26 46 26 42 Z"/>`,
    face: { x: 50, y: 36 },
  },
  b: {
    body: `<path d="M34 76 C36 62 40 56 43 54 L57 54 C60 56 64 62 66 76 Z"/><path d="M50 14 C62 22 67 32 66 42 C65 51 58 56 50 56 C42 56 35 51 34 42 C33 32 38 22 50 14 Z"/><circle cx="50" cy="11" r="5"/>`,
    face: { x: 50, y: 42 },
  },
  n: {
    body: `<path d="${KNIGHT_PATH}"/>`,
    face: { x: 44, y: 33, profile: true },
  },
  q: {
    body: `<path d="M32 76 C34 62 39 56 43 54 L57 54 C61 56 66 62 68 76 Z"/><circle cx="50" cy="42" r="15"/><path d="M33 33 L30 15 L41 24 L50 10 L59 24 L70 15 L67 33 Q50 27 33 33 Z"/>`,
    face: { x: 50, y: 44 },
  },
  k: {
    body: `<path d="M31 76 C33 62 38 56 43 54 L57 54 C62 56 67 62 69 76 Z"/><circle cx="50" cy="43" r="15"/><path d="M35 32 L34 21 L42 26 L50 19 L58 26 L66 21 L65 32 Q50 27 35 32 Z"/><rect x="47" y="3" width="6" height="17" rx="2.5"/><rect x="42" y="7" width="16" height="6" rx="2.5"/>`,
    face: { x: 50, y: 45 },
  },
};

function face(x: number, y: number, white: boolean, profile = false): string {
  const eye = white ? INK : "#FFFFFF";
  const cheek = white ? "#FF9EC2" : "#FF8FB8";
  if (profile) {
    return `<ellipse cx="${x}" cy="${y}" rx="3" ry="3.6" fill="${eye}"/><circle cx="${x + 1}" cy="${y - 1.2}" r="1" fill="${white ? "#fff" : INK}"/>
<ellipse cx="${x - 7}" cy="${y + 9}" rx="4.5" ry="2.6" fill="${cheek}" opacity=".75"/>
<ellipse cx="26" cy="45" rx="1.6" ry="1.2" fill="${eye}" opacity=".8"/>
<path d="M27 50 Q31 52 35 50" stroke="${eye}" stroke-width="2" fill="none" stroke-linecap="round"/>`;
  }
  return `<ellipse cx="${x - 6}" cy="${y}" rx="2.6" ry="3.2" fill="${eye}"/><ellipse cx="${x + 6}" cy="${y}" rx="2.6" ry="3.2" fill="${eye}"/>
<circle cx="${x - 5.2}" cy="${y - 1.1}" r=".9" fill="${white ? "#fff" : INK}"/><circle cx="${x + 6.8}" cy="${y - 1.1}" r=".9" fill="${white ? "#fff" : INK}"/>
<ellipse cx="${x - 11}" cy="${y + 5}" rx="3.6" ry="2.2" fill="${cheek}" opacity=".75"/><ellipse cx="${x + 11}" cy="${y + 5}" rx="3.6" ry="2.2" fill="${cheek}" opacity=".75"/>
<path d="M${x - 3} ${y + 4.5} Q${x} ${y + 7.5} ${x + 3} ${y + 4.5}" stroke="${eye}" stroke-width="1.8" fill="none" stroke-linecap="round"/>`;
}

/** Inneres SVG (ohne <svg>-Hülle) einer Figur. `muted` = geschlagen (grau). */
export function pieceSvg(symbol: string, muted = false): string {
  const t = symbol.toLowerCase() as PieceType;
  const white = symbol === symbol.toUpperCase();
  const shape = SHAPES[t];
  const ribbon = muted ? "#B9B7C9" : PIECES[t].ribbon;
  const fill = muted ? (white ? "#F2F1F6" : "#8C8AA0") : white ? WHITE_BODY : BLACK_BODY;
  const stroke = muted ? "#8C8AA0" : INK;
  const { x, y, profile } = shape.face;
  const mane = t === "n"
    ? `<g fill="${ribbon}">${[[61, 21], [67, 28], [71, 37], [72, 47], [71, 57]].map(([cx, cy]) => `<circle cx="${cx}" cy="${cy}" r="4.6"/>`).join("")}</g>`
    : "";
  return `<g stroke="#FFFFFF" stroke-width="9" stroke-linejoin="round" fill="#FFFFFF">${shape.body}${BASE}</g>
<g fill="${fill}" stroke="${stroke}" stroke-width="3.4" stroke-linejoin="round">${shape.body}</g>
${mane}
<rect x="20" y="80" width="60" height="12" rx="6" fill="${fill}" stroke="${stroke}" stroke-width="3.4"/>
<rect x="28" y="72" width="44" height="9" rx="4.5" fill="${ribbon}" stroke="${stroke}" stroke-width="3"/>
${muted ? "" : face(x, y, white, profile)}`;
}
