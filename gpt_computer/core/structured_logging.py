"""
Structured Logging Module

.. deprecated:: 0.3.0
    Importing from 'gpt_computer.core.structured_logging' is deprecated. Use
    'from gpt_computer.infrastructure.logging import ...' instead.
"""

import warnings

warnings.warn(
    "Importing from 'gpt_computer.core.structured_logging' is deprecated and will be removed in version 1.0.0. "
    "Use 'from gpt_computer.infrastructure.logging import ...' instead. "
    "See MIGRATION_GUIDE.md for details.",
    DeprecationWarning,
    stacklevel=2,
)

from gpt_computer.infrastructure.logging.structured import (  # noqa: E402
    CorrelationContext,
    StructuredFormatter,
    StructuredLogger,
    get_logger,
    log_performance,
    setup_structured_logging,
)

__all__ = [
    "CorrelationContext",
    "StructuredFormatter",
    "StructuredLogger",
    "get_logger",
    "setup_structured_logging",
    "log_performance",
]
