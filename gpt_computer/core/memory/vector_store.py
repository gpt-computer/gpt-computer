"""
Vector Store Module

.. deprecated:: 0.3.0
    Importing from 'gpt_computer.core.memory.vector_store' is deprecated. Use
    'from gpt_computer.agent.memory import VectorStore' instead.
"""

import warnings

warnings.warn(
    "Importing from 'gpt_computer.core.memory.vector_store' is deprecated and will be removed in version 1.0.0. "
    "Use 'from gpt_computer.agent.memory import VectorStore' instead. "
    "See MIGRATION_GUIDE.md for details.",
    DeprecationWarning,
    stacklevel=2,
)

from gpt_computer.agent.memory.vector_store import (  # noqa: E402
    EmbeddingModel,
    VectorStore,
)

__all__ = ["VectorStore", "EmbeddingModel"]
