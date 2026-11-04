"""
Constants Module

.. deprecated:: 0.3.0
    Importing from 'gpt_computer.core.default.constants' is deprecated. Use
    'from gpt_computer.agent.default import MAX_EDIT_REFINEMENT_STEPS' instead.
"""

import warnings

warnings.warn(
    "Importing from 'gpt_computer.core.default.constants' is deprecated and will be removed in version 1.0.0. "
    "Use 'from gpt_computer.agent.default import MAX_EDIT_REFINEMENT_STEPS' instead. "
    "See MIGRATION_GUIDE.md for details.",
    DeprecationWarning,
    stacklevel=2,
)

from gpt_computer.agent.default.constants import MAX_EDIT_REFINEMENT_STEPS  # noqa: E402

__all__ = ["MAX_EDIT_REFINEMENT_STEPS"]
