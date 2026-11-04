"""
GUI Module

.. deprecated:: 0.3.0
    Importing from 'gptc.gui' is deprecated. Use
    'from gpt_computer.interfaces.gui import ...' instead.
"""

import warnings

warnings.warn(
    "Importing from 'gptc.gui' is deprecated and will be removed in version 1.0.0. "
    "Use 'from gpt_computer.interfaces.gui import ...' instead. "
    "See MIGRATION_GUIDE.md for details.",
    DeprecationWarning,
    stacklevel=2,
)

# Re-export from gptc.gui for compatibility during migration
from gptc.gui import *  # noqa: E402, F401, F403
