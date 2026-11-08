<script lang="ts">
  import { onMount } from "svelte";
  import * as THREE from "three";
  import { OrbitControls } from "three/addons/controls/OrbitControls.js";
  import { SVGLoader } from "three/addons/loaders/SVGLoader.js";
  import { RoundedBoxGeometry } from "three/addons/geometries/RoundedBoxGeometry.js";
  import { game } from "../lib/game.svelte";
  import { squareName, squareRC } from "../lib/chess";
  import { KNIGHT_PATH } from "../lib/pieceArt";
  import { PIECES, RANK_COLORS, type PieceType } from "../lib/pieces";

  let host: HTMLDivElement;
  let failed = $state(false);

  // Brettkoordinaten: Feld a1 liegt bei x=-3.5, z=+3.5 (Weiß unten, Kamera auf +z).
  const sqPos = (sq: string) => {
    const [r, c] = squareRC(sq);
    return new THREE.Vector3(c - 3.5, 0, r - 3.5);
  };

  onMount(() => {
    let renderer: THREE.WebGLRenderer;
    try {
      renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    } catch {
      failed = true;
      game.view = "2d";
      return;
    }
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFShadowMap;
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 0.92;
    host.appendChild(renderer.domElement);

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(29, 1, 0.1, 100);
    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enablePan = false;
    controls.enableDamping = true;
    controls.minPolarAngle = 0.12;
    controls.maxPolarAngle = 1.12;
    controls.minDistance = 9;
    controls.maxDistance = 21;
    controls.target.set(0, 0, 0.3);

    // Licht: weiches Himmelslicht und eine Sonne für Schatten.
    scene.add(new THREE.HemisphereLight(0xffffff, 0x8f80d6, 1.25));
    const sun = new THREE.DirectionalLight(0xffffff, 1.7);
    sun.position.set(-6, 8, 7);
    sun.castShadow = true;
    sun.shadow.mapSize.set(1024, 1024);
    sun.shadow.camera.left = -6; sun.shadow.camera.right = 6;
    sun.shadow.camera.top = 6; sun.shadow.camera.bottom = -6;
    sun.shadow.radius = 4;
    sun.shadow.bias = -0.0008;
    scene.add(sun);
    // Gegenlicht zeichnet die Umrisse der hellen Figuren nach
    const rim = new THREE.DirectionalLight(0xb9a8ff, 1.4);
    rim.position.set(3, 5, -9);
    scene.add(rim);

    // Brett
    const css = getComputedStyle(document.documentElement);
    const col = (v: string) => new THREE.Color(css.getPropertyValue(v).trim());
    const frame = new THREE.Mesh(new RoundedBoxGeometry(9, 0.5, 9, 4, 0.22), new THREE.MeshStandardMaterial({ color: col("--frame"), roughness: 0.55 }));
    frame.position.y = -0.27;
    frame.receiveShadow = true;
    scene.add(frame);
    const squareGeo = new THREE.BoxGeometry(1, 0.06, 1);
    const lightMat = new THREE.MeshStandardMaterial({ color: col("--sq-light-3d"), roughness: 0.6 });
    const darkMat = new THREE.MeshStandardMaterial({ color: col("--sq-dark"), roughness: 0.6 });
    const squareMeshes: THREE.Mesh[] = [];
    for (let r = 0; r < 8; r++) for (let c = 0; c < 8; c++) {
      const m = new THREE.Mesh(squareGeo, (r + c) % 2 ? darkMat : lightMat);
      m.position.set(c - 3.5, -0.02, r - 3.5);
      m.receiveShadow = true;
      m.userData.square = squareName(r, c);
      squareMeshes.push(m);
      scene.add(m);
    }

    // Koordinaten am Rand
    const labelGroup = new THREE.Group();
    scene.add(labelGroup);
    function makeLabel(text: string) {
      const cv = document.createElement("canvas");
      cv.width = cv.height = 64;
      const g = cv.getContext("2d")!;
      g.fillStyle = css.getPropertyValue("--frame-ink").trim();
      g.font = "700 40px Nunito, sans-serif";
      g.textAlign = "center"; g.textBaseline = "middle";
      g.fillText(text, 32, 34);
      const tex = new THREE.CanvasTexture(cv);
      tex.colorSpace = THREE.SRGBColorSpace;
      const mesh = new THREE.Mesh(new THREE.PlaneGeometry(0.34, 0.34), new THREE.MeshBasicMaterial({ map: tex, transparent: true }));
      mesh.rotation.x = -Math.PI / 2;
      return mesh;
    }
    for (let i = 0; i < 8; i++) {
      const f = makeLabel(String.fromCharCode(97 + i));
      f.position.set(i - 3.5, 0.005, 4.22);
      labelGroup.add(f);
      const n = makeLabel(String(8 - i));
      n.position.set(-4.22, 0.005, i - 3.5);
      labelGroup.add(n);
    }

    // Figuren: gedrechselte Körper (Lathe), der Springer aus demselben Umriss wie in 2D.
    const lathe = (pts: [number, number][]) =>
      new THREE.LatheGeometry(pts.map(([x, y]) => new THREE.Vector2(x, y)), 40);
    const baseGeo = lathe([[0, 0], [0.36, 0], [0.4, 0.04], [0.4, 0.12], [0.36, 0.16], [0.28, 0.17], [0, 0.17]]);
    const collarGeo = new THREE.TorusGeometry(0.262, 0.032, 10, 40);
    const bodies: Record<PieceType, THREE.BufferGeometry[]> = {
      p: [lathe([[0, 0.15], [0.27, 0.15], [0.2, 0.36], [0.14, 0.5], [0.12, 0.56], [0, 0.56]]), new THREE.SphereGeometry(0.19, 32, 20).translate(0, 0.68, 0)],
      r: [
        lathe([[0, 0.15], [0.29, 0.15], [0.25, 0.6], [0.31, 0.64], [0.31, 0.84], [0.21, 0.84], [0.21, 0.78], [0, 0.78]]),
        // Zinnen: vier Klötze auf dem Rand
        ...[0, 1, 2, 3].map((i) => {
          const a = (i * Math.PI) / 2 + Math.PI / 4;
          return new RoundedBoxGeometry(0.17, 0.16, 0.12, 2, 0.03).rotateY(-a).translate(Math.cos(a) * 0.255, 0.91, Math.sin(a) * 0.255);
        }),
      ],
      b: [lathe([[0, 0.15], [0.27, 0.15], [0.17, 0.5], [0.13, 0.6], [0.2, 0.7], [0.22, 0.82], [0.16, 0.96], [0.06, 1.04], [0, 1.05]]), new THREE.SphereGeometry(0.06, 16, 12).translate(0, 1.1, 0)],
      q: [
        lathe([[0, 0.15], [0.29, 0.15], [0.18, 0.55], [0.15, 0.7], [0, 0.7]]),
        new THREE.SphereGeometry(0.2, 32, 20).translate(0, 0.86, 0),
        lathe([[0.05, 0.98], [0.22, 1.02], [0.28, 1.18], [0.22, 1.12], [0, 1.1]]),
        // Kronenzacken als Kugeln
        ...[0, 1, 2, 3, 4, 5].map((i) => {
          const a = (i * Math.PI) / 3;
          return new THREE.SphereGeometry(0.055, 14, 10).translate(Math.cos(a) * 0.27, 1.22, Math.sin(a) * 0.27);
        }),
        new THREE.SphereGeometry(0.07, 16, 12).translate(0, 1.2, 0),
      ],
      k: [lathe([[0, 0.15], [0.3, 0.15], [0.19, 0.55], [0.16, 0.72], [0, 0.72]]), new THREE.SphereGeometry(0.21, 32, 20).translate(0, 0.9, 0), lathe([[0.06, 1.04], [0.21, 1.06], [0.25, 1.2], [0, 1.18]]), new RoundedBoxGeometry(0.07, 0.3, 0.07, 2, 0.02).translate(0, 1.36, 0), new RoundedBoxGeometry(0.22, 0.07, 0.07, 2, 0.02).translate(0, 1.38, 0)],
      n: [],
    };
    // Springer-Kopf aus dem SVG-Pfad (100er-Raster) extrudieren
    {
      const data = new SVGLoader().parse(`<svg xmlns="http://www.w3.org/2000/svg"><path d="${KNIGHT_PATH}"/></svg>`);
      const shapes = data.paths[0].toShapes();
      const geo = new THREE.ExtrudeGeometry(shapes, { depth: 26, bevelEnabled: true, bevelThickness: 6, bevelSize: 4, bevelSegments: 4, curveSegments: 16 });
      geo.translate(-47, -75, -13);
      geo.scale(0.0118, -0.0118, -0.0118); // zwei Spiegelungen: Flächen bleiben richtig herum
      geo.translate(0, 0.17, 0);
      bodies.n = [lathe([[0, 0.15], [0.27, 0.15], [0.24, 0.24], [0, 0.24]]), geo];
    }
    const faceHeight: Record<PieceType, number> = { p: 0.68, r: 0.7, b: 0.74, q: 0.86, k: 0.9, n: 0.8 };
    const faceRadius: Record<PieceType, number> = { p: 0.19, r: 0.3, b: 0.2, q: 0.2, k: 0.21, n: 0.16 };

    const mats = {
      w: new THREE.MeshPhysicalMaterial({ color: 0xf6ecdf, roughness: 0.5, clearcoat: 0.35, clearcoatRoughness: 0.45 }),
      b: new THREE.MeshPhysicalMaterial({ color: 0x353a6e, roughness: 0.32, clearcoat: 0.9, clearcoatRoughness: 0.2 }),
      eyeDark: new THREE.MeshBasicMaterial({ color: 0x2a2f5a }),
      eyeLight: new THREE.MeshBasicMaterial({ color: 0xffffff }),
      cheek: new THREE.MeshBasicMaterial({ color: 0xff9ec2, transparent: true, opacity: 0.8 }),
    };
    const ribbonMats = Object.fromEntries(
      (Object.keys(PIECES) as PieceType[]).map((t) => [t, new THREE.MeshStandardMaterial({ color: PIECES[t].ribbon, roughness: 0.45 })]),
    ) as unknown as Record<PieceType, THREE.Material>;
    const eyeGeo = new THREE.SphereGeometry(0.052, 16, 12);
    const maneGeo = new THREE.SphereGeometry(0.06, 12, 10);
    const cheekGeo = new THREE.CircleGeometry(0.058, 20);

    function buildPiece(symbol: string): THREE.Group {
      const t = symbol.toLowerCase() as PieceType;
      const white = symbol === symbol.toUpperCase();
      const g = new THREE.Group();
      const mat = white ? mats.w : mats.b;
      for (const geo of [baseGeo, ...bodies[t]]) {
        const m = new THREE.Mesh(geo, mat);
        m.castShadow = true;
        m.receiveShadow = true;
        g.add(m);
      }
      const collar = new THREE.Mesh(collarGeo, ribbonMats[t]);
      collar.rotation.x = Math.PI / 2;
      collar.position.y = 0.2;
      g.add(collar);
      if (t === "n") {
        // Mähne an denselben Punkten wie in der 2D-Zeichnung
        for (const [x, y] of [[61, 21], [67, 28], [71, 37], [72, 47], [71, 57]]) {
          const mane = new THREE.Mesh(maneGeo, ribbonMats.n);
          mane.position.set((x - 47) * 0.0118, (75 - y) * 0.0118 + 0.17, 0);
          mane.scale.set(1, 1, 2.6);
          g.add(mane);
        }
      }
      // Gesicht zur Kamera-Seite (+z)
      const face = new THREE.Group();
      const h = faceHeight[t], rad = faceRadius[t];
      const eyeMat = white ? mats.eyeDark : mats.eyeLight;
      if (t === "n") {
        // Profil: Auge seitlich auf beiden Seiten des Kopfes
        for (const s of [1, -1]) {
          const e = new THREE.Mesh(eyeGeo, eyeMat);
          e.position.set(-0.035, 0.66, s * 0.235);
          e.scale.setScalar(1.15);
          const ch = new THREE.Mesh(cheekGeo, mats.cheek);
          ch.position.set(-0.16, 0.56, s * 0.236);
          ch.rotation.y = s > 0 ? 0 : Math.PI;
          face.add(ch);
          face.add(e);
        }
      } else {
        for (const s of [-1, 1]) {
          const e = new THREE.Mesh(eyeGeo, eyeMat);
          e.position.set(s * 0.085, h + 0.03, rad * 0.9);
          e.scale.set(1, 1.25, 0.6);
          face.add(e);
          const ch = new THREE.Mesh(cheekGeo, mats.cheek);
          ch.position.set(s * 0.14, h - 0.045, rad * 0.86 + 0.012);
          ch.rotation.y = s * 0.55;
          face.add(ch);
        }
      }
      if (t !== "n") face.rotation.y = camAngle;
      g.add(face);
      g.userData.face = face;
      if (t === "n") g.rotation.y = white ? 0 : Math.PI; // Springer schauen zur Brettmitte
      return g;
    }

    const pieceGroup = new THREE.Group();
    scene.add(pieceGroup);
    let meshBySquare = new Map<string, THREE.Group>();
    let shownFen = "";

    function rebuildPieces() {
      pieceGroup.clear();
      meshBySquare = new Map();
      for (let r = 0; r < 8; r++) for (let c = 0; c < 8; c++) {
        const p = game.grid[r][c];
        if (!p) continue;
        const sq = squareName(r, c);
        const m = buildPiece(p);
        m.position.copy(sqPos(sq));
        meshBySquare.set(sq, m);
        pieceGroup.add(m);
      }
      shownFen = game.fen;
    }

    // Markierungen: Auswahl, letzter Zug, Zielpunkte
    const markGroup = new THREE.Group();
    scene.add(markGroup);
    const tileGeo = new THREE.PlaneGeometry(0.96, 0.96).rotateX(-Math.PI / 2);
    const dotGeo = new THREE.CircleGeometry(0.15, 28).rotateX(-Math.PI / 2);
    const ringGeo = new THREE.RingGeometry(0.36, 0.45, 40).rotateX(-Math.PI / 2);
    const markMats = {
      last: new THREE.MeshBasicMaterial({ color: col("--butter"), transparent: true, opacity: 0.5 }),
      sel: new THREE.MeshBasicMaterial({ color: col("--ink"), transparent: true, opacity: 0.22 }),
      target: new THREE.MeshBasicMaterial({ color: col("--ink"), transparent: true, opacity: 0.35 }),
    };
    function rebuildMarks() {
      markGroup.clear();
      const add = (geo: THREE.BufferGeometry, mat: THREE.Material, sq: string, y: number) => {
        const m = new THREE.Mesh(geo, mat);
        m.position.copy(sqPos(sq)).setY(y);
        markGroup.add(m);
      };
      if (game.lastMove) { add(tileGeo, markMats.last, game.lastMove.from, 0.013); add(tileGeo, markMats.last, game.lastMove.to, 0.013); }
      if (game.selected) add(tileGeo, markMats.sel, game.selected, 0.016);
      for (const t of game.targets) add(game.pieceAt(t) ? ringGeo : dotGeo, markMats.target, t, 0.02);
      if (game.hintsFresh) {
        for (const m of [...game.topMoves].reverse()) markGroup.add(makeArrow(m.from, m.to, m.rank));
      }
    }

    function makeArrow(from: string, to: string, rank: number) {
      const a = sqPos(from), b = sqPos(to);
      const dir = new THREE.Vector3().subVectors(b, a);
      const len = dir.length();
      const w = [0.17, 0.12, 0.09][rank - 1] ?? 0.09;
      const head = w * 2.4;
      const s = new THREE.Shape();
      const start = 0.25, shaft = len - head;
      s.moveTo(start, -w / 2); s.lineTo(shaft, -w / 2); s.lineTo(shaft, -head * 0.62);
      s.lineTo(len, 0); s.lineTo(shaft, head * 0.62); s.lineTo(shaft, w / 2); s.lineTo(start, w / 2);
      const geo = new THREE.ShapeGeometry(s).rotateX(-Math.PI / 2);
      const mat = new THREE.MeshBasicMaterial({ color: RANK_COLORS[rank - 1], transparent: true, opacity: rank === 1 ? 0.9 : 0.78, depthWrite: false, depthTest: false });
      const m = new THREE.Mesh(geo, mat);
      m.position.set(a.x, 0.03 + (3 - rank) * 0.002, a.z);
      m.rotation.y = -Math.atan2(dir.z, dir.x);
      m.renderOrder = 10;
      return m;
    }

    // Animationen: jede bekommt k von 0 bis 1 über ihre Dauer, optional mit Verzögerung.
    type Anim = { t0: number; dur: number; step: (k: number) => void; done?: () => void };
    let anims: Anim[] = [];
    let slowMo = 1; // nur für Tests: Zeitlupe, weil Software-Rendering wenige Bilder pro Sekunde schafft
    const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    function slide(mesh: THREE.Object3D, from: THREE.Vector3, to: THREE.Vector3, dur: number, hop: number, done?: () => void) {
      anims.push({
        t0: performance.now(), dur: dur * slowMo, done,
        step: (k) => {
          const e = 1 - Math.pow(1 - k, 3);
          mesh.position.lerpVectors(from, to, e);
          mesh.position.y = Math.sin(Math.PI * k) * hop;
        },
      });
    }

    // Geschlagene Figur: kleiner Hopser, kippt weg, schrumpft; dazu Zuckerperlen.
    const confettiGeo = new THREE.SphereGeometry(0.07, 10, 8);
    const CONFETTI = ["#F2559A", "#1FAA7E", "#F5C24B", "#8E6BE3", "#3D93E8", "#F0784A"];
    function knockOut(mesh: THREE.Object3D, delay: number) {
      scene.attach(mesh); // aus der Figurengruppe lösen, damit ein Neuaufbau sie nicht vorzeitig entfernt
      const start = mesh.position.clone();
      const tilt = (Math.random() < 0.5 ? -1 : 1) * 1.2;
      anims.push({
        t0: performance.now() + delay * slowMo, dur: 460 * slowMo,
        step: (k) => {
          const e = 1 - Math.pow(1 - k, 2);
          mesh.position.set(start.x, Math.sin(Math.PI * Math.min(1, k * 1.6)) * 0.45, start.z);
          mesh.rotation.z = tilt * e;
          mesh.scale.setScalar(Math.max(0.001, 1 - Math.pow(k, 1.6)));
        },
        done: () => scene.remove(mesh),
      });
      const burst = new THREE.Group();
      burst.position.copy(start).setY(0.45);
      scene.add(burst);
      const parts = Array.from({ length: 14 }, (_, i) => {
        const mat = new THREE.MeshBasicMaterial({ color: CONFETTI[i % CONFETTI.length], transparent: true });
        const m = new THREE.Mesh(confettiGeo, mat);
        const a = (i / 14) * Math.PI * 2 + Math.random() * 0.4;
        const sp = 1.6 + Math.random() * 1.2;
        m.userData.v = new THREE.Vector3(Math.cos(a) * sp, 2.4 + Math.random() * 1.6, Math.sin(a) * sp);
        burst.add(m);
        return m;
      });
      anims.push({
        t0: performance.now() + (delay + 60) * slowMo, dur: 620 * slowMo,
        step: (k) => {
          const t = k * 0.62;
          for (const m of parts) {
            const v = m.userData.v as THREE.Vector3;
            m.position.set(v.x * t, v.y * t - 4.9 * t * t, v.z * t);
            (m.material as THREE.MeshBasicMaterial).opacity = 1 - k * k;
          }
        },
        done: () => {
          scene.remove(burst);
          for (const m of parts) (m.material as THREE.Material).dispose();
        },
      });
    }

    function animateMove(from: string, to: string) {
      const mesh = meshBySquare.get(from);
      if (!mesh || reduced) { rebuildPieces(); return; }
      const fx = game.fx;
      const captured = fx && fx.capturedSq ? meshBySquare.get(fx.capturedSq) : undefined;
      const knight = game.pieceAt(to).toLowerCase() === "n";
      const dur = 380;
      if (captured) {
        meshBySquare.delete(fx!.capturedSq);
        knockOut(captured, dur * 0.62); // kurz bevor der Angreifer landet
      }
      meshBySquare.delete(from);
      meshBySquare.set(to, mesh);
      const fenAtStart = game.fen;
      shownFen = fenAtStart;
      // Danach sauber neu aufbauen (Rochade-Turm, Umwandlung), außer ein neuerer Zug läuft schon
      slide(mesh, sqPos(from), sqPos(to), dur, knight ? 0.9 : 0.35, () => { if (game.fen === fenAtStart) rebuildPieces(); });
    }

    function hopSelected(sq: string) {
      const mesh = meshBySquare.get(sq);
      if (!mesh || reduced) return;
      const p = sqPos(sq);
      slide(mesh, p, p, 420, 0.32);
    }

    // Kamera
    let camAngle = 0;
    function placeCamera(flipped: boolean) {
      const z = flipped ? -1 : 1;
      camera.position.set(0, 14.2, 10 * z);
      controls.target.set(0, 0, 0.45 * z);
      controls.update();
      camAngle = flipped ? Math.PI : 0;
      for (const [sq, m] of meshBySquare) if (game.pieceAt(sq).toLowerCase() !== "n") m.userData.face.rotation.y = camAngle;
    }

    function resize() {
      const w = host.clientWidth, h = host.clientHeight;
      renderer.setSize(w, h, false);
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
    }
    const ro = new ResizeObserver(resize);
    ro.observe(host);
    resize();

    // Antippen: Strahl auf die Felder
    const ray = new THREE.Raycaster();
    let down: { x: number; y: number } | null = null;
    renderer.domElement.addEventListener("pointerdown", (e) => (down = { x: e.clientX, y: e.clientY }));
    renderer.domElement.addEventListener("pointerup", (e) => {
      if (!down || Math.hypot(e.clientX - down.x, e.clientY - down.y) > 8) return;
      const rect = renderer.domElement.getBoundingClientRect();
      ray.setFromCamera(new THREE.Vector2(((e.clientX - rect.left) / rect.width) * 2 - 1, -((e.clientY - rect.top) / rect.height) * 2 + 1), camera);
      // Figuren zuerst (höher als das Feld), dann Felder
      const hitPiece = ray.intersectObjects(pieceGroup.children, true)[0];
      if (hitPiece) {
        let o: THREE.Object3D | null = hitPiece.object;
        while (o && o.parent !== pieceGroup) o = o.parent;
        const sq = [...meshBySquare.entries()].find(([, m]) => m === o)?.[0];
        if (sq) { game.tapSquare(sq); return; }
      }
      const hit = ray.intersectObjects(squareMeshes)[0];
      if (hit) game.tapSquare(hit.object.userData.square);
    });

    // Für Tests: Bildschirmposition eines Feldes
    (window as unknown as { brett3d: unknown }).brett3d = {
      runningAnimations: () => anims.length,
      setSlowMotion: (f: number) => (slowMo = f),
      squareToScreen(sq: string) {
        // Mit Figur auf die Körpermitte zielen: auf dem Bildschirm verdecken vordere Figuren den Fußpunkt.
        const v = sqPos(sq).setY(game.pieceAt(sq) ? 0.45 : 0).project(camera);
        const rect = renderer.domElement.getBoundingClientRect();
        return { x: rect.left + ((v.x + 1) / 2) * rect.width, y: rect.top + ((1 - v.y) / 2) * rect.height };
      },
    };

    rebuildPieces();
    placeCamera(game.flipped);

    let raf = 0;
    const tick = (now: number) => {
      raf = requestAnimationFrame(tick);
      anims = anims.filter((a) => {
        if (now < a.t0) return true;
        const k = Math.min(1, (now - a.t0) / a.dur);
        a.step(k);
        if (k >= 1) { a.done?.(); return false; }
        return true;
      });
      controls.update();
      renderer.render(scene, camera);
    };
    raf = requestAnimationFrame(tick);

    // Auf Zustandsänderungen reagieren
    const stop = $effect.root(() => {
      $effect(() => {
        const fen = game.fen;
        const lm = game.lastMove;
        if (fen === shownFen) return;
        if (lm && meshBySquare.has(lm.from)) animateMove(lm.from, lm.to);
        else rebuildPieces();
      });
      $effect(() => {
        void game.selected; void game.targets; void game.lastMove; void game.topMoves; void game.hintsFresh; void game.fen;
        rebuildMarks();
      });
      $effect(() => {
        void game.plateBump;
        if (game.selected) hopSelected(game.selected);
      });
      $effect(() => placeCamera(game.flipped));
    });

    return () => {
      stop();
      cancelAnimationFrame(raf);
      ro.disconnect();
      controls.dispose();
      renderer.dispose();
      renderer.domElement.remove();
    };
  });
</script>

<div class="stage" bind:this={host} aria-label="3D-Schachbrett, mit dem Finger drehbar" role="img">
  {#if failed}<p class="fail">3D geht auf diesem Gerät nicht, die 2D-Ansicht ist aktiv.</p>{/if}
</div>

<style>
  .stage { width: 100%; height: 100%; position: relative; touch-action: none; }
  .stage :global(canvas) { width: 100% !important; height: 100% !important; display: block; cursor: pointer; }
  .fail { position: absolute; inset: auto 12px 12px; font-size: 0.9rem; }
</style>
