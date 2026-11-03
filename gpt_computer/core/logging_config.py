"""
Logging Configuration Module

.. deprecated:: 0.3.0
    Importing from 'gpt_computer.core.logging_config' is deprecated. Use
    'from gpt_computer.infrastructure.logging import ...' instead.
"""

import warnings

warnings.warn(
    "Importing from 'gpt_computer.core.logging_config' is deprecated and will be removed in version 1.0.0. "
    "Use 'from gpt_computer.infrastructure.logging import ...' instead. "
    "See MIGRATION_GUIDE.md for details.",
    DeprecationWarning,
    stacklevel=2,
)

from gpt_computer.infrastructure.logging.config import (  # noqa: E402
    MemoryLogHandler,
    setup_logging,
)

__all__ = ["MemoryLogHandler", "setup_logging"]
