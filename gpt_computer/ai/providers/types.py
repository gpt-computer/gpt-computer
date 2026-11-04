"""Provider type definitions (canonical).

The canonical definitions live in :mod:`gpt_computer.ai.providers.base`. This
module re-exports them for callers that prefer the ``types`` name, mirroring the
legacy ``gptc.providers.types`` layout.
"""

from __future__ import annotations

from .base import BaseProvider, BaseRetryProvider, ProviderType, Streaming

__all__ = ["BaseProvider", "BaseRetryProvider", "ProviderType", "Streaming"]
