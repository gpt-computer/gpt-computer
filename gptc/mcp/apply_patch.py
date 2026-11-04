# ruff: noqa: F403
"""Compatibility shim for the legacy ``gptc.mcp.apply_patch`` module."""

import warnings

warnings.warn(
    "Importing from 'gptc.mcp.apply_patch' is deprecated and will be removed in version 1.0.0. "
    "Use 'from gpt_computer.interfaces.mcp.apply_patch import ...' instead. "
    "See MIGRATION_GUIDE.md for details.",
    DeprecationWarning,
    stacklevel=2,
)

from gpt_computer.interfaces.mcp.apply_patch import *  # noqa: E402,F401,F403
