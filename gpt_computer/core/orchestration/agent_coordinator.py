"""
Agent Coordinator

Registry, capability discovery, and resource allocation for the multi-agent
coordination layer. Tracks agent health/status, enforces per-agent concurrency
limits, and exposes structured metrics + audit hooks.

Classes:
    AgentCoordinator: Central registry and scheduler-facing allocation API.
    CoordinatorError: Base error raised by the coordinator.
    AgentConflictError: Raised on duplicate/unregistered agent operations.
    CandidatePicker: Internal helper ranking candidate agents for a task.

Functions:
    create_coordinator(audit=None) -> AgentCoordinator
"""

from __future__ import annotations

import asyncio
import logging

from typing import Any, Dict, List, Optional

from gpt_computer.core.orchestration.human_in_the_loop import HumanApprovalManager
from gpt_computer.core.orchestration.models import (
    AgentHandle,
    AgentStatus,
    AuditTrail,
    utcnow_iso,
)


class CoordinatorError(Exception):
    """Base error raised by the coordinator."""


class AgentConflictError(CoordinatorError):
    """Raised when an agent id is reused without an explicit override."""


class CandidateUnavailable(Exception):
    """Raised when no agent can accept a task's required capabilities."""


class AgentCoordinator:
    """
    Central registry + scheduler for agents participating in workflows.

    Agents are registered with declared capabilities, a priority, and a
    concurrency budget. The coordinator discovers the best candidate for a task
    and reserves it, guaranteeing capacity-aware, audit-friendly execution.
    """

    def __init__(
        self,
        audit: Optional[AuditTrail] = None,
        approvals: Optional[HumanApprovalManager] = None,
    ):
        self.logger = logging.getLogger("orchestration.coordinator")
        self.audit = audit
        self.approvals = approvals
        self._agents: Dict[str, AgentHandle] = {}
        self._lock = asyncio.Lock()
        self._registrations: Dict[str, str] = {}

    # ------------------------------------------------------------------ #
    # Registration
    # ------------------------------------------------------------------ #
    def register_agent(
        self,
        agent_id: str,
        name: Optional[str] = None,
        capabilities: Optional[List[str]] = None,
        description: str = "",
        executor: Optional[Any] = None,
        max_concurrency: int = 5,
        priority: int = 10,
        tags: Optional[Dict[str, Any]] = None,
        accept_duplicate: bool = False,
    ) -> AgentHandle:
        """
        Register an agent in the roster.

        Args:
            agent_id: Unique logical id used across the org.
            name: Human friendly name (defaults to agent_id).
            capabilities: Capability tags used for capability-based routing.
            description: Free-form description.
            executor: Callable ``async def executor(task, context)``.
            max_concurrency: Max simultaneous tasks this agent may run.
            priority: Lower values win arbitration for scarce capacity.
            accept_duplicate: If True, allow re-registration of an existing id.

        Raises:
            AgentConflictError: On duplicate id unless ``accept_duplicate``.
        """
        if agent_id in self._agents and not accept_duplicate:
            raise AgentConflictError(f"Agent '{agent_id}' already registered")

        handle = self._agents.get(agent_id)
        if handle is not None:
            self.logger.info("Re-registering agent %s", agent_id)
        handle = AgentHandle(
            agent_id=agent_id,
            name=name or agent_id,
            capabilities=list(capabilities or []),
            description=description,
            executor=executor,
            max_concurrency=max_concurrency,
            priority=priority,
            tags=dict(tags or {}),
        )
        handle.status = AgentStatus.ACTIVE
        self._agents[agent_id] = handle
        self._registrations[agent_id] = utcnow_iso()
        self._audit("coordinator.agent_registered", resource=agent_id)
        return handle

    def unregister_agent(self, agent_id: str) -> bool:
        """Remove an agent from the roster. Returns True if removed."""
        handle = self._agents.pop(agent_id, None)
        if handle is None:
            return False
        self._registrations.pop(agent_id, None)
        self._audit("coordinator.agent_unregistered", resource=agent_id)
        return True

    def get_agent(self, agent_id: str) -> Optional[AgentHandle]:
        """Return the registered handle for ``agent_id``."""
        return self._agents.get(agent_id)

    def list_agents(self) -> List[AgentHandle]:
        """Return the full roster of registered agents."""
        return list(self._agents.values())

    def set_agent_status(self, agent_id: str, status: str) -> bool:
        """
        Transition an agent's runtime status.

        Supported statuses come from :class:`AgentStatus`. Invalid transitions
        (e.g. scheduling to an unknown status) are rejected.
        """
        valid = {
            AgentStatus.ACTIVE,
            AgentStatus.PAUSED,
            AgentStatus.DRAINING,
            AgentStatus.OFFLINE,
        }
        if status not in valid:
            raise ValueError(
                f"Unknown agent status '{status}'. Use one of {sorted(valid)}"
            )
        handle = self._agents.get(agent_id)
        if handle is None:
            return False
        handle.status = status
        self._audit(
            "coordinator.agent_status",
            resource=agent_id,
            detail={"status": status},
        )
        return True

    # ------------------------------------------------------------------ #
    # Discovery
    # ------------------------------------------------------------------ #
    def find_agents(
        self,
        capabilities: Optional[List[str]] = None,
        *,
        exclude: Optional[List[str]] = None,
        require_all: bool = True,
        max_results: Optional[int] = None,
    ) -> List[AgentHandle]:
        """
        Find agents matching a capability set (or any, when omitted).

        Results are sorted by priority (lower first) then concurrency headroom
        (more headroom first).

        Args:
            capabilities: Capabilities required; empty list matches all.
            exclude: Agent ids never to return.
            require_all: If True, an agent must claim every capability; if
                False, any overlap suffices.
            max_results: Optional result cap.
        """
        exclude_set = set(exclude or [])
        pool = [
            a
            for a in self._agents.values()
            if a.agent_id not in exclude_set
            and a.status
            in (
                AgentStatus.ACTIVE,
                AgentStatus.DRAINING,
            )
        ]
        if capabilities:
            pool = [a for a in pool if self._satisfies(a, capabilities, require_all)]

        def headroom(a: AgentHandle) -> int:
            return a.max_concurrency - a.active_tasks

        pool.sort(
            key=lambda a: (
                a.priority,
                -headroom(a),
                a.agent_id,
            )
        )
        if max_results is not None:
            pool = pool[:max_results]
        return pool

    def _satisfies(
        self, handle: AgentHandle, capabilities: List[str], require_all: bool
    ) -> bool:
        handle_caps = set(handle.capabilities)
        if require_all:
            return set(capabilities).issubset(handle_caps)
        return bool(set(capabilities) & handle_caps)

    # ------------------------------------------------------------------ #
    # Resource allocation
    # ------------------------------------------------------------------ #
    async def acquire(
        self, agent_id: str, *, task: Optional[str] = None
    ) -> Optional[AgentHandle]:
        """
        Reserve capacity on ``agent_id`` if it is currently available.

        Respects ``max_concurrency`` and agent status. Returns the handle on
        success, None otherwise (the caller should pick another candidate).
        """
        async with self._lock:
            handle = self._agents.get(agent_id)
            if handle is None or not handle.available:
                return None
            handle.active_tasks += 1
            handle.total_tasks += 1
            handle.last_active_at = utcnow_iso()
        self._audit(
            "coordinator.acquire",
            resource=agent_id,
            detail={"task": task, "active_now": handle.active_tasks},
        )
        return handle

    def release(self, agent_id: str) -> bool:
        """
        Release reserved capacity on an agent.

        Idempotent; returns False if the agent is unknown or already free.
        """
        handle = self._agents.get(agent_id)
        if handle is None or handle.active_tasks <= 0:
            return False
        handle.active_tasks -= 1
        self._audit(
            "coordinator.release",
            resource=agent_id,
            detail={"active_after": handle.active_tasks},
        )
        return True

    def record_failure(self, agent_id: str) -> None:
        """Increment the failure counter for observability/fallback scoring."""
        handle = self._agents.get(agent_id)
        if handle is not None:
            handle.total_failures += 1

    async def dispatch_to_capability(
        self,
        task: str,
        capabilities: List[str],
        *,
        context: Optional[Dict[str, Any]] = None,
        task_metadata: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """
        Find and invoke an available agent for ``task`` based on capabilities.

        This is the capability-first entry point: an agent that claims the
        required capabilities and has capacity is located, reserved, executed,
        and released. The task arg is passed as ``task`` into the executor.

        Raises:
            CandidateUnavailable: when no registered agent can handle it.
            RuntimeError: when the chosen candidate fails during execution.
        """
        candidates = self.find_agents(list(capabilities), max_results=1)
        if not candidates:
            raise CandidateUnavailable(
                f"No available agent for capabilities: {sorted(capabilities)}"
            )
        handle = candidates[0]
        acquired = await self.acquire(handle.agent_id, task=str(task))
        if acquired is None:
            raise CandidateUnavailable(
                f"Agent '{handle.agent_id}' acquired capacity; retry later"
            )
        try:
            if handle.executor is None:
                raise CoordinatorError(f"Agent '{handle.agent_id}' has no executor")
            return await handle.executor(task, context or {})
        finally:
            self.release(handle.agent_id)

    # ------------------------------------------------------------------ #
    # Observability
    # ------------------------------------------------------------------ #
    def get_metrics(self) -> Dict[str, Any]:
        """Aggregate roster metrics for dashboards/monitoring."""
        active = sum(1 for a in self._agents.values() if a.status == AgentStatus.ACTIVE)
        total_capacity = sum(
            a.max_concurrency - a.active_tasks for a in self._agents.values()
        )
        return {
            "total_agents": len(self._agents),
            "active_agents": active,
            "available_capacity": total_capacity,
            "total_tasks_routed": sum(a.total_tasks for a in self._agents.values()),
            "total_failures": sum(a.total_failures for a in self._agents.values()),
        }

    def export_state(self) -> Dict[str, Any]:
        """Serialize the roster for persistence / disaster recovery."""
        return {
            "agents": {
                agent_id: handle.as_dict() for agent_id, handle in self._agents.items()
            },
            "registered_at": dict(self._registrations),
        }

    def import_state(self, payload: Dict[str, Any]) -> int:
        """Restore a roster from a previous ``export_state`` payload."""
        count = 0
        encoded = payload.get("agents", {})
        registrations = payload.get("registered_at", {})
        for agent_id, data in encoded.items():
            self._agents[agent_id] = AgentHandle(
                agent_id=agent_id,
                name=data.get("name", agent_id),
                capabilities=data.get("capabilities", []),
                description=data.get("description", ""),
                max_concurrency=data.get("max_concurrency", 5),
                priority=data.get("priority", 10),
                status=data.get("status", AgentStatus.ACTIVE),
            )
            if agent_id in registrations:
                self._registrations[agent_id] = registrations[agent_id]
            count += 1
        return count

    def _audit(self, event: str, resource: str, detail: Optional[Dict] = None) -> None:
        if self.audit is not None:
            self.audit.record(event, actor="coordinator", resource=resource)


def create_coordinator(
    audit: Optional[AuditTrail] = None,
    approvals: Optional[HumanApprovalManager] = None,
) -> AgentCoordinator:
    """Factory for a :class:`AgentCoordinator`."""
    return AgentCoordinator(audit=audit, approvals=approvals)
