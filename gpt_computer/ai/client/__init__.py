"""
AI Client Package

Canonical location of the full AI client implementation, migrated from
``gptc.client``. The legacy package is now a compatibility shim.

Classes:
    Client: Synchronous AI client.
    AsyncClient: Asynchronous AI client.
    ChatCompletion: Chat completion interface.
    ClientFactory: Factory for creating client instances.
    AI: Legacy agent AI class (deprecated, re-exported).
    Message: Chat message type (deprecated, re-exported).
    AsyncAI: Async agent AI class (deprecated, re-exported).
    AIResponse: Async AI response type (deprecated, re-exported).
"""

import importlib

from gpt_computer.ai.client._impl import (
    AsyncClient,
    BaseClient,
    ChatCompletion,
    ChatCompletionChunk,
    Client,
    ClientFactory,
    ImagesResponse,
    IterResponse,
)
from gpt_computer.ai.client.types import Proxies

_LEGACY_EXPORTS = {
    "AI": "gpt_computer.core.ai",
    "Message": "gpt_computer.core.ai",
    "AIResponse": "gpt_computer.core.ai_async",
    "AsyncAI": "gpt_computer.core.ai_async",
}


def __getattr__(name):
    module_name = _LEGACY_EXPORTS.get(name)
    if module_name is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    module = importlib.import_module(module_name)
    return getattr(module, name)


__all__ = [
    "AI",
    "AIResponse",
    "AsyncAI",
    "AsyncClient",
    "BaseClient",
    "ChatCompletion",
    "ChatCompletionChunk",
    "Client",
    "ClientFactory",
    "ImagesResponse",
    "IterResponse",
    "Message",
    "Proxies",
]
