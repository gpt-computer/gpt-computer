from __future__ import annotations

import importlib
import logging
import warnings

warnings.warn(
    "Importing from 'gptc' is deprecated and will be removed in version 1.0.0. "
    "Use the corresponding import from 'gpt_computer.ai' instead. "
    "See MIGRATION_GUIDE.md for details.",
    DeprecationWarning,
    stacklevel=2,
)

from gpt_computer.infrastructure import debug  # noqa: E402,F401

from . import version  # noqa: E402,F401
from .cookies import get_cookies, get_cookies_async, set_cookies  # noqa: E402,F401

__all__ = [
    "ChatCompletion",
    "Client",
    "AsyncClient",
    "Model",
    "ClientFactory",
    "create_custom_provider",
]

# Configure logger
logger = logging.getLogger("gptc")
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter(logging.BASIC_FORMAT))
logger.addHandler(handler)
logger.setLevel(logging.ERROR)


def __getattr__(name):
    """Lazily resolve migrated public objects."""
    if name == "ChatCompletion":
        from gpt_computer.ai.chat_completion import ChatCompletionAPI

        return ChatCompletionAPI
    lazy_modules = {
        "get_async_provider_method": "gpt_computer.ai.providers.base_provider",
        "get_provider_method": "gpt_computer.ai.providers.base_provider",
        "async_concat_chunks": "gpt_computer.ai.providers.helper",
        "concat_chunks": "gpt_computer.ai.providers.helper",
        "ProviderType": "gpt_computer.ai.providers.types",
        "AsyncResult": "gptc.typing",
        "CreateResult": "gptc.typing",
        "ImageType": "gptc.typing",
        "Messages": "gptc.typing",
        "to_sync_generator": "gpt_computer.ai.providers.asyncio",
    }
    if name in lazy_modules:
        module = importlib.import_module(lazy_modules[name])
        return getattr(module, name)
    if name in ("Client", "AsyncClient", "ClientFactory"):
        from gpt_computer.ai import client as _client

        return getattr(_client, name)
    if name == "Model":
        from gpt_computer.ai import models as _models

        return _models.Model
    if name == "create_custom_provider":
        from .client.factory import create_custom_provider

        return create_custom_provider
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
