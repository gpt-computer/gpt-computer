"""
Git Operations Module

.. deprecated:: 0.3.0
    Importing from 'gpt_computer.core.git' is deprecated. Use
    'from gpt_computer.infrastructure.git import ...' instead.
"""

import warnings

warnings.warn(
    "Importing from 'gpt_computer.core.git' is deprecated and will be removed in version 1.0.0. "
    "Use 'from gpt_computer.infrastructure.git import ...' instead. "
    "See MIGRATION_GUIDE.md for details.",
    DeprecationWarning,
    stacklevel=2,
)

from gpt_computer.infrastructure.git.operations import (  # noqa: E402
    filter_by_gitignore,
    filter_files_with_uncommitted_changes,
    has_uncommitted_changes,
    init_git_repo,
    is_git_installed,
    is_git_repo,
    stage_files,
    stage_uncommitted_to_git,
)

__all__ = [
    "is_git_installed",
    "is_git_repo",
    "init_git_repo",
    "has_uncommitted_changes",
    "filter_files_with_uncommitted_changes",
    "stage_files",
    "filter_by_gitignore",
    "stage_uncommitted_to_git",
]
