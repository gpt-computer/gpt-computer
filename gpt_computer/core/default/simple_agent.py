"""
Simple Agent Module

.. deprecated:: 0.3.0
    Importing from 'gpt_computer.core.default.simple_agent' is deprecated. Use
    'from gpt_computer.agent.default.simple_agent import SimpleAgent' instead.
"""

import warnings

warnings.warn(
    "Importing from 'gpt_computer.core.default.simple_agent' is deprecated and will be removed in version 1.0.0. "
    "Use 'from gpt_computer.agent.default.simple_agent import SimpleAgent' instead. "
    "See MIGRATION_GUIDE.md for details.",
    DeprecationWarning,
    stacklevel=2,
)

from gpt_computer.agent.default.simple_agent import (  # noqa: E402
    SimpleAgent,
    default_config_agent,
)

__all__ = ["SimpleAgent", "default_config_agent"]
