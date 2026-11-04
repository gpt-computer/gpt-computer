"""
Context OS Module

.. deprecated:: 0.3.0
    Importing from 'gpt_computer.context_os' is deprecated. Use
    'from gpt_computer.analysis.context import ...' instead.
"""

import warnings

warnings.warn(
    "Importing from 'gpt_computer.context_os' is deprecated and will be removed in version 1.0.0. "
    "Use 'from gpt_computer.analysis.context import ...' instead. "
    "See MIGRATION_GUIDE.md for details.",
    DeprecationWarning,
    stacklevel=2,
)

from gpt_computer.analysis.context import (  # noqa: E402
    AgentOrchestrator,
    Context,
    ContextGraph,
    ContextManager,
    ContextMetadata,
    ContextState,
    ContextStatus,
    ContextType,
    DocumentEntity,
    Entity,
    ExecutionFabric,
    KnowledgeEntity,
    PersonEntity,
    RepositoryEntity,
    ServiceEntity,
    TaskEntity,
    WorldModel,
)

__all__ = [
    "Context",
    "ContextState",
    "ContextType",
    "ContextStatus",
    "ContextMetadata",
    "ContextGraph",
    "ContextManager",
    "AgentOrchestrator",
    "ExecutionFabric",
    "WorldModel",
    "Entity",
    "RepositoryEntity",
    "PersonEntity",
    "TaskEntity",
    "DocumentEntity",
    "ServiceEntity",
    "KnowledgeEntity",
]
