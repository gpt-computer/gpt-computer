"""
Repository Intelligence Module

.. deprecated:: 0.3.0
    Importing from 'gpt_computer.repository_intelligence' is deprecated. Use
    'from gpt_computer.analysis.repository import ...' instead.
"""

import warnings

warnings.warn(
    "Importing from 'gpt_computer.repository_intelligence' is deprecated and will be removed in version 1.0.0. "
    "Use 'from gpt_computer.analysis.repository import ...' instead. "
    "See MIGRATION_GUIDE.md for details.",
    DeprecationWarning,
    stacklevel=2,
)

from gpt_computer.analysis.repository import (  # noqa: E402
    ArchitectureInfo,
    DebugAgent,
    ExplainAgent,
    KnowledgeGraph,
    PerformanceAnalysis,
    RefactorAgent,
    RepositoryAnalysis,
    SecurityAgent,
    SemanticEdge,
    SemanticGraph,
    SemanticNode,
    ThreatAnalysis,
    TreeSitterAnalyzer,
    VisualizationAgent,
)

__all__ = [
    "SemanticNode",
    "SemanticEdge",
    "SemanticGraph",
    "ArchitectureInfo",
    "ThreatAnalysis",
    "PerformanceAnalysis",
    "TreeSitterAnalyzer",
    "KnowledgeGraph",
    "ExplainAgent",
    "DebugAgent",
    "RefactorAgent",
    "SecurityAgent",
    "VisualizationAgent",
    "RepositoryAnalysis",
]
