"""
CLI Learning Module

.. deprecated:: 0.3.0
    Importing from 'gpt_computer.applications.cli.learning' is deprecated. Use
    'from gpt_computer.interfaces.cli.learning import ...' instead.
"""

import warnings

warnings.warn(
    "Importing from 'gpt_computer.applications.cli.learning' is deprecated and will be removed in version 1.0.0. "
    "Use 'from gpt_computer.interfaces.cli.learning import ...' instead. "
    "See MIGRATION_GUIDE.md for details.",
    DeprecationWarning,
    stacklevel=2,
)

from gpt_computer.interfaces.cli.learning import (  # noqa: E402
    TERM_CHOICES,
    Learning,
    Review,
    ask_collection_consent,
    ask_for_valid_input,
    check_collection_consent,
    extract_learning,
    get_session,
    human_review_input,
)

__all__ = [
    "Review",
    "Learning",
    "TERM_CHOICES",
    "human_review_input",
    "ask_for_valid_input",
    "check_collection_consent",
    "ask_collection_consent",
    "extract_learning",
    "get_session",
]
