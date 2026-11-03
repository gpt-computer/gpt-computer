"""Compatibility shim for the legacy ``gptc.providers.retry_provider`` module.

The canonical implementation now lives in
:mod:`gpt_computer.ai.providers.retry_provider`. Importing from
``gptc.providers.retry_provider`` remains supported until version 1.0.0 and
emits a :class:`DeprecationWarning`.
"""

import warnings

warnings.warn(
    "Importing from 'gptc.providers.retry_provider' is deprecated and will be removed in version 1.0.0. "
    "Use 'from gpt_computer.ai.providers.retry_provider import ...' instead. "
    "See MIGRATION_GUIDE.md for details.",
    DeprecationWarning,
    stacklevel=2,
)

from gpt_computer.ai.providers.retry_provider import (  # noqa: E402,F401
    IterListProvider,
    ProviderCircuitBreaker,
    RetryProvider,
    RotatedProvider,
    _prepare_provider_kwargs,
    _resolve_model,
    raise_exceptions,
)

__all__ = [
    "IterListProvider",
    "ProviderCircuitBreaker",
    "RetryProvider",
    "RotatedProvider",
    "raise_exceptions",
]
