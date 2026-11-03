"""
CLI Data Collection Module

.. deprecated:: 0.3.0
    Importing from 'gpt_computer.applications.cli.collect' is deprecated. Use
    'from gpt_computer.interfaces.cli.collect import ...' instead.
"""

import warnings

warnings.warn(
    "Importing from 'gpt_computer.applications.cli.collect' is deprecated and will be removed in version 1.0.0. "
    "Use 'from gpt_computer.interfaces.cli.collect import ...' instead. "
    "See MIGRATION_GUIDE.md for details.",
    DeprecationWarning,
    stacklevel=2,
)

from gpt_computer.interfaces.cli.collect import (  # noqa: E402
    collect_and_send_human_review,
    collect_learnings,
    send_learning,
)

__all__ = ["send_learning", "collect_learnings", "collect_and_send_human_review"]
