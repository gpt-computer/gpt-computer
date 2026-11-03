import warnings

warnings.warn(
    "Importing from 'gptc.providers' is deprecated and will be removed in version 1.0.0. "
    "Use 'from gpt_computer.ai.providers import ...' instead. "
    "See MIGRATION_GUIDE.md for details.",
    DeprecationWarning,
    stacklevel=2,
)

# Re-export base provider types from the new structure
from gpt_computer.ai.providers.base import (  # noqa: E402
    BaseProvider,
    BaseRetryProvider,
    ProviderType,
    Streaming,
)

__all__ = [
    "AnyProvider",
    "BaseProvider",
    "BaseRetryProvider",
    "ProviderType",
    "Streaming",
]


def __getattr__(name):
    """Lazily expose legacy provider implementations during the migration.

    ``AnyProvider`` still lives in the legacy tree and pulls in the dynamic
    provider loader. Importing it lazily avoids a package-initialisation cycle
    and keeps the cost off callers that only need the base types.
    """
    if name == "AnyProvider":
        from gpt_computer.ai.providers.any_provider import AnyProvider

        return AnyProvider
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
