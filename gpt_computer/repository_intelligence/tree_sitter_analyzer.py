"""
Tree Sitter Analyzer Module

.. deprecated:: 0.3.0
    Importing from 'gpt_computer.repository_intelligence.tree_sitter_analyzer' is deprecated. Use
    'from gpt_computer.analysis.repository import TreeSitterAnalyzer' instead.
"""

import warnings

warnings.warn(
    "Importing from 'gpt_computer.repository_intelligence.tree_sitter_analyzer' is deprecated and will be removed in version 1.0.0. "
    "Use 'from gpt_computer.analysis.repository import TreeSitterAnalyzer' instead. "
    "See MIGRATION_GUIDE.md for details.",
    DeprecationWarning,
    stacklevel=2,
)

from gpt_computer.analysis.repository.tree_sitter_analyzer import (  # noqa: E402
    TreeSitterAnalyzer,
)

__all__ = ["TreeSitterAnalyzer"]
