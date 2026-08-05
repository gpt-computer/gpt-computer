from pathlib import Path
from typing import Any, Dict, List

from gpt_computer.repository_intelligence.models import (
    EdgeType,
    NodeType,
    RepositoryAnalysis,
    SemanticGraph,
    SemanticNode,
)


class ExplainAgent:
    def __init__(self):
        self.explanations: Dict[str, Dict[str, Any]] = {}

    def explain_node(
        self, node: SemanticNode, semantic_graph: SemanticGraph
    ) -> Dict[str, Any]:
        explanation = {
            "name": node.name,
            "type": node.node_type.value,
            "file_path": node.file_path,
            "location": f"Line {node.line_start}-{node.line_end}",
        }

        if node.node_type == NodeType.CLASS:
            explanation.update(self._explain_class(node, semantic_graph))
        elif node.node_type == NodeType.FUNCTION:
            explanation.update(self._explain_function(node, semantic_graph))
        elif node.node_type == NodeType.METHOD:
            explanation.update(self._explain_method(node, semantic_graph))
        elif node.node_type == NodeType.IMPORT:
            explanation.update(self._explain_import(node))
        elif node.node_type == NodeType.VARIABLE:
            explanation.update(self._explain_variable(node, semantic_graph))

        return explanation

    def _explain_class(
        self, node: SemanticNode, semantic_graph: SemanticGraph
    ) -> Dict[str, Any]:
        explanation: Dict[str, Any] = {
            "purpose": self._infer_class_purpose(node),
            "methods": [],
            "attributes": [],
            "inheritance": [],
            "dependencies": [],
        }

        for edge in semantic_graph.edges:
            if edge.edge_type == EdgeType.CONTAINS and edge.target_id == node.id:
                target = semantic_graph.get_node(edge.target_id)
                if target:
                    if target.node_type == NodeType.METHOD:
                        explanation["methods"].append(target.name)
                    elif target.node_type == NodeType.VARIABLE:
                        explanation["attributes"].append(target.name)

            if edge.edge_type == EdgeType.INHERITS and edge.source_id == node.id:
                target = semantic_graph.get_node(edge.target_id)
                if target:
                    explanation["inheritance"].append(target.name)

            if edge.edge_type == EdgeType.IMPORTS and edge.source_id == node.id:
                target = semantic_graph.get_node(edge.target_id)
                if target:
                    explanation["dependencies"].append(target.name)

        return explanation

    def _explain_function(
        self, node: SemanticNode, semantic_graph: SemanticGraph
    ) -> Dict[str, Any]:
        explanation: Dict[str, Any] = {
            "purpose": self._infer_function_purpose(node),
            "parameters": [],
            "return_type": node.return_type,
            "called_functions": [],
            "complexity": node.complexity,
            "risk_level": self._assess_function_risk(node),
        }

        if node.signature:
            params_str = (
                node.signature.split("(")[1].split(")")[0]
                if "(" in node.signature
                else ""
            )
            explanation["parameters"] = [
                param.strip() for param in params_str.split(",") if param.strip()
            ]

        for edge in semantic_graph.edges:
            if edge.edge_type == EdgeType.CALLS and edge.source_id == node.id:
                target = semantic_graph.get_node(edge.target_id)
                if target:
                    explanation["called_functions"].append(target.name)

        return explanation

    def _explain_method(
        self, node: SemanticNode, semantic_graph: SemanticGraph
    ) -> Dict[str, Any]:
        explanation = self._explain_function(node, semantic_graph)
        explanation["class_context"] = self._get_class_context(node, semantic_graph)
        return explanation

    def _explain_import(self, node: SemanticNode) -> Dict[str, Any]:
        return {
            "module": node.qualified_name,
            "type": "external" if "." in node.qualified_name else "internal",
            "usage": self._infer_import_usage(node),
        }

    def _explain_variable(
        self, node: SemanticNode, semantic_graph: SemanticGraph
    ) -> Dict[str, Any]:
        return {
            "type": node.node_type.value,
            "usage": self._infer_variable_usage(node),
            "scope": self._infer_variable_scope(node, semantic_graph),
        }

    def _infer_class_purpose(self, node: SemanticNode) -> str:
        name = node.name.lower()
        if "manager" in name or "controller" in name:
            return "Manages business logic or data"
        elif "model" in name or "entity" in name:
            return "Represents data or domain concepts"
        elif "service" in name:
            return "Provides business services"
        elif "handler" in name or "processor" in name:
            return "Processes requests or data"
        else:
            return "Custom class implementation"

    def _infer_function_purpose(self, node: SemanticNode) -> str:
        name = node.name.lower()
        if "get" in name or "fetch" in name or "retrieve" in name:
            return "Retrieves data or resources"
        elif "create" in name or "make" in name or "build" in name:
            return "Creates or constructs objects/data"
        elif "update" in name or "modify" in name or "save" in name:
            return "Updates or persists data"
        elif "delete" in name or "remove" in name or "destroy" in name:
            return "Deletes or removes data"
        elif "process" in name or "handle" in name or "execute" in name:
            return "Processes input or executes logic"
        elif "validate" in name or "check" in name or "verify" in name:
            return "Validates input or state"
        else:
            return "Performs general operations"

    def _assess_function_risk(self, node: SemanticNode) -> str:
        if node.complexity > 10:
            return "high"
        elif node.complexity > 5:
            return "medium"
        else:
            return "low"

    def _get_class_context(
        self, node: SemanticNode, semantic_graph: SemanticGraph
    ) -> Dict[str, Any]:
        for edge in semantic_graph.edges:
            if edge.edge_type == EdgeType.CONTAINS and edge.target_id == node.id:
                parent = semantic_graph.get_node(edge.source_id)
                if parent:
                    return {
                        "class_name": parent.name,
                        "class_type": parent.node_type.value,
                    }
        return {}

    def _infer_import_usage(self, node: SemanticNode) -> str:
        if "os" in node.name.lower():
            return "System operations"
        elif "json" in node.name.lower():
            return "JSON serialization/deserialization"
        elif "pandas" in node.name.lower():
            return "Data manipulation"
        elif "numpy" in node.name.lower():
            return "Numerical computations"
        elif "requests" in node.name.lower():
            return "HTTP requests"
        else:
            return "External library or module"

    def _infer_variable_usage(self, node: SemanticNode) -> str:
        if node.name.isupper():
            return "Constant or configuration"
        elif node.name.startswith("_"):
            return "Private or internal variable"
        else:
            return "Regular variable"

    def _infer_variable_scope(
        self, node: SemanticNode, semantic_graph: SemanticGraph
    ) -> str:
        if node.line_start == 0:
            return "module"
        elif node.parent_id:
            parent = None
            for n in semantic_graph.nodes.values():
                if n.id == node.parent_id:
                    parent = n
                    break
            if parent and parent.node_type == NodeType.CLASS:
                return "class"
            elif parent and parent.node_type == NodeType.FUNCTION:
                return "function"
        return "global"

    def explain_repository(self, analysis: RepositoryAnalysis) -> Dict[str, Any]:
        explanation = {
            "overview": self._get_repository_overview(analysis),
            "key_components": self._get_key_components(analysis),
            "architecture": self._get_architecture_summary(analysis),
            "insights": self._get_insights(analysis),
            "recommendations": self._get_recommendations(analysis),
        }

        return explanation

    def _get_repository_overview(self, analysis: RepositoryAnalysis) -> Dict[str, Any]:
        return {
            "total_files": analysis.files_analyzed,
            "total_symbols": analysis.total_symbols,
            "main_language": self._detect_main_language(analysis),
            "complexity_score": self._calculate_overall_complexity(analysis),
            "risk_level": self._calculate_repository_risk(analysis),
        }

    def _get_key_components(self, analysis: RepositoryAnalysis) -> List[Dict[str, Any]]:
        components = []

        classes = [
            n
            for n in analysis.semantic_graph.nodes.values()
            if n.node_type == NodeType.CLASS
        ]
        for cls in classes[:10]:
            components.append(self.explain_node(cls, analysis.semantic_graph))

        functions = [
            n
            for n in analysis.semantic_graph.nodes.values()
            if n.node_type == NodeType.FUNCTION
        ]
        for fn in functions[:10]:
            components.append(self.explain_node(fn, analysis.semantic_graph))

        return components

    def _get_architecture_summary(self, analysis: RepositoryAnalysis) -> Dict[str, Any]:
        return {
            "modules": analysis.architecture.modules,
            "entry_points": analysis.architecture.entry_points,
            "dependencies": analysis.architecture.dependencies,
            "patterns": analysis.architecture.patterns,
            "design_patterns": analysis.architecture.design_patterns,
        }

    def _get_insights(self, analysis: RepositoryAnalysis) -> List[str]:
        insights = []

        if analysis.threats.risk_score > 0.5:
            insights.append("High security risk detected - review security issues")

        if analysis.performance.performance_score < 0.5:
            insights.append(
                "Performance bottlenecks identified - optimize complex functions"
            )

        if len(analysis.architecture.dependencies) > 10:
            insights.append("High dependency count - consider dependency injection")

        return insights

    def _get_recommendations(self, analysis: RepositoryAnalysis) -> List[str]:
        recommendations = []

        for issue in analysis.threats.security_issues:
            recommendations.append(f"Fix security issue: {issue['description']}")

        for bottleneck in analysis.performance.bottlenecks:
            recommendations.append(f"Optimize: {bottleneck['description']}")

        return recommendations

    def _detect_main_language(self, analysis: RepositoryAnalysis) -> str:
        file_counts: dict[str, int] = {}
        for node in analysis.semantic_graph.nodes.values():
            if node.node_type == NodeType.FILE:
                ext = Path(node.file_path).suffix
                file_counts[ext] = file_counts.get(ext, 0) + 1

        if file_counts:
            return max(file_counts.items(), key=lambda x: x[1])[0]
        return "unknown"

    def _calculate_overall_complexity(self, analysis: RepositoryAnalysis) -> float:
        total_complexity = sum(
            n.complexity for n in analysis.semantic_graph.nodes.values()
        )
        return total_complexity / max(1, len(analysis.semantic_graph.nodes))

    def _calculate_repository_risk(self, analysis: RepositoryAnalysis) -> str:
        risk_score = analysis.threats.risk_score
        if risk_score > 0.7:
            return "high"
        elif risk_score > 0.3:
            return "medium"
        else:
            return "low"
