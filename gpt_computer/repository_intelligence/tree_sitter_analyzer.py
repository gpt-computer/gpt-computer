import os

from pathlib import Path
from typing import Any, Optional

from gpt_computer.codemap.models import CodemapConfig
from gpt_computer.repository_intelligence.models import (
    ArchitectureInfo,
    EdgeType,
    NodeType,
    PerformanceAnalysis,
    RepositoryAnalysis,
    SemanticEdge,
    SemanticGraph,
    SemanticNode,
    ThreatAnalysis,
)

try:
    import tree_sitter
    import tree_sitter_languages as ts_languages

    TREESITTER_AVAILABLE = True
except ImportError:
    TREESITTER_AVAILABLE = False


class TreeSitterAnalyzer:
    def __init__(self, config: Optional[CodemapConfig] = None):
        self.config = config or CodemapConfig()
        self.supported_languages = {
            "python": "python",
            "javascript": "javascript",
            "typescript": "typescript",
            "java": "java",
            "cpp": "cpp",
            "c": "c",
            "go": "go",
            "rust": "rust",
            "ruby": "ruby",
            "php": "php",
            "csharp": "csharp",
            "kotlin": "kotlin",
        }

    def _get_language(self, file_path: str) -> Optional[str]:
        ext = Path(file_path).suffix.lower()
        ext_to_lang = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".tsx": "typescript",
            ".java": "java",
            ".cpp": "cpp",
            ".cc": "cpp",
            ".cxx": "cpp",
            ".c": "c",
            ".go": "go",
            ".rs": "rust",
            ".rb": "ruby",
            ".php": "php",
            ".cs": "csharp",
            ".kt": "kotlin",
            ".kts": "kotlin",
        }
        return ext_to_lang.get(ext)

    def analyze_file(
        self, file_path: str, semantic_graph: SemanticGraph
    ) -> tuple[int, Optional[str]]:
        if not TREESITTER_AVAILABLE:
            return 0, "tree-sitter not installed"

        language = self._get_language(file_path)
        if not language:
            return 0, f"Unsupported language for {file_path}"

        try:
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                source = f.read()
        except Exception as e:
            return 0, f"Cannot read {file_path}: {e}"

        if len(source) > self.config.max_file_size:
            return 0, f"File too large: {file_path}"

        try:
            parser = tree_sitter.Parser()
            language_module = ts_languages.LANGUAGE_MAP[language]
            tree = parser.parse(source)

            self._extract_semantic_info(
                tree, language_module, file_path, semantic_graph
            )
            return len(semantic_graph.nodes), None
        except Exception as e:
            return 0, f"Tree-sitter error in {file_path}: {e}"

    def _extract_semantic_info(
        self,
        tree: tree_sitter.Tree,
        language_module: Any,
        file_path: str,
        semantic_graph: SemanticGraph,
    ) -> None:
        visitor = TreeSitterVisitor(language_module, file_path, semantic_graph)
        visitor.visit(tree.root_node)

    def analyze(self, path: Optional[str] = None) -> RepositoryAnalysis:
        root = path or self.config.root_path
        self.config.root_path = root

        result = RepositoryAnalysis()
        root_path = Path(root)

        if not root_path.exists():
            raise ValueError(f"Path does not exist: {root}")

        py_files: list[Path] = []
        if root_path.is_file():
            if self._should_include(str(root_path)):
                py_files.append(root_path)
        else:
            for f in root_path.rglob("*"):
                if f.is_file() and self._should_include(str(f)):
                    py_files.append(f)

        for py_file in py_files:
            n_syms, error = self.analyze_file(str(py_file), result.semantic_graph)
            if error:
                result.semantic_graph.nodes.get(
                    "error"
                ) or result.semantic_graph.add_node(
                    SemanticNode(
                        name="error",
                        node_type=NodeType.FILE,
                        file_path=str(py_file),
                        qualified_name=str(py_file),
                        metadata={"error": error},
                    )
                )

        result.files_analyzed = len(py_files)
        result.total_symbols = len(result.semantic_graph.nodes)

        self._analyze_architecture(result)
        self._analyze_threats(result)
        self._analyze_performance(result)

        return result

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

    def _analyze_architecture(self, result: RepositoryAnalysis) -> None:
        arch = ArchitectureInfo()

        files = [
            n
            for n in result.semantic_graph.nodes.values()
            if n.node_type == NodeType.FILE
        ]
        arch.modules = [f.qualified_name for f in files]

        classes = [
            n
            for n in result.semantic_graph.nodes.values()
            if n.node_type == NodeType.CLASS
        ]
        arch.entry_points = [
            c.qualified_name for c in classes if c.metadata.get("is_entry_point", False)
        ]

        imports = [
            e for e in result.semantic_graph.edges if e.edge_type == EdgeType.IMPORTS
        ]
        arch.dependencies = [
            f"{result.semantic_graph.get_node(e.source_id).name} -> {result.semantic_graph.get_node(e.target_id).name}"
            for e in imports
            if result.semantic_graph.get_node(e.source_id)
            and result.semantic_graph.get_node(e.target_id)
        ]

        result.architecture = arch

    def _analyze_threats(self, result: RepositoryAnalysis) -> None:
        threats = ThreatAnalysis()

        security_issues = []
        for node in result.semantic_graph.nodes.values():
            if node.node_type == NodeType.FUNCTION and node.metadata.get(
                "has_hardcoded_secrets", False
            ):
                security_issues.append(
                    {
                        "type": "hardcoded_secrets",
                        "location": node.qualified_name,
                        "severity": "high",
                        "description": f"Function {node.name} may contain hardcoded secrets",
                    }
                )

            if node.node_type == NodeType.IMPORT and "eval" in node.name.lower():
                security_issues.append(
                    {
                        "type": "unsafe_eval",
                        "location": node.qualified_name,
                        "severity": "medium",
                        "description": f"Import of eval function detected in {node.name}",
                    }
                )

        threats.security_issues = security_issues
        threats.risk_score = min(1.0, len(security_issues) * 0.2)
        threats.recommendations = [
            "Implement input validation",
            "Use parameterized queries",
            "Regular security audits",
        ]

        result.threats = threats

    def _analyze_performance(self, result: RepositoryAnalysis) -> None:
        perf = PerformanceAnalysis()

        bottlenecks = []
        for node in result.semantic_graph.nodes.values():
            if node.node_type in (NodeType.FUNCTION, NodeType.METHOD):
                if node.complexity > 10 or node.cyclomatic_complexity > 5:
                    bottlenecks.append(
                        {
                            "type": "high_complexity",
                            "location": node.qualified_name,
                            "complexity": node.complexity,
                            "cyclomatic": node.cyclomatic_complexity,
                            "severity": "medium",
                            "description": f"Function {node.name} has high complexity",
                        }
                    )

                if node.lines_of_code > 50:
                    bottlenecks.append(
                        {
                            "type": "long_function",
                            "location": node.qualified_name,
                            "loc": node.lines_of_code,
                            "severity": "low",
                            "description": f"Function {node.name} is too long ({node.lines_of_code} lines)",
                        }
                    )

        perf.bottlenecks = bottlenecks
        perf.performance_score = max(0.0, 1.0 - (len(bottlenecks) * 0.1))
        perf.recommendations = [
            "Refactor complex functions",
            "Implement caching",
            "Optimize database queries",
        ]

        result.performance = perf


class TreeSitterVisitor:
    def __init__(
        self, language_module: Any, file_path: str, semantic_graph: SemanticGraph
    ):
        self.language_module = language_module
        self.file_path = file_path
        self.semantic_graph = semantic_graph
        self.scope_stack: list[str] = []

    def visit(self, node: tree_sitter.Node) -> None:
        node_type = self.language_module.node_type_names[node.type]
        self._process_node(node, node_type)

        for child in node.children:
            self.visit(child)

    def _process_node(self, node: tree_sitter.Node, node_type: str) -> None:
        if node_type in self.language_module.keyword_names:
            return

        node_name = node.text.decode("utf-8") if node.text else ""
        node_type_enum = self._map_node_type(node_type, node_name)

        if node_type_enum == NodeType.FILE:
            return

        qual_name = (
            ".".join(self.scope_stack + [node_name]) if self.scope_stack else node_name
        )

        semantic_node = SemanticNode(
            name=node_name,
            node_type=node_type_enum,
            file_path=self.file_path,
            qualified_name=qual_name,
            line_start=node.start_point[0] + 1,
            line_end=node.end_point[0] + 1,
            column_start=node.start_point[1],
            column_end=node.end_point[1],
            metadata={"tree_sitter_type": node_type},
        )

        self.scope_stack.append(node_name)
        node_id = self.semantic_graph.add_node(semantic_node)
        self.scope_stack.pop()

        if self.scope_stack:
            parent_id = self.semantic_graph.add_node(
                SemanticNode(
                    name=self.scope_stack[-1],
                    node_type=NodeType.CLASS
                    if node_type_enum == NodeType.METHOD
                    else node_type_enum,
                    file_path=self.file_path,
                    qualified_name=".".join(self.scope_stack),
                )
            )
            self.semantic_graph.add_edge(
                SemanticEdge(
                    source_id=node_id,
                    target_id=parent_id,
                    edge_type=EdgeType.CONTAINS,
                )
            )

    def _map_node_type(self, node_type: str, name: str) -> NodeType:
        type_mapping = {
            "function_definition": NodeType.FUNCTION,
            "method_definition": NodeType.METHOD,
            "class_definition": NodeType.CLASS,
            "import_statement": NodeType.IMPORT,
            "import_from_statement": NodeType.IMPORT,
            "variable_definition": NodeType.VARIABLE,
            "constant_definition": NodeType.CONSTANT,
            "interface_definition": NodeType.INTERFACE,
            "enum_definition": NodeType.ENUM,
            "package_declaration": NodeType.PACKAGE,
            "module": NodeType.MODULE,
        }

        return type_mapping.get(node_type, NodeType.FILE)
