import json

from typing import Any, Dict, List

from gpt_computer.repository_intelligence.models import (
    EdgeType,
    NodeType,
    RepositoryAnalysis,
    SemanticEdge,
    SemanticGraph,
    SemanticNode,
)


class VisualizationAgent:
    def __init__(self):
        self.visualizations: Dict[str, Dict[str, Any]] = {}

    def create_graph_visualization(
        self, analysis: RepositoryAnalysis
    ) -> Dict[str, Any]:
        graph_config = {
            "title": f"Repository Architecture - {analysis.files_analyzed} files",
            "nodes": self._prepare_nodes_for_visualization(analysis.semantic_graph),
            "edges": self._prepare_edges_for_visualization(analysis.semantic_graph),
            "layout": self._determine_layout(analysis),
            "styling": self._get_styling_config(analysis),
            "interactivity": self._get_interactivity_config(),
            "metrics": self._get_visualization_metrics(analysis),
        }

        return graph_config

    def _prepare_nodes_for_visualization(
        self, semantic_graph: SemanticGraph
    ) -> List[Dict[str, Any]]:
        nodes = []

        for node in semantic_graph.nodes.values():
            node_config = {
                "id": node.id,
                "label": node.name,
                "type": node.node_type.value,
                "file_path": node.file_path,
                "qualified_name": node.qualified_name,
                "position": self._calculate_node_position(node),
                "size": self._calculate_node_size(node),
                "color": self._get_node_color(node),
                "tooltip": self._generate_node_tooltip(node),
                "metadata": {
                    "complexity": node.complexity,
                    "lines_of_code": node.lines_of_code,
                    "cyclomatic_complexity": node.cyclomatic_complexity,
                    "docstring": node.docstring[:100] if node.docstring else "",
                    "signature": node.signature,
                },
            }

            nodes.append(node_config)

        return nodes

    def _prepare_edges_for_visualization(
        self, semantic_graph: SemanticGraph
    ) -> List[Dict[str, Any]]:
        edges = []

        for edge in semantic_graph.edges:
            source = semantic_graph.get_node(edge.source_id)
            target = semantic_graph.get_node(edge.target_id)

            if source and target:
                edge_config = {
                    "id": edge.id,
                    "source": edge.source_id,
                    "target": edge.target_id,
                    "type": edge.edge_type.value,
                    "label": self._get_edge_label(edge),
                    "weight": edge.weight,
                    "color": self._get_edge_color(edge),
                    "width": self._calculate_edge_width(edge),
                    "tooltip": self._generate_edge_tooltip(edge, source, target),
                }

                edges.append(edge_config)

        return edges

    def _calculate_node_position(self, node: SemanticNode) -> Dict[str, float]:
        position = {
            "x": 0.0,
            "y": 0.0,
        }

        if node.node_type == NodeType.FILE:
            position["x"] = 0.0
            position["y"] = 0.0
        elif node.node_type == NodeType.CLASS:
            position["x"] = 100.0
            position["y"] = 100.0
        elif node.node_type == NodeType.FUNCTION:
            position["x"] = 200.0
            position["y"] = 200.0
        elif node.node_type == NodeType.METHOD:
            position["x"] = 300.0
            position["y"] = 300.0
        else:
            position["x"] = 400.0
            position["y"] = 400.0

        return position

    def _calculate_node_size(self, node: SemanticNode) -> float:
        base_size = 10.0

        if node.node_type == NodeType.CLASS:
            return base_size + node.complexity * 2
        elif node.node_type == NodeType.FUNCTION:
            return base_size + node.lines_of_code / 5
        elif node.node_type == NodeType.METHOD:
            return base_size + node.complexity
        else:
            return base_size

    def _get_node_color(self, node: SemanticNode) -> str:
        color_map = {
            NodeType.FILE: "#3498db",
            NodeType.CLASS: "#e74c3c",
            NodeType.FUNCTION: "#2ecc71",
            NodeType.METHOD: "#f39c12",
            NodeType.IMPORT: "#95a5a6",
            NodeType.VARIABLE: "#34495e",
            NodeType.INTERFACE: "#16a085",
            NodeType.ENUM: "#d35400",
            NodeType.CONSTANT: "#c0392b",
            NodeType.MODULE: "#7f8c8d",
            NodeType.PACKAGE: "#8e44ad",
        }

        return color_map.get(node.node_type, "#95a5a6")

    def _generate_node_tooltip(self, node: SemanticNode) -> str:
        tooltip = f"<strong>{node.name}</strong><br>"
        tooltip += f"Type: {node.node_type.value}<br>"
        tooltip += f"File: {node.file_path}<br>"
        tooltip += f"Lines: {node.line_start}-{node.line_end}<br>"
        tooltip += f"Complexity: {node.complexity}<br>"
        tooltip += f"LOC: {node.lines_of_code}<br>"

        if node.docstring:
            tooltip += f"Doc: {node.docstring[:100]}...<br>"

        if node.signature:
            tooltip += f"Signature: {node.signature}<br>"

        return tooltip

    def _get_edge_label(self, edge: SemanticEdge) -> str:
        labels = {
            EdgeType.IMPORTS: "→",
            EdgeType.CALLS: "calls",
            EdgeType.INHERITS: "inherits",
            EdgeType.CONTAINS: "contains",
            EdgeType.IMPLEMENTS: "implements",
            EdgeType.DECORATES: "decorates",
            EdgeType.ACCESSES: "accesses",
            EdgeType.RETURNS: "returns",
            EdgeType.PARAMETERS: "params",
            EdgeType.DATA_FLOW: "→",
            EdgeType.CONTROL_FLOW: "→",
        }

        return labels.get(edge.edge_type, "")

    def _get_edge_color(self, edge: SemanticEdge) -> str:
        color_map = {
            EdgeType.IMPORTS: "#95a5a6",
            EdgeType.CALLS: "#3498db",
            EdgeType.INHERITS: "#e74c3c",
            EdgeType.CONTAINS: "#2ecc71",
            EdgeType.IMPLEMENTS: "#f39c12",
            EdgeType.DECORATES: "#9b59b6",
            EdgeType.ACCESSES: "#34495e",
            EdgeType.RETURNS: "#16a085",
            EdgeType.PARAMETERS: "#d35400",
            EdgeType.DATA_FLOW: "#e67e22",
            EdgeType.CONTROL_FLOW: "#e74c3c",
        }

        return color_map.get(edge.edge_type, "#95a5a6")

    def _calculate_edge_width(self, edge: SemanticEdge) -> float:
        return 1.0 + edge.weight * 2

    def _generate_edge_tooltip(
        self, edge: SemanticEdge, source: SemanticNode, target: SemanticNode
    ) -> str:
        tooltip = f"<strong>{source.name}</strong> {edge.edge_type.value} <strong>{target.name}</strong><br>"
        tooltip += f"Type: {edge.edge_type.value}<br>"
        tooltip += f"Weight: {edge.weight}<br>"

        return tooltip

    def _determine_layout(self, analysis: RepositoryAnalysis) -> Dict[str, Any]:
        return {
            "type": "force-directed",
            "charge": -100,
            "link_distance": 100,
            "gravity": 0.1,
        }

    def _get_styling_config(self, analysis: RepositoryAnalysis) -> Dict[str, Any]:
        return {
            "background_color": "#1e1e1e",
            "grid_enabled": True,
            "node_labels": True,
            "edge_labels": False,
            "tooltip_enabled": True,
            "animation_enabled": True,
        }

    def _get_interactivity_config(self) -> Dict[str, Any]:
        return {
            "node_click": "show_details",
            "node_hover": "show_tooltip",
            "edge_click": "show_relationship",
            "filter_by_type": True,
            "search_enabled": True,
            "export_enabled": True,
        }

    def _get_visualization_metrics(
        self, analysis: RepositoryAnalysis
    ) -> Dict[str, Any]:
        return {
            "total_nodes": len(analysis.semantic_graph.nodes),
            "total_edges": len(analysis.semantic_graph.edges),
            "files_count": len(
                [
                    n
                    for n in analysis.semantic_graph.nodes.values()
                    if n.node_type == NodeType.FILE
                ]
            ),
            "classes_count": len(
                [
                    n
                    for n in analysis.semantic_graph.nodes.values()
                    if n.node_type == NodeType.CLASS
                ]
            ),
            "functions_count": len(
                [
                    n
                    for n in analysis.semantic_graph.nodes.values()
                    if n.node_type == NodeType.FUNCTION
                ]
            ),
            "methods_count": len(
                [
                    n
                    for n in analysis.semantic_graph.nodes.values()
                    if n.node_type == NodeType.METHOD
                ]
            ),
        }

    def create_html_visualization(
        self, analysis: RepositoryAnalysis, output_path: str
    ) -> str:
        graph_config = self.create_graph_visualization(analysis)

        # Escape braces in JavaScript template literals
        graph_config_json = (
            json.dumps(graph_config).replace("{", "{{").replace("}", "}}")
        )

        # Use format() to insert values safely
        html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background-color: #1e1e1e;
            color: #e0e0e0;
            margin: 0;
            padding: 20px;
        }}
        .container {{
            width: 100%;
            height: 800px;
            border: 1px solid #333;
            border-radius: 8px;
            background-color: #252525;
        }}
        .controls {{
            margin-bottom: 20px;
            display: flex;
            gap: 10px;
        }}
        .control-btn {{
            padding: 8px 16px;
            background-color: #333;
            color: #e0e0e0;
            border: 1px solid #555;
            border-radius: 4px;
            cursor: pointer;
        }}
        .control-btn:hover {{
            background-color: #444;
        }}
        .info-panel {{
            margin-top: 20px;
            padding: 15px;
            background-color: #2d2d2d;
            border-radius: 8px;
            border: 1px solid #444;
        }}
        .metric-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 10px;
            margin-top: 10px;
        }}
        .metric-card {{
            padding: 10px;
            background-color: #333;
            border-radius: 4px;
            text-align: center;
        }}
        .metric-value {{
            font-size: 24px;
            font-weight: bold;
            color: #4a9eff;
        }}
        .metric-label {{
            font-size: 12px;
            color: #aaa;
        }}
    </style>
</head>
<body>
    <h1>{title}</h1>

    <div class="controls">
        <button class="control-btn" onclick="toggleNodeLabels()">Toggle Labels</button>
        <button class="control-btn" onclick="toggleEdgeLabels()">Toggle Edge Labels</button>
        <button class="control-btn" onclick="changeLayout('force')">Force Layout</button>
        <button class="control-btn" onclick="changeLayout('tree')">Tree Layout</button>
        <button class="control-btn" onclick="exportGraph()">Export Graph</button>
    </div>

    <div id="graph" class="container"></div>

    <div class="info-panel">
        <h3>Graph Metrics</h3>
        <div class="metric-grid">
            <div class="metric-card">
                <div class="metric-value">{total_nodes}</div>
                <div class="metric-label">Total Nodes</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{total_edges}</div>
                <div class="metric-label">Total Edges</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{files_count}</div>
                <div class="metric-label">Files</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{classes_count}</div>
                <div class="metric-label">Classes</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{functions_count}</div>
                <div class="metric-label">Functions</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{methods_count}</div>
                <div class="metric-label">Methods</div>
            </div>
        </div>
    </div>

    <script>
        const graphData = {graph_config_json};

        const width = document.getElementById('graph').clientWidth;
        const height = document.getElementById('graph').clientHeight;

        const svg = d3.select("#graph").append("svg").attr("width", width).attr("height", height);

        const nodes = graphData.nodes.map(n => Object.assign({}, n));
        const edges = graphData.edges.map(e => Object.assign({}, e));

        const simulation = d3.forceSimulation(nodes)
            .force("link", d3.forceLink(edges).id(d => d.id).distance(100))
            .force("charge", d3.forceManyBody().strength(-200))
            .force("center", d3.forceCenter(width / 2, height / 2))
            .force("collision", d3.forceCollide(10));

        const link = svg.append("g")
            .selectAll("line")
            .data(edges)
            .enter().append("line")
            .attr("stroke", d => d.color)
            .attr("stroke-width", d => d.width)
            .on("click", (event, d) => showEdgeDetails(d));

        const node = svg.append("g")
            .selectAll("circle")
            .data(nodes)
            .enter().append("circle")
            .attr("r", d => d.size / 10)
            .attr("fill", d => d.color)
            .on("click", (event, d) => showNodeDetails(d))
            .on("mouseover", (event, d) => showTooltip(d, event))
            .on("mouseout", () => hideTooltip());

        node.append("text")
            .text(d => d.label)
            .attr("text-anchor", "middle")
            .attr("dy", "0.35em")
            .style("font-size", "12px")
            .style("fill", "#fff")
            .style("display", d => d.showLabel ? "block" : "none");

        simulation.on("tick", () => {{
            link.attr("x1", d => d.source.x)
                .attr("y1", d => d.source.y)
                .attr("x2", d => d.target.x)
                .attr("y2", d => d.target.y);

            node.attr("transform", d => `translate(${{d.x}},${{d.y}})`);
        }});

        function toggleNodeLabels() {{
            nodes.forEach(n => n.showLabel = !n.showLabel);
            node.selectAll("text").style("display", d => d.showLabel ? "block" : "none");
        }}

        function toggleEdgeLabels() {{
            link.selectAll("text").style("display", d => d.showLabel ? "block" : "none");
        }}

        function changeLayout(type) {{
            if (type === 'force') {{
                simulation.force("link", d3.forceLink(edges).id(d => d.id).distance(100));
                simulation.force("charge", d3.forceManyBody().strength(-200));
            }} else if (type === 'tree') {{
                // Tree layout implementation would go here
                console.log("Tree layout not implemented yet");
            }}
            simulation.restart();
        }}

        function showNodeDetails(node) {{
            console.log("Node details:", node);
            // Show node details in a panel
        }}

        function showEdgeDetails(edge) {{
            console.log("Edge details:", edge);
            // Show edge details in a panel
        }}

        function showTooltip(node, event) {{
            const tooltip = document.createElement("div");
            tooltip.style.position = "absolute";
            tooltip.style.backgroundColor = "#333";
            tooltip.style.color = "#fff";
            tooltip.style.padding = "10px";
            tooltip.style.borderRadius = "4px";
            tooltip.style.pointerEvents = "none";
            tooltip.innerHTML = node.tooltip;

            document.body.appendChild(tooltip);

            tooltip.style.left = (event.pageX + 10) + "px";
            tooltip.style.top = (event.pageY + 10) + "px";
        }}

        function hideTooltip() {{
            const tooltips = document.querySelectorAll("div[style*='position: absolute']");
            tooltips.forEach(t => t.remove());
        }}

        function exportGraph() {{
            const data = {{
                nodes: nodes,
                edges: edges,
                metadata: graphData
            }};

            const blob = new Blob([JSON.stringify(data, null, 2)], {{ type: 'application/json' }});
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'repository-graph.json';
            a.click();
            URL.revokeObjectURL(url);
        }}
    </script>
</body>
</html>
        """

        html_template = html_template.format(
            title=graph_config["title"],
            total_nodes=graph_config["metrics"]["total_nodes"],
            total_edges=graph_config["metrics"]["total_edges"],
            files_count=graph_config["metrics"]["files_count"],
            classes_count=graph_config["metrics"]["classes_count"],
            functions_count=graph_config["metrics"]["functions_count"],
            methods_count=graph_config["metrics"]["methods_count"],
            graph_config_json=graph_config_json,
        )

        with open(output_path, "w") as f:
            f.write(html_template)

        return output_path

    def create_terminal_visualization(self, analysis: RepositoryAnalysis) -> str:
        lines = []
        lines.append("=" * 60)
        lines.append(f"Repository Architecture: {analysis.files_analyzed} files")
        lines.append("=" * 60)

        files = [
            n
            for n in analysis.semantic_graph.nodes.values()
            if n.node_type == NodeType.FILE
        ]
        for file in files:
            lines.append(f"\n{file.qualified_name}")
            lines.append("-" * 40)

            classes = [
                n
                for n in analysis.semantic_graph.nodes.values()
                if n.node_type == NodeType.CLASS and n.file_path == file.file_path
            ]
            for cls in classes:
                lines.append(f"  class {cls.name}")
                methods = [
                    n
                    for n in analysis.semantic_graph.nodes.values()
                    if n.node_type == NodeType.METHOD and n.parent_id == cls.id
                ]
                for method in methods[:5]:
                    lines.append(f"    def {method.name}()")
                if len(methods) > 5:
                    lines.append(f"    ... {len(methods) - 5} more methods")

            functions = [
                n
                for n in analysis.semantic_graph.nodes.values()
                if n.node_type == NodeType.FUNCTION and n.file_path == file.file_path
            ]
            for fn in functions[:3]:
                lines.append(f"  def {fn.name}()")

        lines.append("\n" + "=" * 60)
        lines.append("Summary:")
        lines.append(f"  Total Symbols: {analysis.total_symbols}")
        lines.append(
            f"  Classes: {len([n for n in analysis.semantic_graph.nodes.values() if n.node_type == NodeType.CLASS])}"
        )
        lines.append(
            f"  Functions: {len([n for n in analysis.semantic_graph.nodes.values() if n.node_type == NodeType.FUNCTION])}"
        )
        lines.append(
            f"  Methods: {len([n for n in analysis.semantic_graph.nodes.values() if n.node_type == NodeType.METHOD])}"
        )
        lines.append(f"  Relationships: {len(analysis.semantic_graph.edges)}")

        return "\n".join(lines)
