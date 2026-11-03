"""
Base Execution Environment Module

.. deprecated:: 0.3.0
    Importing from 'gpt_computer.core.base_execution_env' is deprecated. Use
    'from gpt_computer.execution import BaseExecutionEnv' instead.
"""

import warnings

warnings.warn(
    "Importing from 'gpt_computer.core.base_execution_env' is deprecated and will be removed in version 1.0.0. "
    "Use 'from gpt_computer.execution import BaseExecutionEnv' instead. "
    "See MIGRATION_GUIDE.md for details.",
    DeprecationWarning,
    stacklevel=2,
)

from gpt_computer.execution.base import BaseExecutionEnv  # noqa: E402

__all__ = ["BaseExecutionEnv"]
