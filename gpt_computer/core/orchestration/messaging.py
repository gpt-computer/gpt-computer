"""
Inter-agent Communication Bus

In-memory, async message routing primitives that let agents coordinate with
each other: direct send, topic-based publish/subscribe, and request/reply with
correlation tracking and configurable timeouts. All traffic is recorded for
auditability.

Classes:
    ReplyTimeoutError: Raised when a request/reply round-trip times out.
    MessageDeliveryError: Raised when a message cannot be routed.
    MessageBus: The routing + audit core.

Functions:
    create_message_bus(audit=None) -> MessageBus
"""

from __future__ import annotations

import asyncio
import inspect
import logging

from collections import deque
from typing import Any, Callable, Deque, Dict, List, Optional

from gpt_computer.core.orchestration.models import AgentMessage, AuditTrail, new_id

MessageHandler = Callable[..., Any]
SubscriptionToken = str


class ReplyTimeoutError(Exception):
    """Raised when a request() does not receive a reply in time."""


class MessageDeliveryError(Exception):
    """Raised when a message cannot be routed to a recipient."""


class MessageBus:
    """
    Asynchronous message conduit between agents.

    Agents register a private inbox (``register_agent``) or subscribe to
    topics (``subscribe``). Messages carry correlation/reply metadata so a full
    conversation can be traced back and audited.
    """

    def __init__(
        self,
        audit: Optional[AuditTrail] = None,
        history_limit: int = 2000,
    ):
        self.logger = logging.getLogger("orchestration.messaging")
        self.audit = audit
        self._history: Deque[AgentMessage] = deque(maxlen=history_limit)
        self._agent_inboxes: Dict[str, MessageHandler] = {}
        self._topic_handlers: Dict[str, Dict[str, MessageHandler]] = {}
        self._reply_futures: Dict[str, asyncio.Future] = {}

    # ------------------------------------------------------------------ #
    # Registration
    # ------------------------------------------------------------------ #
    def register_agent(self, agent_id: str, handler: MessageHandler) -> None:
        """Register a private inbox handler for ``agent_id``."""
        if not callable(handler):
            raise ValueError("Inbox handler must be callable")
        self._agent_inboxes[agent_id] = handler

    def unregister_agent(self, agent_id: str) -> bool:
        """Remove a direct inbox. Returns True if one existed."""
        return self._agent_inboxes.pop(agent_id, None) is not None

    def subscribe_topic(self, topic: str, handler: MessageHandler) -> str:
        """Subscribe ``handler`` to topic ``topic``. Returns a token."""
        sub_id = new_id("sub")
        self._topic_handlers.setdefault(topic, {})[sub_id] = handler
        return f"{topic}::{sub_id}"

    def unsubscribe_topic(self, token: str) -> bool:
        """Remove a subscription created by :meth:`subscribe_topic`."""
        topic, _, sub_id = token.rpartition("::")
        handlers = self._topic_handlers.get(topic)
        if not handlers:
            return False
        removed = handlers.pop(sub_id, None) is not None
        if not handlers:
            self._topic_handlers.pop(topic, None)
        return removed

    # ------------------------------------------------------------------ #
    # Routing
    # ------------------------------------------------------------------ #
    async def send(
        self,
        agent_id: str,
        subject: str,
        payload: Any = None,
        *,
        sender: str = "unknown",
        reply_to: str = "",
        correlation_id: str = "",
        message_type: str = "event",
    ) -> Optional[AgentMessage]:
        """
        Deliver a message to the private inbox of ``agent_id``.

        If the inbox handler returns a value, a correlated reply is prepared.
        """
        handler = self._agent_inboxes.get(agent_id)
        if handler is None:
            raise MessageDeliveryError(f"No inbox registered for agent '{agent_id}'")

        message = self._new_message(
            sender=sender,
            recipient=agent_id,
            subject=subject,
            payload=payload,
            reply_to=reply_to,
            correlation_id=correlation_id,
            message_type=message_type,
        )
        result = await self._invoke_handler(handler, message)
        self._record(message)
        if result is not None:
            reply = self._new_reply(message, result)
            self._on_reply(reply)
        return message

    async def publish(
        self,
        topic: str,
        payload: Any = None,
        *,
        sender: str = "unknown",
        ensure_delivery: bool = True,
    ) -> int:
        """
        Broadcast a message to all handlers subscribed to ``topic``.

        Returns the number of handlers that received it. With
        ``ensure_delivery=True`` (default) the message is also placed in the
        history and audit trail even if no handler is attached.
        """
        message = self._new_message(
            sender=sender,
            recipient=topic,
            subject=topic,
            payload=payload,
            message_type="event",
        )
        handlers = list(self._topic_handlers.get(topic, {}).values())
        delivered = 0
        for handler in handlers:
            try:
                await self._invoke_handler(handler, message)
                delivered += 1
            except Exception as exc:  # pragma: no cover - defensive audit
                self.logger.error(
                    "Handler failed for topic %s: %s", topic, exc, exc_info=True
                )
        if ensure_delivery or delivered:
            self._record(message)
        return delivered

    async def request(
        self,
        agent_id: str,
        subject: str,
        payload: Any = None,
        *,
        sender: str = "system",
        timeout: float = 10.0,
    ) -> AgentMessage:
        """
        Send a request to an agent inbox and wait for the correlated reply.

        The inbox handler replies automatically when it returns a value, or a
        reply can be prepared explicitly with :meth:`reply_to`.

        Raises:
            ReplyTimeoutError: if no reply arrives within ``timeout`` seconds.
        """
        loop = asyncio.get_running_loop()
        correlation = new_id("req")
        future: asyncio.Future = loop.create_future()
        self._reply_futures[correlation] = future
        try:
            await self.send(
                agent_id,
                subject,
                payload,
                sender=sender,
                correlation_id=correlation,
                message_type="request",
            )
            return await asyncio.wait_for(future, timeout=timeout)
        except asyncio.TimeoutError as exc:
            raise ReplyTimeoutError(
                f"No reply from agent '{agent_id}' on '{subject}' " f"within {timeout}s"
            ) from exc
        finally:
            self._reply_futures.pop(correlation, None)

    def reply_to(self, message: AgentMessage, payload: Any) -> None:
        """Prepare a correlated reply to ``message`` without routing."""
        reply = self._new_reply(message, payload)
        self._on_reply(reply)

    def _new_message(
        self,
        *,
        sender: str,
        recipient: str,
        subject: str,
        payload: Any,
        reply_to: str = "",
        correlation_id: str = "",
        message_type: str = "event",
    ) -> AgentMessage:
        return AgentMessage(
            sender=sender if sender else "unknown",
            recipient=recipient,
            subject=subject,
            payload=payload,
            reply_to=reply_to,
            correlation_id=correlation_id,
            message_type=message_type,
        )

    def _new_reply(self, trigger: AgentMessage, payload: Any) -> AgentMessage:
        return AgentMessage(
            sender=trigger.recipient,
            recipient=trigger.sender,
            subject=trigger.subject,
            payload=payload,
            reply_to=trigger.reply_to,
            correlation_id=trigger.correlation_id,
            message_type="reply",
        )

    def _on_reply(self, message: AgentMessage) -> None:
        """Record and optionally complete a pending request future."""
        self._record(message)
        future = self._reply_futures.get(message.correlation_id)
        if future is not None and not future.done():
            future.set_result(message)

    async def _invoke_handler(
        self, handler: MessageHandler, message: AgentMessage
    ) -> Any:
        """Await a handler regardless of whether it is coroutine-based."""
        result = handler(message)
        if inspect.isawaitable(result):
            result = await result
        return result

    def _record(self, message: AgentMessage) -> None:
        self._history.append(message)
        if self.audit:
            self.audit.record(
                f"bus.{message.message_type}",
                actor=message.sender,
                resource=message.subject,
                message=message.subject,
                detail={
                    "message_id": message.message_id,
                    "recipient": message.recipient,
                    "correlation_id": message.correlation_id,
                },
            )

    def history(
        self, *, topic: Optional[str] = None, limit: Optional[int] = None
    ) -> List[AgentMessage]:
        """Return recorded messages, optionally filtered by topic."""
        entries = [m for m in self._history if topic is None or m.subject == topic]
        if limit is not None:
            entries = entries[-limit:]
        return list(entries)


def create_message_bus(audit: Optional[AuditTrail] = None) -> MessageBus:
    """Factory for an empty :class:`MessageBus`."""
    return MessageBus(audit=audit)
