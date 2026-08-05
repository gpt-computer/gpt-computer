from typing import Any, Dict, List

from gpt_computer.repository_intelligence.models import (
    NodeType,
    RepositoryAnalysis,
    SemanticGraph,
    SemanticNode,
)


class DebugAgent:
    def __init__(self):
        self.debug_info: Dict[str, Dict[str, Any]] = {}

    def debug_node(
        self, node: SemanticNode, semantic_graph: SemanticGraph
    ) -> Dict[str, Any]:
        debug_info = {
            "name": node.name,
            "type": node.node_type.value,
            "file_path": node.file_path,
            "location": f"Line {node.line_start}-{node.line_end}",
            "issues": [],
            "suggestions": [],
        }

        if node.node_type == NodeType.FUNCTION:
            debug_info.update(self._debug_function(node, semantic_graph))
        elif node.node_type == NodeType.CLASS:
            debug_info.update(self._debug_class(node, semantic_graph))
        elif node.node_type == NodeType.METHOD:
            debug_info.update(self._debug_method(node, semantic_graph))

        return debug_info

    def _debug_function(
        self, node: SemanticNode, semantic_graph: SemanticGraph
    ) -> Dict[str, Any]:
        issues = []
        suggestions = []

        if node.complexity > 10:
            issues.append(f"High cyclomatic complexity: {node.complexity}")
            suggestions.append("Consider refactoring into smaller functions")

        if node.lines_of_code > 50:
            issues.append(f"Function too long: {node.lines_of_code} lines")
            suggestions.append("Extract logic into helper functions")

        if not node.docstring:
            suggestions.append("Add docstring for better documentation")

        if node.return_type == "None" and "return" not in node.signature.lower():
            suggestions.append("Consider if function should return a value")

        return {"issues": issues, "suggestions": suggestions}

    def _debug_class(
        self, node: SemanticNode, semantic_graph: SemanticGraph
    ) -> Dict[str, Any]:
        issues = []
        suggestions = []

        methods = [
            n
            for n in semantic_graph.nodes.values()
            if n.node_type == NodeType.METHOD and n.parent_id == node.id
        ]
        if len(methods) > 10:
            issues.append(f"Too many methods: {len(methods)}")
            suggestions.append("Consider breaking into multiple classes")

        if not any(m.name == "__init__" for m in methods):
            suggestions.append("Add __init__ method for initialization")

        return {"issues": issues, "suggestions": suggestions}

    def _debug_method(
        self, node: SemanticNode, semantic_graph: SemanticGraph
    ) -> Dict[str, Any]:
        issues = []
        suggestions = []

        if node.complexity > 5:
            issues.append(f"Method complexity: {node.complexity}")
            suggestions.append("Simplify method logic")

        if node.lines_of_code > 30:
            issues.append(f"Method too long: {node.lines_of_code} lines")
            suggestions.append("Extract to helper method")

        return {"issues": issues, "suggestions": suggestions}

    def debug_repository(self, analysis: RepositoryAnalysis) -> Dict[str, Any]:
        debug_info = {
            "overview": self._get_repository_debug_overview(analysis),
            "problematic_nodes": self._get_problematic_nodes(analysis),
            "performance_issues": self._get_performance_issues(analysis),
            "security_issues": self._get_security_issues(analysis),
            "recommendations": self._get_debug_recommendations(analysis),
        }

        return debug_info

    def _get_repository_debug_overview(
        self, analysis: RepositoryAnalysis
    ) -> Dict[str, Any]:
        return {
            "total_files": analysis.files_analyzed,
            "total_symbols": analysis.total_symbols,
            "complexity_distribution": self._get_complexity_distribution(analysis),
            "issue_count": self._count_issues(analysis),
        }

    def _get_complexity_distribution(
        self, analysis: RepositoryAnalysis
    ) -> Dict[str, int]:
        distribution = {"low": 0, "medium": 0, "high": 0}
        for node in analysis.semantic_graph.nodes.values():
            if node.complexity < 5:
                distribution["low"] += 1
            elif node.complexity < 10:
                distribution["medium"] += 1
            else:
                distribution["high"] += 1
        return distribution

    def _count_issues(self, analysis: RepositoryAnalysis) -> int:
        count = 0
        for node in analysis.semantic_graph.nodes.values():
            if node.node_type in (NodeType.FUNCTION, NodeType.METHOD):
                if node.complexity > 10 or node.lines_of_code > 50:
                    count += 1
        return count

    def _get_problematic_nodes(
        self, analysis: RepositoryAnalysis
    ) -> List[Dict[str, Any]]:
        problematic = []

        for node in analysis.semantic_graph.nodes.values():
            if node.node_type in (NodeType.FUNCTION, NodeType.METHOD):
                issues = []
                if node.complexity > 10:
                    issues.append(f"Complexity: {node.complexity}")
                if node.lines_of_code > 50:
                    issues.append(f"Length: {node.lines_of_code} lines")

                if issues:
                    problematic.append(
                        {
                            "node": node.name,
                            "type": node.node_type.value,
                            "file": node.file_path,
                            "issues": issues,
                        }
                    )

        return sorted(problematic, key=lambda x: len(x["issues"]), reverse=True)[:10]

    def _get_performance_issues(
        self, analysis: RepositoryAnalysis
    ) -> List[Dict[str, Any]]:
        issues = []

        for bottleneck in analysis.performance.bottlenecks:
            issues.append(
                {
                    "type": bottleneck["type"],
                    "location": bottleneck["location"],
                    "severity": bottleneck["severity"],
                    "description": bottleneck["description"],
                }
            )

        return issues

    def _get_security_issues(
        self, analysis: RepositoryAnalysis
    ) -> List[Dict[str, Any]]:
        issues = []

        for issue in analysis.threats.security_issues:
            issues.append(
                {
                    "type": issue["type"],
                    "location": issue["location"],
                    "severity": issue["severity"],
                    "description": issue["description"],
                }
            )

        return issues

    def _get_debug_recommendations(self, analysis: RepositoryAnalysis) -> List[str]:
        recommendations = []

        for node in analysis.semantic_graph.nodes.values():
            if node.node_type in (NodeType.FUNCTION, NodeType.METHOD):
                if node.complexity > 10:
                    recommendations.append(f"Refactor {node.name} to reduce complexity")
                if node.lines_of_code > 50:
                    recommendations.append(f"Extract helper functions from {node.name}")

        return recommendations[:10]
