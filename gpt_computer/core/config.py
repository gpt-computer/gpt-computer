"""
Configuration Module

.. deprecated:: 0.3.0
    Importing from 'gpt_computer.core.config' is deprecated. Use
    'from gpt_computer.infrastructure.config import ...' instead.
"""

import warnings

warnings.warn(
    "Importing from 'gpt_computer.core.config' is deprecated and will be removed in version 1.0.0. "
    "Use 'from gpt_computer.infrastructure.config import ...' instead. "
    "See MIGRATION_GUIDE.md for details.",
    DeprecationWarning,
    stacklevel=2,
)

from gpt_computer.infrastructure.config.loader import (  # noqa: E402
    load_config,
    reload_config,
)
from gpt_computer.infrastructure.config.settings import (  # noqa: E402
    Settings,
    get_settings,
)

__all__ = ["Settings", "get_settings", "load_config", "reload_config"]
