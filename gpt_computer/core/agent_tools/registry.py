"""
Agent Tools Registry Module

.. deprecated:: 0.3.0
    Importing from 'gpt_computer.core.agent_tools.registry' is deprecated. Use
    'from gpt_computer.agent.tools import Tool, ToolRegistry' instead.
"""

import warnings

warnings.warn(
    "Importing from 'gpt_computer.core.agent_tools.registry' is deprecated and will be removed in version 1.0.0. "
    "Use 'from gpt_computer.agent.tools import Tool, ToolRegistry' instead. "
    "See MIGRATION_GUIDE.md for details.",
    DeprecationWarning,
    stacklevel=2,
)

from gpt_computer.agent.tools.registry import Tool, ToolRegistry  # noqa: E402

__all__ = ["Tool", "ToolRegistry"]
