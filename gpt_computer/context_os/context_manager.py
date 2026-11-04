"""
Context Manager Module

.. deprecated:: 0.3.0
    Importing from 'gpt_computer.context_os.context_manager' is deprecated. Use
    'from gpt_computer.analysis.context import ContextManager' instead.
"""

import warnings

warnings.warn(
    "Importing from 'gpt_computer.context_os.context_manager' is deprecated and will be removed in version 1.0.0. "
    "Use 'from gpt_computer.analysis.context import ContextManager' instead. "
    "See MIGRATION_GUIDE.md for details.",
    DeprecationWarning,
    stacklevel=2,
)

from gpt_computer.analysis.context.context_manager import ContextManager  # noqa: E402

__all__ = ["ContextManager"]
