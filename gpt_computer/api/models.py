"""
API Models Module

.. deprecated:: 0.3.0
    Importing from 'gpt_computer.api.models' is deprecated. Use
    'from gpt_computer.interfaces.api.models import ...' instead.
"""

import warnings

warnings.warn(
    "Importing from 'gpt_computer.api.models' is deprecated and will be removed in version 1.0.0. "
    "Use 'from gpt_computer.interfaces.api.models import ...' instead. "
    "See MIGRATION_GUIDE.md for details.",
    DeprecationWarning,
    stacklevel=2,
)

from gpt_computer.interfaces.api.models import (  # noqa: E402
    AgentRunRequest,
    AgentRunResponse,
    HealthResponse,
)

__all__ = ["AgentRunRequest", "AgentRunResponse", "HealthResponse"]
