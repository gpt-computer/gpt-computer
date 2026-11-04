"""
Execution Fabric Module

.. deprecated:: 0.3.0
    Importing from 'gpt_computer.context_os.execution_fabric' is deprecated. Use
    'from gpt_computer.analysis.context import ExecutionFabric' instead.
"""

import warnings

warnings.warn(
    "Importing from 'gpt_computer.context_os.execution_fabric' is deprecated and will be removed in version 1.0.0. "
    "Use 'from gpt_computer.analysis.context import ExecutionFabric' instead. "
    "See MIGRATION_GUIDE.md for details.",
    DeprecationWarning,
    stacklevel=2,
)

from gpt_computer.analysis.context.execution_fabric import ExecutionFabric  # noqa: E402

__all__ = ["ExecutionFabric"]
