"""
Paths Module

.. deprecated:: 0.3.0
    Importing from 'gpt_computer.core.default.paths' is deprecated. Use
    'from gpt_computer.agent.default import ...' instead.
"""

import warnings

warnings.warn(
    "Importing from 'gpt_computer.core.default.paths' is deprecated and will be removed in version 1.0.0. "
    "Use 'from gpt_computer.agent.default.paths import ...' instead. "
    "See MIGRATION_GUIDE.md for details.",
    DeprecationWarning,
    stacklevel=2,
)

from gpt_computer.agent.default.paths import (  # noqa: E402
    CODE_GEN_LOG_FILE,
    DEBUG_LOG_FILE,
    DIFF_LOG_FILE,
    ENTRYPOINT_FILE,
    ENTRYPOINT_LOG_FILE,
    IMPROVE_LOG_FILE,
    MEMORY_REL_PATH,
    META_DATA_REL_PATH,
    PREPROMPTS_PATH,
    memory_path,
    metadata_path,
)

__all__ = [
    "CODE_GEN_LOG_FILE",
    "DEBUG_LOG_FILE",
    "DIFF_LOG_FILE",
    "ENTRYPOINT_FILE",
    "ENTRYPOINT_LOG_FILE",
    "IMPROVE_LOG_FILE",
    "MEMORY_REL_PATH",
    "META_DATA_REL_PATH",
    "PREPROMPTS_PATH",
    "memory_path",
    "metadata_path",
]
