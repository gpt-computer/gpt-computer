"""
AsyncAI Module - Enhanced AI Interface with Structured Logging

This module provides an enhanced AsyncAI class that extends the base AI functionality
with structured logging, performance monitoring, correlation tracking, and improved
async capabilities.

Classes:
    AsyncAI: Enhanced AI class with structured logging and monitoring
    AIRequest: Request context for AI operations
    AIResponse: Response wrapper with metadata

Functions:
    create_async_ai(**kwargs) -> AsyncAI
        Factory function to create AsyncAI instances.
"""

from __future__ import annotations

import asyncio
import time
import uuid

from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from gpt_computer.core.ai import AI, Message
from gpt_computer.core.structured_logging import (
    CorrelationContext,
    get_logger,
    log_performance,
)


@dataclass
class AIRequest:
    """
    Request context for AI operations with metadata.
    """

    messages: List[Message]
    model_name: str
    temperature: float
    correlation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AIResponse:
    """
    Response wrapper with metadata and performance metrics.
    """

    messages: List[Message]
    request_id: str
    correlation_id: str
    response_time_ms: float
    tokens_used: Optional[int] = None
    success: bool = True
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class AsyncAI(AI):
    """
    Enhanced AI class with structured logging, performance monitoring,
    and correlation tracking for better observability.
    """

    def __init__(self, **kwargs):
        """Initialize AsyncAI with enhanced logging capabilities."""
        super().__init__(**kwargs)
        self.logger = get_logger(f"AsyncAI.{self.model_name}")
        self._request_count = 0
        self._total_tokens = 0
        self._total_response_time = 0.0

    @asynccontextmanager
    async def _request_context(self, operation: str):
        """Context manager for request tracking with correlation ID."""
        correlation_id = str(uuid.uuid4())
        token = CorrelationContext.set_correlation_id(correlation_id)

        try:
            self.logger.info(
                f"Starting {operation}",
                operation=operation,
                model=self.model_name,
                correlation_id=correlation_id,
            )
            yield correlation_id
        except Exception as e:
            self.logger.log_error_with_context(
                e,
                {"operation": operation, "model": self.model_name},
                correlation_id=correlation_id,
            )
            raise
        finally:
            CorrelationContext.reset(token)

    @log_performance(get_logger("AsyncAI"), "start_conversation")
    async def start(self, system: str, user: Any, *, step_name: str) -> List[Message]:
        """
        Start conversation with enhanced logging and correlation tracking.

        Args:
            system: System message content
            user: User message content
            step_name: Name of the step for tracking

        Returns:
            List of messages in the conversation
        """
        async with self._request_context("start_conversation") as correlation_id:
            self.logger.info(
                "Starting conversation",
                step_name=step_name,
                system_length=len(str(system)),
                user_length=len(str(user)),
                correlation_id=correlation_id,
            )

            start_time = time.time()
            try:
                messages = await super().start(system, user, step_name=step_name)
                response_time = (time.time() - start_time) * 1000

                self.logger.log_api_call(
                    model=self.model_name,
                    tokens_used=self._estimate_tokens(messages),
                    response_time=response_time / 1000,
                    operation="start",
                    step_name=step_name,
                    correlation_id=correlation_id,
                )

                return messages

            except Exception as e:
                response_time = (time.time() - start_time) * 1000
                self.logger.error(
                    "Conversation start failed",
                    operation="start",
                    step_name=step_name,
                    response_time_ms=response_time,
                    error=str(e),
                    correlation_id=correlation_id,
                )
                raise

    @log_performance(get_logger("AsyncAI"), "advance_conversation")
    async def next(
        self,
        messages: List[Message],
        prompt: Optional[str] = None,
        *,
        step_name: str,
    ) -> List[Message]:
        """
        Advance conversation with enhanced logging and performance monitoring.

        Args:
            messages: Current message history
            prompt: Optional additional prompt
            step_name: Name of the step for tracking

        Returns:
            Updated list of messages
        """
        async with self._request_context("advance_conversation") as correlation_id:
            self.logger.info(
                "Advancing conversation",
                step_name=step_name,
                message_count=len(messages),
                has_prompt=prompt is not None,
                correlation_id=correlation_id,
            )

            start_time = time.time()
            try:
                result_messages = await super().next(
                    messages, prompt, step_name=step_name
                )
                response_time = (time.time() - start_time) * 1000

                # Log performance metrics
                tokens_used = self._estimate_tokens(result_messages)
                self._update_metrics(tokens_used, response_time / 1000)

                self.logger.log_api_call(
                    model=self.model_name,
                    tokens_used=tokens_used,
                    response_time=response_time / 1000,
                    operation="next",
                    step_name=step_name,
                    message_count=len(result_messages),
                    correlation_id=correlation_id,
                )

                return result_messages

            except Exception as e:
                response_time = (time.time() - start_time) * 1000
                self.logger.error(
                    "Conversation advance failed",
                    operation="next",
                    step_name=step_name,
                    response_time_ms=response_time,
                    error=str(e),
                    correlation_id=correlation_id,
                )
                raise

    async def start_with_context(
        self, system: str, user: Any, *, step_name: str, **metadata
    ) -> AIResponse:
        """
        Start conversation with full response context.

        Args:
            system: System message content
            user: User message content
            step_name: Name of the step for tracking
            **metadata: Additional metadata to include

        Returns:
            AIResponse with full context and metrics
        """
        async with self._request_context("start_with_context") as correlation_id:
            start_time = time.time()

            try:
                messages = await self.start(system, user, step_name=step_name)
                response_time = (time.time() - start_time) * 1000

                return AIResponse(
                    messages=messages,
                    request_id=str(uuid.uuid4()),
                    correlation_id=correlation_id,
                    response_time_ms=response_time,
                    tokens_used=self._estimate_tokens(messages),
                    success=True,
                    metadata=metadata,
                )

            except Exception as e:
                response_time = (time.time() - start_time) * 1000
                return AIResponse(
                    messages=[],
                    request_id=str(uuid.uuid4()),
                    correlation_id=correlation_id,
                    response_time_ms=response_time,
                    success=False,
                    error=str(e),
                    metadata=metadata,
                )

    async def next_with_context(
        self,
        messages: List[Message],
        prompt: Optional[str] = None,
        *,
        step_name: str,
        **metadata,
    ) -> AIResponse:
        """
        Advance conversation with full response context.

        Args:
            messages: Current message history
            prompt: Optional additional prompt
            step_name: Name of the step for tracking
            **metadata: Additional metadata to include

        Returns:
            AIResponse with full context and metrics
        """
        async with self._request_context("next_with_context") as correlation_id:
            start_time = time.time()

            try:
                result_messages = await self.next(messages, prompt, step_name=step_name)
                response_time = (time.time() - start_time) * 1000

                return AIResponse(
                    messages=result_messages,
                    request_id=str(uuid.uuid4()),
                    correlation_id=correlation_id,
                    response_time_ms=response_time,
                    tokens_used=self._estimate_tokens(result_messages),
                    success=True,
                    metadata=metadata,
                )

            except Exception as e:
                response_time = (time.time() - start_time) * 1000
                return AIResponse(
                    messages=messages,
                    request_id=str(uuid.uuid4()),
                    correlation_id=correlation_id,
                    response_time_ms=response_time,
                    success=False,
                    error=str(e),
                    metadata=metadata,
                )

    async def batch_process(
        self, requests: List[Dict[str, Any]], max_concurrency: int = 5
    ) -> List[AIResponse]:
        """
        Process multiple requests concurrently with controlled concurrency.

        Args:
            requests: List of request dictionaries
            max_concurrency: Maximum concurrent requests

        Returns:
            List of AIResponse objects
        """
        semaphore = asyncio.Semaphore(max_concurrency)

        async def process_single_request(request_data):
            async with semaphore:
                return await self.next_with_context(**request_data)

        self.logger.info(
            "Starting batch processing",
            request_count=len(requests),
            max_concurrency=max_concurrency,
        )

        start_time = time.time()
        responses = await asyncio.gather(
            *[process_single_request(req) for req in requests], return_exceptions=True
        )
        total_time = time.time() - start_time

        # Convert exceptions to error responses
        processed_responses = []
        for i, response in enumerate(responses):
            if isinstance(response, Exception):
                processed_responses.append(
                    AIResponse(
                        messages=[],
                        request_id=str(uuid.uuid4()),
                        correlation_id=str(uuid.uuid4()),
                        response_time_ms=0,
                        success=False,
                        error=str(response),
                    )
                )
            else:
                processed_responses.append(response)

        self.logger.info(
            "Batch processing completed",
            total_requests=len(requests),
            successful=sum(1 for r in processed_responses if r.success),
            failed=sum(1 for r in processed_responses if not r.success),
            total_time_ms=total_time * 1000,
        )

        return processed_responses

    def get_metrics(self) -> Dict[str, Any]:
        """
        Get performance metrics for this AI instance.

        Returns:
            Dictionary with performance metrics
        """
        avg_response_time = (
            self._total_response_time / self._request_count
            if self._request_count > 0
            else 0
        )

        return {
            "model_name": self.model_name,
            "total_requests": self._request_count,
            "total_tokens": self._total_tokens,
            "average_response_time_ms": avg_response_time * 1000,
            "average_tokens_per_request": (
                self._total_tokens / self._request_count
                if self._request_count > 0
                else 0
            ),
        }

    def _estimate_tokens(self, messages: List[Message]) -> int:
        """
        Estimate token count for messages (rough approximation).

        Args:
            messages: List of messages to estimate tokens for

        Returns:
            Estimated token count
        """
        total_chars = 0
        for message in messages:
            content = str(message.content)
            total_chars += len(content)

        # Rough approximation: ~4 characters per token
        return total_chars // 4

    def _update_metrics(self, tokens_used: int, response_time: float) -> None:
        """
        Update internal performance metrics.

        Args:
            tokens_used: Number of tokens used in request
            response_time: Response time in seconds
        """
        self._request_count += 1
        self._total_tokens += tokens_used
        self._total_response_time += response_time


def create_async_ai(**kwargs) -> AsyncAI:
    """
    Factory function to create AsyncAI instances.

    Args:
        **kwargs: Arguments to pass to AsyncAI constructor

    Returns:
        AsyncAI instance
    """
    return AsyncAI(**kwargs)
