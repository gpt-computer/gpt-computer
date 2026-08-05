import json
import os

from pathlib import Path

from termcolor import colored

from gpt_computer.codemap.models import CodemapResult, SymbolKind


class Visualizer:
    def __init__(self, result: CodemapResult):
        self.result = result
        self.graph = result.graph

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.result.to_dict(), indent=indent)

    def export_json(self, output_path: str) -> str:
        path = Path(output_path)
        path.write_text(self.to_json())
        return str(path.absolute())

    def _build_tree(self) -> dict:
        tree: dict = {}
        for sym in self.graph.get_symbols_by_kind(SymbolKind.FILE):
            rel_path = os.path.relpath(sym.file_path, self.result.config.root_path)
            parts = rel_path.split(os.sep)
            current = tree
            for part in parts[:-1]:
                if part not in current:
                    current[part] = {}
                current = current[part]
            file_key = f"{parts[-1]}"
            file_symbols = self.graph.get_symbols_in_file(sym.file_path)
            file_tree: dict[str, list[str]] = {
                "classes": [],
                "functions": [],
                "methods": [],
            }
            for fs in file_symbols:
                if fs.id == sym.id:
                    continue
                if fs.kind == SymbolKind.CLASS:
                    entry = fs.name
                    if fs.metadata.get("base_classes"):
                        entry += f"({', '.join(fs.metadata['base_classes'])})"
                    file_tree["classes"].append(entry)
                elif fs.kind == SymbolKind.FUNCTION:
                    entry = fs.name
                    if fs.metadata.get("params"):
                        entry += f"({', '.join(fs.metadata['params'])})"
                    file_tree["functions"].append(entry)
            for sym in file_symbols:
                if sym.kind == SymbolKind.METHOD and sym.parent_id:
                    parent = self.graph.get_symbol(sym.parent_id)
                    if parent and parent.kind == SymbolKind.CLASS:
                        cls_name = parent.name
                        if cls_name not in file_tree:
                            file_tree[cls_name + ".methods"] = []
                        entry = sym.name
                        if sym.metadata.get("params"):
                            entry += f"({', '.join(sym.metadata['params'])})"
                        file_tree[cls_name + ".methods"].append(entry)

            current[file_key] = file_tree
        return tree

    def terminal_tree(self) -> str:
        lines: list[str] = []
        root = self.result.config.root_path
        lines.append(colored(f"\nCodemap: {root}", "cyan", attrs=["bold"]))
        lines.append(colored("=" * 60, "cyan"))

        tree = self._build_tree()

        def _render(subtree: dict, prefix: str = "", is_last: bool = True) -> None:
            items = list(subtree.items())
            for i, (key, value) in enumerate(items):
                connector = "└── " if i == len(items) - 1 else "├── "
                if isinstance(value, dict):
                    if any(isinstance(v, dict) for v in value.values()):
                        lines.append(f"{prefix}{connector}{colored(key, 'yellow')}")
                        extension = "    " if i == len(items) - 1 else "│   "
                        _render(value, prefix + extension, i == len(items) - 1)
                    else:
                        file_color = "green"
                        files_count = len(value.get("classes", [])) + len(
                            value.get("functions", [])
                        )
                        lines.append(
                            f"{prefix}{connector}{colored(key, file_color)} "
                            f"({files_count} symbols)"
                        )
                        ext = "    " if i == len(items) - 1 else "│   "
                        for cls in value.get("classes", []):
                            lines.append(
                                f"{prefix}{ext}{colored('└── class ', 'magenta')}{colored(cls, 'white')}"
                            )
                        for fn in value.get("functions", []):
                            lines.append(
                                f"{prefix}{ext}{colored('└── def ', 'blue')}{colored(fn, 'white')}"
                            )

        _render(tree)

        summary = self.result.summary()
        lines.append("")
        lines.append(colored("Summary:", "cyan", attrs=["bold"]))
        lines.append(f"  Files:    {summary['files']}")
        lines.append(f"  Classes:  {summary['classes']}")
        lines.append(f"  Functions: {summary['functions']}")
        lines.append(f"  Methods:  {summary['methods']}")
        lines.append(f"  Imports:  {summary['imports']}")
        lines.append(f"  Total LOC: {self.result.total_lines}")

        return "\n".join(lines)

    def to_html(self, title: str = "Codemap") -> str:
        graph_data = self.graph.to_dict()
        graph_json = json.dumps(graph_data)
        summary = self.result.summary()

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<script src="https://d3js.org/d3.v7.min.js"></script>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0d1117; color: #c9d1d9; }}
.header {{ background: #161b22; border-bottom: 1px solid #30363d; padding: 20px 32px; }}
.header h1 {{ font-size: 24px; color: #58a6ff; }}
.header .subtitle {{ color: #8b949e; font-size: 14px; margin-top: 4px; }}
.container {{ display: flex; height: calc(100vh - 100px); }}
.sidebar {{ width: 320px; background: #161b22; border-right: 1px solid #30363d; overflow-y: auto; padding: 16px; }}
.sidebar h2 {{ font-size: 14px; text-transform: uppercase; color: #8b949e; margin: 12px 0 8px; letter-spacing: 0.5px; }}
.sidebar h2:first-child {{ margin-top: 0; }}
.metric {{ display: flex; justify-content: space-between; padding: 6px 0; border-bottom: 1px solid #21262d; font-size: 13px; }}
.metric .label {{ color: #8b949e; }}
.metric .value {{ color: #f0f6fc; font-weight: 600; }}
.file-list {{ list-style: none; }}
.file-list li {{ padding: 4px 8px; font-size: 12px; cursor: pointer; border-radius: 4px; color: #58a6ff; }}
.file-list li:hover {{ background: #1f2937; }}
.main {{ flex: 1; display: flex; flex-direction: column; }}
.toolbar {{ padding: 8px 16px; background: #161b22; border-bottom: 1px solid #30363d; display: flex; gap: 8px; align-items: center; }}
.toolbar label {{ color: #8b949e; font-size: 12px; }}
.toolbar select {{ background: #0d1117; color: #c9d1d9; border: 1px solid #30363d; padding: 4px 8px; border-radius: 4px; font-size: 12px; }}
#graph {{ flex: 1; }}
.node circle {{ stroke: #fff; stroke-width: 1.5px; cursor: pointer; }}
.node text {{ font-size: 11px; pointer-events: none; fill: #c9d1d9; }}
.link {{ stroke: #30363d; stroke-opacity: 0.6; }}
.link:hover {{ stroke-opacity: 1; }}
.tooltip {{ position: absolute; background: #1f2937; color: #f0f6fc; padding: 8px 12px; border-radius: 6px; font-size: 12px; pointer-events: none; border: 1px solid #30363d; max-width: 300px; display: none; }}
.legend {{ display: flex; gap: 16px; padding: 8px 16px; background: #161b22; border-top: 1px solid #30363d; font-size: 11px; }}
.legend-item {{ display: flex; align-items: center; gap: 4px; }}
.legend-dot {{ width: 10px; height: 10px; border-radius: 50%; }}
</style>
</head>
<body>
<div class="header">
  <h1>{title}</h1>
  <div class="subtitle">{self.result.config.root_path} &mdash; {summary["files"]} files, {summary["total_symbols"]} symbols</div>
</div>
<div class="container">
  <div class="sidebar">
    <h2>Metrics</h2>
    <div class="metric"><span class="label">Files</span><span class="value">{summary["files"]}</span></div>
    <div class="metric"><span class="label">Classes</span><span class="value">{summary["classes"]}</span></div>
    <div class="metric"><span class="label">Functions</span><span class="value">{summary["functions"]}</span></div>
    <div class="metric"><span class="label">Methods</span><span class="value">{summary["methods"]}</span></div>
    <div class="metric"><span class="label">Imports</span><span class="value">{summary["imports"]}</span></div>
    <div class="metric"><span class="label">Relationships</span><span class="value">{summary["relationships"]}</span></div>
    <div class="metric"><span class="label">Total LOC</span><span class="value">{self.result.total_lines}</span></div>
    <h2>Files</h2>
    <ul class="file-list" id="fileList"></ul>
  </div>
  <div class="main">
    <div class="toolbar">
      <label>Layout:</label>
      <select id="layoutSelect">
        <option value="force">Force Directed</option>
        <option value="tree">Radial Tree</option>
      </select>
      <label>Filter:</label>
      <select id="filterSelect">
        <option value="all">All Symbols</option>
        <option value="class">Classes Only</option>
        <option value="function">Functions Only</option>
        <option value="file">Files Only</option>
      </select>
    </div>
    <div id="graph"></div>
    <div class="legend">
      <div class="legend-item"><span class="legend-dot" style="background:#58a6ff"></span> File</div>
      <div class="legend-item"><span class="legend-dot" style="background:#f0883e"></span> Class</div>
      <div class="legend-item"><span class="legend-dot" style="background:#3fb950"></span> Function</div>
      <div class="legend-item"><span class="legend-dot" style="background:#d2a8ff"></span> Method</div>
      <div class="legend-item"><span class="legend-dot" style="background:#ff7b72"></span> Import</div>
      <div class="legend-item"><span style="color:#58a6ff">&#8594;</span> click node for details</div>
    </div>
  </div>
</div>
<div class="tooltip" id="tooltip"></div>

<script>
const graphData = {graph_json};

const colorMap = {{
  file: "#58a6ff",
  class: "#f0883e",
  function: "#3fb950",
  method: "#d2a8ff",
  import: "#ff7b72",
  variable: "#79c0ff",
  constant: "#ffa657",
  module: "#8b949e",
}};

const symbolsMap = graphData.symbols;
const relationships = graphData.relationships;
let nodes = Object.values(symbolsMap).filter(s => s.kind !== 'import');
const links = relationships.map(r => ({{
  source: r.source_id,
  target: r.target_id,
  kind: r.kind,
}}));

const nodeIds = new Set(nodes.map(n => n.id));
const filteredLinks = links.filter(l => nodeIds.has(l.source) && nodeIds.has(l.target));

const width = document.getElementById('graph').clientWidth || 800;
const height = document.getElementById('graph').clientHeight || 600;

const svg = d3.select("#graph")
  .append("svg")
  .attr("width", width)
  .attr("height", height);

const tooltip = document.getElementById('tooltip');

function getColor(kind) {{ return colorMap[kind] || "#8b949e"; }}

function renderForce() {{
  svg.selectAll("*").remove();

  const simulation = d3.forceSimulation(nodes)
    .force("link", d3.forceLink(filteredLinks).id(d => d.id).distance(100))
    .force("charge", d3.forceManyBody().strength(-200))
    .force("center", d3.forceCenter(width / 2, height / 2))
    .force("collision", d3.forceCollide(30));

  const link = svg.append("g")
    .selectAll("line")
    .data(filteredLinks)
    .join("line")
    .attr("class", "link")
    .attr("stroke-width", 1);

  const node = svg.append("g")
    .selectAll("g")
    .data(nodes)
    .join("g")
    .attr("class", "node")
    .call(d3.drag()
      .on("start", (event, d) => {{
        if (!event.active) simulation.alphaTarget(0.3).restart();
        d.fx = d.x;
        d.fy = d.y;
      }})
      .on("drag", (event, d) => {{
        d.fx = event.x;
        d.fy = event.y;
      }})
      .on("end", (event, d) => {{
        if (!event.active) simulation.alphaTarget(0);
        d.fx = null;
        d.fy = null;
      }}));

  node.append("circle")
    .attr("r", d => d.kind === 'file' ? 8 : d.kind === 'class' ? 6 : 4)
    .attr("fill", d => getColor(d.kind))
    .on("mouseover", (event, d) => {{
      tooltip.style.display = "block";
      tooltip.innerHTML = `<strong>${{d.name}}</strong><br>kind: ${{d.kind}}<br>file: ${{d.file_path.split('/').pop()}}<br>line: ${{d.line_start}}-${{d.line_end}}`;
      tooltip.style.left = (event.pageX + 12) + "px";
      tooltip.style.top = (event.pageY - 10) + "px";
    }})
    .on("mouseout", () => {{ tooltip.style.display = "none"; }});

  node.append("text")
    .text(d => d.name.length > 18 ? d.name.slice(0, 16) + '..' : d.name)
    .attr("x", d => (d.kind === 'file' ? 12 : 10))
    .attr("y", 4);

  simulation.on("tick", () => {{
    link.attr("x1", d => d.source.x)
      .attr("y1", d => d.source.y)
      .attr("x2", d => d.target.x)
      .attr("y2", d => d.target.y);
    node.attr("transform", d => `translate(${{d.x}},${{d.y}})`);
  }});
}}

function renderTree() {{
  svg.selectAll("*").remove();

  const root = d3.hierarchy({{children: nodes.map(n => ({{...n, children: []}}))}}, d => d.children);
  const treeLayout = d3.tree().size([width - 100, height - 100]);
  treeLayout(root);

  const g = svg.append("g").attr("transform", "translate(50,50)");

  g.selectAll("line")
    .data(root.links())
    .join("line")
    .attr("class", "link")
    .attr("x1", d => d.source.x)
    .attr("y1", d => d.source.y)
    .attr("x2", d => d.target.x)
    .attr("y2", d => d.target.y);

  g.selectAll("g")
    .data(root.descendants())
    .join("g")
    .attr("transform", d => `translate(${{d.x}},${{d.y}})`)
    .append("circle")
    .attr("r", 4)
    .attr("fill", d => getColor(d.data.kind));
}}

renderForce();

document.getElementById('layoutSelect').addEventListener('change', function() {{
  if (this.value === 'force') renderForce();
  else renderTree();
}});

document.getElementById('filterSelect').addEventListener('change', function() {{
  const val = this.value;
  if (val === 'all') {{
    nodes = Object.values(symbolsMap).filter(s => s.kind !== 'import');
  }} else if (val === 'class') {{
    nodes = Object.values(symbolsMap).filter(s => s.kind === 'class' || s.kind === 'file');
  }} else if (val === 'function') {{
    nodes = Object.values(symbolsMap).filter(s => s.kind === 'function' || s.kind === 'method' || s.kind === 'file');
  }} else if (val === 'file') {{
    nodes = Object.values(symbolsMap).filter(s => s.kind === 'file');
  }}
  const nIds = new Set(nodes.map(n => n.id));
  filteredLinks.length = 0;
  links.forEach(l => {{ if (nIds.has(l.source) && nIds.has(l.target)) filteredLinks.push(l); }});
  const layout = document.getElementById('layoutSelect').value;
  if (layout === 'force') renderForce();
  else renderTree();
}});

const fileList = document.getElementById('fileList');
Object.values(symbolsMap).filter(s => s.kind === 'file').forEach(f => {{
  const li = document.createElement('li');
  li.textContent = f.file_path.split('/').pop();
  li.onclick = () => {{
    nodes = Object.values(symbolsMap).filter(s => s.file_path === f.file_path);
    const nIds = new Set(nodes.map(n => n.id));
    filteredLinks.length = 0;
    links.forEach(l => {{ if (nIds.has(l.source) && nIds.has(l.target)) filteredLinks.push(l); }});
    renderForce();
  }};
  fileList.appendChild(li);
}});
</script>
</body>
</html>"""
        return html

    def export_html(self, output_path: str, title: str = "Codemap") -> str:
        path = Path(output_path)
        path.write_text(self.to_html(title))
        return str(path.absolute())
