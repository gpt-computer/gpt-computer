from gpt_computer.core.orchestration.models import (
    AgentHandle,
    AgentMessage,
    AgentStatus,
    AuditEvent,
    AuditTrail,
    RetryPolicy,
    StepExecution,
    StepStatus,
    WorkflowSpec,
    WorkflowStatus,
    WorkflowStep,
)


def test_retry_policy_delay_is_capped():
    policy = RetryPolicy(base_delay=1.0, backoff_factor=2.0, max_delay=3.0)
    assert policy.delay_for(0) == 1.0
    assert policy.delay_for(1) == 2.0
    assert policy.delay_for(10) == 3.0  # capped
    assert policy.delay_for(2) == 3.0


def test_agent_handle_availability_properties():
    handle = AgentHandle(agent_id="a", name="a", capabilities=["x"], max_concurrency=2)
    assert handle.available
    assert handle.accepting_new_work
    handle.active_tasks = 2
    assert not handle.available
    assert not handle.accepting_new_work

    draining = AgentHandle(agent_id="d", name="d", max_concurrency=1)
    draining.status = AgentStatus.DRAINING
    assert draining.available  # draining still accepts in-flight work
    assert not draining.accepting_new_work


def test_agent_handle_as_dict():
    handle = AgentHandle(
        agent_id="a",
        name="A",
        capabilities=["scan"],
        tags={"region": "us"},
        active_tasks=1,
    )
    data = handle.as_dict()
    assert data["agent_id"] == "a"
    assert data["active_tasks"] == 1
    assert data["tags"] == {"region": "us"}


def test_workflow_step_helpers():
    step = WorkflowStep(step_id="s1", capabilities=["x"], inputs={"a": 1})
    assert step.needs_executor is True
    step.as_dict()["step_id"] == "s1"
    data = step.as_dict()
    assert data["capabilities"] == ["x"]
    assert data["inputs"] == {"a": 1}


def test_workflow_spec_helpers():
    spec = WorkflowSpec(name="wf")
    spec.add_step(WorkflowStep("one"))
    spec.add_step(WorkflowStep("two"))
    assert spec.step("one") is not None
    assert spec.step("missing") is None
    assert spec.step_ids == ["one", "two"]
    data = spec.as_dict()
    assert data["name"] == "wf"
    assert len(data["steps"]) == 2


def test_workflow_run_state_properties():
    spec = WorkflowSpec(name="wf", steps=[WorkflowStep("s1"), WorkflowStep("s2")])
    from gpt_computer.core.orchestration.models import WorkflowRun

    run = WorkflowRun(workflow=spec, inputs={"x": 1})
    assert not run.completed
    assert not run.failed
    assert run.unresolved_steps == ["s1", "s2"]

    run.step_executions["s1"] = StepExecution(step_id="s1", status=StepStatus.SUCCEEDED)
    run.status = WorkflowStatus.COMPLETED
    assert run.completed
    assert not run.failed
    assert run.unresolved_steps == ["s2"]

    serialized = run.as_dict()
    assert serialized["status"] == "completed"
    assert serialized["inputs"] == {"x": 1}
    assert "s1" in serialized["step_executions"]


def test_workflow_run_serialization():
    from gpt_computer.core.orchestration.models import WorkflowRun

    run = WorkflowRun(workflow=WorkflowSpec("wf"))
    run.status = WorkflowStatus.FAILED
    run.error = "boom"
    data = run.as_dict()
    assert data["status"] == "failed"
    assert data["error"] == "boom"


def test_audit_event_as_dict():
    event = AuditEvent(event="go", actor="agent", resource="r", run_id="run1")
    data = event.as_dict()
    assert data["event"] == "go"
    assert data["run_id"] == "run1"
    assert data["detail"] == {}


def test_audit_trail_prunes_to_max_entries():
    trail = AuditTrail(max_entries=3)
    for idx in range(5):
        trail.record(f"event_{idx}")
    assert len(trail.entries()) == 3
    assert trail.entries()[0].event == "event_2"


def test_audit_trail_serialization_and_filtering():
    trail = AuditTrail()
    trail.record("a", run_id="one")
    trail.record("b", run_id="two")
    assert len(trail.entries(run_id="one")) == 1
    assert len(trail.to_dict()) == 2
    trail.clear()
    assert len(trail.entries()) == 0


def test_agent_message_as_dict():
    message = AgentMessage(sender="a", recipient="b", subject="s", payload={"k": "v"})
    data = message.as_dict()
    assert data["sender"] == "a"
    assert data["subject"] == "s"
    assert data["payload"] == {"k": "v"}
