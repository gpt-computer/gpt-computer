"""Compatibility shim for ``gptc.client.factory``."""

import warnings

warnings.warn(
    "Importing from 'gptc.client.factory' is deprecated and will be removed in version 1.0.0. "
    "Use 'from gpt_computer.ai.client.factory import ...' instead. "
    "See MIGRATION_GUIDE.md for details.",
    DeprecationWarning,
    stacklevel=2,
)

from gpt_computer.ai.client.factory import (  # noqa: E402,F401
    AbstractClientFactory,
    create_custom_provider,
)

__all__ = ["AbstractClientFactory", "create_custom_provider"]
