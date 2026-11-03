"""
File Store Module

.. deprecated:: 0.3.0
    Importing from 'gpt_computer.core.default.file_store' is deprecated. Use
    'from gpt_computer.infrastructure.files import FileStore' instead.
"""

import warnings

warnings.warn(
    "Importing from 'gpt_computer.core.default.file_store' is deprecated and will be removed in version 1.0.0. "
    "Use 'from gpt_computer.infrastructure.files import FileStore' instead. "
    "See MIGRATION_GUIDE.md for details.",
    DeprecationWarning,
    stacklevel=2,
)

from gpt_computer.infrastructure.files.file_store import FileStore  # noqa: E402

__all__ = ["FileStore"]
