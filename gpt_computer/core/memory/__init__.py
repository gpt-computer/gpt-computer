"""
Memory Package

.. deprecated:: 0.3.0
    Importing from 'gpt_computer.core.memory' is deprecated. Use
    'from gpt_computer.agent.memory import ...' instead.
"""

import warnings

warnings.warn(
    "Importing from 'gpt_computer.core.memory' is deprecated and will be removed in version 1.0.0. "
    "Use 'from gpt_computer.agent.memory import ...' instead. "
    "See MIGRATION_GUIDE.md for details.",
    DeprecationWarning,
    stacklevel=2,
)

from gpt_computer.agent.memory import (  # noqa: E402
    BaseMemory,
    DiskMemory,
    EmbeddingModel,
    VectorStore,
)

__all__ = ["BaseMemory", "DiskMemory", "VectorStore", "EmbeddingModel"]
