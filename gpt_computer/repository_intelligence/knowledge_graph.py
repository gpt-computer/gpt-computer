"""
Knowledge Graph Module

.. deprecated:: 0.3.0
    Importing from 'gpt_computer.repository_intelligence.knowledge_graph' is deprecated. Use
    'from gpt_computer.analysis.repository import KnowledgeGraph' instead.
"""

import warnings

warnings.warn(
    "Importing from 'gpt_computer.repository_intelligence.knowledge_graph' is deprecated and will be removed in version 1.0.0. "
    "Use 'from gpt_computer.analysis.repository import KnowledgeGraph' instead. "
    "See MIGRATION_GUIDE.md for details.",
    DeprecationWarning,
    stacklevel=2,
)

from gpt_computer.analysis.repository.knowledge_graph import (  # noqa: E402
    KnowledgeGraph,
)

__all__ = ["KnowledgeGraph"]
