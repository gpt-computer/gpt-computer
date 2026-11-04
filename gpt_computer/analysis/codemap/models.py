import uuid

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


class SymbolKind(Enum):
    FILE = "file"
    MODULE = "module"
    CLASS = "class"
    FUNCTION = "function"
    METHOD = "method"
    VARIABLE = "variable"
    IMPORT = "import"
    INTERFACE = "interface"
    ENUM = "enum"
    CONSTANT = "constant"
    DECORATOR = "decorator"
    TYPE_ALIAS = "type_alias"


class RelationshipKind(Enum):
    IMPORTS = "imports"
    CALLS = "calls"
    INHERITS = "inherits"
    CONTAINS = "contains"
    IMPLEMENTS = "implements"
    USES = "uses"
    DECORATES = "decorates"
    ASSIGNED_TO = "assigned_to"
    RETURN_TYPE = "return_type"
    PARAMETER_TYPE = "parameter_type"


@dataclass
class Symbol:
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    name: str = ""
    kind: SymbolKind = SymbolKind.FILE
    file_path: str = ""
    qualified_name: str = ""
    line_start: int = 0
    line_end: int = 0
    column_start: int = 0
    column_end: int = 0
    docstring: str = ""
    parent_id: Optional[str] = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Relationship:
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    source_id: str = ""
    target_id: str = ""
    kind: RelationshipKind = RelationshipKind.USES
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class CodeGraph:
    symbols: dict[str, Symbol] = field(default_factory=dict)
    relationships: list[Relationship] = field(default_factory=list)

    def add_symbol(self, symbol: Symbol) -> str:
        self.symbols[symbol.id] = symbol
        return symbol.id

    def add_relationship(self, rel: Relationship) -> str:
        self.relationships.append(rel)
        return rel.id

    def get_symbol(self, symbol_id: str) -> Optional[Symbol]:
        return self.symbols.get(symbol_id)

    def get_relationships(
        self, symbol_id: Optional[str] = None, kind: Optional[RelationshipKind] = None
    ) -> list[Relationship]:
        result = self.relationships
        if symbol_id:
            result = [
                r
                for r in result
                if r.source_id == symbol_id or r.target_id == symbol_id
            ]
        if kind:
            result = [r for r in result if r.kind == kind]
        return result

    def get_symbols_by_kind(self, kind: SymbolKind) -> list[Symbol]:
        return [s for s in self.symbols.values() if s.kind == kind]

    def get_symbols_in_file(self, file_path: str) -> list[Symbol]:
        return [s for s in self.symbols.values() if s.file_path == file_path]

    def merge(self, other: "CodeGraph") -> None:
        self.symbols.update(other.symbols)
        existing_ids = {r.id for r in self.relationships}
        for rel in other.relationships:
            if rel.id not in existing_ids:
                self.relationships.append(rel)

    def to_dict(self) -> dict[str, Any]:
        return {
            "symbols": {
                sid: {
                    "id": s.id,
                    "name": s.name,
                    "kind": s.kind.value,
                    "file_path": s.file_path,
                    "qualified_name": s.qualified_name,
                    "line_start": s.line_start,
                    "line_end": s.line_end,
                    "column_start": s.column_start,
                    "column_end": s.column_end,
                    "docstring": s.docstring[:200] if s.docstring else "",
                    "parent_id": s.parent_id,
                    "metadata": s.metadata,
                }
                for sid, s in self.symbols.items()
            },
            "relationships": [
                {
                    "id": r.id,
                    "source_id": r.source_id,
                    "target_id": r.target_id,
                    "kind": r.kind.value,
                    "metadata": r.metadata,
                }
                for r in self.relationships
            ],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CodeGraph":
        graph = cls()
        for sid, sdata in data.get("symbols", {}).items():
            s = Symbol(
                id=sdata["id"],
                name=sdata["name"],
                kind=SymbolKind(sdata["kind"]),
                file_path=sdata["file_path"],
                qualified_name=sdata["qualified_name"],
                line_start=sdata["line_start"],
                line_end=sdata["line_end"],
                column_start=sdata["column_start"],
                column_end=sdata["column_end"],
                docstring=sdata.get("docstring", ""),
                parent_id=sdata.get("parent_id"),
                metadata=sdata.get("metadata", {}),
            )
            graph.symbols[s.id] = s
        for rdata in data.get("relationships", []):
            r = Relationship(
                id=rdata["id"],
                source_id=rdata["source_id"],
                target_id=rdata["target_id"],
                kind=RelationshipKind(rdata["kind"]),
                metadata=rdata.get("metadata", {}),
            )
            graph.relationships.append(r)
        return graph


@dataclass
class CodemapConfig:
    root_path: str = "."
    include_patterns: list[str] = field(default_factory=lambda: ["*.py"])
    exclude_patterns: list[str] = field(
        default_factory=lambda: [
            "__pycache__",
            ".git",
            "node_modules",
            "venv",
            ".venv",
            ".env",
            "dist",
            "build",
            "*.egg-info",
            ".mypy_cache",
            ".pytest_cache",
            "htmlcov",
        ]
    )
    max_file_size: int = 1024 * 100
    analyze_docstrings: bool = True
    analyze_calls: bool = True
    analyze_inheritance: bool = True
    analyze_imports: bool = True
    analyze_data_flow: bool = False


@dataclass
class CodemapResult:
    graph: CodeGraph = field(default_factory=CodeGraph)
    config: CodemapConfig = field(default_factory=CodemapConfig)
    files_analyzed: int = 0
    total_lines: int = 0
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "graph": self.graph.to_dict(),
            "config": {
                "root_path": self.config.root_path,
                "files_analyzed": self.files_analyzed,
                "total_lines": self.total_lines,
            },
            "metrics": self.summary(),
            "errors": self.errors,
        }

    def summary(self) -> dict[str, Any]:
        symbols = self.graph.symbols
        return {
            "files": len(self.graph.get_symbols_by_kind(SymbolKind.FILE)),
            "classes": len(self.graph.get_symbols_by_kind(SymbolKind.CLASS)),
            "functions": len(self.graph.get_symbols_by_kind(SymbolKind.FUNCTION)),
            "methods": len(self.graph.get_symbols_by_kind(SymbolKind.METHOD)),
            "imports": len(self.graph.get_symbols_by_kind(SymbolKind.IMPORT)),
            "variables": len(self.graph.get_symbols_by_kind(SymbolKind.VARIABLE)),
            "relationships": len(self.graph.relationships),
            "total_symbols": len(symbols),
        }
