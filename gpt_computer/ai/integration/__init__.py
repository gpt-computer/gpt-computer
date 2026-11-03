"""Optional AI framework integrations."""

from __future__ import annotations

import importlib

_EXPORTS = {
    "ChatAI": "langchain",
    "LangChainIntegration": "langchain",
    "AIModel": "pydantic_ai",
    "PydanticAIIntegration": "pydantic_ai",
}

__all__ = sorted(_EXPORTS)


def __getattr__(name):
    module_name = _EXPORTS.get(name)
    if module_name is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    module = importlib.import_module(f"{__name__}.{module_name}")
    return getattr(module, name)
