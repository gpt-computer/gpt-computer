import uuid

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


class NodeType(Enum):
    FILE = "file"
    CLASS = "class"
    FUNCTION = "function"
    METHOD = "method"
    VARIABLE = "variable"
    IMPORT = "import"
    INTERFACE = "interface"
    ENUM = "enum"
    CONSTANT = "constant"
    MODULE = "module"
    PACKAGE = "package"


class EdgeType(Enum):
    IMPORTS = "imports"
    CALLS = "calls"
    INHERITS = "inherits"
    CONTAINS = "contains"
    IMPLEMENTS = "implements"
    DECORATES = "decorates"
    ACCESSES = "accesses"
    RETURNS = "returns"
    PARAMETERS = "parameters"
    DATA_FLOW = "data_flow"
    CONTROL_FLOW = "control_flow"


@dataclass
class SemanticNode:
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    name: str = ""
    node_type: NodeType = NodeType.FILE
    file_path: str = ""
    qualified_name: str = ""
    line_start: int = 0
    line_end: int = 0
    complexity: float = 0.0
    cyclomatic_complexity: int = 1
    lines_of_code: int = 0
    docstring: str = ""
    signature: str = ""
    return_type: str = ""
    parent_id: Optional[str] = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class SemanticEdge:
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    source_id: str = ""
    target_id: str = ""
    edge_type: EdgeType = EdgeType.CONTAINS
    weight: float = 1.0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class SemanticGraph:
    nodes: dict[str, SemanticNode] = field(default_factory=dict)
    edges: list[SemanticEdge] = field(default_factory=list)

    def add_node(self, node: SemanticNode) -> str:
        self.nodes[node.id] = node
        return node.id

    def add_edge(self, edge: SemanticEdge) -> str:
        self.edges.append(edge)
        return edge.id

    def get_node(self, node_id: str) -> Optional[SemanticNode]:
        return self.nodes.get(node_id)

    def get_nodes_by_type(self, node_type: NodeType) -> list[SemanticNode]:
        return [n for n in self.nodes.values() if n.node_type == node_type]

    def get_nodes_in_file(self, file_path: str) -> list[SemanticNode]:
        return [n for n in self.nodes.values() if n.file_path == file_path]

    def get_edges_by_type(self, edge_type: EdgeType) -> list[SemanticEdge]:
        return [e for e in self.edges if e.edge_type == edge_type]

    def get_edges(
        self, source_id: Optional[str] = None, target_id: Optional[str] = None
    ) -> list[SemanticEdge]:
        result = self.edges
        if source_id:
            result = [e for e in result if e.source_id == source_id]
        if target_id:
            result = [e for e in result if e.target_id == target_id]
        return result

    def merge(self, other: "SemanticGraph") -> None:
        self.nodes.update(other.nodes)
        existing_ids = {e.id for e in self.edges}
        for edge in other.edges:
            if edge.id not in existing_ids:
                self.edges.append(edge)

    def to_dict(self) -> dict[str, Any]:
        return {
            "nodes": {
                nid: {
                    "id": n.id,
                    "name": n.name,
                    "node_type": n.node_type.value,
                    "file_path": n.file_path,
                    "qualified_name": n.qualified_name,
                    "line_start": n.line_start,
                    "line_end": n.line_end,
                    "complexity": n.complexity,
                    "cyclomatic_complexity": n.cyclomatic_complexity,
                    "lines_of_code": n.lines_of_code,
                    "docstring": n.docstring[:200] if n.docstring else "",
                    "signature": n.signature,
                    "return_type": n.return_type,
                    "parent_id": n.parent_id,
                    "metadata": n.metadata,
                }
                for nid, n in self.nodes.items()
            },
            "edges": [
                {
                    "id": e.id,
                    "source_id": e.source_id,
                    "target_id": e.target_id,
                    "edge_type": e.edge_type.value,
                    "weight": e.weight,
                    "metadata": e.metadata,
                }
                for e in self.edges
            ],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SemanticGraph":
        graph = cls()
        for nid, ndata in data.get("nodes", {}).items():
            n = SemanticNode(
                id=ndata["id"],
                name=ndata["name"],
                node_type=NodeType(ndata["node_type"]),
                file_path=ndata["file_path"],
                qualified_name=ndata["qualified_name"],
                line_start=ndata["line_start"],
                line_end=ndata["line_end"],
                complexity=ndata.get("complexity", 0.0),
                cyclomatic_complexity=ndata.get("cyclomatic_complexity", 1),
                lines_of_code=ndata.get("lines_of_code", 0),
                docstring=ndata.get("docstring", ""),
                signature=ndata.get("signature", ""),
                return_type=ndata.get("return_type", ""),
                parent_id=ndata.get("parent_id"),
                metadata=ndata.get("metadata", {}),
            )
            graph.nodes[n.id] = n
        for edata in data.get("edges", []):
            e = SemanticEdge(
                id=edata["id"],
                source_id=edata["source_id"],
                target_id=edata["target_id"],
                edge_type=EdgeType(edata["edge_type"]),
                weight=edata.get("weight", 1.0),
                metadata=edata.get("metadata", {}),
            )
            graph.edges.append(e)
        return graph


@dataclass
class ArchitectureInfo:
    modules: list[str] = field(default_factory=list)
    entry_points: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)
    patterns: list[str] = field(default_factory=list)
    design_patterns: list[str] = field(default_factory=list)
    coupling: dict[str, float] = field(default_factory=dict)
    cohesion: dict[str, float] = field(default_factory=dict)
    metrics: dict[str, Any] = field(default_factory=dict)


@dataclass
class ThreatAnalysis:
    vulnerabilities: list[dict[str, Any]] = field(default_factory=list)
    security_issues: list[dict[str, Any]] = field(default_factory=list)
    risk_score: float = 0.0
    recommendations: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "vulnerabilities": self.vulnerabilities,
            "security_issues": self.security_issues,
            "risk_score": self.risk_score,
            "recommendations": self.recommendations,
        }


@dataclass
class PerformanceAnalysis:
    bottlenecks: list[dict[str, Any]] = field(default_factory=list)
    optimization_opportunities: list[dict[str, Any]] = field(default_factory=list)
    performance_score: float = 0.0
    recommendations: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "bottlenecks": self.bottlenecks,
            "optimization_opportunities": self.optimization_opportunities,
            "performance_score": self.performance_score,
            "recommendations": self.recommendations,
        }


@dataclass
class RepositoryAnalysis:
    semantic_graph: SemanticGraph = field(default_factory=SemanticGraph)
    architecture: ArchitectureInfo = field(default_factory=ArchitectureInfo)
    threats: ThreatAnalysis = field(default_factory=ThreatAnalysis)
    performance: PerformanceAnalysis = field(default_factory=PerformanceAnalysis)
    files_analyzed: int = 0
    total_symbols: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "semantic_graph": self.semantic_graph.to_dict(),
            "architecture": {
                "modules": self.architecture.modules,
                "entry_points": self.architecture.entry_points,
                "dependencies": self.architecture.dependencies,
                "patterns": self.architecture.patterns,
                "design_patterns": self.architecture.design_patterns,
                "coupling": self.architecture.coupling,
                "cohesion": self.architecture.cohesion,
                "metrics": self.architecture.metrics,
            },
            "threats": {
                "vulnerabilities": self.threats.vulnerabilities,
                "security_issues": self.threats.security_issues,
                "risk_score": self.threats.risk_score,
                "recommendations": self.threats.recommendations,
            },
            "performance": {
                "bottlenecks": self.performance.bottlenecks,
                "optimization_opportunities": self.performance.optimization_opportunities,
                "performance_score": self.performance.performance_score,
                "recommendations": self.performance.recommendations,
            },
            "files_analyzed": self.files_analyzed,
            "total_symbols": self.total_symbols,
        }
