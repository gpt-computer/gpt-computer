"""
Orchestration Data Models

Shared data primitives used by the multi-agent coordination layer: agent
handles, retry/resource policies, workflow definitions, run state, inter-agent
messages, and audit records.

Classes:
    RetryPolicy: Failure handling policy (attempts, exponential backoff)
    AgentHandle: Registered agent descriptor with runtime allocation state
    WorkflowStep: A single executable unit inside a workflow
    WorkflowSpec: Defines an executable, auditable workflow
    WorkflowRun: Mutable runtime state for a specific workflow execution
    StepExecution: Observation record for one step attempt
    AuditEvent / AuditTrail: Structured, append-only audit log
    AgentMessage: Inter-agent communication envelope
"""

from __future__ import annotations

import uuid

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Awaitable, Callable, Dict, List, Optional, Tuple, Type

# A callable that produces a value, possibly asynchronously.
AgentExecutor = Callable[..., Awaitable[Any]]


def utcnow_iso() -> str:
    """Return the current UTC time as an ISO-8601 formatted string."""
    return datetime.now(timezone.utc).isoformat()


def new_id(prefix: str) -> str:
    """Generate a short, unique, human-friendly identifier."""
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


class WorkflowStatus:
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class StepStatus:
    PENDING = "pending"
    RUNNING = "running"
    AWAITING_APPROVAL = "awaiting_approval"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    SKIPPED = "skipped"


class AgentStatus:
    ACTIVE = "active"
    PAUSED = "paused"
    DRAINING = "draining"
    OFFLINE = "offline"


@dataclass
class RetryPolicy:
    """
    Configures how a failing step should be retried.

    Attributes:
        max_attempts: Maximum number of attempts per step/agent.
        base_delay: Initial delay between attempts, in seconds.
        backoff_factor: Exponential multiplier between attempts.
        max_delay: Upper bound on the delay between attempts.
        retry_on: Tuple of exception types that trigger a retry. All other
            exceptions are treated as terminal and abort the step.
    """

    max_attempts: int = 3
    base_delay: float = 0.05
    backoff_factor: float = 2.0
    max_delay: float = 2.0
    retry_on: Tuple[Type[BaseException], ...] = (Exception,)

    def delay_for(self, attempt_index: int) -> float:
        """
        Compute the backoff delay before the given attempt.

        Args:
            attempt_index: Zero-based index of the attempt that is about to run.

        Returns:
            Delay in seconds, capped at ``max_delay``.
        """
        delay = self.base_delay * (self.backoff_factor**attempt_index)
        return min(delay, self.max_delay)


@dataclass
class AgentHandle:
    """
    Descriptor for an agent participating in orchestration.

    Static spec fields (capabilities, priority, executor, limits) describe the
    agent; runtime fields track live resource allocation and health.
    """

    agent_id: str
    name: str
    capabilities: List[str] = field(default_factory=list)
    description: str = ""
    executor: Optional[AgentExecutor] = None
    max_concurrency: int = 5
    priority: int = 10
    tags: Dict[str, Any] = field(default_factory=dict)

    # Runtime allocation/health state
    status: str = AgentStatus.ACTIVE
    active_tasks: int = 0
    total_tasks: int = 0
    total_failures: int = 0
    last_active_at: Optional[str] = None

    @property
    def available(self) -> bool:
        """True when the agent can accept new work right now."""
        return (
            self.status in (AgentStatus.ACTIVE, AgentStatus.DRAINING)
            and self.active_tasks < self.max_concurrency
        )

    @property
    def accepting_new_work(self) -> bool:
        """True when the agent can accept new work and is not draining."""
        return self.status == AgentStatus.ACTIVE and (
            self.active_tasks < self.max_concurrency
        )

    def as_dict(self) -> Dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "capabilities": list(self.capabilities),
            "description": self.description,
            "status": self.status,
            "max_concurrency": self.max_concurrency,
            "priority": self.priority,
            "active_tasks": self.active_tasks,
            "total_tasks": self.total_tasks,
            "total_failures": self.total_failures,
            "last_active_at": self.last_active_at,
            "tags": dict(self.tags),
        }


@dataclass
class WorkflowStep:
    """
    A single executable unit within a workflow.

    A step is executed by exactly one suitable executor chosen from:
    ``handler`` (inline callable), an explicitly pinned ``agent_id``, any
    ``fallback_agent_ids``, or agents discovered via ``capabilities``.
    """

    step_id: str
    task: str = ""
    capabilities: List[str] = field(default_factory=list)
    agent_id: Optional[str] = None
    handler: Optional[AgentExecutor] = None
    inputs: Dict[str, Any] = field(default_factory=dict)
    depends_on: List[str] = field(default_factory=list)
    timeout_seconds: Optional[float] = None
    retry_policy: Optional[RetryPolicy] = None
    fallback_agent_ids: List[str] = field(default_factory=list)
    require_approval: bool = False
    approval_summary: str = ""
    approval_timeout_seconds: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def needs_executor(self) -> bool:
        return True

    def as_dict(self) -> Dict[str, Any]:
        return {
            "step_id": self.step_id,
            "task": self.task,
            "capabilities": list(self.capabilities),
            "agent_id": self.agent_id,
            "inputs": dict(self.inputs),
            "depends_on": list(self.depends_on),
            "timeout_seconds": self.timeout_seconds,
            "require_approval": self.require_approval,
            "approval_summary": self.approval_summary,
            "fallback_agent_ids": list(self.fallback_agent_ids),
            "metadata": dict(self.metadata),
        }


@dataclass
class WorkflowSpec:
    """
    Immutable definition of a workflow to be executed by the engine.
    """

    name: str
    steps: List[WorkflowStep] = field(default_factory=list)
    description: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_step(self, step: WorkflowStep) -> "WorkflowSpec":
        """Append a step to the workflow. Returns self for chaining."""
        self.steps.append(step)
        return self

    def step(self, step_id: str) -> Optional[WorkflowStep]:
        """Return the step matching ``step_id`` or None."""
        for step in self.steps:
            if step.step_id == step_id:
                return step
        return None

    @property
    def step_ids(self) -> List[str]:
        return [step.step_id for step in self.steps]

    def as_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "steps": [step.as_dict() for step in self.steps],
            "metadata": dict(self.metadata),
        }


@dataclass
class StepExecution:
    """Per-step runtime record for observability and audit."""

    step_id: str
    status: str = StepStatus.PENDING
    attempts: int = 0
    resolved_agent_id: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    result: Any = None
    error: Optional[str] = None


class WorkflowRun:
    """
    Mutable runtime state for a single execution of a ``WorkflowSpec``.

    The engine writes into this object as the workflow progresses; it is also
    the payload handed to audit and monitoring hooks.
    """

    def __init__(
        self,
        workflow: WorkflowSpec,
        inputs: Optional[Dict[str, Any]] = None,
        run_id: Optional[str] = None,
    ):
        self.run_id = run_id or new_id("run")
        self.workflow = workflow
        self.inputs: Dict[str, Any] = dict(inputs or {})
        self.status: str = WorkflowStatus.PENDING
        self.context: Dict[str, Any] = dict(self.inputs)
        self.step_results: Dict[str, Any] = {}
        self.step_executions: Dict[str, StepExecution] = {}
        self.error: Optional[str] = None
        self.created_at = utcnow_iso()
        self.started_at: Optional[str] = None
        self.completed_at: Optional[str] = None
        self.metadata: Dict[str, Any] = {}

    @property
    def completed(self) -> bool:
        return self.status == WorkflowStatus.COMPLETED

    @property
    def failed(self) -> bool:
        return self.status == WorkflowStatus.FAILED

    @property
    def unresolved_steps(self) -> List[str]:
        pending_ids = []
        for step in self.workflow.steps:
            execution = self.step_executions.get(step.step_id)
            if execution is None or execution.status != StepStatus.SUCCEEDED:
                pending_ids.append(step.step_id)
        return pending_ids

    def as_dict(self) -> Dict[str, Any]:
        return {
            "run_id": self.run_id,
            "workflow": self.workflow.as_dict(),
            "inputs": dict(self.inputs),
            "context": self.context,
            "status": self.status,
            "error": self.error,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "step_results": dict(self.step_results),
            "step_executions": {
                step_id: {
                    "status": exec_.status,
                    "attempts": exec_.attempts,
                    "resolved_agent_id": exec_.resolved_agent_id,
                    "error": exec_.error,
                }
                for step_id, exec_ in self.step_executions.items()
            },
            "metadata": dict(self.metadata),
        }


@dataclass
class AuditEvent:
    """A single immutable entry in an audit trail."""

    event: str
    actor: str = "system"
    resource: str = ""
    run_id: Optional[str] = None
    step_id: Optional[str] = None
    message: str = ""
    timestamp: str = field(default_factory=utcnow_iso)
    detail: Dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> Dict[str, Any]:
        return {
            "event": self.event,
            "actor": self.actor,
            "resource": self.resource,
            "run_id": self.run_id,
            "step_id": self.step_id,
            "message": self.message,
            "timestamp": self.timestamp,
            "detail": dict(self.detail),
        }


class AuditTrail:
    """
    Append-only, in-memory audit log for observability and compliance.

    All orchestration components (coordinator, engine, bus, approvals) write
    into a shared trail so a full, correlated trace of a workflow exists.
    """

    def __init__(self, max_entries: int = 5000):
        self._entries: List[AuditEvent] = []
        self._max_entries = max_entries

    def record(
        self,
        event: str,
        *,
        actor: str = "system",
        resource: str = "",
        run_id: Optional[str] = None,
        step_id: Optional[str] = None,
        message: str = "",
        detail: Optional[Dict[str, Any]] = None,
    ) -> AuditEvent:
        """Append an event to the trail and return it."""
        entry = AuditEvent(
            event=event,
            actor=actor,
            resource=resource,
            run_id=run_id,
            step_id=step_id,
            message=message,
            detail=dict(detail or {}),
        )
        self._entries.append(entry)
        if self._max_entries and len(self._entries) > self._max_entries:
            self._entries = self._entries[-self._max_entries :]
        return entry

    def entries(self, *, run_id: Optional[str] = None) -> List[AuditEvent]:
        """Return the audit entries, optionally filtered by run."""
        if run_id is None:
            return list(self._entries)
        return [e for e in self._entries if e.run_id == run_id]

    def to_dict(self) -> List[Dict[str, Any]]:
        """Serialize the whole trail to a list of plain dicts."""
        return [entry.as_dict() for entry in self._entries]

    def clear(self) -> None:
        """Remove all entries (used mainly by tests)."""
        self._entries.clear()


@dataclass
class AgentMessage:
    """Envelope for messages exchanged between agents via the message bus."""

    message_id: str = field(default_factory=lambda: new_id("msg"))
    sender: str = ""
    recipient: str = ""
    subject: str = ""
    payload: Any = None
    reply_to: str = ""
    correlation_id: str = ""
    message_type: str = "event"
    timestamp: str = field(default_factory=utcnow_iso)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> Dict[str, Any]:
        return {
            "message_id": self.message_id,
            "sender": self.sender,
            "recipient": self.recipient,
            "subject": self.subject,
            "payload": self.payload,
            "reply_to": self.reply_to,
            "correlation_id": self.correlation_id,
            "message_type": self.message_type,
            "timestamp": self.timestamp,
            "metadata": dict(self.metadata),
        }
