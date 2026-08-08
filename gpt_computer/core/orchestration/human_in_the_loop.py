"""
Human-in-the-Loop Approval Primitives

Provides the approval gate used by the workflow engine so steps that touch
sensitive operations (merges, releases, infrastructure mutations, etc.) pause
and wait for an explicit human decision.

Classes:
    ApprovalStatus: States an approval request can occupy.
    ApprovalRequest: A single pending approval decision.
    HumanApprovalManager: Registry + event-driven wait/signalling for approvals.

Functions:
    create_approval_manager(on_request=None) -> HumanApprovalManager
"""

from __future__ import annotations

import asyncio
import logging
import time

from enum import Enum
from typing import Any, Awaitable, Callable, Dict, List, Optional

from gpt_computer.core.orchestration.models import AuditTrail, utcnow_iso


class ApprovalStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"


class ApprovalDecision(Exception):
    """Raised when an approval request is acted on illegally."""


class ApprovalRequest:
    """
    A single human-in-the-loop decision point.

    ``request()`` blocks until the request is approved, rejected, or expired;
    the outcome is available on the returned object.
    """

    def __init__(
        self,
        approval_id: str,
        summary: str,
        payload: Any = None,
        *,
        run_id: Optional[str] = None,
        step_id: Optional[str] = None,
        timeout_seconds: Optional[float] = None,
        requested_by: str = "workflow_engine",
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.approval_id = approval_id
        self.summary = summary
        self.payload = payload
        self.run_id = run_id
        self.step_id = step_id
        self.timeout_seconds = timeout_seconds
        self.status = ApprovalStatus.PENDING
        self.requested_by = requested_by
        self.metadata = dict(metadata or {})
        self.requested_at = utcnow_iso()
        self.decided_at: Optional[str] = None
        self.decided_by: Optional[str] = None
        self.reason: Optional[str] = None

    @property
    def approved(self) -> bool:
        return self.status == ApprovalStatus.APPROVED

    @property
    def pending(self) -> bool:
        return (
            self.status == ApprovalStatus.PENDING
            or self.status == ApprovalStatus.EXPIRED
        )

    def _decide(self, status: ApprovalStatus, decided_by: str, reason: str) -> bool:
        if self.status != ApprovalStatus.PENDING:
            raise ApprovalDecision(
                f"Approval {self.approval_id} is already {self.status.value}"
            )
        self.status = status
        self.decided_at = utcnow_iso()
        self.decided_by = decided_by
        self.reason = reason
        return True

    def as_dict(self) -> Dict[str, Any]:
        return {
            "approval_id": self.approval_id,
            "summary": self.summary,
            "run_id": self.run_id,
            "step_id": self.step_id,
            "status": self.status.value,
            "requested_by": self.requested_by,
            "requested_at": self.requested_at,
            "decided_at": self.decided_at,
            "decided_by": self.decided_by,
            "reason": self.reason,
            "timeout_seconds": self.timeout_seconds,
        }


class HumanApprovalManager:
    """
    Manages the lifecycle of in-flight approval requests.

    Approvals are asynchronous: the engine calls :meth:`request` and blocks on
    the request event, while a human (or an operator service) resolves it with
    :meth:`approve` / :meth:`reject`. Resolving an approval signals the waiter
    through an ``asyncio.Event``, so a decision made before the engine awaits
    is not lost.
    """

    def __init__(
        self,
        audit: Optional[AuditTrail] = None,
        on_request: Optional[
            Callable[[ApprovalRequest], Optional[Awaitable[None]]]
        ] = None,
        default_timeout_seconds: Optional[float] = None,
    ):
        self.logger = logging.getLogger("orchestration.human_in_the_loop")
        self.audit = audit
        self._requests: Dict[str, ApprovalRequest] = {}
        self._events: Dict[str, asyncio.Event] = {}
        self._on_request = on_request
        self.default_timeout_seconds = default_timeout_seconds

    async def request(
        self,
        summary: str,
        payload: Any = None,
        *,
        run_id: Optional[str] = None,
        step_id: Optional[str] = None,
        timeout: Optional[float] = None,
        requested_by: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ApprovalRequest:
        """
        Register and await a human decision.

        Args:
            summary: Human-readable description of what is being approved.
            payload: Context passed through to the human.
            run_id: Optional workflow run id for traceability.
            step_id: Optional workflow step id for traceability.
            timeout: Maximum seconds to wait. ``None`` waits indefinitely.
            requested_by: Actor making the request.

        Returns:
            The resolved :class:`ApprovalRequest`.
        """
        approval_id = f"approval_{int(time.time() * 1000)}"
        timeout = (
            self.default_timeout_seconds
            if timeout is None and self.default_timeout_seconds
            else timeout
        )
        request = ApprovalRequest(
            approval_id,
            summary,
            payload,
            run_id=run_id,
            step_id=step_id,
            timeout_seconds=timeout,
            requested_by=requested_by or "workflow_engine",
            metadata=metadata,
        )
        self._requests[approval_id] = request
        self._events[approval_id] = asyncio.Event()

        if self.audit:
            self.audit.record(
                "approval.requested",
                actor=request.requested_by,
                resource=approval_id,
                run_id=run_id,
                step_id=step_id,
                message=summary,
                detail={"timeout_seconds": timeout},
            )
        self.logger.info("Approval requested: %s (%s)", approval_id, summary)

        if self._on_request:
            try:
                result = self._on_request(request)
                if result is not None and hasattr(result, "__await__"):
                    await result
            except Exception:  # pragma: no cover - defensive
                self.logger.warning(
                    "Approval notification handler failed", exc_info=True
                )

        if timeout is not None:
            try:
                await asyncio.wait_for(
                    self._events[approval_id].wait(), timeout=timeout
                )
            except asyncio.TimeoutError:
                request.status = ApprovalStatus.EXPIRED
                if self.audit:
                    self.audit.record(
                        "approval.expired",
                        actor="system",
                        resource=approval_id,
                        run_id=run_id,
                        step_id=step_id,
                        message=summary,
                    )
        else:
            await self._events[approval_id].wait()

        self._events.pop(approval_id, None)
        self._requests.pop(approval_id, None)
        return request

    def approve(
        self,
        approval_id: str,
        *,
        approved_by: str = "human",
        reason: str = "",
    ) -> bool:
        """Resolve a pending approval with an 'approved' decision."""
        request = self._resolve(approval_id)
        request._decide(ApprovalStatus.APPROVED, approved_by, reason)
        self._events[approval_id].set()
        self._record_decision(request)
        return True

    def reject(
        self,
        approval_id: str,
        *,
        rejected_by: str = "human",
        reason: str = "",
    ) -> bool:
        """Resolve a pending approval with a 'rejected' decision."""
        request = self._resolve(approval_id)
        request._decide(ApprovalStatus.REJECTED, rejected_by, reason)
        self._events[approval_id].set()
        self._record_decision(request)
        return True

    def _resolve(self, approval_id: str) -> ApprovalRequest:
        request = self._requests.get(approval_id)
        if request is None:
            raise ApprovalDecision(f"Unknown approval request: {approval_id}")
        return request

    def _record_decision(self, request: ApprovalRequest) -> None:
        if not self.audit:
            return
        self.audit.record(
            f"approval.{request.status.value}",
            actor=request.decided_by or "unknown",
            resource=request.approval_id,
            run_id=request.run_id,
            step_id=request.step_id,
            message=request.summary,
            detail={"reason": request.reason or ""},
        )

    def get(self, approval_id: str) -> Optional[ApprovalRequest]:
        """Return the pending request, or None if already resolved."""
        return self._requests.get(approval_id)

    def list_pending(self) -> List[ApprovalRequest]:
        """Return all approval requests still awaiting a decision."""
        return [
            r for r in self._requests.values() if r.status == ApprovalStatus.PENDING
        ]

    @property
    def pending_count(self) -> int:
        return len(self.list_pending())

    def shutdown(self) -> None:
        """Resolve any unanswered approvals as expired on orderly shutdown."""
        for approval in list(self._requests.values()):
            if approval.status == ApprovalStatus.PENDING:
                try:
                    approval._decide(
                        ApprovalStatus.EXPIRED, "system_shutdown", "manager stopped"
                    )
                except ApprovalDecision:  # pragma: no cover - defensive
                    continue
                self._record_decision(approval)
                self.logger.info(
                    "Approval %s expired on shutdown", approval.approval_id
                )


def create_approval_manager(**kwargs) -> HumanApprovalManager:
    """Factory that returns a configured :class:`HumanApprovalManager`."""
    return HumanApprovalManager(**kwargs)
