"""
OpenTelemetry Tracing Module

.. deprecated:: 0.3.0
    Importing from 'gpt_computer.core.tracing' is deprecated. Use
    'from gpt_computer.infrastructure.tracing import ...' instead.
"""

import warnings

warnings.warn(
    "Importing from 'gpt_computer.core.tracing' is deprecated and will be removed in version 1.0.0. "
    "Use 'from gpt_computer.infrastructure.tracing import ...' instead. "
    "See MIGRATION_GUIDE.md for details.",
    DeprecationWarning,
    stacklevel=2,
)

from gpt_computer.infrastructure.tracing.tracer import (  # noqa: E402
    SpanWrapper,
    TracingManager,
    get_tracer,
    get_tracing_manager,
    setup_tracing,
    trace_async_function,
)

__all__ = [
    "TracingManager",
    "SpanWrapper",
    "get_tracing_manager",
    "setup_tracing",
    "get_tracer",
    "trace_async_function",
]
