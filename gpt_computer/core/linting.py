"""
Linting Module

.. deprecated:: 0.3.0
    Importing from 'gpt_computer.core.linting' is deprecated. Use
    'from gpt_computer.infrastructure.linting import ...' instead.
"""

import warnings

warnings.warn(
    "Importing from 'gpt_computer.core.linting' is deprecated and will be removed in version 1.0.0. "
    "Use 'from gpt_computer.infrastructure.linting import ...' instead. "
    "See MIGRATION_GUIDE.md for details.",
    DeprecationWarning,
    stacklevel=2,
)

from gpt_computer.infrastructure.linting.checker import Linting  # noqa: E402

__all__ = ["Linting"]
