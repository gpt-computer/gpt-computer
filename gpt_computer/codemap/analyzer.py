from __future__ import annotations

import ast
import os

from pathlib import Path
from typing import Optional

from gpt_computer.codemap.models import (
    CodeGraph,
    CodemapConfig,
    CodemapResult,
    Relationship,
    RelationshipKind,
    Symbol,
    SymbolKind,
)


class _SymbolVisitor(ast.NodeVisitor):
    def __init__(self, file_path: str, source_lines: list[str]):
        self.file_path = file_path
        self.source_lines = source_lines
        self.graph = CodeGraph()
        self.current_class: Optional[Symbol] = None
        self._scope_stack: list[str] = []

    def _qualified_name(self, name: str) -> str:
        parts = self._scope_stack + [name]
        return ".".join(parts)

    def _make_symbol(
        self,
        name: str,
        kind: SymbolKind,
        node: ast.AST,
    ) -> Symbol:
        qualname = self._qualified_name(name)
        sym = Symbol(
            name=name,
            kind=kind,
            file_path=self.file_path,
            qualified_name=qualname,
            line_start=node.lineno,
            line_end=getattr(node, "end_lineno", node.lineno),
            column_start=getattr(node, "col_offset", 0),
            column_end=getattr(node, "end_col_offset", 0),
        )
        if self.current_class:
            sym.parent_id = self.current_class.id
        return sym

    def _docstring(self, node: ast.AST) -> str:
        body = getattr(node, "body", [])
        if (
            body
            and isinstance(body[0], ast.Expr)
            and isinstance(body[0].value, ast.Constant)
            and isinstance(body[0].value.value, str)
        ):
            return body[0].value.value.strip()
        return ""

    def _decorator_names(self, node: ast.AST) -> list[str]:
        return [
            d.id
            if isinstance(d, ast.Name)
            else (d.attr if isinstance(d, ast.Attribute) else ast.unparse(d))
            for d in node.decorator_list
        ]

    def visit_Module(self, node: ast.Module) -> None:
        module_sym = Symbol(
            name=os.path.basename(self.file_path),
            kind=SymbolKind.FILE,
            file_path=self.file_path,
            qualified_name=self.file_path,
            line_start=1,
            line_end=len(self.source_lines),
            docstring=self._docstring(node),
        )
        self.graph.add_symbol(module_sym)
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        sym = self._make_symbol(node.name, SymbolKind.CLASS, node)
        sym.docstring = self._docstring(node)
        decorators = self._decorator_names(node)
        if decorators:
            sym.metadata["decorators"] = decorators

        if node.bases:
            sym.metadata["base_classes"] = [ast.unparse(b) for b in node.bases]

        self.graph.add_symbol(sym)

        for base in node.bases:
            base_name = ast.unparse(base)
            base_sym = Symbol(
                name=base_name,
                kind=SymbolKind.CLASS,
                file_path=self.file_path,
                qualified_name=base_name,
                line_start=node.lineno,
                line_end=node.lineno,
            )
            base_id = self.graph.add_symbol(base_sym)
            self.graph.add_relationship(
                Relationship(
                    source_id=sym.id,
                    target_id=base_id,
                    kind=RelationshipKind.INHERITS,
                )
            )

        old_class = self.current_class
        self.current_class = sym
        self._scope_stack.append(node.name)
        self.generic_visit(node)
        self._scope_stack.pop()
        self.current_class = old_class

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        kind = SymbolKind.METHOD if self.current_class else SymbolKind.FUNCTION
        sym = self._make_symbol(node.name, kind, node)
        sym.docstring = self._docstring(node)

        decorators = self._decorator_names(node)
        if decorators:
            sym.metadata["decorators"] = decorators

        if node.returns:
            sym.metadata["return_type"] = ast.unparse(node.returns)

        params = []
        for arg in node.args.args:
            arg_info = arg.arg
            if arg.annotation:
                arg_info += f": {ast.unparse(arg.annotation)}"
            params.append(arg_info)
        if node.args.vararg:
            params.append(f"*{node.args.vararg.arg}")
        if node.args.kwonlyargs:
            for arg in node.args.kwonlyargs:
                arg_info = arg.arg
                if arg.annotation:
                    arg_info += f": {ast.unparse(arg.annotation)}"
                params.append(arg_info)
        if node.args.kwarg:
            params.append(f"**{node.args.kwarg.arg}")
        sym.metadata["params"] = params
        sym.metadata["async"] = False

        self.graph.add_symbol(sym)

        if self.current_class:
            self.graph.add_relationship(
                Relationship(
                    source_id=sym.id,
                    target_id=self.current_class.id,
                    kind=RelationshipKind.CONTAINS,
                )
            )

        self._scope_stack.append(node.name)
        self.generic_visit(node)
        self._scope_stack.pop()

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        kind = SymbolKind.METHOD if self.current_class else SymbolKind.FUNCTION
        sym = self._make_symbol(node.name, kind, node)
        sym.docstring = self._docstring(node)

        decorators = self._decorator_names(node)
        if decorators:
            sym.metadata["decorators"] = decorators

        if node.returns:
            sym.metadata["return_type"] = ast.unparse(node.returns)

        params = []
        for arg in node.args.args:
            arg_info = arg.arg
            if arg.annotation:
                arg_info += f": {ast.unparse(arg.annotation)}"
            params.append(arg_info)
        sym.metadata["params"] = params
        sym.metadata["async"] = True

        self.graph.add_symbol(sym)

        if self.current_class:
            self.graph.add_relationship(
                Relationship(
                    source_id=sym.id,
                    target_id=self.current_class.id,
                    kind=RelationshipKind.CONTAINS,
                )
            )

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            sym = Symbol(
                name=alias.asname or alias.name,
                kind=SymbolKind.IMPORT,
                file_path=self.file_path,
                qualified_name=alias.name,
                line_start=node.lineno,
                line_end=node.lineno,
                metadata={"asname": alias.asname} if alias.asname else {},
            )
            self.graph.add_symbol(sym)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        module = node.module or ""
        for alias in node.names:
            full_import = f"{module}.{alias.name}" if module else alias.name
            sym = Symbol(
                name=alias.asname or alias.name,
                kind=SymbolKind.IMPORT,
                file_path=self.file_path,
                qualified_name=full_import,
                line_start=node.lineno,
                line_end=node.lineno,
                metadata={
                    "module": module,
                    "asname": alias.asname,
                }
                if alias.asname
                else {"module": module},
            )
            self.graph.add_symbol(sym)

    def visit_Assign(self, node: ast.Assign) -> None:
        for target in node.targets:
            if isinstance(target, ast.Name):
                if target.id.isupper() and len(target.id) > 1:
                    kind = SymbolKind.CONSTANT
                else:
                    kind = SymbolKind.VARIABLE
                sym = self._make_symbol(target.id, kind, node)
                if isinstance(node.value, ast.Constant):
                    sym.metadata["value"] = repr(node.value.value)
                elif isinstance(node.value, (ast.List, ast.Dict, ast.Set, ast.Tuple)):
                    sym.metadata["value_type"] = type(node.value).__name__
                self.graph.add_symbol(sym)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        if isinstance(node.target, ast.Name):
            kind = (
                SymbolKind.CONSTANT
                if (node.target.id.isupper() and len(node.target.id) > 1)
                else SymbolKind.VARIABLE
            )
            sym = self._make_symbol(node.target.id, kind, node)
            sym.metadata["annotation"] = ast.unparse(node.annotation)
            self.graph.add_symbol(sym)

    def visit_Call(self, node: ast.Call) -> None:
        called_name = ""
        if isinstance(node.func, ast.Name):
            called_name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            called_name = ast.unparse(node.func)

        if called_name:
            called_sym = Symbol(
                name=called_name,
                kind=SymbolKind.FUNCTION,
                file_path=self.file_path,
                qualified_name=called_name,
                line_start=node.lineno,
                line_end=node.lineno,
            )
            called_id = self.graph.add_symbol(called_sym)
            if self._scope_stack:
                context_name = self._qualified_name("")
                for sym_id, sym in self.graph.symbols.items():
                    if sym.qualified_name == context_name.rstrip(".") or (
                        self.current_class and sym.id == self.current_class.id
                    ):
                        self.graph.add_relationship(
                            Relationship(
                                source_id=sym_id,
                                target_id=called_id,
                                kind=RelationshipKind.CALLS,
                            )
                        )
        self.generic_visit(node)


class PythonAnalyzer:
    def __init__(self, config: Optional[CodemapConfig] = None):
        self.config = config or CodemapConfig()

    def _should_include(self, file_path: str) -> bool:
        rel = os.path.relpath(file_path, self.config.root_path)
        for pat in self.config.exclude_patterns:
            if pat in rel.split(os.sep):
                return False
        for ext in self.config.include_patterns:
            if ext.startswith("*"):
                if file_path.endswith(ext[1:]):
                    return True
        return any(
            file_path.endswith(e.replace("*", "")) for e in self.config.include_patterns
        )

    def analyze_file(
        self, file_path: str, graph: CodeGraph
    ) -> tuple[int, int, Optional[str]]:
        try:
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                source = f.read()
        except Exception as e:
            return 0, 0, f"Cannot read {file_path}: {e}"

        if len(source) > self.config.max_file_size:
            return 0, 0, f"File too large: {file_path}"

        source_lines = source.splitlines()
        try:
            tree = ast.parse(source, filename=file_path)
        except SyntaxError as e:
            return 0, len(source_lines), f"Syntax error in {file_path}: {e}"

        visitor = _SymbolVisitor(file_path, source_lines)
        visitor.visit(tree)
        graph.merge(visitor.graph)

        return len(visitor.graph.symbols), len(source_lines), None

    def analyze(self, path: Optional[str] = None) -> CodemapResult:
        root = path or self.config.root_path
        self.config.root_path = root

        result = CodemapResult(config=self.config)
        root_path = Path(root)

        if not root_path.exists():
            result.errors.append(f"Path does not exist: {root}")
            return result

        py_files: list[Path] = []
        if root_path.is_file():
            if self._should_include(str(root_path)):
                py_files.append(root_path)
        else:
            for f in root_path.rglob("*"):
                if f.is_file() and self._should_include(str(f)):
                    py_files.append(f)

        for py_file in py_files:
            n_syms, n_lines, error = self.analyze_file(str(py_file), result.graph)
            if error:
                result.errors.append(error)
            result.files_analyzed += 1 if n_syms > 0 or not error else 0
            result.total_lines += n_lines

        result.files_analyzed = len(py_files)
        return result
