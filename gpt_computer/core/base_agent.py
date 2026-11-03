"""
Base Agent Module

.. deprecated:: 0.3.0
    Importing from 'gpt_computer.core.base_agent' is deprecated. Use
    'from gpt_computer.agent import BaseAgent' instead.
"""

import warnings

warnings.warn(
    "Importing from 'gpt_computer.core.base_agent' is deprecated and will be removed in version 1.0.0. "
    "Use 'from gpt_computer.agent import BaseAgent' instead. "
    "See MIGRATION_GUIDE.md for details.",
    DeprecationWarning,
    stacklevel=2,
)

from gpt_computer.agent.base import BaseAgent  # noqa: E402

__all__ = ["BaseAgent"]
