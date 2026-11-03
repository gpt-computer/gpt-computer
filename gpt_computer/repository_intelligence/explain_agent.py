"""
Explain Agent Module

.. deprecated:: 0.3.0
    Importing from 'gpt_computer.repository_intelligence.explain_agent' is deprecated. Use
    'from gpt_computer.analysis.repository import ExplainAgent' instead.
"""

import warnings

warnings.warn(
    "Importing from 'gpt_computer.repository_intelligence.explain_agent' is deprecated and will be removed in version 1.0.0. "
    "Use 'from gpt_computer.analysis.repository import ExplainAgent' instead. "
    "See MIGRATION_GUIDE.md for details.",
    DeprecationWarning,
    stacklevel=2,
)

from gpt_computer.analysis.repository.explain_agent import ExplainAgent  # noqa: E402

__all__ = ["ExplainAgent"]
