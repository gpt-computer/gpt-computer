"""
Refactor Agent Module

.. deprecated:: 0.3.0
    Importing from 'gpt_computer.repository_intelligence.refactor_agent' is deprecated. Use
    'from gpt_computer.analysis.repository import RefactorAgent' instead.
"""

import warnings

warnings.warn(
    "Importing from 'gpt_computer.repository_intelligence.refactor_agent' is deprecated and will be removed in version 1.0.0. "
    "Use 'from gpt_computer.analysis.repository import RefactorAgent' instead. "
    "See MIGRATION_GUIDE.md for details.",
    DeprecationWarning,
    stacklevel=2,
)

from gpt_computer.analysis.repository.refactor_agent import RefactorAgent  # noqa: E402

__all__ = ["RefactorAgent"]
