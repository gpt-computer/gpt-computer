"""
Preprompts Holder Module

.. deprecated:: 0.3.0
    Importing from 'gpt_computer.core.preprompts_holder' is deprecated. Use
    'from gpt_computer.agent import PrepromptsHolder' instead.
"""

import warnings

warnings.warn(
    "Importing from 'gpt_computer.core.preprompts_holder' is deprecated and will be removed in version 1.0.0. "
    "Use 'from gpt_computer.agent import PrepromptsHolder' instead. "
    "See MIGRATION_GUIDE.md for details.",
    DeprecationWarning,
    stacklevel=2,
)

from gpt_computer.agent.pp_holder import PrepromptsHolder  # noqa: E402

__all__ = ["PrepromptsHolder"]
