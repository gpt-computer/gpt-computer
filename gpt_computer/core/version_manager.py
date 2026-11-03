"""
Version Manager Module

This module provides an abstract base class for a version manager that handles the creation of snapshots
for code. Implementations of this class are expected to provide methods to create a snapshot of the given
code and return a reference to it.
"""

import warnings

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Union

warnings.warn(
    "Importing from 'gpt_computer.core.version_manager' is deprecated and will be removed in version 1.0.0. "
    "See MIGRATION_GUIDE.md for details.",
    DeprecationWarning,
    stacklevel=2,
)

from gpt_computer.core.files_dict import FilesDict  # noqa: E402


class BaseVersionManager(ABC):
    """
    Abstract base class for a version manager.

    Defines the interface for version managers that handle the creation of snapshots for code.
    Implementations of this class are expected to provide methods to create a snapshot of the given
    code and return a reference to it.
    """

    @abstractmethod
    def __init__(self, path: Union[str, Path]):
        pass

    @abstractmethod
    def snapshot(self, files_dict: FilesDict) -> str:
        pass
