// Die Figuren als Freunde: Name, Bändchenfarbe und ein Satz, wie sie zieht.
export type PieceType = "k" | "q" | "r" | "b" | "n" | "p";

// ribbon: Bändchen, Ringe, Pfeile (ohne Text). deep: Flächen mit weißer Schrift (Kontrast mind. 4.5:1).
export const PIECES: Record<PieceType, { type: string; ribbon: string; deep: string; soft: string; note: string; names: [string, string] }> = {
  k: { type: "König", ribbon: "#E9A92A", deep: "#976D1B", soft: "#FFF3D1", note: "Geht ein Feld in jede Richtung. Er muss gut beschützt werden.", names: ["Kuno", "Kasimir"] },
  q: { type: "Dame", ribbon: "#F2559A", deep: "#C6457E", soft: "#FFE3EF", note: "Zieht gerade und schräg, so weit sie will.", names: ["Dora", "Mira"] },
  r: { type: "Turm", ribbon: "#3D93E8", deep: "#3177BB", soft: "#DFEFFF", note: "Fährt gerade: vor, zurück und zur Seite.", names: ["Theo", "Tilda"] },
  b: { type: "Läufer", ribbon: "#8E6BE3", deep: "#8161CE", soft: "#ECE5FF", note: "Gleitet schräg und bleibt immer auf seiner Farbe.", names: ["Lilo", "Leo"] },
  n: { type: "Springer", ribbon: "#1FAA7E", deep: "#188462", soft: "#DDF6EC", note: "Springt im L und hüpft über alle drüber.", names: ["Fritzi", "Flocke"] },
  p: { type: "Bauer", ribbon: "#F0784A", deep: "#B65B38", soft: "#FFE7DC", note: "Geht vorwärts, schlägt aber schräg.", names: ["Paul", "Pia"] },
};

export function pieceInfo(symbol: string) {
  const t = symbol.toLowerCase() as PieceType;
  const white = symbol === symbol.toUpperCase();
  const p = PIECES[t];
  return { ...p, key: t, white, name: p.names[white ? 0 : 1], label: `${white ? "Weißer" : "Schwarzer"} ${p.type}`.replace("Weißer Dame", "Weiße Dame").replace("Schwarzer Dame", "Schwarze Dame") };
}

/** Bewertung in Worten, aus Sicht von Weiß (cp) bzw. Matt in n (positiv = Weiß setzt matt). */
export function evalWords(cp: number | null, mate: number | null): string {
  if (mate !== null && mate !== undefined) {
    if (mate === 0) return "Matt!";
    const side = mate > 0 ? "Weiß" : "Schwarz";
    const n = Math.abs(mate);
    return `${side} kann in ${n} ${n === 1 ? "Zug" : "Zügen"} matt setzen`;
  }
  const v = cp ?? 0;
  const a = Math.abs(v);
  const side = v > 0 ? "Weiß" : "Schwarz";
  if (a < 40) return "Alles ausgeglichen";
  if (a < 120) return `${side} steht etwas besser`;
  if (a < 350) return `${side} steht besser`;
  return `${side} steht klar besser`;
}

/** Anteil Weiß im Bewertungsbalken (0..1). */
export function evalShare(cp: number | null, mate: number | null): number {
  if (mate !== null && mate !== undefined) return mate > 0 ? 1 : mate < 0 ? 0 : 0.5;
  const v = Math.max(-1500, Math.min(1500, cp ?? 0));
  return 1 / (1 + Math.exp(-v / 300));
}

export const RANK_COLORS = ["#F2559A", "#8E6BE3", "#3D93E8"];
/** Rangfarben für Flächen mit weißer Ziffer. */
export const RANK_DEEP = ["#C6457E", "#8161CE", "#3177BB"];
