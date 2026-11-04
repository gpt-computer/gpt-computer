"""Compatibility shim for the legacy ``gptc.files`` module."""

import warnings

warnings.warn(
    "Importing from 'gptc.files' is deprecated and will be removed in version 1.0.0. "
    "Use 'from gpt_computer.infrastructure.files.secure import ...' instead. "
    "See MIGRATION_GUIDE.md for details.",
    DeprecationWarning,
    stacklevel=2,
)

from gpt_computer.infrastructure.files.secure import *  # noqa: E402,F401,F403
