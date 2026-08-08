"""
Workflow Engine

Runs multi-step AI workflows with capability-based scheduling, concurrent
dispatch of ready steps, retry/backoff, agent fallback, per-step timeouts, and
optional human-in-the-loop approval gates. Every transition is audited.

Classes:
    WorkflowExecutionError: Raised when a step fails past retries/fallback.
    WorkflowConfigurationError: Raised on invalid workflow definitions.
    WorkflowEngine: Executes workflow specs asynchronously.

Functions:
    create_workflow_engine(...) -> WorkflowEngine
"""

from __future__ import annotations

import asyncio
import logging

from typing import Any, Dict, List, Optional, Tuple

from gpt_computer.core.orchestration.agent_coordinator import AgentCoordinator
from gpt_computer.core.orchestration.human_in_the_loop import HumanApprovalManager
from gpt_computer.core.orchestration.models import (
    AuditTrail,
    StepExecution,
    StepStatus,
    WorkflowRun,
    WorkflowSpec,
    WorkflowStatus,
    utcnow_iso,
)


class WorkflowExecutionError(Exception):
    """A step failed after exhausting retries and fallback capacity."""


class WorkflowConfigurationError(Exception):
    """The workflow definition is invalid or incomplete."""


# A candidate executor for a step - ("agent", AgentHandle) or ("handler", fn).
Candidate = Tuple[str, Any]


class WorkflowEngine:
    """
    Executes :class:`~gpt_computer.core.orchestration.models.WorkflowSpec`.

    Steps are dispatched onto the coordinator's agents or inline handlers,
    respecting dependencies, retries, fallback, timeouts, and approvals.
    Runs are tracked by id and exported to the audit trail for compliance.
    """

    def __init__(
        self,
        coordinator: Optional[AgentCoordinator] = None,
        approvals: Optional[HumanApprovalManager] = None,
        audit: Optional[AuditTrail] = None,
        default_retry_policy=None,
        default_approval_timeout: Optional[float] = None,
    ):
        from gpt_computer.core.orchestration.models import RetryPolicy

        self.audit = audit or AuditTrail()
        self.approvals = approvals or HumanApprovalManager(audit=self.audit)
        self.coordinator = coordinator or AgentCoordinator(
            audit=self.audit, approvals=self.approvals
        )
        self.default_retry_policy = default_retry_policy or RetryPolicy()
        self.default_approval_timeout = default_approval_timeout
        self.logger = logging.getLogger("orchestration.workflow_engine")
        self._runs: Dict[str, WorkflowRun] = {}

    # ------------------------------------------------------------------ #
    # Workflow definition helpers
    # ------------------------------------------------------------------ #
    def create_workflow(
        self,
        name: str,
        steps: Optional[List[Any]] = None,
        description: str = "",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> WorkflowSpec:
        """Create a :class:`WorkflowSpec`."""
        return WorkflowSpec(
            name=name,
            steps=list(steps or []),
            description=description,
            metadata=dict(metadata or {}),
        )

    def attach_handlers(
        self,
        spec: WorkflowSpec,
        handlers: Dict[str, Any],
    ) -> WorkflowSpec:
        """Bind inline handlers to steps by step_id."""
        for step in spec.steps:
            if step.step_id in handlers:
                step.handler = handlers[step.step_id]
        return spec

    # ------------------------------------------------------------------ #
    # Run lifecycle
    # ------------------------------------------------------------------ #
    def create_run(
        self,
        workflow: WorkflowSpec,
        inputs: Optional[Dict[str, Any]] = None,
        run_id: Optional[str] = None,
    ) -> WorkflowRun:
        """Instantiate (but do not start) a run for a workflow."""
        run = WorkflowRun(workflow=workflow, inputs=inputs, run_id=run_id)
        self._runs[run.run_id] = run
        return run

    def get_run(self, run_id: str) -> Optional[WorkflowRun]:
        """Return a previously created run by id."""
        return self._runs.get(run_id)

    def list_runs(self) -> List[WorkflowRun]:
        """Return all known runs, most recent first."""
        return list(reversed(list(self._runs.values())))

    async def run_workflow(
        self,
        workflow: WorkflowSpec,
        inputs: Optional[Dict[str, Any]] = None,
        run_id: Optional[str] = None,
    ) -> WorkflowRun:
        """Create and execute a run to completion, then return it."""
        run = self.create_run(workflow, inputs=inputs, run_id=run_id)
        return await self.execute(run)

    async def execute(self, run: WorkflowRun) -> WorkflowRun:
        """Execute a run, dispatching ready steps concurrently, to completion."""
        if run.status in (WorkflowStatus.COMPLETED, WorkflowStatus.FAILED):
            return run

        run.status = WorkflowStatus.RUNNING
        run.started_at = utcnow_iso()
        self._audit("workflow.started", run.run_id, None)

        steps = run.workflow.steps
        by_id = {s.step_id: s for s in steps}
        started: set = set()
        completed: set = set()

        try:
            while True:
                ready = [
                    s
                    for s in steps
                    if s.step_id not in started
                    and all(dep in completed for dep in s.depends_on)
                ]
                if not ready:
                    break
                started.update(s.step_id for s in ready)
                outcomes = await asyncio.gather(
                    *(self._run_step(run, s, by_id) for s in ready),
                    return_exceptions=True,
                )
                for step, outcome in zip(ready, outcomes):
                    if isinstance(outcome, BaseException):
                        run.status = WorkflowStatus.FAILED
                        run.error = str(outcome)
                        self._audit(
                            "workflow.failed",
                            run.run_id,
                            step.step_id,
                            {"error": str(outcome)},
                        )
                        return run
                    completed.add(step.step_id)

            if all(s.step_id in completed for s in steps):
                run.status = WorkflowStatus.COMPLETED
                self._audit("workflow.completed", run.run_id, None)
            else:
                run.status = WorkflowStatus.FAILED
                run.error = "Unresolved step dependencies (workflow deadlock)"
                self._audit(
                    "workflow.failed",
                    run.run_id,
                    None,
                    {"error": run.error},
                )
        except asyncio.CancelledError:  # pragma: no cover - defensive
            run.status = WorkflowStatus.CANCELLED
            raise
        finally:
            run.completed_at = utcnow_iso()
        return run

    # ------------------------------------------------------------------ #
    # Step execution
    # ------------------------------------------------------------------ #
    async def _run_step(
        self, run: WorkflowRun, step: Any, by_id: Dict[str, Any]
    ) -> Any:
        step_exec = StepExecution(step_id=step.step_id)
        run.step_executions[step.step_id] = step_exec
        step_exec.status = StepStatus.RUNNING
        step_exec.started_at = utcnow_iso()
        self._audit(
            "workflow.step_started",
            run.run_id,
            step.step_id,
            {"task": step.task},
        )

        task_input = self._build_task_input(run, step)

        if step.require_approval:
            await self._request_approval(run, step, task_input)

        retry_policy = step.retry_policy or self.default_retry_policy
        candidates = self._candidates(step)
        if not candidates:
            raise WorkflowConfigurationError(
                f"Step '{step.step_id}' has no executable source: "
                "no agent_id, no handler, and no matching capabilities"
            )

        last_error: Optional[BaseException] = None
        for source_id, payload in candidates:
            try:
                return await self._run_source(
                    run, step, step_exec, source_id, payload, task_input, retry_policy
                )
            except WorkflowExecutionError as exc:
                last_error = exc

        step_exec.status = StepStatus.FAILED
        step_exec.error = str(last_error)
        raise WorkflowExecutionError(
            f"Step '{step.step_id}' failed on all candidates: {last_error}"
        )

    def _candidates(self, step: Any) -> List[Candidate]:
        """Rank executor candidates for a step."""
        candidates: List[Candidate] = []
        seen: set = set()

        def add_agent(agent_id: str) -> None:
            if agent_id in seen:
                return
            handle = self.coordinator.get_agent(agent_id)
            if handle is None:
                self.logger.warning(
                    "Step '%s' references unknown agent '%s'", step.step_id, agent_id
                )
                return
            seen.add(agent_id)
            candidates.append(("agent", handle))

        if step.agent_id:
            add_agent(step.agent_id)
        for fb in step.fallback_agent_ids:
            add_agent(fb)
        if step.capabilities:
            for handle in self.coordinator.find_agents(step.capabilities):
                add_agent(handle.agent_id)
        if step.handler is not None:
            candidates.append(("handler", step.handler))
        return candidates

    async def _run_source(
        self,
        run: WorkflowRun,
        step: Any,
        step_exec: StepExecution,
        source_id: str,
        payload: Any,
        task_input: Dict[str, Any],
        retry_policy,
    ) -> Any:
        if source_id == "agent":
            acquired = await self.coordinator.acquire(
                payload.agent_id, task=step.step_id
            )
            if acquired is None:
                raise WorkflowExecutionError(
                    f"Agent '{payload.agent_id}' has no capacity "
                    f"for step '{step.step_id}'"
                )
        try:
            last_exception: Optional[BaseException] = None
            for attempt in range(1, retry_policy.max_attempts + 1):
                step_exec.attempts += 1
                step_exec.resolved_agent_id = (
                    payload.agent_id if source_id == "agent" else None
                )
                try:
                    result = await self._invoke_with_timeout(
                        payload, run, step, task_input
                    )
                except asyncio.TimeoutError as exc:
                    last_exception = exc
                    retryable = True
                except Exception as exc:
                    last_exception = exc
                    retryable = isinstance(exc, retry_policy.retry_on)
                else:
                    step_exec.status = StepStatus.SUCCEEDED
                    step_exec.completed_at = utcnow_iso()
                    step_exec.result = result
                    run.step_results[step.step_id] = result
                    run.context[step.step_id] = result
                    self._audit(
                        "workflow.step_succeeded",
                        run.run_id,
                        step.step_id,
                        {
                            "agent": step_exec.resolved_agent_id,
                            "attempt": attempt,
                        },
                    )
                    return result

                self._audit(
                    "workflow.step_attempt_failed",
                    run.run_id,
                    step.step_id,
                    {
                        "attempt": attempt,
                        "agent": step_exec.resolved_agent_id,
                        "error": str(last_exception),
                    },
                )
                if retryable and attempt < retry_policy.max_attempts:
                    delay = retry_policy.delay_for(attempt - 1)
                    await asyncio.sleep(delay)
                    continue
                break
        finally:
            if source_id == "agent":
                self.coordinator.release(payload.agent_id)

        step_exec.status = StepStatus.FAILED
        step_exec.error = (
            str(last_exception) if last_exception is not None else "unknown failure"
        )
        raise WorkflowExecutionError(
            f"Step '{step.step_id}' failed on source "
            f"{source_id} ({step_exec.resolved_agent_id}): "
            f"{step_exec.error}"
        )

    async def _invoke_with_timeout(
        self, payload: Any, run: WorkflowRun, step: Any, task_input: Dict[str, Any]
    ) -> Any:
        coro = self._invoke(payload, run, step, task_input)
        if step.timeout_seconds:
            return await asyncio.wait_for(coro, timeout=step.timeout_seconds)
        return await coro

    async def _invoke(
        self, payload: Any, run: WorkflowRun, step: Any, task_input: Dict[str, Any]
    ) -> Any:
        executor = getattr(payload, "executor", payload)
        if not callable(executor):
            raise WorkflowConfigurationError(
                f"Step '{step.step_id}' executor is not callable"
            )
        return await executor(task_input, run.context)

    def _build_task_input(self, run: WorkflowRun, step: Any) -> Dict[str, Any]:
        task = dict(run.inputs)
        task.update(step.inputs)
        for dep in step.depends_on:
            if dep in run.step_results:  # pragma: no cover - deps pre-verified
                task[dep] = run.step_results[dep]
        return task

    async def _request_approval(
        self, run: WorkflowRun, step: Any, task_input: Dict[str, Any]
    ) -> None:
        self._audit(
            "workflow.approval_pending",
            run.run_id,
            step.step_id,
            {"summary": step.approval_summary or step.task},
        )
        timeout = step.approval_timeout_seconds or self.default_approval_timeout
        approval = await self.approvals.request(
            step.approval_summary or step.task or step.step_id,
            payload=task_input,
            run_id=run.run_id,
            step_id=step.step_id,
            timeout=timeout,
            requested_by=f"workflow:{run.run_id}",
        )
        if not approval.approved:
            raise WorkflowExecutionError(
                f"Step '{step.step_id}' rejected at approval gate "
                f"({approval.status.value}: {approval.reason or 'no reason'})"
            )

    # ------------------------------------------------------------------ #
    # Utilities
    # ------------------------------------------------------------------ #
    def cancel(self, run_id: str) -> bool:
        """Mark an in-flight run as cancelled; returns False if not active."""
        run = self._runs.get(run_id)
        if run is None or run.status != WorkflowStatus.RUNNING:
            return False
        run.status = WorkflowStatus.CANCELLED
        return True

    def metrics(self) -> Dict[str, Any]:
        """Quick summary of engine activity for dashboards."""
        runs = list(self._runs.values())
        return {
            "total_runs": len(runs),
            "completed": sum(1 for r in runs if r.status == WorkflowStatus.COMPLETED),
            "failed": sum(1 for r in runs if r.status == WorkflowStatus.FAILED),
            "active": sum(1 for r in runs if r.status == WorkflowStatus.RUNNING),
        }

    def _audit(
        self,
        event: str,
        run_id: Optional[str],
        step_id: Optional[str],
        detail: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.audit.record(
            event,
            actor="workflow_engine",
            resource=run_id or "",
            run_id=run_id,
            step_id=step_id,
            detail=dict(detail or {}),
        )


def create_workflow_engine(
    *,
    coordinator: Optional[AgentCoordinator] = None,
    approvals: Optional[HumanApprovalManager] = None,
    audit: Optional[AuditTrail] = None,
    default_retry_policy=None,
    default_approval_timeout: Optional[float] = None,
) -> WorkflowEngine:
    """Factory for a :class:`WorkflowEngine`."""
    return WorkflowEngine(
        coordinator=coordinator,
        approvals=approvals,
        audit=audit,
        default_retry_policy=default_retry_policy,
        default_approval_timeout=default_approval_timeout,
    )
