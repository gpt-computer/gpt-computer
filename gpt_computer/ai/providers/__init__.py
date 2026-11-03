"""AI provider abstractions.

The canonical provider interfaces live in :mod:`gpt_computer.ai.providers.base`.
Concrete provider adapters are migrated incrementally; until then, legacy
provider implementations remain importable through the ``gptc`` compatibility
package.

Exports:
    BaseProvider: Abstract provider interface.
    BaseRetryProvider: Base class for retry/fallback providers.
    ProviderType: Union type accepted by the client layer.
    Streaming: Wrapper for streamed provider chunks.
"""

from gpt_computer.ai.providers.base import (
    BaseProvider,
    BaseRetryProvider,
    ProviderType,
    Streaming,
)

__all__ = [
    "BaseProvider",
    "BaseRetryProvider",
    "ProviderType",
    "Streaming",
]
