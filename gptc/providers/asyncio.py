"""Compatibility shim for the legacy ``gptc.providers.asyncio`` module."""

import warnings

warnings.warn(
    "Importing from 'gptc.providers.asyncio' is deprecated and will be removed in version 1.0.0. "
    "Use 'from gpt_computer.ai.providers.asyncio import ...' instead. "
    "See MIGRATION_GUIDE.md for details.",
    DeprecationWarning,
    stacklevel=2,
)

from gpt_computer.ai.providers.asyncio import (  # noqa: E402,F401
    async_generator_to_list,
    await_callback,
    get_running_loop,
    to_async_iterator,
    to_sync_generator,
    to_thread,
)

__all__ = [
    "async_generator_to_list",
    "await_callback",
    "get_running_loop",
    "to_async_iterator",
    "to_sync_generator",
    "to_thread",
]
