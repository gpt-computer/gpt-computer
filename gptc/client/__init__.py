"""Compatibility shim for the legacy ``gptc.client`` package.

The full implementation now lives in :mod:`gpt_computer.ai.client`. Importing
from ``gptc.client`` remains supported until version 1.0.0 and emits a
:class:`DeprecationWarning`.
"""

import warnings

warnings.warn(
    "Importing from 'gptc.client' is deprecated and will be removed in version 1.0.0. "
    "Use 'from gpt_computer.ai.client import ...' instead. "
    "See MIGRATION_GUIDE.md for details.",
    DeprecationWarning,
    stacklevel=2,
)

from gpt_computer.ai.client import (  # noqa: E402,F401
    AsyncClient,
    BaseClient,
    ChatCompletion,
    ChatCompletionChunk,
    Client,
    ClientFactory,
    ImagesResponse,
    IterResponse,
)
from gpt_computer.ai.client._impl import (  # noqa: E402,F401
    AsyncChat,
    AsyncCompletions,
    AsyncImages,
    Chat,
    Completions,
    Images,
)
from gpt_computer.ai.client.types import Proxies  # noqa: E402,F401

__all__ = [
    "AsyncChat",
    "AsyncClient",
    "AsyncCompletions",
    "AsyncImages",
    "BaseClient",
    "Chat",
    "ChatCompletion",
    "ChatCompletionChunk",
    "Client",
    "ClientFactory",
    "Completions",
    "Images",
    "ImagesResponse",
    "IterResponse",
    "Proxies",
]
