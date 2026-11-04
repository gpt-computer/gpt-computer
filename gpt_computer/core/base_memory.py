"""
Base Memory Module

.. deprecated:: 0.3.0
    Importing from 'gpt_computer.core.base_memory' is deprecated. Use
    'from gpt_computer.agent.memory import BaseMemory' instead.
"""

import warnings

warnings.warn(
    "Importing from 'gpt_computer.core.base_memory' is deprecated and will be removed in version 1.0.0. "
    "Use 'from gpt_computer.agent.memory import BaseMemory' instead. "
    "See MIGRATION_GUIDE.md for details.",
    DeprecationWarning,
    stacklevel=2,
)

from gpt_computer.agent.memory.base import BaseMemory  # noqa: E402

__all__ = ["BaseMemory"]
