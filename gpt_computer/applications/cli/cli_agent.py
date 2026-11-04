"""
CLI Agent Module

.. deprecated:: 0.3.0
    Importing from 'gpt_computer.applications.cli.cli_agent' is deprecated. Use
    'from gpt_computer.interfaces.cli.cli_agent import ...' instead.
"""

import warnings

warnings.warn(
    "Importing from 'gpt_computer.applications.cli.cli_agent' is deprecated and will be removed in version 1.0.0. "
    "Use 'from gpt_computer.interfaces.cli.cli_agent import ...' instead. "
    "See MIGRATION_GUIDE.md for details.",
    DeprecationWarning,
    stacklevel=2,
)

from gpt_computer.interfaces.cli.cli_agent import CliAgent  # noqa: E402

__all__ = ["CliAgent"]
