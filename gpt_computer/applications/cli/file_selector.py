"""
CLI File Selector Module

.. deprecated:: 0.3.0
    Importing from 'gpt_computer.applications.cli.file_selector' is deprecated. Use
    'from gpt_computer.interfaces.cli.file_selector import ...' instead.
"""

import warnings

warnings.warn(
    "Importing from 'gpt_computer.applications.cli.file_selector' is deprecated and will be removed in version 1.0.0. "
    "Use 'from gpt_computer.interfaces.cli.file_selector import ...' instead. "
    "See MIGRATION_GUIDE.md for details.",
    DeprecationWarning,
    stacklevel=2,
)

from gpt_computer.interfaces.cli.file_selector import (  # noqa: E402
    DisplayablePath,
    FileSelector,
)

__all__ = ["FileSelector", "DisplayablePath"]
