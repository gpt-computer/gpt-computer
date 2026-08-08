import asyncio

import pytest

from gpt_computer.core.orchestration.human_in_the_loop import (
    ApprovalDecision,
    ApprovalStatus,
    HumanApprovalManager,
    create_approval_manager,
)
from gpt_computer.core.orchestration.models import AuditTrail


@pytest.mark.asyncio
async def test_approve_resolves_request():
    manager = HumanApprovalManager()

    async def expect_approved():
        request = await manager.request("deploy to prod", {"env": "prod"})
        assert request.approved is True
        assert request.status == ApprovalStatus.APPROVED
        assert request.decided_by == "ops-lead"

    waiter = asyncio.create_task(expect_approved())
    await asyncio.sleep(0.01)
    assert manager.pending_count == 1

    pending = manager.list_pending()[0]
    assert manager.approve(pending.approval_id, approved_by="ops-lead", reason="LTGT")
    await waiter


@pytest.mark.asyncio
async def test_reject_via_request():
    manager = HumanApprovalManager()

    async def expect_rejected():
        request = await manager.request("rollback prod", {"scope": "all"})
        assert request.approved is False
        assert request.status == ApprovalStatus.REJECTED
        assert request.reason == "too risky"

    waiter = asyncio.create_task(expect_rejected())
    await asyncio.sleep(0.01)
    pending = manager.list_pending()[0]
    manager.reject(pending.approval_id, rejected_by="ops-lead", reason="too risky")
    await waiter


@pytest.mark.asyncio
async def test_timeout_expires_request():
    manager = HumanApprovalManager()
    request = await manager.request("slow decision", None, timeout=0.05)
    assert request.status == ApprovalStatus.EXPIRED
    assert request.approved is False


@pytest.mark.asyncio
async def test_immediate_approval_before_await_is_delivered():
    manager = HumanApprovalManager()

    async def run_gate():
        approval = await manager.request("no wait", None)
        return approval.approved

    task = asyncio.create_task(run_gate())
    await asyncio.sleep(0.01)
    pending = manager.list_pending()[0]
    manager.approve(pending.approval_id, approved_by="autoreview")
    assert await task is True


def test_approve_unknown_approval_is_safe():
    manager = HumanApprovalManager()
    with pytest.raises(ApprovalDecision):
        manager.approve("does-not-exist")


def test_request_properties_and_serialization():
    from gpt_computer.core.orchestration.human_in_the_loop import ApprovalRequest

    request = ApprovalRequest("abc", "summary", payload={"x": 1})
    assert request.pending
    assert not request.approved
    data = request.as_dict()
    assert data["approval_id"] == "abc"
    assert data["summary"] == "summary"
    assert data["status"] == "pending"


@pytest.mark.asyncio
async def test_double_decision_raises():
    manager = HumanApprovalManager()

    async def waiter():
        return await manager.request("long", None)

    task = asyncio.create_task(waiter())
    await asyncio.sleep(0.01)
    pending = manager.list_pending()[0]
    assert manager.approve(pending.approval_id, approved_by="one") is True
    with pytest.raises(ApprovalDecision):
        manager.reject(pending.approval_id, rejected_by="two")
    await task


@pytest.mark.asyncio
async def test_get_returns_pending_then_none():
    manager = HumanApprovalManager()

    async def waiter():
        return await manager.request("peek", None)

    task = asyncio.create_task(waiter())
    await asyncio.sleep(0.01)
    pending = manager.list_pending()[0]
    assert manager.get(pending.approval_id) is pending
    manager.approve(pending.approval_id, approved_by="viewer")
    await task
    assert manager.get(pending.approval_id) is None


@pytest.mark.asyncio
async def test_on_request_callback_is_notified():
    notified = []
    manager = HumanApprovalManager(on_request=notified.append)

    async def waiter():
        return await manager.request("callback", None)

    task = asyncio.create_task(waiter())
    await asyncio.sleep(0.01)
    assert len(notified) == 1
    assert notified[0].summary == "callback"
    pending = manager.list_pending()[0]
    manager.approve(pending.approval_id, approved_by="x")
    await task


@pytest.mark.asyncio
async def test_async_on_request_callback_is_awaited():
    events = []

    async def async_notify(request):
        events.append(request.summary)

    manager = HumanApprovalManager(on_request=async_notify)

    async def waiter():
        return await manager.request("announce", None)

    task = asyncio.create_task(waiter())
    await asyncio.sleep(0.01)
    assert events == ["announce"]  # callback completed before the gate resolves
    assert manager.pending_count == 1
    manager.approve(manager.list_pending()[0].approval_id, approved_by="x")
    await task


@pytest.mark.asyncio
async def test_expiry_recorded_in_audit_trail():
    audit = AuditTrail()
    manager = HumanApprovalManager(audit=audit)
    request = await manager.request("expiry", None, timeout=0.02)
    assert request.status == ApprovalStatus.EXPIRED
    events = [e.event for e in audit.entries()]
    assert "approval.requested" in events
    assert "approval.expired" in events


@pytest.mark.asyncio
async def test_decisions_recorded_in_audit_trail():
    audit = AuditTrail()
    manager = HumanApprovalManager(audit=audit)

    async def waiter():
        return await manager.request("capture", None)

    task = asyncio.create_task(waiter())
    await asyncio.sleep(0.01)
    pending = manager.list_pending()[0]
    manager.approve(pending.approval_id, approved_by="ops")

    await task
    events = [e.event for e in audit.entries()]
    assert "approval.approved" in events


def test_create_approval_manager_factory():
    manager = create_approval_manager()
    assert isinstance(manager, HumanApprovalManager)
    assert manager.default_timeout_seconds is None


@pytest.mark.asyncio
async def test_top_level_default_timeout_applies():
    manager = create_approval_manager(default_timeout_seconds=0.02)
    request = await manager.request("bounded", None)
    assert request.status == ApprovalStatus.EXPIRED


@pytest.mark.asyncio
async def test_pending_count_tracks_live_requests():
    manager = HumanApprovalManager()

    async def wait_long():
        await manager.request("durable approval", None)

    task = asyncio.create_task(wait_long())
    await asyncio.sleep(0.01)
    assert manager.pending_count == 1
    manager.shutdown()
    await asyncio.sleep(0.01)
    assert manager.pending_count == 0
    task.cancel()
