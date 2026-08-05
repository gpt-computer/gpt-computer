import json
import os
import webbrowser

from pathlib import Path

import typer

from termcolor import colored

from gpt_computer.codemap.models import CodemapConfig
from gpt_computer.repository_intelligence.debug_agent import DebugAgent
from gpt_computer.repository_intelligence.explain_agent import ExplainAgent
from gpt_computer.repository_intelligence.knowledge_graph import KnowledgeGraph
from gpt_computer.repository_intelligence.refactor_agent import RefactorAgent
from gpt_computer.repository_intelligence.security_agent import SecurityAgent
from gpt_computer.repository_intelligence.tree_sitter_analyzer import TreeSitterAnalyzer
from gpt_computer.repository_intelligence.visualization_agent import VisualizationAgent

app = typer.Typer(
    help="Repository Intelligence - Advanced code analysis and intelligence"
)


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
    """Analyze a repository with advanced intelligence capabilities."""
    config = CodemapConfig(
        root_path=os.path.abspath(path),
        include_patterns=include,
        exclude_patterns=exclude,
    )

    analyzer = TreeSitterAnalyzer(config)
    result = analyzer.analyze()

    if result.errors:
        for err in result.errors[:10]:
            typer.echo(colored(f"  {err}", "yellow"))

    # Create knowledge graph
    kg = KnowledgeGraph.from_semantic_graph(result.semantic_graph)

    # Generate explanations
    explain_agent = ExplainAgent()
    explanations = explain_agent.explain_repository(result)

    # Generate debug info
    debug_agent = DebugAgent()
    debug_info = debug_agent.debug_repository(result)

    # Generate security report
    security_agent = SecurityAgent()
    security_report = security_agent.generate_security_report(result)

    # Generate refactoring suggestions
    refactor_agent = RefactorAgent()
    refactoring_plan = refactor_agent.create_refactoring_plan(result)

    # Create visualizations
    visualization_agent = VisualizationAgent()
    html_viz = visualization_agent.create_html_visualization(
        result, "/tmp/repository_viz.html"
    )
    terminal_viz = visualization_agent.create_terminal_visualization(result)

    # Output results
    typer.echo(
        colored("\nRepository Intelligence Analysis Complete!", "green", attrs=["bold"])
    )
    typer.echo(colored("=" * 60, "green"))

    typer.echo(f"Files analyzed: {result.files_analyzed}")
    typer.echo(f"Total symbols: {result.total_symbols}")
    typer.echo(
        f"Classes: {len([n for n in result.semantic_graph.nodes.values() if n.node_type.name == 'CLASS'])}"
    )
    typer.echo(
        f"Functions: {len([n for n in result.semantic_graph.nodes.values() if n.node_type.name == 'FUNCTION'])}"
    )
    typer.echo(
        f"Methods: {len([n for n in result.semantic_graph.nodes.values() if n.node_type.name == 'METHOD'])}"
    )

    typer.echo(f"\nSecurity Risk Score: {security_report['summary']['risk_score']:.2f}")
    typer.echo(f"Security Risk Level: {security_report['summary']['risk_level']}")

    typer.echo(f"\nRefactoring Priority: {refactoring_plan['priority']}")
    typer.echo(
        f"Estimated Effort: {refactoring_plan['estimated_effort']['person_hours']} person-hours"
    )

    if output:
        report = {
            "repository_analysis": result.to_dict(),
            "knowledge_graph": kg.to_dict(),
            "explanations": explanations,
            "debug_info": debug_info,
            "security_report": security_report,
            "refactoring_plan": refactoring_plan,
        }

        with open(output, "w") as f:
            json.dump(report, f, indent=2)

        typer.echo(colored(f"\nFull report exported to: {output}", "green"))

    # Show terminal visualization
    typer.echo(colored("\nTerminal Visualization:", "cyan", attrs=["bold"]))
    typer.echo(terminal_viz)

    # Show security summary
    if security_report["summary"]["risk_level"] != "low":
        typer.echo(colored("\nSecurity Issues Found:", "red", attrs=["bold"]))
        for issue in security_report["security_issues"][:5]:
            typer.echo(f"  {issue['severity'].upper()}: {issue['description']}")

    # Show refactoring suggestions
    if refactoring_plan["priority"] != "low":
        typer.echo(colored("\nRefactoring Suggestions:", "yellow", attrs=["bold"]))
        for suggestion in refactoring_plan["steps"][:3]:
            typer.echo(f"  {suggestion['description']} ({suggestion['effort']} effort)")

    # Open HTML visualization if browser available
    try:
        webbrowser.open(f"file://{Path(html_viz).absolute()}")
        typer.echo(
            colored(
                f"\nInteractive visualization opened in browser: {html_viz}", "green"
            )
        )
    except:
        typer.echo(colored(f"\nHTML visualization saved to: {html_viz}", "green"))


@app.command()
def explain(
    path: str = typer.Argument(".", help="Path to project"),
    output: str = typer.Option(
        "", "--output", "-o", help="Output file for explanation"
    ),
):
    """Generate comprehensive explanations of the repository."""
    config = CodemapConfig(root_path=os.path.abspath(path))
    analyzer = TreeSitterAnalyzer(config)
    result = analyzer.analyze()

    explain_agent = ExplainAgent()
    explanations = explain_agent.explain_repository(result)

    typer.echo(colored("\nRepository Explanation:", "cyan", attrs=["bold"]))
    typer.echo(colored("=" * 60, "cyan"))

    typer.echo("\nOverview:")
    typer.echo(f"  Files: {explanations['overview']['files']}")
    typer.echo(f"  Total Symbols: {explanations['overview']['total_symbols']}")
    typer.echo(f"  Main Language: {explanations['overview']['main_language']}")
    typer.echo(
        f"  Complexity Score: {explanations['overview']['complexity_score']:.2f}"
    )
    typer.echo(f"  Risk Level: {explanations['overview']['risk_level']}")

    typer.echo(f"\nKey Components ({len(explanations['key_components'])}):")
    for i, component in enumerate(explanations["key_components"][:5], 1):
        typer.echo(f"  {i}. {component['name']} ({component['type']})")

    typer.echo("\nArchitecture:")
    typer.echo(f"  Modules: {len(explanations['architecture']['modules'])}")
    typer.echo(f"  Entry Points: {len(explanations['architecture']['entry_points'])}")
    typer.echo(f"  Dependencies: {len(explanations['architecture']['dependencies'])}")

    typer.echo("\nInsights:")
    for insight in explanations["insights"]:
        typer.echo(f"  • {insight}")

    if output:
        with open(output, "w") as f:
            json.dump(explanations, f, indent=2)
        typer.echo(colored(f"\nExplanation saved to: {output}", "green"))


@app.command()
def security(
    path: str = typer.Argument(".", help="Path to project"),
    output: str = typer.Option(
        "", "--output", "-o", help="Output file for security report"
    ),
):
    """Generate security analysis report."""
    config = CodemapConfig(root_path=os.path.abspath(path))
    analyzer = TreeSitterAnalyzer(config)
    result = analyzer.analyze()

    security_agent = SecurityAgent()
    report = security_agent.generate_security_report(result)

    typer.echo(colored("\nSecurity Analysis Report:", "red", attrs=["bold"]))
    typer.echo(colored("=" * 60, "red"))

    typer.echo("\nSummary:")
    typer.echo(f"  Total Vulnerabilities: {report['summary']['total_vulnerabilities']}")
    typer.echo(f"  Total Security Issues: {report['summary']['total_security_issues']}")
    typer.echo(f"  Risk Score: {report['summary']['risk_score']:.2f}")
    typer.echo(f"  Risk Level: {report['summary']['risk_level']}")

    typer.echo("\nSeverity Breakdown:")
    for severity, count in report["severity_breakdown"].items():
        typer.echo(f"  {severity.title()}: {count}")

    typer.echo(f"\nFiles Affected: {len(report['files_affected'])}")
    if report["files_affected"]:
        typer.echo(f"  {report['files_affected'][0]}")
        if len(report["files_affected"]) > 1:
            typer.echo(f"  ... and {len(report['files_affected']) - 1} more")

    typer.echo(f"\nRecommendations ({len(report['recommendations'])}):")
    for i, rec in enumerate(report["recommendations"], 1):
        typer.echo(f"  {i}. {rec}")

    if output:
        with open(output, "w") as f:
            json.dump(report, f, indent=2)
        typer.echo(colored(f"\nSecurity report saved to: {output}", "green"))


@app.command()
def debug(
    path: str = typer.Argument(".", help="Path to project"),
    output: str = typer.Option(
        "", "--output", "-o", help="Output file for debug report"
    ),
):
    """Generate debug analysis report."""
    config = CodemapConfig(root_path=os.path.abspath(path))
    analyzer = TreeSitterAnalyzer(config)
    result = analyzer.analyze()

    debug_agent = DebugAgent()
    report = debug_agent.debug_repository(result)

    typer.echo(colored("\nDebug Analysis Report:", "yellow", attrs=["bold"]))
    typer.echo(colored("=" * 60, "yellow"))

    typer.echo("\nOverview:")
    typer.echo(f"  Total Files: {report['overview']['total_files']}")
    typer.echo(f"  Total Symbols: {report['overview']['total_symbols']}")
    typer.echo(
        f"  Complexity Distribution: {report['overview']['complexity_distribution']}"
    )
    typer.echo(f"  Issue Count: {report['overview']['issue_count']}")

    typer.echo(f"\nProblematic Nodes ({len(report['problematic_nodes'])}):")
    for node in report["problematic_nodes"][:5]:
        typer.echo(f"  {node['node']} ({node['type']}) - {node['file']}")
        typer.echo(f"    Issues: {', '.join(node['issues'])}")

    typer.echo(f"\nPerformance Issues ({len(report['performance_issues'])}):")
    for issue in report["performance_issues"]:
        typer.echo(f"  {issue['type']}: {issue['description']} ({issue['severity']})")

    typer.echo(f"\nSecurity Issues ({len(report['security_issues'])}):")
    for issue in report["security_issues"]:
        typer.echo(f"  {issue['type']}: {issue['description']} ({issue['severity']})")

    typer.echo(f"\nRecommendations ({len(report['recommendations'])}):")
    for i, rec in enumerate(report["recommendations"], 1):
        typer.echo(f"  {i}. {rec}")

    if output:
        with open(output, "w") as f:
            json.dump(report, f, indent=2)
        typer.echo(colored(f"\nDebug report saved to: {output}", "green"))


@app.command()
def refactor(
    path: str = typer.Argument(".", help="Path to project"),
    output: str = typer.Option(
        "", "--output", "-o", help="Output file for refactoring plan"
    ),
):
    """Generate refactoring plan."""
    config = CodemapConfig(root_path=os.path.abspath(path))
    analyzer = TreeSitterAnalyzer(config)
    result = analyzer.analyze()

    refactor_agent = RefactorAgent()
    plan = refactor_agent.create_refactoring_plan(result)

    typer.echo(colored("\nRefactoring Plan:", "blue", attrs=["bold"]))
    typer.echo(colored("=" * 60, "blue"))

    typer.echo(f"\nPriority: {plan['priority'].upper()}")
    typer.echo(
        f"Estimated Effort: {plan['estimated_effort']['person_hours']} person-hours"
    )
    typer.echo(f"Risk Level: {plan['risk_level'].upper()}")

    typer.echo("\nExpected Benefits:")
    for benefit, value in plan["expected_benefits"].items():
        typer.echo(f"  {benefit.replace('_', ' ').title()}: {value}")

    typer.echo(f"\nRefactoring Steps ({len(plan['steps'])}):")
    for i, step in enumerate(plan["steps"], 1):
        typer.echo(f"  {i}. {step['description']}")
        typer.echo(f"     Effort: {step['effort']}, Risk: {step['risk']}")

    typer.echo(f"\nSuggestions ({len(plan['expected_benefits'])}):")
    suggestions = refactor_agent.generate_refactoring_suggestions(result)
    for i, suggestion in enumerate(suggestions, 1):
        typer.echo(
            f"  {i}. {suggestion['description']} ({suggestion['impact']} impact)"
        )

    if output:
        with open(output, "w") as f:
            json.dump(plan, f, indent=2)
        typer.echo(colored(f"\nRefactoring plan saved to: {output}", "green"))
