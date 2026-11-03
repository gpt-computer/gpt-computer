"""Compatibility shim for ``gptc.client.models``."""

import warnings

warnings.warn(
    "Importing from 'gptc.client.models' is deprecated and will be removed in version 1.0.0. "
    "Use 'from gpt_computer.ai.client.models import ...' instead. "
    "See MIGRATION_GUIDE.md for details.",
    DeprecationWarning,
    stacklevel=2,
)

from gpt_computer.ai.client.models import ClientModels  # noqa: E402,F401

__all__ = ["ClientModels"]
