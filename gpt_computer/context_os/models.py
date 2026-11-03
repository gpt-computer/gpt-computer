"""
Models Module

.. deprecated:: 0.3.0
    Importing from 'gpt_computer.context_os.models' is deprecated. Use
    'from gpt_computer.analysis.context.models import ...' instead.
"""

import warnings

warnings.warn(
    "Importing from 'gpt_computer.context_os.models' is deprecated and will be removed in version 1.0.0. "
    "Use 'from gpt_computer.analysis.context.models import ...' instead. "
    "See MIGRATION_GUIDE.md for details.",
    DeprecationWarning,
    stacklevel=2,
)

from gpt_computer.analysis.context.models import (  # noqa: E402
    Context,
    ContextGraph,
    ContextMetadata,
    ContextState,
    ContextStatus,
    ContextType,
)

__all__ = [
    "ContextType",
    "ContextStatus",
    "ContextMetadata",
    "ContextState",
    "Context",
    "ContextGraph",
]
