"""
CLI Entrypoint Module

.. deprecated:: 0.3.0
    Importing from 'gpt_computer.applications.cli.main' is deprecated. Use
    'from gpt_computer.interfaces.cli.main import ...' instead.
"""

import warnings

warnings.warn(
    "Importing from 'gpt_computer.applications.cli.main' is deprecated and will be removed in version 1.0.0. "
    "Use 'from gpt_computer.interfaces.cli.main import ...' instead. "
    "See MIGRATION_GUIDE.md for details.",
    DeprecationWarning,
    stacklevel=2,
)

from gpt_computer.interfaces.cli.main import app, list, load_prompt, main  # noqa: E402

__all__ = ["app", "main", "list", "load_prompt"]
