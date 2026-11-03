"""Compatibility shim for the legacy ``gptc.providers.types`` module.

The canonical definitions now live in
:mod:`gpt_computer.ai.providers.types` (re-exported from
:mod:`gpt_computer.ai.providers.base`). Importing from ``gptc.providers.types``
remains supported until version 1.0.0 and emits a :class:`DeprecationWarning`.
"""

import warnings

warnings.warn(
    "Importing from 'gptc.providers.types' is deprecated and will be removed in version 1.0.0. "
    "Use 'from gpt_computer.ai.providers.types import ...' instead. "
    "See MIGRATION_GUIDE.md for details.",
    DeprecationWarning,
    stacklevel=2,
)

from gpt_computer.ai.providers.types import (  # noqa: E402,F401
    BaseProvider,
    BaseRetryProvider,
    ProviderType,
    Streaming,
)

__all__ = ["BaseProvider", "BaseRetryProvider", "ProviderType", "Streaming"]
