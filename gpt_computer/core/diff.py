"""
Diff Utilities Module

.. deprecated:: 0.3.0
    Importing from 'gpt_computer.core.diff' is deprecated. Use
    'from gpt_computer.infrastructure.diff import ...' instead.
"""

import warnings

warnings.warn(
    "Importing from 'gpt_computer.core.diff' is deprecated and will be removed in version 1.0.0. "
    "Use 'from gpt_computer.infrastructure.diff import ...' instead. "
    "See MIGRATION_GUIDE.md for details.",
    DeprecationWarning,
    stacklevel=2,
)

from gpt_computer.infrastructure.diff.parser import (  # noqa: E402
    ADD,
    REMOVE,
    RETAIN,
    Diff,
    Hunk,
    count_ratio,
    is_similar,
)

__all__ = ["Hunk", "Diff", "is_similar", "count_ratio", "RETAIN", "ADD", "REMOVE"]
