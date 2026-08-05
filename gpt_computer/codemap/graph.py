from __future__ import annotations

import os

from typing import Optional

from gpt_computer.codemap.models import (
    CodemapResult,
    Relationship,
    RelationshipKind,
    Symbol,
    SymbolKind,
)


class GraphBuilder:
    def __init__(self, result: CodemapResult):
        self.result = result
        self.graph = result.graph

    def build_file_dependencies(self) -> None:
        file_symbols = self.graph.get_symbols_by_kind(SymbolKind.FILE)
        file_map: dict[str, str] = {s.file_path: s.id for s in file_symbols}

        import_symbols = self.graph.get_symbols_by_kind(SymbolKind.IMPORT)
        for imp in import_symbols:
            import_path = imp.qualified_name.replace(".", "/")
            for file_path, file_id in file_map.items():
                rel_file = file_path.replace(os.sep, "/")
                if import_path in rel_file.replace(".py", ""):
                    self.graph.add_relationship(
                        Relationship(
                            source_id=imp.id,
                            target_id=file_id,
                            kind=RelationshipKind.IMPORTS,
                        )
                    )

    def build_package_structure(self) -> None:
        seen_dirs: dict[str, str] = {}
        file_symbols = self.graph.get_symbols_by_kind(SymbolKind.FILE)
        for fs in file_symbols:
            dir_path = os.path.dirname(fs.file_path)
            if not dir_path or dir_path == self.result.config.root_path:
                continue
            parts = (
                dir_path.replace(self.result.config.root_path, "")
                .strip(os.sep)
                .split(os.sep)
            )
            parts = [p for p in parts if p]
            parent_id: Optional[str] = None
            for i, part in enumerate(parts):
                dir_key = os.sep.join(parts[: i + 1])
                if dir_key not in seen_dirs:
                    mod_sym = Symbol(
                        name=part,
                        kind=SymbolKind.MODULE,
                        file_path=os.path.join(self.result.config.root_path, dir_key),
                        qualified_name=".".join(parts[: i + 1]),
                        line_start=1,
                        line_end=1,
                        parent_id=parent_id,
                    )
                    seen_dirs[dir_key] = mod_sym.id
                    self.graph.add_symbol(mod_sym)
                    if parent_id:
                        self.graph.add_relationship(
                            Relationship(
                                source_id=mod_sym.id,
                                target_id=parent_id,
                                kind=RelationshipKind.CONTAINS,
                            )
                        )
                parent_id = seen_dirs[dir_key]
            if parent_id:
                self.graph.add_relationship(
                    Relationship(
                        source_id=fs.id,
                        target_id=parent_id,
                        kind=RelationshipKind.CONTAINS,
                    )
                )

    def compute_complexity(self) -> None:
        for sym in self.graph.symbols.values():
            if sym.kind in (SymbolKind.FUNCTION, SymbolKind.METHOD):
                loc = sym.line_end - sym.line_start + 1
                sym.metadata["loc"] = loc
                if loc < 10:
                    sym.metadata["complexity"] = "low"
                elif loc < 30:
                    sym.metadata["complexity"] = "medium"
                else:
                    sym.metadata["complexity"] = "high"

    def compute_module_metrics(self) -> dict[str, dict]:
        file_map: dict[str, dict] = {}
        for sym in self.graph.symbols.values():
            fp = sym.file_path
            if fp not in file_map:
                file_map[fp] = {
                    "classes": 0,
                    "functions": 0,
                    "methods": 0,
                    "imports": 0,
                    "variables": 0,
                    "constants": 0,
                    "loc": 0,
                }
            if sym.kind == SymbolKind.CLASS:
                file_map[fp]["classes"] += 1
            elif sym.kind == SymbolKind.FUNCTION:
                file_map[fp]["functions"] += 1
            elif sym.kind == SymbolKind.METHOD:
                file_map[fp]["methods"] += 1
            elif sym.kind == SymbolKind.IMPORT:
                file_map[fp]["imports"] += 1
            elif sym.kind == SymbolKind.VARIABLE:
                file_map[fp]["variables"] += 1
            elif sym.kind == SymbolKind.CONSTANT:
                file_map[fp]["constants"] += 1

        for sym in self.graph.get_symbols_by_kind(SymbolKind.FILE):
            fp = sym.file_path
            if fp in file_map:
                file_map[fp]["loc"] = sym.line_end

        return file_map

    def detect_circular_dependencies(self) -> list[list[str]]:
        file_ids = {s.id for s in self.graph.get_symbols_by_kind(SymbolKind.FILE)}
        import_rels = self.graph.get_relationships(kind=RelationshipKind.IMPORTS)

        adj: dict[str, list[str]] = {fid: [] for fid in file_ids}
        for rel in import_rels:
            if rel.source_id in adj and rel.target_id in adj:
                adj[rel.source_id].append(rel.target_id)

        visited: set[str] = set()
        path_stack: list[str] = []
        cycles: list[list[str]] = []

        def dfs(node: str) -> None:
            visited.add(node)
            path_stack.append(node)
            for neighbor in adj.get(node, []):
                if neighbor in path_stack:
                    cycle_start = path_stack.index(neighbor)
                    cycles.append(path_stack[cycle_start:] + [neighbor])
                elif neighbor not in visited:
                    dfs(neighbor)
            path_stack.pop()

        for fid in file_ids:
            if fid not in visited:
                dfs(fid)

        resolved: list[list[str]] = []
        seen_cycles: set[str] = set()
        for cycle in cycles:
            key = "->".join(sorted(cycle))
            if key not in seen_cycles:
                seen_cycles.add(key)
                resolved.append(cycle)

        named_cycles = []
        for cycle in resolved:
            named = []
            for cid in cycle:
                s = self.graph.get_symbol(cid)
                named.append(s.qualified_name if s else cid)
            named_cycles.append(named)
        return named_cycles

    def build(self) -> GraphBuilder:
        self.build_file_dependencies()
        self.build_package_structure()
        self.compute_complexity()
        return self
