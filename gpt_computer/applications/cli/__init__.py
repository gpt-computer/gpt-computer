"""
CLI Applications Package

.. deprecated:: 0.3.0
    Importing from 'gpt_computer.applications.cli' is deprecated. Use
    'from gpt_computer.interfaces.cli import ...' instead.
"""

import warnings

warnings.warn(
    "Importing from 'gpt_computer.applications.cli' is deprecated and will be removed in version 1.0.0. "
    "Use 'from gpt_computer.interfaces.cli import ...' instead. "
    "See MIGRATION_GUIDE.md for details.",
    DeprecationWarning,
    stacklevel=2,
)

from gpt_computer.interfaces.cli import (  # noqa: E402
    CliAgent,
    FileSelector,
    Learning,
    Review,
    ask_collection_consent,
    check_collection_consent,
    collect_and_send_human_review,
    extract_learning,
    get_session,
    human_review_input,
)

__all__ = [
    "CliAgent",
    "collect_and_send_human_review",
    "FileSelector",
    "Learning",
    "Review",
    "extract_learning",
    "human_review_input",
    "ask_collection_consent",
    "check_collection_consent",
    "get_session",
]
