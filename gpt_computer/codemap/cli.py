import os
import webbrowser

from pathlib import Path

import typer

from termcolor import colored

from gpt_computer.codemap.analyzer import PythonAnalyzer
from gpt_computer.codemap.graph import GraphBuilder
from gpt_computer.codemap.models import CodemapConfig
from gpt_computer.codemap.visualizer import Visualizer

app = typer.Typer(help="Codemap: analyze and visualize code structure")


@app.command()
def analyze(
    path: str = typer.Argument(".", help="Path to project or file to analyze"),
    output: str = typer.Option(
        "", "--output", "-o", help="Output file for JSON export"
    ),
    exclude: list[str] = typer.Option(
        ["__pycache__", ".git", "node_modules", "venv", ".venv"],
        "--exclude",
        "-e",
        help="Patterns to exclude",
    ),
    include: list[str] = typer.Option(
        ["*.py"], "--include", "-i", help="Patterns to include"
    ),
):
    """Analyze a Python project and extract its code graph."""
    config = CodemapConfig(
        root_path=os.path.abspath(path),
        include_patterns=include,
        exclude_patterns=exclude,
    )
    analyzer = PythonAnalyzer(config)
    result = analyzer.analyze()

    if result.errors:
        for err in result.errors[:10]:
            typer.echo(colored(f"  {err}", "yellow"))

    builder = GraphBuilder(result)
    builder.build()

    visualizer = Visualizer(result)
    typer.echo(visualizer.terminal_tree())

    if output:
        out_path = visualizer.export_json(output)
        typer.echo(colored(f"\nJSON exported to: {out_path}", "green"))

    cycles = builder.detect_circular_dependencies()
    if cycles:
        typer.echo(
            colored(f"\nWarning: {len(cycles)} circular dependencies detected!", "red")
        )
        for cycle in cycles[:5]:
            typer.echo(f"  {' -> '.join(cycle)}")


@app.command()
def view(
    path: str = typer.Argument(".", help="Path to project or codemap JSON"),
    output: str = typer.Option(
        "codemap.html", "--output", "-o", help="Output HTML file"
    ),
    open_browser: bool = typer.Option(
        True, "--open/--no-open", help="Open in browser automatically"
    ),
    title: str = typer.Option("Codemap", "--title", "-t", help="Page title"),
):
    """Generate an interactive HTML visualization of the codebase."""
    if path.endswith(".json"):
        import json

        with open(path) as f:
            data = json.load(f)
        from gpt_computer.codemap.models import CodeGraph, CodemapResult

        graph = CodeGraph.from_dict(data.get("graph", {}))
        config = CodemapConfig(root_path=data.get("config", {}).get("root_path", "."))
        result = CodemapResult(graph=graph, config=config)
        result.files_analyzed = data.get("config", {}).get("files_analyzed", 0)
        result.total_lines = data.get("config", {}).get("total_lines", 0)
    else:
        config = CodemapConfig(root_path=os.path.abspath(path))
        analyzer = PythonAnalyzer(config)
        result = analyzer.analyze()
        builder = GraphBuilder(result)
        builder.build()

    visualizer = Visualizer(result)
    out_path = visualizer.export_html(output, title=title)
    typer.echo(colored(f"Codemap HTML: {out_path}", "green"))

    if open_browser:
        webbrowser.open(f"file://{Path(out_path).absolute()}")


@app.command()
def export_json(
    path: str = typer.Argument(".", help="Path to project or file"),
    output: str = typer.Option(
        "codemap.json", "--output", "-o", help="Output JSON file"
    ),
    pretty: bool = typer.Option(True, "--pretty/--compact", help="Pretty print JSON"),
):
    """Export codemap as JSON."""
    config = CodemapConfig(root_path=os.path.abspath(path))
    analyzer = PythonAnalyzer(config)
    result = analyzer.analyze()

    builder = GraphBuilder(result)
    builder.build()

    visualizer = Visualizer(result)
    out_path = visualizer.export_json(output)
    typer.echo(colored(f"JSON exported to: {out_path}", "green"))
    summary = result.summary()
    typer.echo(
        f"Symbols: {summary['total_symbols']}, Files: {summary['files']}, LOC: {result.total_lines}"
    )


@app.command()
def tree(
    path: str = typer.Argument(".", help="Path to project"),
    depth: int = typer.Option(3, "--depth", "-d", help="Max depth to display"),
):
    """Display a terminal tree view of the code structure."""
    config = CodemapConfig(root_path=os.path.abspath(path))
    analyzer = PythonAnalyzer(config)
    result = analyzer.analyze()
    builder = GraphBuilder(result)
    builder.build()
    visualizer = Visualizer(result)
    typer.echo(visualizer.terminal_tree())


@app.command()
def info(
    path: str = typer.Argument(".", help="Path to project"),
):
    """Show summary metrics for a codebase."""
    config = CodemapConfig(root_path=os.path.abspath(path))
    analyzer = PythonAnalyzer(config)
    result = analyzer.analyze()
    builder = GraphBuilder(result)
    builder.build()

    summary = result.summary()
    module_metrics = builder.compute_module_metrics()

    typer.echo(
        colored(
            f"\nRepository Analysis: {os.path.abspath(path)}", "cyan", attrs=["bold"]
        )
    )
    typer.echo(colored("=" * 50, "cyan"))
    typer.echo(f"  Files:      {summary['files']}")
    typer.echo(f"  Classes:    {summary['classes']}")
    typer.echo(f"  Functions:  {summary['functions']}")
    typer.echo(f"  Methods:    {summary['methods']}")
    typer.echo(f"  Imports:    {summary['imports']}")
    typer.echo(f"  Variables:  {summary['variables']}")
    typer.echo(f"  Relationships: {summary['relationships']}")
    typer.echo(f"  Total Symbols: {summary['total_symbols']}")
    typer.echo(f"  Total LOC:  {result.total_lines}")

    if module_metrics:
        typer.echo(colored("\nModule Breakdown:", "cyan", attrs=["bold"]))
        typer.echo(f"  {'File':<40} {'Cls':>3} {'Fn':>3} {'LOC':>5}")
        typer.echo(f"  {'-' * 40} {'---':>3} {'---':>3} {'---':>5}")
        for file_path, metrics in sorted(module_metrics.items()):
            fname = os.path.relpath(file_path, path)[:39]
            typer.echo(
                f"  {fname:<40} {metrics['classes']:>3} {metrics['functions']:>3} {metrics['loc']:>5}"
            )

    cycles = builder.detect_circular_dependencies()
    if cycles:
        typer.echo(colored(f"\nCircular Dependencies: {len(cycles)}", "red"))
        for cycle in cycles[:3]:
            typer.echo(f"  {' -> '.join(cycle)}")
