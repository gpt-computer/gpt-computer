"""
API Module

.. deprecated:: 0.3.0
    Importing from 'gpt_computer.api' is deprecated. Use
    'from gpt_computer.interfaces.api import ...' instead.
"""

import warnings

warnings.warn(
    "Importing from 'gpt_computer.api' is deprecated and will be removed in version 1.0.0. "
    "Use 'from gpt_computer.interfaces.api import ...' instead. "
    "See MIGRATION_GUIDE.md for details.",
    DeprecationWarning,
    stacklevel=2,
)

from gpt_computer.interfaces.api.main import app  # noqa: E402
from gpt_computer.interfaces.api.models import (  # noqa: E402
    AgentRunRequest,
    AgentRunResponse,
    HealthResponse,
)

__all__ = ["AgentRunRequest", "AgentRunResponse", "HealthResponse", "app"]
