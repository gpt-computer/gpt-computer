"""Compatibility shim for ``gptc.client.types``."""

import warnings

warnings.warn(
    "Importing from 'gptc.client.types' is deprecated and will be removed in version 1.0.0. "
    "Use 'from gpt_computer.ai.client.types import ...' instead. "
    "See MIGRATION_GUIDE.md for details.",
    DeprecationWarning,
    stacklevel=2,
)

from gpt_computer.ai.client.types import (  # noqa: E402,F401
    AsyncIterResponse,
    Client,
    IterResponse,
    Proxies,
)

__all__ = ["AsyncIterResponse", "Client", "IterResponse", "Proxies"]
