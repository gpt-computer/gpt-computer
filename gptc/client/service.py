"""Compatibility shim for ``gptc.client.service``."""

import warnings

warnings.warn(
    "Importing from 'gptc.client.service' is deprecated and will be removed in version 1.0.0. "
    "Use 'from gpt_computer.ai.client.service import ...' instead. "
    "See MIGRATION_GUIDE.md for details.",
    DeprecationWarning,
    stacklevel=2,
)

from gpt_computer.ai.client.service import (  # noqa: E402,F401
    convert_to_provider,
    get_last_provider,
    get_model_and_provider,
)

__all__ = ["convert_to_provider", "get_last_provider", "get_model_and_provider"]
