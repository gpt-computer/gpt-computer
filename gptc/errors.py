"""Compatibility shim for the legacy ``gptc.errors`` module.

The canonical error definitions now live in :mod:`gpt_computer.ai.errors`.
Importing from ``gptc.errors`` remains supported until version 1.0.0 and
emits a :class:`DeprecationWarning`.
"""

import warnings

warnings.warn(
    "Importing from 'gptc.errors' is deprecated and will be removed in version 1.0.0. "
    "Use 'from gpt_computer.ai.errors import ...' instead. "
    "See MIGRATION_GUIDE.md for details.",
    DeprecationWarning,
    stacklevel=2,
)

from gpt_computer.ai.errors import (  # noqa: E402,F401
    BadRequestError,
    CloudflareError,
    ConversationLimitError,
    GPTCError,
    MissingAuthError,
    MissingRequirementsError,
    ModelNotAllowedError,
    ModelNotFoundError,
    NestAsyncioError,
    NoMediaResponseError,
    NoValidHarFileError,
    PaymentRequiredError,
    ProviderException,
    ProviderNotFoundError,
    ProviderNotWorkingError,
    RateLimitError,
    ResponseError,
    ResponseStatusError,
    RetryNoProviderError,
    RetryProviderError,
    StreamNotSupportedError,
    TimeoutError,
    VersionNotFoundError,
)

__all__ = [
    "BadRequestError",
    "CloudflareError",
    "ConversationLimitError",
    "GPTCError",
    "MissingAuthError",
    "MissingRequirementsError",
    "ModelNotAllowedError",
    "ModelNotFoundError",
    "NestAsyncioError",
    "NoMediaResponseError",
    "NoValidHarFileError",
    "PaymentRequiredError",
    "ProviderException",
    "ProviderNotFoundError",
    "ProviderNotWorkingError",
    "RateLimitError",
    "ResponseError",
    "ResponseStatusError",
    "RetryNoProviderError",
    "RetryProviderError",
    "StreamNotSupportedError",
    "TimeoutError",
    "VersionNotFoundError",
]
