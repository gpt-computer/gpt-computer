"""
Debug Agent Module

.. deprecated:: 0.3.0
    Importing from 'gpt_computer.repository_intelligence.debug_agent' is deprecated. Use
    'from gpt_computer.analysis.repository import DebugAgent' instead.
"""

import warnings

warnings.warn(
    "Importing from 'gpt_computer.repository_intelligence.debug_agent' is deprecated and will be removed in version 1.0.0. "
    "Use 'from gpt_computer.analysis.repository import DebugAgent' instead. "
    "See MIGRATION_GUIDE.md for details.",
    DeprecationWarning,
    stacklevel=2,
)

from gpt_computer.analysis.repository.debug_agent import DebugAgent  # noqa: E402

__all__ = ["DebugAgent"]
