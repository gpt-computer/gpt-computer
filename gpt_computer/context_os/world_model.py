"""
World Model Module

.. deprecated:: 0.3.0
    Importing from 'gpt_computer.context_os.world_model' is deprecated. Use
    'from gpt_computer.analysis.context import WorldModel' instead.
"""

import warnings

warnings.warn(
    "Importing from 'gpt_computer.context_os.world_model' is deprecated and will be removed in version 1.0.0. "
    "Use 'from gpt_computer.analysis.context import WorldModel' instead. "
    "See MIGRATION_GUIDE.md for details.",
    DeprecationWarning,
    stacklevel=2,
)

from gpt_computer.analysis.context.world_model import (  # noqa: E402
    DocumentEntity,
    Entity,
    KnowledgeEntity,
    PersonEntity,
    RepositoryEntity,
    ServiceEntity,
    TaskEntity,
    WorldModel,
)

__all__ = [
    "Entity",
    "RepositoryEntity",
    "PersonEntity",
    "TaskEntity",
    "DocumentEntity",
    "ServiceEntity",
    "KnowledgeEntity",
    "WorldModel",
]
