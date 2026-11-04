"""
ReAct Agent Module

.. deprecated:: 0.3.0
    Importing from 'gpt_computer.core.agent.react' is deprecated. Use
    'from gpt_computer.agent.react import ReActAgent' instead.
"""

import warnings

warnings.warn(
    "Importing from 'gpt_computer.core.agent.react' is deprecated and will be removed in version 1.0.0. "
    "Use 'from gpt_computer.agent.react import ReActAgent' instead. "
    "See MIGRATION_GUIDE.md for details.",
    DeprecationWarning,
    stacklevel=2,
)

from gpt_computer.agent.react import ReActAgent  # noqa: E402

__all__ = ["ReActAgent"]
