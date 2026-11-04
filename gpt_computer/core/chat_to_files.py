"""
Chat-to-Files Module

.. deprecated:: 0.3.0
    Importing from 'gpt_computer.core.chat_to_files' is deprecated. Use
    'from gpt_computer.agent.tools import ...' instead.
"""

import warnings

warnings.warn(
    "Importing from 'gpt_computer.core.chat_to_files' is deprecated and will be removed in version 1.0.0. "
    "Use 'from gpt_computer.agent.tools.chat_to_files import ...' instead. "
    "See MIGRATION_GUIDE.md for details.",
    DeprecationWarning,
    stacklevel=2,
)

from gpt_computer.agent.tools.chat_to_files import (  # noqa: E402
    apply_diffs,
    chat_to_files_dict,
    parse_diffs,
)

__all__ = ["chat_to_files_dict", "apply_diffs", "parse_diffs"]
