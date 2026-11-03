"""
Tray Module

.. deprecated:: 0.3.0
    Importing from 'gptc.tray' is deprecated. Use
    'from gpt_computer.interfaces.tray import ...' instead.
"""

import warnings

warnings.warn(
    "Importing from 'gptc.tray' is deprecated and will be removed in version 1.0.0. "
    "Use 'from gpt_computer.interfaces.tray import ...' instead. "
    "See MIGRATION_GUIDE.md for details.",
    DeprecationWarning,
    stacklevel=2,
)

# Note: gptc.tray is not re-exported here as it's deprecated
# Import from gpt_computer.interfaces.tray directly if needed
