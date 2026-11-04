"""
Files Dictionary Module

.. deprecated:: 0.3.0
    Importing from 'gpt_computer.core.files_dict' is deprecated. Use
    'from gpt_computer.infrastructure.files import ...' instead.
"""

import warnings

warnings.warn(
    "Importing from 'gpt_computer.core.files_dict' is deprecated and will be removed in version 1.0.0. "
    "Use 'from gpt_computer.infrastructure.files import ...' instead. "
    "See MIGRATION_GUIDE.md for details.",
    DeprecationWarning,
    stacklevel=2,
)

from gpt_computer.infrastructure.files.operations import (  # noqa: E402
    FilesDict,
    file_to_lines_dict,
)

__all__ = ["FilesDict", "file_to_lines_dict"]
