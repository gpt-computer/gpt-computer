# ruff: noqa: F403
"""Compatibility shim for the legacy ``gptc.providers.config_provider`` module."""

import warnings

warnings.warn(
    "Importing from 'gptc.providers.config_provider' is deprecated and will be removed in version 1.0.0. "
    "Use 'from gpt_computer.ai.providers.config_provider import ...' instead. "
    "See MIGRATION_GUIDE.md for details.",
    DeprecationWarning,
    stacklevel=2,
)

from gpt_computer.ai.providers.config_provider import *  # noqa: E402,F401,F403
