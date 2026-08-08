"""
Multi-Agent Coordination Layer

Provides an enterprise-grade orchestration stack built on top of the
gpt-computer engine:

* :mod:`agent_coordinator` - agent registry, capability discovery, resource
  allocation, concurrency limits, health/status, audit.
* :mod:`workflow_engine` - DAG scheduling of multi-step AI workflows with
  retry/backoff, fallback, timeouts, and human-in-the-loop approval gates.
* :mod:`messaging` - inter-agent communication primitives (direct send,
  topic pub/sub, request/reply with correlation).
* :mod:`human_in_the_loop` - approval requests for sensitive operations.
* :mod:`models` - shared data primitives (agents, workflows, runs, audits).

Modern examples: code review pipelines, security scans, CI tool chains.

Modules:
    models: data primitives shared across the orchestration layer
    agent_coordinator: registry + allocation
    messaging: inter-agent message bus
    human_in_the_loop: approval gates
    workflow_engine: workflow scheduler and executor
"""

from __future__ import annotations

from gpt_computer.core.orchestration.agent_coordinator import (
    AgentConflictError,
    AgentCoordinator,
    CandidateUnavailable,
    CoordinatorError,
    create_coordinator,
)
from gpt_computer.core.orchestration.human_in_the_loop import (
    ApprovalRequest,
    ApprovalStatus,
    HumanApprovalManager,
    create_approval_manager,
)
from gpt_computer.core.orchestration.messaging import (
    MessageBus,
    MessageDeliveryError,
    ReplyTimeoutError,
    create_message_bus,
)
from gpt_computer.core.orchestration.models import (
    AgentHandle,
    AgentMessage,
    AgentStatus,
    AuditEvent,
    AuditTrail,
    RetryPolicy,
    StepExecution,
    StepStatus,
    WorkflowRun,
    WorkflowSpec,
    WorkflowStatus,
    WorkflowStep,
)
from gpt_computer.core.orchestration.workflow_engine import (
    WorkflowConfigurationError,
    WorkflowEngine,
    WorkflowExecutionError,
    create_workflow_engine,
)

__all__ = [
    "AgentConflictError",
    "AgentCoordinator",
    "AgentHandle",
    "AgentMessage",
    "AgentStatus",
    "ApprovalRequest",
    "ApprovalStatus",
    "AuditEvent",
    "AuditTrail",
    "CandidateUnavailable",
    "CoordinatorError",
    "HumanApprovalManager",
    "MessageBus",
    "MessageDeliveryError",
    "ReplyTimeoutError",
    "RetryPolicy",
    "StepExecution",
    "StepStatus",
    "WorkflowConfigurationError",
    "WorkflowEngine",
    "WorkflowExecutionError",
    "WorkflowRun",
    "WorkflowSpec",
    "WorkflowStatus",
    "WorkflowStep",
    "create_approval_manager",
    "create_coordinator",
    "create_message_bus",
    "create_workflow_engine",
]
