from typing import Any, Dict, List

from gpt_computer.repository_intelligence.models import (
    NodeType,
    RepositoryAnalysis,
    SemanticNode,
)


class RefactorAgent:
    def __init__(self):
        self.refactoring_plans: Dict[str, Dict[str, Any]] = {}

    def analyze_refactoring_opportunities(
        self, analysis: RepositoryAnalysis
    ) -> Dict[str, Any]:
        opportunities = {
            "extract_methods": [],
            "extract_classes": [],
            "rename_variables": [],
            "remove_duplication": [],
            "simplify_conditions": [],
            "reorganize_structure": [],
        }

        for node in analysis.semantic_graph.nodes.values():
            if node.node_type == NodeType.FUNCTION:
                self._analyze_function_refactoring(node, opportunities)
            elif node.node_type == NodeType.CLASS:
                self._analyze_class_refactoring(node, opportunities, analysis)

        return opportunities

    def _analyze_function_refactoring(
        self, node: SemanticNode, opportunities: Dict[str, Any]
    ) -> None:
        if node.complexity > 10:
            opportunities["extract_methods"].append(
                {
                    "function": node.name,
                    "file": node.file_path,
                    "complexity": node.complexity,
                    "current_lines": node.lines_of_code,
                    "estimated_methods": max(2, node.complexity // 5),
                }
            )

        if node.lines_of_code > 50:
            opportunities["extract_methods"].append(
                {
                    "function": node.name,
                    "file": node.file_path,
                    "lines": node.lines_of_code,
                    "estimated_helpers": node.lines_of_code // 20,
                }
            )

    def _analyze_class_refactoring(
        self,
        node: SemanticNode,
        opportunities: Dict[str, Any],
        analysis: RepositoryAnalysis,
    ) -> None:
        methods = [
            n
            for n in analysis.semantic_graph.nodes.values()
            if n.node_type == NodeType.METHOD and n.parent_id == node.id
        ]

        if len(methods) > 10:
            opportunities["extract_classes"].append(
                {
                    "class": node.name,
                    "file": node.file_path,
                    "methods": len(methods),
                    "estimated_classes": max(2, len(methods) // 5),
                }
            )

    def create_refactoring_plan(self, analysis: RepositoryAnalysis) -> Dict[str, Any]:
        opportunities = self.analyze_refactoring_opportunities(analysis)

        plan = {
            "priority": self._calculate_refactoring_priority(opportunities),
            "estimated_effort": self._estimate_refactoring_effort(opportunities),
            "risk_level": self._assess_refactoring_risk(opportunities),
            "steps": self._create_refactoring_steps(opportunities),
            "expected_benefits": self._calculate_expected_benefits(opportunities),
        }

        return plan

    def _calculate_refactoring_priority(self, opportunities: Dict[str, Any]) -> str:
        total_score = (
            len(opportunities["extract_methods"]) * 3
            + len(opportunities["extract_classes"]) * 4
            + len(opportunities["simplify_conditions"]) * 2
            + len(opportunities["remove_duplication"]) * 3
        )

        if total_score > 20:
            return "high"
        elif total_score > 10:
            return "medium"
        else:
            return "low"

    def _estimate_refactoring_effort(
        self, opportunities: Dict[str, Any]
    ) -> Dict[str, Any]:
        effort = {
            "person_hours": 0,
            "complexity": "low",
            "risk": "low",
        }

        effort["person_hours"] = (
            len(opportunities["extract_methods"]) * 4
            + len(opportunities["extract_classes"]) * 8
            + len(opportunities["simplify_conditions"]) * 2
            + len(opportunities["remove_duplication"]) * 3
        )

        if effort["person_hours"] > 40:
            effort["complexity"] = "high"
            effort["risk"] = "medium"
        elif effort["person_hours"] > 20:
            effort["complexity"] = "medium"

        return effort

    def _assess_refactoring_risk(self, opportunities: Dict[str, Any]) -> str:
        risk_factors = 0

        if len(opportunities["extract_methods"]) > 5:
            risk_factors += 2
        if len(opportunities["extract_classes"]) > 2:
            risk_factors += 3
        if len(opportunities["simplify_conditions"]) > 3:
            risk_factors += 1

        if risk_factors > 5:
            return "high"
        elif risk_factors > 2:
            return "medium"
        else:
            return "low"

    def _create_refactoring_steps(
        self, opportunities: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        steps = []

        for method in opportunities["extract_methods"][:5]:
            steps.append(
                {
                    "id": f"extract_{method['function']}",
                    "type": "extract_method",
                    "description": f"Extract helper methods from {method['function']}",
                    "effort": "medium",
                    "risk": "low",
                    "files": [method["file"]],
                }
            )

        for cls in opportunities["extract_classes"][:3]:
            steps.append(
                {
                    "id": f"split_{cls['class']}",
                    "type": "split_class",
                    "description": f"Split {cls['class']} into {cls['estimated_classes']} classes",
                    "effort": "high",
                    "risk": "medium",
                    "files": [cls["file"]],
                }
            )

        return steps

    def _calculate_expected_benefits(
        self, opportunities: Dict[str, Any]
    ) -> Dict[str, Any]:
        benefits = {
            "complexity_reduction": 0,
            "maintainability_improvement": 0,
            "testability_improvement": 0,
            "bug_reduction": 0,
        }

        benefits["complexity_reduction"] = len(opportunities["extract_methods"]) * 3
        benefits["maintainability_improvement"] = (
            len(opportunities["extract_methods"]) * 2
        )
        benefits["testability_improvement"] = len(opportunities["extract_classes"]) * 3
        benefits["bug_reduction"] = len(opportunities["remove_duplication"]) * 2

        return benefits

    def generate_refactoring_suggestions(
        self, analysis: RepositoryAnalysis
    ) -> List[Dict[str, Any]]:
        suggestions = []

        for node in analysis.semantic_graph.nodes.values():
            if node.node_type == NodeType.FUNCTION:
                if node.complexity > 10:
                    suggestions.append(
                        {
                            "type": "extract_method",
                            "target": node.name,
                            "file": node.file_path,
                            "reason": f"High complexity ({node.complexity})",
                            "impact": "high",
                        }
                    )

                if node.lines_of_code > 50:
                    suggestions.append(
                        {
                            "type": "split_function",
                            "target": node.name,
                            "file": node.file_path,
                            "reason": f"Too long ({node.lines_of_code} lines)",
                            "impact": "medium",
                        }
                    )

        return suggestions[:10]
