"""
Prompt Module

.. deprecated:: 0.3.0
    Importing from 'gpt_computer.core.prompt' is deprecated. Use
    'from gpt_computer.agent import Prompt' instead.
"""

import warnings

warnings.warn(
    "Importing from 'gpt_computer.core.prompt' is deprecated and will be removed in version 1.0.0. "
    "Use 'from gpt_computer.agent import Prompt' instead. "
    "See MIGRATION_GUIDE.md for details.",
    DeprecationWarning,
    stacklevel=2,
)

from gpt_computer.agent.prompt import Prompt  # noqa: E402

__all__ = ["Prompt"]
