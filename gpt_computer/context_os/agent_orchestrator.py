"""
Agent Orchestrator Module

.. deprecated:: 0.3.0
    Importing from 'gpt_computer.context_os.agent_orchestrator' is deprecated. Use
    'from gpt_computer.analysis.context import AgentOrchestrator' instead.
"""

import warnings

warnings.warn(
    "Importing from 'gpt_computer.context_os.agent_orchestrator' is deprecated and will be removed in version 1.0.0. "
    "Use 'from gpt_computer.analysis.context import AgentOrchestrator' instead. "
    "See MIGRATION_GUIDE.md for details.",
    DeprecationWarning,
    stacklevel=2,
)

from gpt_computer.analysis.context.agent_orchestrator import (  # noqa: E402
    AgentOrchestrator,
)

__all__ = ["AgentOrchestrator"]
