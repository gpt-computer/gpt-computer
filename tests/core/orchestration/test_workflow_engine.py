import asyncio
import time

import pytest

from gpt_computer.core.orchestration.agent_coordinator import AgentCoordinator
from gpt_computer.core.orchestration.models import (
    AuditTrail,
    RetryPolicy,
    WorkflowSpec,
    WorkflowStatus,
    WorkflowStep,
)
from gpt_computer.core.orchestration.workflow_engine import (
    WorkflowEngine,
    create_workflow_engine,
)

from .helpers import make_executor


@pytest.fixture
def engine():
    audit = AuditTrail()
    return WorkflowEngine(audit=audit), audit


@pytest.mark.asyncio
async def test_simple_sequential_workflow(engine):
    wf_engine, audit = engine
    spec = WorkflowSpec(
        name="review",
        steps=[
            WorkflowStep(step_id="analyze", handler=make_executor({"score": 0.9})),
            WorkflowStep(
                step_id="decide",
                handler=make_executor({"verdict": "approve"}),
                depends_on=["analyze"],
            ),
        ],
    )
    run = await wf_engine.run_workflow(spec, {"repo": "gpt-computer"})
    assert run.status == WorkflowStatus.COMPLETED
    assert run.step_results["analyze"] == {"score": 0.9}
    assert run.step_results["decide"] == {"verdict": "approve"}
    events = [e.event for e in audit.entries(run_id=run.run_id)]
    assert "workflow.started" in events
    assert "workflow.completed" in events


@pytest.mark.asyncio
async def test_dependency_payload_flows_downstream(engine):
    wf_engine, _ = engine

    async def scanner(task, ctx):
        return ["CVE-1", "CVE-2"]

    async def reporter(task, ctx):
        return {"repository": task["repo"], "findings": task["scan"]}

    spec = WorkflowSpec(
        name="security2",
        steps=[
            WorkflowStep(step_id="scan", handler=scanner),
            WorkflowStep(step_id="report", handler=reporter, depends_on=["scan"]),
        ],
    )
    run = await wf_engine.run_workflow(spec, {"repo": "demo"})
    assert run.step_results["report"] == {
        "repository": "demo",
        "findings": ["CVE-1", "CVE-2"],
    }


@pytest.mark.asyncio
async def test_parallel_steps_run_concurrently(engine):
    wf_engine, _ = engine
    started = []

    async def slow_left(task, ctx):
        started.append(time.monotonic())
        await asyncio.sleep(0.1)
        return "left"

    async def slow_right(task, ctx):
        started.append(time.monotonic())
        await asyncio.sleep(0.1)
        return "right"

    spec = WorkflowSpec(
        name="parallel",
        steps=[
            WorkflowStep(step_id="left", handler=slow_left),
            WorkflowStep(step_id="right", handler=slow_right),
        ],
    )

    t0 = time.monotonic()
    run = await wf_engine.run_workflow(spec)
    run_duration = time.monotonic() - t0

    assert run.status == WorkflowStatus.COMPLETED
    # If run serially, two 0.1s steps take ~0.2s. Concurrency keeps it ~0.1s.
    assert run_duration < 0.16
    assert len(started) == 2


@pytest.mark.asyncio
async def test_retry_after_transient_failure(engine):
    wf_engine, _ = engine
    attempts = {"n": 0}

    async def flaky(task, ctx):
        attempts["n"] += 1
        if attempts["n"] < 3:
            raise RuntimeError("transient failure")
        return {"done": True}

    spec = WorkflowSpec(
        name="retry",
        steps=[
            WorkflowStep(
                step_id="flaky",
                handler=flaky,
                retry_policy=RetryPolicy(max_attempts=4, base_delay=0.01),
            )
        ],
    )
    run = await wf_engine.run_workflow(spec)
    assert run.status == WorkflowStatus.COMPLETED
    assert attempts["n"] == 3
    assert run.step_executions["flaky"].attempts == 3


@pytest.mark.asyncio
async def test_failure_after_retries_exhausted_run(engine):
    wf_engine, _ = engine

    async def always_fails(task, ctx):
        raise RuntimeError("permanent")

    spec = WorkflowSpec(
        name="permanent",
        steps=[
            WorkflowStep(
                step_id="x",
                handler=always_fails,
                retry_policy=RetryPolicy(max_attempts=2, base_delay=0.01),
            )
        ],
    )
    run = await wf_engine.run_workflow(spec)
    assert run.status == WorkflowStatus.FAILED
    assert "permanent" in run.error


@pytest.mark.asyncio
async def test_agent_fallback_to_fallback_agent(engine):
    wf_engine, _ = engine

    async def boom(task, ctx):
        raise RuntimeError("primary offline")

    backup_result = {"via": "backup"}

    coordinator = AgentCoordinator()
    coordinator.register_agent("primary", capabilities=["ops"], executor=boom)
    coordinator.register_agent(
        "backup", capabilities=["ops"], executor=make_executor(backup_result)
    )
    wf_engine = WorkflowEngine(coordinator=coordinator)

    spec = WorkflowSpec(
        name="fallback",
        steps=[
            WorkflowStep(
                step_id="deploy",
                agent_id="primary",
                fallback_agent_ids=["backup"],
            )
        ],
    )
    run = await wf_engine.run_workflow(spec)
    assert run.status == WorkflowStatus.COMPLETED
    assert run.step_results["deploy"] == backup_result
    assert coordinator.get_agent("backup").total_tasks == 1


@pytest.mark.asyncio
async def test_capability_auto_dispatch(engine):
    coordinator = AgentCoordinator()
    coordinator.register_agent(
        "scanner", capabilities=["security_scan"], executor=make_executor([1, 2])
    )
    wf_engine = WorkflowEngine(coordinator=coordinator)

    spec = WorkflowSpec(
        name="scan",
        steps=[WorkflowStep(step_id="scan", capabilities=["security_scan"])],
    )
    run = await wf_engine.run_workflow(spec, {"repo": "x"})
    assert run.status == WorkflowStatus.COMPLETED
    assert run.step_results["scan"] == [1, 2]


@pytest.mark.asyncio
async def test_capacity_shortage_falls_back(engine):
    coordinator = AgentCoordinator()

    async def primary(task, ctx):
        await asyncio.sleep(10)
        return {"via": "primary"}

    # Higher-priority agent (checked first) is at full capacity; the engine
    # must route to the spare instead.
    coordinator.register_agent(
        "primary",
        capabilities=["ops"],
        executor=primary,
        max_concurrency=1,
        priority=1,
    )
    coordinator.register_agent(
        "spare", capabilities=["ops"], executor=make_executor({"via": "backup"})
    )
    wf_engine = WorkflowEngine(coordinator=coordinator)
    # Exhaust primary's capacity by holding its single slot.
    await coordinator.acquire("primary")

    spec = WorkflowSpec(
        name="overload",
        steps=[WorkflowStep(step_id="deploy", capabilities=["ops"])],
    )
    run = await wf_engine.run_workflow(spec)
    assert run.status == WorkflowStatus.COMPLETED
    assert run.step_results["deploy"] == {"via": "backup"}
    assert coordinator.get_agent("primary").total_failures >= 0


@pytest.mark.asyncio
async def test_approval_gate_waits_for_human(engine):
    wf_engine, _ = engine

    async def deploy(task, ctx):
        return {"deployed": True}

    spec = WorkflowSpec(
        name="gated_deploy",
        steps=[
            WorkflowStep(
                step_id="deploy",
                handler=deploy,
                require_approval=True,
                approval_summary="Approve production deployment",
            )
        ],
    )
    run = wf_engine.create_run(spec, {"env": "prod"})
    background = asyncio.create_task(wf_engine.execute(run))

    for _ in range(100):
        if wf_engine.approvals.pending_count > 0:
            break
        await asyncio.sleep(0.01)
    assert wf_engine.approvals.pending_count == 1

    pending = wf_engine.approvals.list_pending()[0]
    wf_engine.approvals.approve(pending.approval_id, approved_by="reviewer")

    await background
    assert run.status == WorkflowStatus.COMPLETED
    assert run.step_results["deploy"] == {"deployed": True}


@pytest.mark.asyncio
async def test_approval_rejection_fails_run(engine):
    wf_engine, _ = engine

    async def wipe(task, ctx):
        return {"irreversible": True}

    spec = WorkflowSpec(
        name="reject",
        steps=[
            WorkflowStep(step_id="wipe", handler=wipe, require_approval=True),
        ],
    )
    run = wf_engine.create_run(spec)
    background = asyncio.create_task(wf_engine.execute(run))

    for _ in range(100):
        if wf_engine.approvals.pending_count > 0:
            break
        await asyncio.sleep(0.01)
    pending = wf_engine.approvals.list_pending()[0]
    wf_engine.approvals.reject(pending.approval_id, rejected_by="sre", reason="no")

    await background
    assert run.status == WorkflowStatus.FAILED
    assert "rejected" in run.error


@pytest.mark.asyncio
async def test_step_timeout_fails_run(engine):
    wf_engine, _ = engine

    async def hangs(task, ctx):
        await asyncio.sleep(5)
        return "never"

    spec = WorkflowSpec(
        name="slow",
        steps=[
            WorkflowStep(
                step_id="slow",
                handler=hangs,
                timeout_seconds=0.05,
                retry_policy=RetryPolicy(max_attempts=1),
            )
        ],
    )
    run = await wf_engine.run_workflow(spec)
    assert run.status == WorkflowStatus.FAILED
    assert wf_engine.metrics()["failed"] == 1


@pytest.mark.asyncio
async def test_step_without_executor_fails_cleanly(engine):
    wf_engine, _ = engine
    spec = WorkflowSpec(
        name="empty",
        steps=[WorkflowStep(step_id="orphan", capabilities=["unseen"])],
    )
    run = await wf_engine.run_workflow(spec)
    assert run.status == WorkflowStatus.FAILED
    assert "no executable source" in run.error


def test_engine_definition_helpers(engine):
    wf_engine, _ = engine
    spec = wf_engine.create_workflow(
        name="built", description="via factory", metadata={"team": "core"}
    )
    spec.add_step(WorkflowStep("step_a"))
    spec.add_step(WorkflowStep("step_b"))

    handlers = {
        "step_a": make_executor(1),
        "step_b": make_executor(2),
    }
    wf_engine.attach_handlers(spec, handlers)
    assert spec.step("step_a").handler is not None
    assert spec.step("step_b").handler is not None

    # Binding a handler for a step that does not exist is a no-op.
    wf_engine.attach_handlers(spec, {"ghost_step": make_executor(9)})
    assert spec.step("step_a").handler is not None


def test_run_registry(engine):
    wf_engine, _ = engine
    spec = WorkflowSpec("wf", steps=[WorkflowStep("s", handler=make_executor(1))])
    run = wf_engine.create_run(spec, {"x": 1}, run_id="custom-run")
    assert wf_engine.get_run("custom-run") is run
    assert wf_engine.get_run("nope") is None
    assert "custom-run" in [r.run_id for r in wf_engine.list_runs()]


@pytest.mark.asyncio
async def test_deadlock_detected(engine):
    wf_engine, _ = engine
    spec = WorkflowSpec(
        name="cycle",
        steps=[
            WorkflowStep("a", handler=make_executor(1), depends_on=["b"]),
            WorkflowStep("b", handler=make_executor(2), depends_on=["a"]),
        ],
    )
    run = await wf_engine.run_workflow(spec)
    assert run.status == WorkflowStatus.FAILED
    assert "deadlock" in run.error


@pytest.mark.asyncio
async def test_unknown_agent_reference_fails(engine):
    wf_engine, _ = engine
    spec = WorkflowSpec(
        name="ghost",
        steps=[WorkflowStep("deploy", agent_id="does-not-exist")],
    )
    run = await wf_engine.run_workflow(spec)
    assert run.status == WorkflowStatus.FAILED


@pytest.mark.asyncio
async def test_agent_without_executor_fails(engine):
    coordinator = AgentCoordinator()
    coordinator.register_agent("silent", capabilities=["op"])
    wf_engine = WorkflowEngine(coordinator=coordinator)
    spec = WorkflowSpec(
        name="silent",
        steps=[WorkflowStep("run", capabilities=["op"])],
    )
    run = await wf_engine.run_workflow(spec)
    assert run.status == WorkflowStatus.FAILED


def test_cancel_semantics(engine):
    wf_engine, _ = engine
    assert wf_engine.cancel("unknown") is False
    spec = WorkflowSpec("wf", steps=[])
    run = wf_engine.create_run(spec)
    assert wf_engine.cancel(run.run_id) is False  # pending, not running


@pytest.mark.asyncio
async def test_approval_timeout_fails_run(engine):
    wf_engine, _ = engine

    async def sensitive(task, ctx):
        return {"ok": True}

    spec = WorkflowSpec(
        name="sensitive",
        steps=[
            WorkflowStep(
                step_id="gate",
                handler=sensitive,
                require_approval=True,
                approval_timeout_seconds=0.02,
            )
        ],
    )
    run = await wf_engine.run_workflow(spec)
    assert run.status == WorkflowStatus.FAILED
    assert "rejected" in run.error


@pytest.mark.asyncio
async def test_factory_creates_engine(engine):
    _, audit = engine
    wf_engine = create_workflow_engine(audit=audit)
    spec = WorkflowSpec("f", steps=[WorkflowStep("s", handler=make_executor(1))])
    run = await wf_engine.run_workflow(spec)
    assert run.status == WorkflowStatus.COMPLETED


@pytest.mark.asyncio
async def test_execute_is_idempotent_for_completed_runs(engine):
    wf_engine, _ = engine
    spec = WorkflowSpec("wf", steps=[WorkflowStep("s", handler=make_executor(1))])
    run1 = await wf_engine.run_workflow(spec)
    assert run1.status == WorkflowStatus.COMPLETED
    # Re-executing a finished run short-circuits without re-running steps.
    run2 = await wf_engine.execute(run1)
    assert run2 is run1
    assert run1.step_executions["s"].attempts == 1


@pytest.mark.asyncio
async def test_duplicate_agent_in_fallback_list_is_deduplicated(engine):
    coordinator = AgentCoordinator()
    coordinator.register_agent(
        "primary", capabilities=["ops"], executor=make_executor("ok")
    )
    wf_engine = WorkflowEngine(coordinator=coordinator)
    spec = WorkflowSpec(
        name="dedupe",
        steps=[
            WorkflowStep(
                step_id="deploy",
                agent_id="primary",
                fallback_agent_ids=["primary", "primary"],
            )
        ],
    )
    run = await wf_engine.run_workflow(spec)
    assert run.status == WorkflowStatus.COMPLETED
    assert coordinator.get_agent("primary").total_tasks == 1


@pytest.mark.asyncio
async def test_cancel_while_running(engine):
    wf_engine, _ = engine

    async def slow(task, ctx):
        await asyncio.sleep(0.5)
        return "late"

    spec = WorkflowSpec("slow", steps=[WorkflowStep("s", handler=slow)])
    run = wf_engine.create_run(spec)
    background = asyncio.create_task(wf_engine.execute(run))
    for _ in range(100):
        if run.status == WorkflowStatus.RUNNING:
            break
        await asyncio.sleep(0.01)
    assert wf_engine.cancel(run.run_id) is True
    await background
    # cancellation is a best-effort marker; execution still finishes the step
    assert run.status == WorkflowStatus.COMPLETED


@pytest.mark.asyncio
async def test_fallback_to_capability_agent_without_primary(engine):
    coordinator = AgentCoordinator()
    coordinator.register_agent(
        "scanner", capabilities=["scan"], executor=make_executor({"ok": True})
    )
    wf_engine = WorkflowEngine(coordinator=coordinator)
    spec = WorkflowSpec(
        name="scan-any",
        steps=[WorkflowStep("scan", capabilities=["scan"])],
    )
    run = await wf_engine.run_workflow(spec)
    assert run.status == WorkflowStatus.COMPLETED
    assert run.step_results["scan"] == {"ok": True}
