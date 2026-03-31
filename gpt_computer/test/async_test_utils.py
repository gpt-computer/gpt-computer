"""
Async Testing Infrastructure

This module provides testing utilities for async components in the gpt-computer project.
It includes fixtures, test utilities, and performance testing capabilities.

Classes:
    AsyncTestCase: Base class for async test cases
    PerformanceMonitor: Monitor and assert performance metrics
    MockAI: Mock AI implementation for testing

Functions:
    async_test(func)
        Decorator for async test functions
    create_mock_ai(**kwargs) -> MockAI
        Create a mock AI instance for testing
"""

from __future__ import annotations

import asyncio
import time

from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator, Dict, List, Optional, TypeVar

import pytest

from gpt_computer.core.ai import AI, Message
from gpt_computer.core.base_agent import BaseAgent
from gpt_computer.core.files_dict import FilesDict
from gpt_computer.core.prompt import Prompt

# Import structured logging and tracing if available
try:
    from gpt_computer.core.structured_logging import get_logger
    from gpt_computer.core.tracing import setup_tracing

    STRUCTURED_LOGGING_AVAILABLE = True
    TRACING_AVAILABLE = True
except ImportError:
    STRUCTURED_LOGGING_AVAILABLE = False
    TRACING_AVAILABLE = False

T = TypeVar("T")


class PerformanceMonitor:
    """
    Monitor and assert performance metrics for async operations.
    """

    def __init__(self):
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
        self.checkpoints: List[Dict[str, Any]] = []

        if STRUCTURED_LOGGING_AVAILABLE:
            self.logger = get_logger("PerformanceMonitor")
        else:
            self.logger = None

    def start(self) -> None:
        """Start performance monitoring."""
        self.start_time = time.time()
        self.checkpoints = []

        if self.logger:
            self.logger.info("Performance monitoring started")

    def checkpoint(self, name: str) -> None:
        """Add a performance checkpoint."""
        if self.start_time is None:
            raise RuntimeError("Performance monitoring not started")

        checkpoint_time = time.time()
        elapsed = checkpoint_time - self.start_time

        self.checkpoints.append(
            {"name": name, "timestamp": checkpoint_time, "elapsed_ms": elapsed * 1000}
        )

        if self.logger:
            self.logger.info(
                "Performance checkpoint", checkpoint=name, elapsed_ms=elapsed * 1000
            )

    def stop(self) -> float:
        """Stop performance monitoring and return total duration."""
        if self.start_time is None:
            raise RuntimeError("Performance monitoring not started")

        self.end_time = time.time()
        total_duration = self.end_time - self.start_time

        if self.logger:
            self.logger.info(
                "Performance monitoring completed",
                total_duration_ms=total_duration * 1000,
                checkpoints_count=len(self.checkpoints),
            )

        return total_duration

    def assert_duration_between(self, min_ms: float, max_ms: float) -> None:
        """Assert total duration is within expected range."""
        if self.end_time is None:
            raise RuntimeError("Performance monitoring not stopped")

        duration_ms = (self.end_time - self.start_time) * 1000

        assert min_ms <= duration_ms <= max_ms, (
            f"Duration {duration_ms:.2f}ms not within expected range "
            f"[{min_ms:.2f}ms, {max_ms:.2f}ms]"
        )

    def assert_checkpoint_between(
        self, name: str, min_ms: float, max_ms: float
    ) -> None:
        """Assert a specific checkpoint duration is within expected range."""
        for i, checkpoint in enumerate(self.checkpoints):
            if checkpoint["name"] == name:
                elapsed_ms = checkpoint["elapsed_ms"]
                assert min_ms <= elapsed_ms <= max_ms, (
                    f"Checkpoint '{name}' duration {elapsed_ms:.2f}ms not within "
                    f"expected range [{min_ms:.2f}ms, {max_ms:.2f}ms]"
                )
                return

        raise AssertionError(f"Checkpoint '{name}' not found")


class MockAI(AI):
    """
    Mock AI implementation for testing async operations.
    """

    def __init__(self, response_delay: float = 0.1, **kwargs):
        """Initialize mock AI with configurable response delay."""
        # Don't call super().__init__ to avoid actual LLM initialization
        self.model_name = kwargs.get("model_name", "mock-model")
        self.temperature = kwargs.get("temperature", 0.1)
        self.response_delay = response_delay
        self.responses: List[str] = []
        self.call_count = 0
        self.last_messages: Optional[List[Message]] = None

        if STRUCTURED_LOGGING_AVAILABLE:
            self.structured_logger = get_logger(f"MockAI.{self.model_name}")
        else:
            self.structured_logger = None

    def set_responses(self, responses: List[str]) -> None:
        """Set predefined responses for the mock AI."""
        self.responses = responses.copy()
        self.call_count = 0

    async def start(self, system: str, user: Any, *, step_name: str) -> List[Message]:
        """Mock start method with configurable delay."""
        await asyncio.sleep(self.response_delay)

        if self.structured_logger:
            self.structured_logger.info(
                "Mock AI start called",
                step_name=step_name,
                system_length=len(str(system)),
                user_length=len(str(user)),
            )

        response = self._get_next_response()

        from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

        messages = [
            SystemMessage(content=system),
            HumanMessage(content=user),
            AIMessage(content=response),
        ]

        self.last_messages = messages
        return messages

    async def next(
        self,
        messages: List[Message],
        prompt: Optional[str] = None,
        *,
        step_name: str,
    ) -> List[Message]:
        """Mock next method with configurable delay."""
        await asyncio.sleep(self.response_delay)

        if self.structured_logger:
            self.structured_logger.info(
                "Mock AI next called",
                step_name=step_name,
                message_count=len(messages),
                has_prompt=prompt is not None,
            )

        response = self._get_next_response()

        from langchain_core.messages import AIMessage

        new_messages = messages.copy()
        if prompt:
            from langchain_core.messages import HumanMessage

            new_messages.append(HumanMessage(content=prompt))

        new_messages.append(AIMessage(content=response))
        self.last_messages = new_messages

        return new_messages

    def _get_next_response(self) -> str:
        """Get the next response from the predefined list."""
        if not self.responses:
            return f"Mock response #{self.call_count + 1}"

        if self.call_count < len(self.responses):
            response = self.responses[self.call_count]
        else:
            response = self.responses[-1]  # Repeat last response

        self.call_count += 1
        return response


class AsyncTestCase:
    """
    Base class for async test cases with common utilities.
    """

    @pytest.fixture(autouse=True)
    async def setup_async_test(self):
        """Setup async test environment."""
        # Setup tracing if available
        if TRACING_AVAILABLE:
            setup_tracing(
                service_name="gpt-computer-test",
                jaeger_endpoint=None,  # Don't use real Jaeger in tests
                otlp_endpoint=None,  # Don't use real OTLP in tests
                sample_rate=1.0,
            )

        yield

        # Cleanup if needed
        if TRACING_AVAILABLE:
            from gpt_computer.core.tracing import get_tracing_manager

            manager = get_tracing_manager()
            manager.shutdown()

    @asynccontextmanager
    async def assert_performance(
        self, min_ms: float = 0, max_ms: float = 1000
    ) -> AsyncGenerator[PerformanceMonitor, None]:
        """Context manager for performance assertions."""
        monitor = PerformanceMonitor()
        monitor.start()

        try:
            yield monitor
        finally:
            monitor.stop()
            if min_ms > 0 or max_ms < float("inf"):
                monitor.assert_duration_between(min_ms, max_ms)

    def create_mock_ai(
        self, response_delay: float = 0.01, responses: Optional[List[str]] = None
    ) -> MockAI:
        """Create a mock AI instance for testing."""
        ai = MockAI(response_delay=response_delay)
        if responses:
            ai.set_responses(responses)
        return ai

    async def assert_async_call_succeeds(self, coro, timeout: float = 5.0) -> Any:
        """Assert that an async call succeeds within timeout."""
        try:
            result = await asyncio.wait_for(coro, timeout=timeout)
            return result
        except asyncio.TimeoutError:
            raise AssertionError(f"Async call timed out after {timeout} seconds")
        except Exception as e:
            raise AssertionError(f"Async call failed with exception: {e}")

    async def assert_async_call_fails(
        self, coro, timeout: float = 5.0, expected_exception: type = Exception
    ) -> Exception:
        """Assert that an async call fails with expected exception."""
        try:
            await asyncio.wait_for(coro, timeout=timeout)
            raise AssertionError("Expected async call to fail, but it succeeded")
        except asyncio.TimeoutError:
            raise AssertionError(
                f"Async call timed out after {timeout} seconds before failing"
            )
        except Exception as e:
            if not isinstance(e, expected_exception):
                raise AssertionError(
                    f"Expected exception {expected_exception}, got {type(e)}"
                )
            return e


def async_test(timeout: float = 5.0):
    """
    Decorator for async test functions with timeout.

    Args:
        timeout: Maximum time to wait for the test to complete

    Returns:
        Decorated test function
    """

    def decorator(func):
        async def wrapper(*args, **kwargs):
            try:
                result = await asyncio.wait_for(func(*args, **kwargs), timeout=timeout)
                return result
            except asyncio.TimeoutError:
                raise AssertionError(f"Test timed out after {timeout} seconds")

        return wrapper

    return decorator


class MockAgent(BaseAgent):
    """
    Mock agent implementation for testing.
    """

    def __init__(self, init_delay: float = 0.1, improve_delay: float = 0.1):
        self.init_delay = init_delay
        self.improve_delay = improve_delay
        self.init_call_count = 0
        self.improve_call_count = 0

        if STRUCTURED_LOGGING_AVAILABLE:
            self.structured_logger = get_logger("MockAgent")
        else:
            self.structured_logger = None

    async def init(self, prompt: Prompt) -> FilesDict:
        """Mock init method with configurable delay."""
        await asyncio.sleep(self.init_delay)
        self.init_call_count += 1

        if self.structured_logger:
            self.structured_logger.info(
                "Mock agent init called",
                call_count=self.init_call_count,
                prompt_length=len(str(prompt)),
            )

        return FilesDict({"test_file.py": "# Mock generated code\n"})

    async def improve(self, files_dict: FilesDict, prompt: Prompt) -> FilesDict:
        """Mock improve method with configurable delay."""
        await asyncio.sleep(self.improve_delay)
        self.improve_call_count += 1

        if self.structured_logger:
            self.structured_logger.info(
                "Mock agent improve called",
                call_count=self.improve_call_count,
                files_count=len(files_dict),
                prompt_length=len(str(prompt)),
            )

        # Add a comment to indicate improvement
        improved_files = files_dict.copy()
        for filename in improved_files:
            improved_files[filename] += "\n# Improved by mock agent\n"

        return improved_files


# Test utilities
def create_test_prompt(text: str = "Test prompt") -> Prompt:
    """Create a test prompt."""
    return Prompt(text)


def create_test_files() -> FilesDict:
    """Create test files dictionary."""
    return FilesDict(
        {
            "test.py": "# Test file\nprint('hello')\n",
            "README.md": "# Test Project\nThis is a test.\n",
        }
    )


# Performance testing fixtures
@pytest.fixture
async def performance_monitor():
    """Fixture providing a performance monitor."""
    return PerformanceMonitor()


@pytest.fixture
async def mock_ai():
    """Fixture providing a mock AI."""
    return MockAI(response_delay=0.01)


@pytest.fixture
async def mock_agent():
    """Fixture providing a mock agent."""
    return MockAgent(init_delay=0.01, improve_delay=0.01)
