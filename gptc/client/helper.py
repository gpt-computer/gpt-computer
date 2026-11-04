"""Compatibility shim for ``gptc.client.helper``."""

import warnings

warnings.warn(
    "Importing from 'gptc.client.helper' is deprecated and will be removed in version 1.0.0. "
    "Use 'from gpt_computer.ai.client.helper import ...' instead. "
    "See MIGRATION_GUIDE.md for details.",
    DeprecationWarning,
    stacklevel=2,
)

from gpt_computer.ai.client.helper import (  # noqa: E402,F401
    filter_json,
    filter_markdown,
    filter_none,
    find_stop,
    safe_aclose,
)

__all__ = ["filter_json", "filter_markdown", "filter_none", "find_stop", "safe_aclose"]
