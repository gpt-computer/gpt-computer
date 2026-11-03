"""
Legacy API package.

.. deprecated:: 0.3.0
    Import from 'gpt_computer.interfaces.api' instead.
"""

import warnings

warnings.warn(
    "Importing from 'gpt_computer.api' is deprecated and will be removed in version 1.0.0. "
    "Use 'from gpt_computer.interfaces.api import ...' instead. "
    "See MIGRATION_GUIDE.md for details.",
    DeprecationWarning,
    stacklevel=2,
)

from gpt_computer.interfaces.api import (  # noqa: E402
    AgentRunRequest,
    AgentRunResponse,
    HealthResponse,
    app,
)

__all__ = ["AgentRunRequest", "AgentRunResponse", "HealthResponse", "app"]
