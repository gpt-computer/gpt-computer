"""
Models Module

.. deprecated:: 0.3.0
    Importing from 'gpt_computer.repository_intelligence.models' is deprecated. Use
    'from gpt_computer.analysis.repository.models import ...' instead.
"""

import warnings

warnings.warn(
    "Importing from 'gpt_computer.repository_intelligence.models' is deprecated and will be removed in version 1.0.0. "
    "Use 'from gpt_computer.analysis.repository.models import ...' instead. "
    "See MIGRATION_GUIDE.md for details.",
    DeprecationWarning,
    stacklevel=2,
)

from gpt_computer.analysis.repository.models import (  # noqa: E402
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

__all__ = [
    "NodeType",
    "EdgeType",
    "SemanticNode",
    "SemanticEdge",
    "SemanticGraph",
    "ArchitectureInfo",
    "ThreatAnalysis",
    "PerformanceAnalysis",
    "RepositoryAnalysis",
]
