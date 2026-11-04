"""
Codemap Module

.. deprecated:: 0.3.0
    Importing from 'gpt_computer.codemap' is deprecated. Use
    'from gpt_computer.analysis.codemap import ...' instead.
"""

import warnings

warnings.warn(
    "Importing from 'gpt_computer.codemap' is deprecated and will be removed in version 1.0.0. "
    "Use 'from gpt_computer.analysis.codemap import ...' instead. "
    "See MIGRATION_GUIDE.md for details.",
    DeprecationWarning,
    stacklevel=2,
)

from gpt_computer.analysis.codemap import (  # noqa: E402
    CodeGraph,
    CodemapConfig,
    CodemapResult,
    GraphBuilder,
    PythonAnalyzer,
    Relationship,
    RelationshipKind,
    Symbol,
    SymbolKind,
    Visualizer,
)

__all__ = [
    "SymbolKind",
    "RelationshipKind",
    "Symbol",
    "Relationship",
    "CodeGraph",
    "CodemapConfig",
    "CodemapResult",
    "PythonAnalyzer",
    "GraphBuilder",
    "Visualizer",
]
