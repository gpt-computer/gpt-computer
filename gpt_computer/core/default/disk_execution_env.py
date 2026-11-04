"""
Local Disk Execution Environment Module

.. deprecated:: 0.3.0
    Importing from 'gpt_computer.core.default.disk_execution_env' is deprecated. Use
    'from gpt_computer.execution.local import DiskExecutionEnv' instead.
"""

import warnings

warnings.warn(
    "Importing from 'gpt_computer.core.default.disk_execution_env' is deprecated and will be removed in version 1.0.0. "
    "Use 'from gpt_computer.execution.local import DiskExecutionEnv' instead. "
    "See MIGRATION_GUIDE.md for details.",
    DeprecationWarning,
    stacklevel=2,
)

from gpt_computer.execution.local import DiskExecutionEnv  # noqa: E402

__all__ = ["DiskExecutionEnv"]
