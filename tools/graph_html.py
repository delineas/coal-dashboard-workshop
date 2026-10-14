"""Write .codegraph/graph.html: the app flow (route -> page -> API -> endpoint -> table, and tests) drawn with Cytoscape.js.

The page needs network access once, to load Cytoscape.js from cdnjs.
"""
import json
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from codegraph import DB_PATH, ROOT, app_flow  # noqa: E402

OUT = ROOT / ".codegraph" / "graph.html"

PAGE = """<!doctype html>
<meta charset="utf-8">
<title>Code graph · app flow</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/cytoscape/3.30.2/cytoscape.min.js"></script>
<style>
  body { margin: 0; padding: 24px; font: 14px system-ui, sans-serif; background: #f4f5f2; color: #1d2b2e; }
  h1 { margin: 0 0 4px; font-size: 20px; }
  .bar { display: flex; flex-wrap: wrap; gap: 8px 16px; align-items: center; margin: 12px 0; }
  .bar button { padding: 4px 12px; border: 1px solid #9aa; border-radius: 6px; background: #fff; cursor: pointer; }
  .bar button.on { background: #1d2b2e; color: #fff; }
  .bar label { display: flex; gap: 6px; align-items: center; }
  .key { display: inline-block; width: 12px; height: 12px; border-radius: 3px; }
  .wrap { display: flex; gap: 16px; }
  #cy { flex: 1; height: 640px; max-width: 1200px; background: #fff; border: 1px solid #c9d1cf; border-radius: 10px; }
  #info { width: 280px; font-size: 13px; line-height: 1.5; }
  #info code { font-size: 12px; }
</style>
<h1>App flow</h1>
<div>Scroll to zoom, drag to move. Click a node to light up what it touches; click the background to clear.</div>
<div class="bar" id="bar">
  <button data-layout="breadthfirst" class="on">Tree</button>
  <button data-layout="cose">Forces</button>
  <button id="fit">Fit</button>
  <input id="q" placeholder="Find a node…">
</div>
<div class="bar" id="kinds"></div>
<div class="wrap"><div id="cy"></div><div id="info"></div></div>
<script>
const data = __DATA__;
const COLORS = { route: "#1d2b2e", page: "#c96043", component: "#d49369", api: "#c79a21", endpoint: "#3f8f8a", table: "#75b7b2", test: "#9aa5a3" };
const SHAPES = { route: "round-tag", page: "round-rectangle", component: "round-rectangle", api: "round-rectangle", endpoint: "round-rectangle", table: "barrel", test: "ellipse" };
const cy = cytoscape({
  container: document.getElementById("cy"),
  elements: [
    ...data.nodes.map(n => ({ data: n })),
    ...data.edges.map(([s, rel, t], i) => ({ data: { id: "e" + i, source: s, target: t, rel } })),
  ],
  wheelSensitivity: 0.3,
  minZoom: 0.2,
  maxZoom: 3,
  style: [
    { selector: "node", style: {
      label: "data(label)", "font-size": 13, "text-valign": "center", "text-halign": "center", "text-wrap": "wrap", "text-max-width": 140,
      shape: e => SHAPES[e.data("kind")], "background-color": e => COLORS[e.data("kind")],
      color: e => ["route", "page", "endpoint"].includes(e.data("kind")) ? "#fff" : "#1d2b2e",
      width: "label", height: "label", padding: 8 } },
    { selector: "edge", style: {
      width: 1.5, "line-color": "#b8c2c0", "target-arrow-color": "#b8c2c0", "target-arrow-shape": "triangle", "curve-style": "bezier" } },
    { selector: ".faded", style: { opacity: 0.12 } },
    { selector: ".hit", style: { "border-width": 3, "border-color": "#c79a21" } },
  ],
});

let current = "breadthfirst";
function layout(name, animate = true) {
  current = name;
  const shown = cy.elements(":visible");
  const roots = shown.nodes('[kind = "route"], [kind = "test"]');
  shown.layout(name === "breadthfirst"
    ? { name, directed: true, roots, spacingFactor: 0.9, animate, animationDuration: 400, fit: true, padding: 30 }
    : { name, animate, animationDuration: 400, nodeRepulsion: 9000, idealEdgeLength: 90, fit: true, padding: 30 }).run();
}
document.querySelectorAll("[data-layout]").forEach(b => b.onclick = () => {
  document.querySelectorAll("[data-layout]").forEach(x => x.classList.toggle("on", x === b));
  layout(b.dataset.layout);
});
document.getElementById("fit").onclick = () => cy.animate({ fit: { padding: 30 } });

// Start with the main path only: tests and the components that call no API wait behind a checkbox.
const onPath = cy.nodes('[kind = "component"]').filter(n => n.outgoers('edge[rel = "calls"]').length > 0);
const hidden = { test: true, component: true };
function visible() {
  cy.nodes().forEach(n => {
    const k = n.data("kind");
    const show = !hidden[k] || (k === "component" && onPath.contains(n) && !hidden.allComponents);
    n.style("display", show ? "element" : "none");
  });
}
const kinds = document.getElementById("kinds");
const boxes = [["tests", "test", COLORS.test], ["all components", "component", COLORS.component]];
boxes.forEach(([text, k, color]) => {
  const n = cy.nodes(`[kind = "${k}"]`).length;
  const label = document.createElement("label");
  label.innerHTML = `<input type="checkbox"><span class="key" style="background:${color}"></span>show ${text} (${n})`;
  label.querySelector("input").onchange = e => {
    hidden[k] = !e.target.checked;
    if (k === "component") hidden.allComponents = false;
    visible(); layout(current);
  };
  kinds.appendChild(label);
});
const legend = document.createElement("span");
legend.innerHTML = Object.entries(COLORS).map(([k, c]) => `<span class="key" style="background:${c}"></span> ${k}`).join(" &nbsp; ");
kinds.appendChild(legend);

const info = document.getElementById("info");
cy.on("tap", "node", e => {
  const n = e.target, near = n.closedNeighborhood();
  cy.elements().addClass("faded"); near.removeClass("faded");
  const list = rel => n.connectedEdges(`[rel = "${rel}"]`).map(x => (x.source() === n ? x.target() : x.source()).data("label"));
  info.innerHTML = `<b>${n.data("label")}</b> · ${n.data("kind")}<br><code>${n.data("loc") || ""}</code><br>` +
    ["shows", "renders", "calls", "requests", "reads", "tests"].map(r => list(r).length ? `<br><b>${r}</b>: ${list(r).join(", ")}` : "").join("");
});
cy.on("tap", e => { if (e.target === cy) { cy.elements().removeClass("faded"); info.innerHTML = ""; } });
document.getElementById("q").oninput = e => {
  cy.nodes().removeClass("hit");
  const q = e.target.value.toLowerCase();
  if (q) cy.nodes().filter(n => n.data("label").toLowerCase().includes(q)).addClass("hit");
};
visible();
layout("breadthfirst", false);
</script>
"""


def build() -> dict:
    with sqlite3.connect(DB_PATH) as db:
        nodes, edges = app_flow(db)
    return {
        "nodes": [{"id": key, "kind": kind, "label": label, "loc": loc} for key, (kind, label, loc) in nodes.items()],
        "edges": edges,
    }


if __name__ == "__main__":
    data = build()
    OUT.write_text(PAGE.replace("__DATA__", json.dumps(data)))
    print(f"{OUT}: {len(data['nodes'])} nodes, {len(data['edges'])} edges", file=sys.stderr)
