import asyncio

import pytest

from gpt_computer.core.orchestration.messaging import (
    MessageBus,
    MessageDeliveryError,
    ReplyTimeoutError,
    create_message_bus,
)


@pytest.mark.asyncio
async def test_send_to_agent_inbox():
    bus = MessageBus()
    seen = {}

    async def handler(message):
        seen["received"] = message.payload

    bus.register_agent("agent-1", handler)
    await bus.send("agent-1", "code.review", {"file": "a.py"})
    assert seen["received"] == {"file": "a.py"}


@pytest.mark.asyncio
async def test_send_to_unknown_agent_raises():
    bus = MessageBus()
    with pytest.raises(MessageDeliveryError):
        await bus.send("ghost", "topic", "hello")


@pytest.mark.asyncio
async def test_publish_broadcast_to_topic():
    bus = MessageBus()

    def collector(store):
        def handler(message):
            store.append(message.payload)
            return None

        return handler

    received = []
    bus.subscribe_topic("security", collector(received))
    bus.subscribe_topic("security", collector(received))
    await bus.publish("security", {"alert": "x"})
    assert received == [{"alert": "x"}, {"alert": "x"}]


@pytest.mark.asyncio
async def test_unsubscribe_stops_delivery():
    bus = MessageBus()
    received = []

    def handler(message):
        received.append(message.payload)
        return None

    token = bus.subscribe_topic("topic", handler)
    assert bus.unsubscribe_topic(token) is True
    await bus.publish("topic", "ignored")
    assert received == []


@pytest.mark.asyncio
async def test_request_reply_roundtrip():
    bus = MessageBus()

    async def inbox(message):
        return {"total": 42}

    bus.register_agent("worker", inbox)
    reply = await bus.request("worker", "compute.sum", {"a": 2, "b": 40})
    assert reply.payload == {"total": 42}
    assert reply.correlation_id  # correlated back to the requestor


@pytest.mark.asyncio
async def test_request_reply_timeout():
    bus = MessageBus()

    async def silent_inbox(message):
        return None

    bus.register_agent("worker", silent_inbox)
    with pytest.raises(ReplyTimeoutError):
        await bus.request("worker", "slow.op", None, timeout=0.05)


@pytest.mark.asyncio
async def test_explicit_reply_matches_correlation():
    bus = MessageBus()

    async def inbox(message):
        if message.message_type == "request":
            await asyncio.sleep(0.01)
            bus.reply_to(message, {"done": True})

    bus.register_agent("service", inbox)
    reply = await bus.request("service", "work.execute", {"job": 1})
    assert reply.payload == {"done": True}


@pytest.mark.asyncio
async def test_history_records_messages():
    bus = create_message_bus()
    bus.register_agent("agent-1", lambda m: None)
    await bus.send("agent-1", "subject", 1)
    await bus.publish("subject", 2)
    assert len(bus.history()) >= 2
    assert len(bus.history(topic="subject")) >= 1


def test_register_agent_rejects_non_callable():
    bus = MessageBus()
    with pytest.raises(ValueError):
        bus.register_agent("a", "not-callable")


def test_unregister_agent_returns_whether_removed():
    bus = MessageBus()
    assert bus.unregister_agent("ghost") is False
    bus.register_agent("agent-1", lambda m: None)
    assert bus.unregister_agent("agent-1") is True
    assert bus.unregister_agent("agent-1") is False


def test_unsubscribe_unknown_topic_returns_false():
    bus = MessageBus()
    assert bus.unsubscribe_topic("nope::sub") is False


def test_unsubscribe_with_wrong_subscription_id_returns_false():
    bus = MessageBus()
    token = bus.subscribe_topic("topic", lambda m: None)
    topic, _, _ = token.rpartition("::")
    assert bus.unsubscribe_topic(f"{topic}::bogus") is False


@pytest.mark.asyncio
async def test_send_records_auto_reply_without_pending_future():
    bus = MessageBus()

    async def echo(message):
        return message.payload * 2

    bus.register_agent("echo", echo)
    await bus.send("echo", "math", 21)
    # The reply is recorded even though no request() future is pending.
    assert len([m for m in bus.history() if m.message_type == "reply"]) == 1


@pytest.mark.asyncio
async def test_publish_without_subscribers_counts_zero():
    bus = MessageBus()
    assert await bus.publish("empty", {"x": 1}, ensure_delivery=False) == 0
    assert bus.history() == []  # nothing recorded when nothing delivered


@pytest.mark.asyncio
async def test_history_limit_caps_entries():
    bus = MessageBus()
    bus.register_agent("agent-1", lambda m: None)
    for idx in range(5):
        await bus.send("agent-1", "subject", idx)
    limited = bus.history(limit=2)
    assert len(limited) == 2
    assert [m.payload for m in limited] == [3, 4]


@pytest.mark.asyncio
async def test_bus_records_audit_trail_when_provided():
    from gpt_computer.core.orchestration.models import AuditTrail

    audit = AuditTrail()
    bus = create_message_bus(audit=audit)
    bus.register_agent("agent-1", lambda m: None)
    await bus.send("agent-1", "subject", 1)
    events = [e.event for e in audit.entries()]
    assert any(e.startswith("bus.") for e in events)
