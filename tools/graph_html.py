"""Write .codegraph/graph.html: a file-level import graph that opens without a server."""
import json
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / ".codegraph" / "graph.sqlite"
OUT = ROOT / ".codegraph" / "graph.html"

PAGE = """<!doctype html>
<meta charset="utf-8">
<title>Code graph</title>
<style>
  body { margin: 0; font: 12px system-ui, sans-serif; }
  svg { width: 100vw; height: 100vh; display: block; }
  line { stroke: #bbb; stroke-width: 1; marker-end: url(#arrow); }
  text { pointer-events: none; }
  circle { cursor: grab; stroke: #fff; stroke-width: 1.5; }
</style>
<svg>
  <defs><marker id="arrow" viewBox="0 0 10 10" refX="18" refY="5" markerWidth="6" markerHeight="6" orient="auto">
    <path d="M0 0L10 5L0 10z" fill="#bbb"/></marker></defs>
  <g id="edges"></g><g id="nodes"></g>
</svg>
<script>
const data = __DATA__;
const NS = "http://www.w3.org/2000/svg";
const svg = document.querySelector("svg");
const W = innerWidth, H = innerHeight;
const palette = ["#4e79a7", "#f28e2b", "#59a14f", "#e15759", "#76b7b2", "#b07aa1", "#edc948", "#9c755f"];
const groups = [...new Set(data.nodes.map(n => n.group))];
const byId = new Map();
data.nodes.forEach((n, i) => {
  n.x = W / 2 + 200 * Math.cos(i); n.y = H / 2 + 200 * Math.sin(i); n.vx = n.vy = 0;
  byId.set(n.id, n);
});
const links = data.links.map(([s, t]) => ({ s: byId.get(s), t: byId.get(t) }));

function el(tag, attrs, parent) {
  const e = document.createElementNS(NS, tag);
  for (const k in attrs) e.setAttribute(k, attrs[k]);
  parent.appendChild(e);
  return e;
}
const lineEls = links.map(() => el("line", {}, document.getElementById("edges")));
const nodeEls = data.nodes.map(n => {
  const g = el("g", {}, document.getElementById("nodes"));
  el("circle", { r: 6 + Math.sqrt(n.symbols), fill: palette[groups.indexOf(n.group) % palette.length] }, g);
  const t = el("text", { x: 10, y: 4 }, g);
  t.textContent = n.id;
  el("title", {}, g).textContent = n.symbols + " symbols";
  g.addEventListener("pointerdown", e => { drag = n; g.setPointerCapture(e.pointerId); });
  return g;
});
let drag = null;
svg.addEventListener("pointermove", e => { if (drag) { drag.x = e.clientX; drag.y = e.clientY; drag.vx = drag.vy = 0; alpha = 0.5; } });
svg.addEventListener("pointerup", () => { drag = null; });

let alpha = 1;
function tick() {
  const ns = data.nodes;
  for (const a of ns) for (const b of ns) {
    if (a === b) continue;
    let dx = a.x - b.x, dy = a.y - b.y, d2 = dx * dx + dy * dy + 0.01;
    const f = 2500 / d2;
    a.vx += dx * f * alpha; a.vy += dy * f * alpha;
  }
  for (const l of links) {
    const dx = l.t.x - l.s.x, dy = l.t.y - l.s.y, d = Math.hypot(dx, dy) || 1;
    const f = (d - 90) * 0.02 * alpha;
    l.s.vx += dx / d * f; l.s.vy += dy / d * f;
    l.t.vx -= dx / d * f; l.t.vy -= dy / d * f;
  }
  for (const n of ns) {
    n.vx += (W / 2 - n.x) * 0.002 * alpha; n.vy += (H / 2 - n.y) * 0.002 * alpha;
    if (n !== drag) { n.x += n.vx; n.y += n.vy; }
    n.vx *= 0.8; n.vy *= 0.8;
  }
  links.forEach((l, i) => {
    lineEls[i].setAttribute("x1", l.s.x); lineEls[i].setAttribute("y1", l.s.y);
    lineEls[i].setAttribute("x2", l.t.x); lineEls[i].setAttribute("y2", l.t.y);
  });
  data.nodes.forEach((n, i) => nodeEls[i].setAttribute("transform", `translate(${n.x},${n.y})`));
  alpha = Math.max(alpha * 0.995, 0.02);
  requestAnimationFrame(tick);
}
tick();
</script>
"""


def build() -> dict:
    con = sqlite3.connect(DB)
    counts = dict(con.execute("select file, count(*) from symbols group by file"))
    links = con.execute(
        "select distinct file, target from imports where target <> '' and target <> file"
    ).fetchall()
    files = set(counts) | {f for link in links for f in link}
    nodes = [
        {"id": f, "group": "/".join(f.split("/")[:2]), "symbols": counts.get(f, 0)}
        for f in sorted(files)
    ]
    return {"nodes": nodes, "links": links}


if __name__ == "__main__":
    data = build()
    OUT.write_text(PAGE.replace("__DATA__", json.dumps(data)))
    print(f"{OUT}: {len(data['nodes'])} nodes, {len(data['links'])} links", file=sys.stderr)
