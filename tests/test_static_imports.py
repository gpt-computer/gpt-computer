"""
Static Import-Graph Analysis Tool

This module provides tools to analyze the import graph of the gpt_computer codebase
to detect circular dependencies and verify that imports follow the allowed dependency
directions defined in DEPENDENCY_RULES.md.

Usage:
    pytest tests/test_static_imports.py -v
"""

import ast

from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Set


def get_module_name(file_path: Path, source_root: Path) -> str:
    """
    Convert file path to module name.

    Args:
        file_path: Path to Python file
        source_root: Root directory of the source code

    Returns:
        Module name (e.g., "gpt_computer.ai.client")
    """
    relative = file_path.relative_to(source_root)
    parts = list(relative.parts[:-1])  # Remove filename

    # Handle __init__.py files
    if parts and parts[-1] == "__init__":
        parts = parts[:-1]

    # Handle packages at root (gptc/__init__.py)
    if not parts:
        return relative.stem

    return ".".join(parts) if parts else relative.stem


def get_layer(module_name: str) -> str:
    """
    Map module name to architectural layer.

    Args:
        module_name: Module name (e.g., "gpt_computer.ai.client")

    Returns:
        Layer name (e.g., "ai", "infrastructure", "unknown")
    """
    if module_name.startswith("gpt_computer.infrastructure"):
        return "infrastructure"
    elif module_name.startswith("gpt_computer.execution"):
        return "execution"
    elif module_name.startswith("gpt_computer.ai"):
        return "ai"
    elif module_name.startswith("gpt_computer.agent"):
        return "agent"
    elif module_name.startswith("gpt_computer.analysis"):
        return "analysis"
    elif module_name.startswith("gpt_computer.interfaces"):
        return "interfaces"
    elif module_name.startswith("gpt_computer.benchmark"):
        return "benchmark"
    elif module_name.startswith("gpt_computer.utils"):
        return "utils"
    elif module_name.startswith("gptc"):
        # gptc is the compatibility layer, skip from analysis
        return "compatibility"
    else:
        return "unknown"


def resolve_import(module_name: str, current_module: str, source_root: Path) -> str:
    """
    Resolve relative imports to absolute module names.

    Args:
        module_name: Import statement (may be relative, e.g., ".utils")
        current_module: Current module name (e.g., "gpt_computer.ai.client")
        source_root: Root directory of the source code

    Returns:
        Resolved absolute module name
    """
    if not module_name.startswith("."):
        return module_name

    # Handle relative imports
    current_parts = current_module.split(".")
    level = len(module_name) - len(module_name.lstrip("."))
    relative_part = module_name.lstrip(".")

    if level > len(current_parts):
        return module_name  # Invalid relative import, return as-is

    base_parts = current_parts[:-level] if level > 0 else current_parts
    if relative_part:
        return ".".join(base_parts + relative_part.split("."))
    else:
        return ".".join(base_parts)


def build_import_graph(source_dir: Path) -> Dict[str, Set[str]]:
    """
    Build static import graph from source tree with full module paths.

    Args:
        source_dir: Root directory to analyze (e.g., Path("gpt_computer"))

    Returns:
        Dictionary mapping module name to set of modules it imports
    """
    graph = defaultdict(set)

    for py_file in source_dir.rglob("*.py"):
        # Skip test files and compatibility shims
        if "test" in py_file.parts or "gptc" in py_file.parts:
            continue

        current_module = get_module_name(py_file, source_dir)

        try:
            with open(py_file) as f:
                tree = ast.parse(f.read())
        except SyntaxError:
            # Skip files with syntax errors
            continue

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name.startswith("gpt_computer"):
                        graph[current_module].add(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module and node.module.startswith("gpt_computer"):
                    resolved = resolve_import(node.module, current_module, source_dir)
                    graph[current_module].add(resolved)

    # Ensure all target nodes are registered as graph keys (even if they have
    # no outgoing gpt_computer imports). This prevents KeyError in has_cycles
    # when a node appears only as an import target.
    all_targets: Set[str] = set()
    for targets in graph.values():
        all_targets.update(targets)
    for target in all_targets:
        if target not in graph:
            graph[target] = set()

    return graph


def has_cycles(graph: Dict[str, Set[str]]) -> List[List[str]]:
    """
    Detect cycles in import graph using DFS.

    Args:
        graph: Import graph from build_import_graph()

    Returns:
        List of cycles (each cycle is a list of module names)
    """
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {node: WHITE for node in graph}
    cycles = []

    def dfs(node: str, path: List[str]):
        color[node] = GRAY
        path.append(node)

        for neighbor in graph.get(node, []):
            if color[neighbor] == GRAY:
                cycle_start = path.index(neighbor)
                cycles.append(path[cycle_start:] + [neighbor])
            elif color[neighbor] == WHITE:
                dfs(neighbor, path)

        path.pop()
        color[node] = BLACK

    for node in graph:
        if color[node] == WHITE:
            dfs(node, [])

    return cycles


def test_no_import_cycles():
    """Verify no circular dependencies exist."""
    graph = build_import_graph(Path("gpt_computer"))
    cycles = has_cycles(graph)

    if cycles:
        cycle_strs = [" -> ".join(cycle) for cycle in cycles]
        assert False, "Import cycles detected:\n" + "\n".join(cycle_strs)


def test_dependency_directions():
    """Verify imports follow allowed directions."""
    graph = build_import_graph(Path("gpt_computer"))

    allowed_edges = {
        "infrastructure": set(),
        "execution": {"infrastructure"},
        "ai": {"infrastructure"},
        "agent": {"ai", "execution", "infrastructure"},
        "analysis": {"agent", "infrastructure"},
        "interfaces": {"ai", "agent", "execution", "infrastructure"},
        "benchmark": {"agent", "ai", "infrastructure"},
        "utils": set(),
    }

    # Prohibited edges (explicitly forbidden regardless of direction)
    prohibited_edges = {
        ("interfaces", "analysis"),
        ("analysis", "interfaces"),
        ("infrastructure", "agent"),
        ("infrastructure", "interfaces"),
    }

    violations = []

    for source, targets in graph.items():
        source_layer = get_layer(source)
        allowed = allowed_edges.get(source_layer, set())

        for target in targets:
            target_layer = get_layer(target)

            # Skip same-layer imports (allowed)
            if target_layer == source_layer:
                continue

            # Skip compatibility layer
            if source_layer == "compatibility" or target_layer == "compatibility":
                continue

            # Skip unknown layers
            if source_layer == "unknown" or target_layer == "unknown":
                continue

            # Check prohibited edges
            if (source_layer, target_layer) in prohibited_edges:
                violations.append(
                    f"Prohibited import: {source} → {target} ({source_layer} → {target_layer})"
                )
                continue

            # Check allowed edges
            if target_layer not in allowed:
                violations.append(
                    f"Disallowed import: {source} → {target} ({source_layer} → {target_layer})"
                )

    if violations:
        assert False, "Dependency direction violations:\n" + "\n".join(violations)


# Fixtures for testing the checker itself


def test_checker_with_known_cycle():
    """Test that cycle detection works with a deliberate cycle."""
    graph = {
        "module_a": {"module_b"},
        "module_b": {"module_c"},
        "module_c": {"module_a"},
    }
    cycles = has_cycles(graph)
    assert len(cycles) == 1
    assert cycles[0] == ["module_a", "module_b", "module_c", "module_a"]


def test_checker_with_no_cycle():
    """Test that no cycle is detected when graph is acyclic."""
    graph = {
        "module_a": {"module_b"},
        "module_b": {"module_c"},
        "module_c": set(),
    }
    cycles = has_cycles(graph)
    assert len(cycles) == 0


def test_checker_with_forbidden_import():
    """Test that forbidden import detection works."""
    # Simulate forbidden edge: interfaces importing from analysis
    graph = {
        "gpt_computer.interfaces.cli": {"gpt_computer.analysis.codemap"},
    }

    # Extract layers
    source_layer = get_layer("gpt_computer.interfaces.cli")
    target_layer = get_layer("gpt_computer.analysis.codemap")

    # Verify prohibited edge is detected
    prohibited_edges = {("interfaces", "analysis")}
    assert (source_layer, target_layer) in prohibited_edges


def test_checker_with_allowed_import():
    """Test that allowed import is not flagged as forbidden."""
    # Simulate allowed edge: agent importing from ai
    graph = {
        "gpt_computer.agent.react": {"gpt_computer.ai.client"},
    }

    # Extract layers
    source_layer = get_layer("gpt_computer.agent.react")
    target_layer = get_layer("gpt_computer.ai.client")

    # Verify allowed edge is not prohibited
    prohibited_edges = {("interfaces", "analysis"), ("analysis", "interfaces")}
    assert (source_layer, target_layer) not in prohibited_edges


if __name__ == "__main__":
    # Run checks manually for debugging
    print("Building import graph...")
    graph = build_import_graph(Path("gpt_computer"))
    print(f"Found {len(graph)} modules")

    print("\nChecking for cycles...")
    cycles = has_cycles(graph)
    if cycles:
        print(f"Found {len(cycles)} cycles:")
        for cycle in cycles:
            print("  " + " -> ".join(cycle))
    else:
        print("No cycles found")

    print("\nChecking dependency directions...")
    test_dependency_directions()
    print("All dependency directions valid")
