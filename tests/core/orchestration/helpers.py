from typing import Any, Dict, List


def make_executor(value: Any):
    """Build an async executor that returns a fixed value."""

    async def executor(task: Dict[str, Any], context: Dict[str, Any]):
        return value

    return executor


def make_recording_executor(events: List[Dict[str, Any]], label: str):
    """Build an async executor that records invocation metadata."""

    async def executor(task: Dict[str, Any], context: Dict[str, Any]):
        events.append({"label": label, "task": dict(task)})
        return label

    return executor
