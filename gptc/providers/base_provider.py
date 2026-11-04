"""Compatibility shim for the legacy ``gptc.providers.base_provider`` module."""

import warnings

warnings.warn(
    "Importing from 'gptc.providers.base_provider' is deprecated and will be removed in version 1.0.0. "
    "Use 'from gpt_computer.ai.providers.base_provider import ...' instead. "
    "See MIGRATION_GUIDE.md for details.",
    DeprecationWarning,
    stacklevel=2,
)

from gpt_computer.ai.providers.base_provider import (  # noqa: E402,F401
    AbstractProvider,
    AsyncAuthedProvider,
    AsyncGeneratorProvider,
    AsyncProvider,
    AuthFileMixin,
    ProviderModelMixin,
    RaiseErrorMixin,
    get_async_provider_method,
    get_provider_method,
)

__all__ = [
    "AbstractProvider",
    "AsyncAuthedProvider",
    "AsyncGeneratorProvider",
    "AsyncProvider",
    "AuthFileMixin",
    "ProviderModelMixin",
    "RaiseErrorMixin",
    "get_async_provider_method",
    "get_provider_method",
]
