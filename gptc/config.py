"""Compatibility shim for the legacy ``gptc.config`` module."""

import warnings

warnings.warn(
    "Importing from 'gptc.config' is deprecated and will be removed in version 1.0.0. "
    "Use 'from gpt_computer.infrastructure.config.paths import ...' instead. "
    "See MIGRATION_GUIDE.md for details.",
    DeprecationWarning,
    stacklevel=2,
)

from gpt_computer.infrastructure.config.paths import *  # noqa: E402,F401,F403
