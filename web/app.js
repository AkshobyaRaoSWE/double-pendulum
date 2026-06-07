"use strict";

// Double-pendulum chaos visualizer. Fetches an ensemble of pendulum
// trajectories from the Python backend (/api/simulate) and animates them on a
// canvas, each ghost a slightly different hue, each tip leaving a fading trail.
// They start as one and visibly peel apart -- that's the chaos.

const canvas = document.getElementById("pend");
const ctx = canvas.getContext("2d");

let data = null;
let frame = 0;
let trails = [];      // one array of recent tip points per pendulum
let raf = null;

const ORIGIN = { x: canvas.width / 2, y: canvas.height * 0.36 };

function hue(k, n) {
  return `hsl(${Math.round((280 + (k / Math.max(n - 1, 1)) * 140) % 360)}, 85%, 62%)`;
}

function project(x, y, scale) {
  // physics y is up; canvas y is down
  return { x: ORIGIN.x + x * scale, y: ORIGIN.y - y * scale };
}

function step() {
  if (!data) return;
  const n = data.pendulums.length;
  const scale = (canvas.height * 0.30) / data.reach;

  // Fade the previous frame slightly for motion-blur trails.
  ctx.fillStyle = "rgba(6, 7, 11, 0.18)";
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  for (let k = 0; k < n; k++) {
    const pen = data.pendulums[k];
    const j1 = project(pen.x1[frame], pen.y1[frame], scale);
    const j2 = project(pen.x2[frame], pen.y2[frame], scale);
    const color = hue(k, n);

    // tip trail
    trails[k].push(j2);
    if (trails[k].length > 90) trails[k].shift();
    ctx.beginPath();
    for (let i = 0; i < trails[k].length; i++) {
      const t = trails[k][i];
      if (i === 0) ctx.moveTo(t.x, t.y); else ctx.lineTo(t.x, t.y);
    }
    ctx.strokeStyle = color;
    ctx.globalAlpha = 0.35;
    ctx.lineWidth = 1.5;
    ctx.stroke();
    ctx.globalAlpha = 1;

    // rods + bobs (draw the first pendulum brightest)
    ctx.lineWidth = k === 0 ? 3 : 1.5;
    ctx.strokeStyle = color;
    ctx.beginPath();
    ctx.moveTo(ORIGIN.x, ORIGIN.y);
    ctx.lineTo(j1.x, j1.y);
    ctx.lineTo(j2.x, j2.y);
    ctx.stroke();

    ctx.fillStyle = color;
    ctx.beginPath(); ctx.arc(j2.x, j2.y, k === 0 ? 6 : 4, 0, 2 * Math.PI); ctx.fill();
    if (k === 0) {
      ctx.beginPath(); ctx.arc(j1.x, j1.y, 5, 0, 2 * Math.PI); ctx.fill();
    }
  }

  // pivot
  ctx.fillStyle = "#3a3f52";
  ctx.beginPath(); ctx.arc(ORIGIN.x, ORIGIN.y, 4, 0, 2 * Math.PI); ctx.fill();

  const seconds = (frame * data.frame_dt).toFixed(1);
  document.getElementById("hint").textContent =
    `${data.pendulums.length} pendulums | t = ${seconds}s`;

  frame++;
  if (frame >= data.frames) frame = data.frames - 1; // hold on last frame
  else raf = requestAnimationFrame(step);
}

function play(d) {
  data = d;
  frame = 0;
  trails = d.pendulums.map(() => []);
  ctx.fillStyle = "#06070b";
  ctx.fillRect(0, 0, canvas.width, canvas.height);
  if (raf) cancelAnimationFrame(raf);
  raf = requestAnimationFrame(step);
}

async function run() {
  const params = new URLSearchParams({
    th1: document.getElementById("th1").value,
    th2: document.getElementById("th2").value,
    m2: document.getElementById("m2").value,
    l2: document.getElementById("l2").value,
    ghosts: document.getElementById("ghosts").value,
  });
  document.getElementById("hint").textContent = "integrating...";
  try {
    const res = await fetch("/api/simulate?" + params);
    if (!res.ok) throw new Error((await res.json()).error || "request failed");
    play(await res.json());
  } catch (err) {
    // Static-hosting fallback: the pre-generated default ensemble.
    try {
      const res = await fetch("data.json");
      play(await res.json());
      document.getElementById("hint").textContent =
        "default run (start server.py for live parameters)";
    } catch {
      document.getElementById("hint").textContent = "error: " + err.message;
    }
  }
}

["th1", "th2", "m2", "l2", "ghosts"].forEach((id) => {
  const el = document.getElementById(id);
  const out = document.getElementById(id + "Out");
  el.addEventListener("input", () => { out.textContent = el.value; });
});
document.getElementById("run").addEventListener("click", run);
document.getElementById("replay").addEventListener("click", () => { if (data) play(data); });

run();
