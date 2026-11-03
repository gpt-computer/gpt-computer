"""
Agent Steps Module

.. deprecated:: 0.3.0
    Importing from 'gpt_computer.core.default.steps' is deprecated. Use
    'from gpt_computer.agent.default.steps import ...' instead.
"""

import warnings

warnings.warn(
    "Importing from 'gpt_computer.core.default.steps' is deprecated and will be removed in version 1.0.0. "
    "Use 'from gpt_computer.agent.default.steps import ...' instead. "
    "See MIGRATION_GUIDE.md for details.",
    DeprecationWarning,
    stacklevel=2,
)

from gpt_computer.agent.default.steps import (  # noqa: E402
    curr_fn,
    execute_entrypoint,
    gen_code,
    gen_entrypoint,
    handle_improve_mode,
    improve_fn,
    salvage_correct_hunks,
    setup_sys_prompt,
    setup_sys_prompt_existing_code,
)

__all__ = [
    "curr_fn",
    "setup_sys_prompt",
    "setup_sys_prompt_existing_code",
    "gen_code",
    "gen_entrypoint",
    "execute_entrypoint",
    "improve_fn",
    "salvage_correct_hunks",
    "handle_improve_mode",
]
