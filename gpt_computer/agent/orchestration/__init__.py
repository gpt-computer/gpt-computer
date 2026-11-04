"""Multi-Agent Orchestration

This package provides coordination for multiple agents working together
on complex tasks with dependency management and result aggregation.
"""

from .orchestrator import AgentType, Orchestrator, Task, WorkflowResult
from .specialized_agents import (
    ArchitectAgent,
    ImplementationAgent,
    TestAgent,
    ReviewAgent,
)

__all__ = [
    "AgentType",
    "Orchestrator",
    "Task",
    "WorkflowResult",
    "ArchitectAgent",
    "ImplementationAgent",
    "TestAgent",
    "ReviewAgent",
]
