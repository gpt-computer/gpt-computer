"""
Disk Memory Module

.. deprecated:: 0.3.0
    Importing from 'gpt_computer.core.default.disk_memory' is deprecated. Use
    'from gpt_computer.agent.memory import DiskMemory' instead.
"""

import warnings

warnings.warn(
    "Importing from 'gpt_computer.core.default.disk_memory' is deprecated and will be removed in version 1.0.0. "
    "Use 'from gpt_computer.agent.memory import DiskMemory' instead. "
    "See MIGRATION_GUIDE.md for details.",
    DeprecationWarning,
    stacklevel=2,
)

from gpt_computer.agent.memory.disk import DiskMemory  # noqa: E402

__all__ = ["DiskMemory"]
