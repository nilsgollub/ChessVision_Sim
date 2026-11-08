// Dezente Spielgeräusche, direkt im Browser erzeugt (Web Audio): keine Audiodateien, keine fremden Lizenzen.
// Browser starten Audio erst nach einer Berührung; der erste Tipp irgendwo auf der Seite schaltet es frei.

export type Sound = "move" | "capture" | "check" | "win" | "draw" | "nope";

const KEY = "brettfreunde.sound";
const VOLUME = 0.22;

let ctx: AudioContext | null = null;
let master: GainNode | null = null;
let noise: AudioBuffer | null = null;
let enabled = localStorage.getItem(KEY) !== "aus";

/** Für Tests: welche Geräusche gespielt wurden. */
export const soundLog: Sound[] = [];

export function soundEnabled(): boolean {
  return enabled;
}

export function setSoundEnabled(on: boolean) {
  enabled = on;
  localStorage.setItem(KEY, on ? "an" : "aus");
  if (on) play("move");
}

function audio(): AudioContext | null {
  if (ctx) return ctx;
  const AC = window.AudioContext ?? (window as unknown as { webkitAudioContext?: typeof AudioContext }).webkitAudioContext;
  if (!AC) return null;
  ctx = new AC();
  master = ctx.createGain();
  master.gain.value = VOLUME;
  master.connect(ctx.destination);
  noise = ctx.createBuffer(1, Math.round(ctx.sampleRate * 0.05), ctx.sampleRate);
  const d = noise.getChannelData(0);
  for (let i = 0; i < d.length; i++) d[i] = (Math.random() * 2 - 1) * (1 - i / d.length);
  return ctx;
}

function unlock() {
  const c = audio();
  if (c && c.state === "suspended") void c.resume();
}
window.addEventListener("pointerdown", unlock, { capture: true, passive: true });
window.addEventListener("keydown", unlock, { capture: true });

/** Ein Ton mit weichem Einsatz und Ausklang. */
function tone(at: number, freq: number, dur: number, gain: number, type: OscillatorType = "sine", glideTo?: number) {
  const c = ctx!, o = c.createOscillator(), g = c.createGain();
  o.type = type;
  o.frequency.setValueAtTime(freq, at);
  if (glideTo) o.frequency.exponentialRampToValueAtTime(glideTo, at + dur);
  g.gain.setValueAtTime(0.0001, at);
  g.gain.exponentialRampToValueAtTime(gain, at + 0.008);
  g.gain.exponentialRampToValueAtTime(0.0001, at + dur);
  o.connect(g).connect(master!);
  o.start(at);
  o.stop(at + dur + 0.02);
}

/** Kurzes Klopfen wie Holz auf Holz: gefiltertes Rauschen plus tiefer, schnell fallender Ton. */
function knock(at: number, pitch: number, gain: number) {
  const c = ctx!, src = c.createBufferSource(), f = c.createBiquadFilter(), g = c.createGain();
  src.buffer = noise;
  f.type = "bandpass";
  f.frequency.value = pitch * 3;
  f.Q.value = 2.5;
  g.gain.value = gain * 0.9;
  src.connect(f).connect(g).connect(master!);
  src.start(at);
  tone(at, pitch, 0.09, gain, "sine", pitch * 0.55);
}

export function play(kind: Sound) {
  if (!enabled) return;
  soundLog.push(kind);
  const c = audio();
  if (!c || c.state !== "running") return;
  const t = c.currentTime + 0.01;
  switch (kind) {
    case "move":
      knock(t, 420, 0.9);
      break;
    case "capture":
      knock(t, 360, 1);
      // kleines „Plopp“ und zwei Glitzertöne, passend zu den Zuckerperlen
      tone(t + 0.07, 700, 0.12, 0.35, "sine", 1100);
      tone(t + 0.13, 1568, 0.18, 0.12, "triangle");
      tone(t + 0.19, 2093, 0.22, 0.09, "triangle");
      break;
    case "check":
      knock(t, 420, 0.8);
      tone(t + 0.06, 784, 0.25, 0.22, "triangle");
      tone(t + 0.2, 1047, 0.35, 0.2, "triangle");
      break;
    case "win":
      knock(t, 420, 0.8);
      [523, 659, 784, 1047].forEach((f, i) => tone(t + 0.1 + i * 0.11, f, 0.45, 0.2, "triangle"));
      break;
    case "draw":
      knock(t, 420, 0.8);
      tone(t + 0.1, 659, 0.4, 0.18, "triangle");
      tone(t + 0.24, 659, 0.45, 0.16, "triangle");
      break;
    case "nope":
      tone(t, 220, 0.12, 0.35, "sine", 180);
      break;
  }
}
