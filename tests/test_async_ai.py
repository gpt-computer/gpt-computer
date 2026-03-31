"""
Async Tests for AI Components

This module contains tests for the async AI components and structured logging.
"""

import asyncio

from unittest.mock import AsyncMock, patch

import pytest

from gpt_computer.core.ai_async import AIResponse, AsyncAI
from gpt_computer.core.structured_logging import get_logger, setup_structured_logging
from gpt_computer.core.tracing import setup_tracing
from gpt_computer.test.async_test_utils import (
    AsyncTestCase,
    PerformanceMonitor,
    async_test,
)


class TestAsyncAI(AsyncTestCase):
    """Test cases for AsyncAI class."""

    @pytest.fixture
    async def async_ai(self):
        """Fixture providing an AsyncAI instance with mock backend."""
        # Mock the LLM to avoid actual API calls
        with patch(
            "gpt_computer.core.ai_async.AsyncAI._create_chat_model"
        ) as mock_create:
            mock_llm = AsyncMock()
            mock_llm.ainvoke.return_value = AsyncMock(content="Mock response")
            mock_create.return_value = mock_llm

            ai = AsyncAI(model_name="test-model")
            yield ai

    @async_test(timeout=2.0)
    async def test_async_ai_start(self, async_ai):
        """Test AsyncAI start method."""
        system = "You are a helpful assistant."
        user = "Hello, how are you?"

        async with self.assert_performance(min_ms=10, max_ms=500) as monitor:
            messages = await async_ai.start(system, user, step_name="test_start")
            monitor.checkpoint("start_completed")

        assert len(messages) >= 2  # System + User + AI response
        assert messages[0].content == system
        assert messages[1].content == user

    @async_test(timeout=2.0)
    async def test_async_ai_next(self, async_ai):
        """Test AsyncAI next method."""
        from langchain_core.messages import AIMessage, HumanMessage

        messages = [HumanMessage(content="Initial message")]

        async with self.assert_performance(min_ms=10, max_ms=500) as monitor:
            result = await async_ai.next(messages, step_name="test_next")
            monitor.checkpoint("next_completed")

        assert len(result) > len(messages)
        assert any(isinstance(msg, AIMessage) for msg in result)

    @async_test(timeout=3.0)
    async def test_async_ai_start_with_context(self, async_ai):
        """Test AsyncAI start_with_context method."""
        system = "Test system"
        user = "Test user"

        response = await async_ai.start_with_context(
            system, user, step_name="test_context"
        )

        assert isinstance(response, AIResponse)
        assert response.success is True
        assert response.correlation_id is not None
        assert response.response_time_ms >= 0
        assert len(response.messages) >= 2

    @async_test(timeout=3.0)
    async def test_async_ai_batch_processing(self, async_ai):
        """Test AsyncAI batch processing."""
        requests = [
            {
                "messages": [{"type": "human", "content": f"Message {i}"}],
                "step_name": f"batch_test_{i}",
            }
            for i in range(3)
        ]

        responses = await async_ai.batch_process(requests, max_concurrency=2)

        assert len(responses) == 3
        # Note: With mocked LLM, all responses should succeed
        # In real scenarios, some might fail

    def test_async_ai_metrics(self, async_ai):
        """Test AsyncAI metrics collection."""
        metrics = async_ai.get_metrics()

        assert "model_name" in metrics
        assert "total_requests" in metrics
        assert "total_tokens" in metrics
        assert "average_response_time_ms" in metrics
        assert metrics["model_name"] == "test-model"


class TestStructuredLogging(AsyncTestCase):
    """Test cases for structured logging."""

    @async_test(timeout=1.0)
    async def test_structured_logger_creation(self):
        """Test structured logger creation and basic usage."""
        logger = get_logger("test_logger")

        # Test basic logging methods
        logger.info("Test info message", test_key="test_value")
        logger.warning("Test warning", warning_type="test")
        logger.error("Test error", error_code="TEST_ERROR")

        # Test specialized logging methods
        logger.log_api_call("gpt-4", 100, 0.5, endpoint="test")
        logger.log_agent_action("test_agent", "test_action", 0.2, success=True)

        # Should not raise any exceptions
        assert True

    @async_test(timeout=1.0)
    async def test_structured_logging_setup(self):
        """Test structured logging setup."""
        import os
        import tempfile

        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = os.path.join(temp_dir, "test.log")

            # Setup structured logging
            setup_structured_logging(
                level="INFO",
                service_name="test-service",
                log_file=log_file,
                console_output=False,
            )

            logger = get_logger("setup_test")
            logger.info("Test message after setup")

            # Log file should exist and contain our message
            assert os.path.exists(log_file)

            with open(log_file, "r") as f:
                content = f.read()
                assert "test-service" in content
                assert "Test message after setup" in content


class TestTracing(AsyncTestCase):
    """Test cases for distributed tracing."""

    @async_test(timeout=1.0)
    async def test_tracing_setup(self):
        """Test tracing setup without external endpoints."""
        success = setup_tracing(
            service_name="test-tracing",
            jaeger_endpoint=None,
            otlp_endpoint=None,
            sample_rate=1.0,
        )

        # Should succeed even without external endpoints
        assert success is True

    @async_test(timeout=2.0)
    async def test_trace_async_operation(self):
        """Test tracing async operations."""
        from gpt_computer.core.tracing import get_tracing_manager

        manager = get_tracing_manager("test-service")

        async with manager.trace_async_operation(
            "test_operation", "test_tracer"
        ) as span:
            await asyncio.sleep(0.1)  # Simulate work

            # Span might be None if tracing not fully available
            if span:
                # Test adding attributes
                manager.get_tracer("test_tracer")

        # Should not raise any exceptions
        assert True


class TestMockAI(AsyncTestCase):
    """Test cases for MockAI testing utility."""

    @async_test(timeout=2.0)
    async def test_mock_ai_basic_usage(self):
        """Test basic MockAI usage."""
        mock_ai = self.create_mock_ai(response_delay=0.01)

        messages = await mock_ai.start("System", "User", step_name="test")

        assert len(messages) >= 2
        assert mock_ai.call_count == 1
        assert mock_ai.last_messages is not None

    @async_test(timeout=2.0)
    async def test_mock_ai_predefined_responses(self):
        """Test MockAI with predefined responses."""
        responses = ["Response 1", "Response 2", "Response 3"]
        mock_ai = self.create_mock_ai(responses=responses)

        # Get all predefined responses
        for i, expected in enumerate(responses):
            messages = await mock_ai.start("System", f"User {i}", step_name=f"test_{i}")
            assert messages[-1].content == expected

        # Additional calls should repeat the last response
        extra_messages = await mock_ai.start("System", "Extra user", step_name="extra")
        assert extra_messages[-1].content == responses[-1]

    @async_test(timeout=2.0)
    async def test_mock_ai_performance_monitoring(self):
        """Test MockAI with performance monitoring."""
        mock_ai = self.create_mock_ai(response_delay=0.05)

        monitor = PerformanceMonitor()
        monitor.start()

        await mock_ai.start("System", "User", step_name="performance_test")

        duration = monitor.stop()

        # Should take approximately the response delay
        assert 0.04 <= duration <= 0.1  # Allow some variance


class TestPerformanceMonitoring(AsyncTestCase):
    """Test cases for performance monitoring."""

    @async_test(timeout=2.0)
    async def test_performance_monitor_basic(self):
        """Test basic performance monitoring."""
        monitor = PerformanceMonitor()
        monitor.start()

        await asyncio.sleep(0.1)
        monitor.checkpoint("sleep_completed")

        await asyncio.sleep(0.05)

        duration = monitor.stop()

        assert duration >= 0.15  # Should be at least 0.15 seconds
        assert len(monitor.checkpoints) == 1
        assert monitor.checkpoints[0]["name"] == "sleep_completed"

    @async_test(timeout=2.0)
    async def test_performance_monitor_assertions(self):
        """Test performance monitoring assertions."""
        monitor = PerformanceMonitor()
        monitor.start()

        await asyncio.sleep(0.1)

        monitor.stop()

        # Should pass
        monitor.assert_duration_between(0.05, 0.2)

        # Should fail
        with pytest.raises(AssertionError):
            monitor.assert_duration_between(0.5, 1.0)

    @async_test(timeout=2.0)
    async def test_performance_monitor_checkpoint_assertions(self):
        """Test performance monitoring checkpoint assertions."""
        monitor = PerformanceMonitor()
        monitor.start()

        await asyncio.sleep(0.05)
        monitor.checkpoint("checkpoint1")

        await asyncio.sleep(0.05)
        monitor.checkpoint("checkpoint2")

        monitor.stop()

        # Test checkpoint assertions
        monitor.assert_checkpoint_between("checkpoint1", 0.04, 0.1)
        monitor.assert_checkpoint_between("checkpoint2", 0.04, 0.1)

        # Should fail for non-existent checkpoint
        with pytest.raises(AssertionError):
            monitor.assert_checkpoint_between("nonexistent", 0, 1)


class TestIntegration(AsyncTestCase):
    """Integration tests for async components."""

    @async_test(timeout=3.0)
    async def test_async_ai_with_structured_logging(self):
        """Test AsyncAI integration with structured logging."""
        # Setup structured logging
        setup_structured_logging(level="INFO", service_name="integration-test")

        # Create AsyncAI with mock
        with patch(
            "gpt_computer.core.ai_async.AsyncAI._create_chat_model"
        ) as mock_create:
            mock_llm = AsyncMock()
            mock_llm.ainvoke.return_value = AsyncMock(
                content="Integration test response"
            )
            mock_create.return_value = mock_llm

            ai = AsyncAI(model_name="integration-model")

            # Perform operations
            messages = await ai.start(
                "Test system", "Test user", step_name="integration_test"
            )
            response = await ai.start_with_context(
                "System", "User", step_name="context_test"
            )

            # Verify structured logging was used
            assert ai.structured_logger is not None
            assert len(messages) >= 2
            assert response.success is True

    @async_test(timeout=3.0)
    async def test_full_async_workflow(self):
        """Test a complete async workflow with all components."""
        # Setup all components
        setup_structured_logging(level="DEBUG", service_name="workflow-test")

        mock_ai = self.create_mock_ai(
            response_delay=0.02,
            responses=["Initial response", "Follow-up response", "Final response"],
        )

        async with self.assert_performance(min_ms=50, max_ms=200) as monitor:
            # Step 1: Start conversation
            monitor.checkpoint("workflow_start")
            messages = await mock_ai.start(
                "System prompt", "User input", step_name="workflow_step_1"
            )

            # Step 2: Continue conversation
            monitor.checkpoint("workflow_continue")
            messages = await mock_ai.next(
                messages, "Additional question", step_name="workflow_step_2"
            )

            # Step 3: Final response
            monitor.checkpoint("workflow_final")
            messages = await mock_ai.next(messages, step_name="workflow_step_3")

        # Verify the workflow completed successfully
        assert len(messages) >= 4  # System + User + 2 AI responses
        assert mock_ai.call_count == 3
        assert monitor.checkpoints[0]["name"] == "workflow_start"
        assert monitor.checkpoints[-1]["name"] == "workflow_final"
