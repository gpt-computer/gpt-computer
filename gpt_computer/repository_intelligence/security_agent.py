from typing import Any, Dict, List

from gpt_computer.repository_intelligence.models import (
    EdgeType,
    NodeType,
    RepositoryAnalysis,
    SemanticEdge,
    SemanticGraph,
    SemanticNode,
    ThreatAnalysis,
)


class SecurityAgent:
    def __init__(self):
        self.security_findings: List[Dict[str, Any]] = []
        self.vulnerability_database = self._load_vulnerability_database()

    def _load_vulnerability_database(self) -> Dict[str, Dict[str, Any]]:
        return {
            "hardcoded_secrets": {
                "pattern": r"password|secret|key|token",
                "severity": "high",
                "description": "Hardcoded secrets in code",
            },
            "eval_usage": {
                "pattern": r"eval\(|exec\(",
                "severity": "medium",
                "description": "Use of eval/exec functions",
            },
            "sql_injection": {
                "pattern": r"f\"SELECT.*\{.*\}",
                "severity": "high",
                "description": "Potential SQL injection",
            },
            "command_injection": {
                "pattern": r"subprocess\.call\(|os\.system\(",
                "severity": "high",
                "description": "Command injection risk",
            },
            "weak_crypto": {
                "pattern": r"md5\(|sha1\(|md5sum",
                "severity": "medium",
                "description": "Weak cryptographic hash",
            },
            "debug_backdoor": {
                "pattern": r"__debug__|breakpoint\(",
                "severity": "low",
                "description": "Debug statements in production code",
            },
        }

    def analyze_security(self, analysis: RepositoryAnalysis) -> Dict[str, Any]:
        vulnerabilities = []
        security_issues = []

        for node in analysis.semantic_graph.nodes.values():
            node_vulns = self._scan_node_for_vulnerabilities(node)
            vulnerabilities.extend(node_vulns)

            node_issues = self._scan_node_for_security_issues(node)
            security_issues.extend(node_issues)

        for edge in analysis.semantic_graph.edges:
            edge_vulns = self._scan_edge_for_vulnerabilities(
                edge, analysis.semantic_graph
            )
            vulnerabilities.extend(edge_vulns)

        result = ThreatAnalysis(
            vulnerabilities=vulnerabilities,
            security_issues=security_issues,
            risk_score=self._calculate_security_risk(vulnerabilities, security_issues),
            recommendations=self._generate_security_recommendations(
                vulnerabilities, security_issues
            ),
        )

        return result.to_dict()

    def _scan_node_for_vulnerabilities(
        self, node: SemanticNode
    ) -> List[Dict[str, Any]]:
        vulnerabilities = []

        if node.node_type in (NodeType.FUNCTION, NodeType.METHOD):
            if self._contains_hardcoded_secrets(node):
                vulnerabilities.append(
                    {
                        "type": "hardcoded_secrets",
                        "location": node.qualified_name,
                        "severity": "high",
                        "description": f"Function {node.name} may contain hardcoded secrets",
                        "line": node.line_start,
                        "column": node.column_start,
                    }
                )

            if self._uses_eval(node):
                vulnerabilities.append(
                    {
                        "type": "eval_usage",
                        "location": node.qualified_name,
                        "severity": "medium",
                        "description": f"Function {node.name} uses eval/exec",
                        "line": node.line_start,
                        "column": node.column_start,
                    }
                )

            if self._has_weak_crypto(node):
                vulnerabilities.append(
                    {
                        "type": "weak_crypto",
                        "location": node.qualified_name,
                        "severity": "medium",
                        "description": f"Function {node.name} uses weak crypto",
                        "line": node.line_start,
                        "column": node.column_start,
                    }
                )

        if node.node_type == NodeType.IMPORT:
            if self._imports_unsafe_modules(node):
                vulnerabilities.append(
                    {
                        "type": "unsafe_import",
                        "location": node.qualified_name,
                        "severity": "medium",
                        "description": f"Import of potentially unsafe module: {node.name}",
                        "line": node.line_start,
                        "column": node.column_start,
                    }
                )

        return vulnerabilities

    def _scan_node_for_security_issues(
        self, node: SemanticNode
    ) -> List[Dict[str, Any]]:
        issues = []

        if node.node_type == NodeType.FUNCTION:
            if not node.docstring:
                issues.append(
                    {
                        "type": "missing_docstring",
                        "location": node.qualified_name,
                        "severity": "low",
                        "description": f"Function {node.name} lacks documentation",
                        "line": node.line_start,
                        "column": node.column_start,
                    }
                )

            if node.complexity > 15:
                issues.append(
                    {
                        "type": "high_complexity",
                        "location": node.qualified_name,
                        "severity": "medium",
                        "description": f"Function {node.name} has very high complexity",
                        "line": node.line_start,
                        "column": node.column_start,
                    }
                )

        return issues

    def _scan_edge_for_vulnerabilities(
        self, edge: SemanticEdge, semantic_graph: SemanticGraph
    ) -> List[Dict[str, Any]]:
        vulnerabilities = []

        if edge.edge_type == EdgeType.CALLS:
            source = semantic_graph.get_node(edge.source_id)
            target = semantic_graph.get_node(edge.target_id)

            if source and target:
                if (
                    source.node_type == NodeType.FUNCTION
                    and target.node_type == NodeType.FUNCTION
                ):
                    if self._is_unsafe_call(source, target):
                        vulnerabilities.append(
                            {
                                "type": "unsafe_call",
                                "location": f"{source.name} -> {target.name}",
                                "severity": "medium",
                                "description": f"Unsafe function call: {source.name}()",
                                "line": source.line_start,
                                "column": source.column_start,
                            }
                        )

        return vulnerabilities

    def _contains_hardcoded_secrets(self, node: SemanticNode) -> bool:
        if not node.docstring:
            return False

        secret_patterns = ["password", "secret", "key", "token", "api_key", "auth"]
        docstring_lower = node.docstring.lower()
        return any(pattern in docstring_lower for pattern in secret_patterns)

    def _uses_eval(self, node: SemanticNode) -> bool:
        if not node.signature:
            return False

        return "eval(" in node.signature or "exec(" in node.signature

    def _has_weak_crypto(self, node: SemanticNode) -> bool:
        if not node.signature:
            return False

        weak_crypto_patterns = ["md5(", "sha1(", "md5sum", "sha256("]
        return any(pattern in node.signature for pattern in weak_crypto_patterns)

    def _imports_unsafe_modules(self, node: SemanticNode) -> bool:
        unsafe_modules = ["os.system", "subprocess.call", "eval", "exec"]
        return any(unsafe in node.qualified_name for unsafe in unsafe_modules)

    def _is_unsafe_call(self, source: SemanticNode, target: SemanticNode) -> bool:
        unsafe_functions = ["eval", "exec", "os.system", "subprocess.call"]
        return target.name in unsafe_functions

    def _calculate_security_risk(
        self,
        vulnerabilities: List[Dict[str, Any]],
        security_issues: List[Dict[str, Any]],
    ) -> float:
        risk_score = 0.0

        for vuln in vulnerabilities:
            if vuln["severity"] == "high":
                risk_score += 0.3
            elif vuln["severity"] == "medium":
                risk_score += 0.1
            else:
                risk_score += 0.05

        for issue in security_issues:
            if issue["severity"] == "high":
                risk_score += 0.2
            elif issue["severity"] == "medium":
                risk_score += 0.1
            else:
                risk_score += 0.05

        return min(1.0, risk_score)

    def _generate_security_recommendations(
        self,
        vulnerabilities: List[Dict[str, Any]],
        security_issues: List[Dict[str, Any]],
    ) -> List[str]:
        recommendations = []

        for vuln in vulnerabilities:
            if vuln["type"] == "hardcoded_secrets":
                recommendations.append(
                    "Use environment variables or secure vaults for secrets"
                )
            elif vuln["type"] == "eval_usage":
                recommendations.append("Replace eval/exec with safer alternatives")
            elif vuln["type"] == "weak_crypto":
                recommendations.append(
                    "Use strong cryptographic hashes (SHA-256, SHA-512)"
                )
            elif vuln["type"] == "unsafe_import":
                recommendations.append("Validate and sanitize imported modules")

        if not recommendations:
            recommendations.append("Implement regular security audits and code reviews")
            recommendations.append("Use static analysis tools for security scanning")

        return recommendations

    def generate_security_report(self, analysis: RepositoryAnalysis) -> Dict[str, Any]:
        security_data = self.analyze_security(analysis)

        report = {
            "summary": {
                "total_vulnerabilities": len(security_data["vulnerabilities"]),
                "total_security_issues": len(security_data["security_issues"]),
                "risk_score": security_data["risk_score"],
                "risk_level": self._get_risk_level(security_data["risk_score"]),
            },
            "vulnerabilities": security_data["vulnerabilities"],
            "security_issues": security_data["security_issues"],
            "recommendations": security_data["recommendations"],
            "files_affected": self._get_affected_files(security_data),
            "severity_breakdown": self._get_severity_breakdown(security_data),
        }

        return report

    def _get_risk_level(self, risk_score: float) -> str:
        if risk_score > 0.7:
            return "high"
        elif risk_score > 0.3:
            return "medium"
        else:
            return "low"

    def _get_affected_files(self, security_data: Dict[str, Any]) -> List[str]:
        files = set()
        for vuln in security_data["vulnerabilities"]:
            if "file_path" in vuln:
                files.add(vuln["file_path"])
        return sorted(list(files))

    def _get_severity_breakdown(self, security_data: Dict[str, Any]) -> Dict[str, int]:
        breakdown = {"high": 0, "medium": 0, "low": 0}
        for vuln in security_data["vulnerabilities"]:
            breakdown[vuln["severity"]] += 1
        return breakdown
