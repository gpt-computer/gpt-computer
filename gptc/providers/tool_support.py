# ruff: noqa: F403
"""Compatibility shim for the legacy ``gptc.providers.tool_support`` module."""

import warnings

warnings.warn(
    "Importing from 'gptc.providers.tool_support' is deprecated and will be removed in version 1.0.0. "
    "Use 'from gpt_computer.ai.providers.tool_support import ...' instead. "
    "See MIGRATION_GUIDE.md for details.",
    DeprecationWarning,
    stacklevel=2,
)

from gpt_computer.ai.providers.tool_support import *  # noqa: E402,F401,F403
