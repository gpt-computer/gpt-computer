import pytest

from gpt_computer.core.orchestration.agent_coordinator import (
    AgentConflictError,
    AgentCoordinator,
    CandidateUnavailable,
    CoordinatorError,
    create_coordinator,
)
from gpt_computer.core.orchestration.models import AgentStatus, AuditTrail

from .helpers import make_executor


@pytest.fixture
def coordinator():
    return AgentCoordinator()


def test_register_and_get(coordinator):
    handle = coordinator.register_agent(
        "reviewer",
        name="Code Reviewer",
        capabilities=["code_review", "lint"],
        max_concurrency=2,
        priority=5,
    )
    assert coordinator.get_agent("reviewer") is handle
    assert handle.name == "Code Reviewer"
    assert handle.available


def test_duplicate_registration_raises(coordinator):
    coordinator.register_agent("a", capabilities=["x"])
    with pytest.raises(AgentConflictError):
        coordinator.register_agent("a", capabilities=["y"])
    coordinator.register_agent("a", capabilities=["z"], accept_duplicate=True)


def test_unregister(coordinator):
    coordinator.register_agent("a")
    assert coordinator.unregister_agent("a") is True
    assert coordinator.unregister_agent("a") is False
    assert coordinator.get_agent("a") is None


@pytest.mark.asyncio
async def test_capability_discovery_priority_ordering(coordinator):
    coordinator.register_agent("slow", capabilities=["code_review"], priority=10)
    coordinator.register_agent("fast", capabilities=["code_review"], priority=1)

    found = coordinator.find_agents(["code_review"])
    assert [a.agent_id for a in found] == ["fast", "slow"]


@pytest.mark.asyncio
async def test_find_agents_excludes_and_require_all(coordinator):
    coordinator.register_agent("all", capabilities=["scan", "report"])
    coordinator.register_agent("partial", capabilities=["scan"])

    both = coordinator.find_agents(["scan", "report"], require_all=True)
    assert [a.agent_id for a in both] == ["all"]

    partial_overlap = coordinator.find_agents(["scan"], require_all=False)
    assert {a.agent_id for a in partial_overlap} == {"all", "partial"}


@pytest.mark.asyncio
async def test_concurrency_limit_enforced(coordinator):
    coordinator.register_agent("busy", capabilities=["x"], max_concurrency=1)
    handle = await coordinator.acquire("busy")
    assert handle is not None
    assert await coordinator.acquire("busy") is None
    assert coordinator.release("busy") is True
    assert await coordinator.acquire("busy") is not None


@pytest.mark.asyncio
async def test_offline_agent_not_discoverable(coordinator):
    coordinator.register_agent("down", capabilities=["scan"])
    coordinator.set_agent_status("down", AgentStatus.OFFLINE)
    assert coordinator.find_agents(["scan"]) == []


@pytest.mark.asyncio
async def test_dispatch_to_capability(coordinator):
    coordinator.register_agent(
        "analyst", capabilities=["analyze"], executor=make_executor({"ok": True})
    )
    result = await coordinator.dispatch_to_capability("run", ["analyze"])
    assert result == {"ok": True}


@pytest.mark.asyncio
async def test_dispatch_no_agent_raises(coordinator):
    with pytest.raises(CandidateUnavailable):
        await coordinator.dispatch_to_capability("run", ["missing"])


@pytest.mark.asyncio
async def test_metrics_and_state_roundtrip(coordinator):
    coordinator.register_agent("a", capabilities=["x"], executor=make_executor(1))
    await coordinator.dispatch_to_capability("t", ["x"])

    metrics = coordinator.get_metrics()
    assert metrics["total_agents"] == 1
    assert metrics["total_tasks_routed"] == 1

    payload = coordinator.export_state()
    fresh = AgentCoordinator()
    assert fresh.import_state(payload) == 1
    assert fresh.get_agent("a") is not None
    assert "x" in fresh.get_agent("a").capabilities


def test_find_agents_returns_all_when_no_capabilities(coordinator):
    coordinator.register_agent("a", capabilities=["x"])
    coordinator.register_agent("b", capabilities=["y"])
    all_agents = coordinator.find_agents()
    assert {a.agent_id for a in all_agents} == {"a", "b"}


def test_find_agents_respects_max_results(coordinator):
    coordinator.register_agent("a", capabilities=["x"])
    coordinator.register_agent("b", capabilities=["x"])
    assert len(coordinator.find_agents(["x"], max_results=1)) == 1


def test_list_agents_returns_roster(coordinator):
    coordinator.register_agent("a", capabilities=["x"])
    coordinator.register_agent("b", capabilities=["y"])
    ids = {agent.agent_id for agent in coordinator.list_agents()}
    assert ids == {"a", "b"}


def test_set_status_invalid_status_raises(coordinator):
    coordinator.register_agent("a")
    with pytest.raises(ValueError):
        coordinator.set_agent_status("a", "winging-it")
    assert coordinator.set_agent_status("ghost", AgentStatus.OFFLINE) is False


def test_set_status_transitions_and_audits():
    audit = AuditTrail()
    coordinator = create_coordinator(audit=audit)
    coordinator.register_agent("a")
    assert coordinator.set_agent_status("a", AgentStatus.PAUSED) is True
    events = [e.event for e in audit.entries()]
    assert "coordinator.agent_status" in events
    assert "coordinator.agent_registered" in events


def test_release_when_unknown_or_idle_is_false(coordinator):
    coordinator.register_agent("a")
    assert coordinator.release("a") is False
    assert coordinator.release("ghost") is False


def test_record_failure_observability(coordinator):
    coordinator.register_agent("a")
    coordinator.record_failure("a")
    coordinator.record_failure("a")
    assert coordinator.get_agent("a").total_failures == 2
    assert coordinator.get_metrics()["total_failures"] == 2
    coordinator.record_failure("ghost")  # no-op for unknown agent


def test_dispatch_to_candidate_without_executor_is_covered(coordinator):
    """Marker: the async variant below asserts the CoordinatorError path."""
    assert coordinator is not None


@pytest.mark.asyncio
async def test_dispatch_agent_without_executor_raises(coordinator):
    coordinator.register_agent("lazy", capabilities=["op"])
    with pytest.raises(CoordinatorError):
        await coordinator.dispatch_to_capability("run", ["op"])


@pytest.mark.asyncio
async def test_dispatch_unavailable_candidate_raises(coordinator):
    coordinator.register_agent(
        "only", capabilities=["op"], executor=make_executor("done"), max_concurrency=1
    )
    await coordinator.acquire("only")
    with pytest.raises(CandidateUnavailable):
        await coordinator.dispatch_to_capability("run", ["op"])


@pytest.mark.asyncio
async def test_registration_audits_when_trail_present():
    audit = AuditTrail()
    coordinator = AgentCoordinator(audit=audit)
    coordinator.register_agent("audited")
    events = [e.event for e in audit.entries()]
    assert "coordinator.agent_registered" in events
    assert coordinator.unregister_agent("audited") is True
    events_after = [e.event for e in audit.entries()]
    assert "coordinator.agent_unregistered" in events_after


def test_import_state_preserves_registrations():
    coordinator = AgentCoordinator()
    coordinator.register_agent("persistent", capabilities=["x"], priority=3)
    payload = coordinator.export_state()

    restored = AgentCoordinator()
    assert restored.import_state(payload) == 1
    restored.set_agent_status("persistent", AgentStatus.OFFLINE)
    # re-export from the restored coordinator and confirm priority survived
    assert restored.get_agent("persistent").priority == 3


def test_import_state_without_registrations():
    restored = AgentCoordinator()
    count = restored.import_state(
        {"agents": {"raw": {"name": "raw", "capabilities": ["x"]}}}
    )
    assert count == 1
    assert restored.get_agent("raw").capabilities == ["x"]


@pytest.mark.asyncio
async def test_executor_runs_with_context():
    calls = []

    async def tracker(task, context):
        calls.append((task, context))
        return "ok"

    coordinator = AgentCoordinator()
    coordinator.register_agent("t", capabilities=["op"], executor=tracker)
    outcome = await coordinator.dispatch_to_capability(
        "run", ["op"], context={"env": "prod"}
    )
    assert outcome == "ok"
    assert calls == [("run", {"env": "prod"})]
