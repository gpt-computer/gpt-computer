"""
OpenTelemetry Tracing Module

This module provides distributed tracing capabilities using OpenTelemetry
for monitoring and debugging the gpt-computer application.

Classes:
    TracerProvider: Manages OpenTelemetry tracing setup
    SpanWrapper: Wraps operations with tracing spans

Functions:
    setup_tracing(service_name: str) -> TracerProvider
        Initialize OpenTelemetry tracing.
    get_tracer(name: str) -> Tracer
        Get a tracer instance.
    trace_async_function(tracer: Tracer, span_name: str)
        Decorator for tracing async functions.
"""

from __future__ import annotations

import asyncio
import time

from contextlib import asynccontextmanager
from functools import wraps
from typing import AsyncGenerator, Optional, TypeVar

from gpt_computer.core.structured_logging import get_logger

# Type variable for function decorators
F = TypeVar("F")

try:
    from opentelemetry import context, trace
    from opentelemetry.exporter.jaeger.thrift import JaegerExporter
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
    from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
    from opentelemetry.instrumentation.langchain import LangchainInstrumentor
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    from opentelemetry.semconv.trace import SpanAttributes

    OPENTELEMETRY_AVAILABLE = True
except ImportError:
    OPENTELEMETRY_AVAILABLE = False
    trace = None
    context = None


class TracingManager:
    """
    Manages OpenTelemetry tracing setup and configuration.
    """

    def __init__(self, service_name: str = "gpt-computer"):
        self.service_name = service_name
        self.logger = get_logger("TracingManager")
        self._tracer_provider: Optional[TracerProvider] = None
        self._setup_complete = False

    def setup_tracing(
        self,
        jaeger_endpoint: Optional[str] = None,
        otlp_endpoint: Optional[str] = None,
        sample_rate: float = 1.0,
    ) -> bool:
        """
        Initialize OpenTelemetry tracing.

        Args:
            jaeger_endpoint: Jaeger collector endpoint
            otlp_endpoint: OTLP collector endpoint
            sample_rate: Sampling rate (0.0 to 1.0)

        Returns:
            True if setup was successful, False otherwise
        """
        if not OPENTELEMETRY_AVAILABLE:
            self.logger.warning(
                "OpenTelemetry packages not installed. "
                "Install with: pip install opentelemetry-api opentelemetry-sdk "
                "opentelemetry-exporter-jaeger opentelemetry-exporter-otlp "
                "opentelemetry-instrumentation-httpx opentelemetry-instrumentation-langchain"
            )
            return False

        try:
            # Create resource with service information
            resource = Resource.create(
                {
                    "service.name": self.service_name,
                    "service.version": "0.1.0",
                    "service.instance.id": f"{self.service_name}-{int(time.time())}",
                }
            )

            # Create tracer provider
            self._tracer_provider = TracerProvider(resource=resource)

            # Add span processors
            if jaeger_endpoint:
                jaeger_exporter = JaegerExporter(
                    endpoint=jaeger_endpoint,
                    collector_endpoint=jaeger_endpoint,
                )
                self._tracer_provider.add_span_processor(
                    BatchSpanProcessor(jaeger_exporter)
                )
                self.logger.info(f"Jaeger exporter configured: {jaeger_endpoint}")

            if otlp_endpoint:
                otlp_exporter = OTLPSpanExporter(endpoint=otlp_endpoint)
                self._tracer_provider.add_span_processor(
                    BatchSpanProcessor(otlp_exporter)
                )
                self.logger.info(f"OTLP exporter configured: {otlp_endpoint}")

            # Set as global tracer provider
            trace.set_tracer_provider(self._tracer_provider)

            # Instrument HTTP client and LangChain
            HTTPXClientInstrumentor().instrument()
            LangchainInstrumentor().instrument()

            self._setup_complete = True
            self.logger.info(
                "OpenTelemetry tracing initialized",
                service=self.service_name,
                sample_rate=sample_rate,
                jaeger_enabled=jaeger_endpoint is not None,
                otlp_enabled=otlp_endpoint is not None,
            )

            return True

        except Exception as e:
            self.logger.log_error_with_context(
                e, {"service": self.service_name, "operation": "setup_tracing"}
            )
            return False

    def get_tracer(self, name: str) -> Optional[trace.Tracer]:
        """
        Get a tracer instance.

        Args:
            name: Tracer name

        Returns:
            Tracer instance or None if not available
        """
        if not self._setup_complete or not OPENTELEMETRY_AVAILABLE:
            return None

        return trace.get_tracer(name)

    @asynccontextmanager
    async def trace_async_operation(
        self, operation_name: str, tracer_name: str = "default", **attributes
    ) -> AsyncGenerator[Optional[trace.Span], None]:
        """
        Context manager for tracing async operations.

        Args:
            operation_name: Name of the operation
            tracer_name: Name of the tracer
            **attributes: Span attributes

        Yields:
            Span instance or None if tracing not available
        """
        tracer = self.get_tracer(tracer_name)
        if not tracer:
            yield None
            return

        with tracer.start_as_current_span(operation_name) as span:
            if span:
                # Set standard attributes
                span.set_attribute(SpanAttributes.SERVICE_NAME, self.service_name)
                span.set_attribute("operation.name", operation_name)

                # Set custom attributes
                for key, value in attributes.items():
                    span.set_attribute(key, value)

                self.logger.debug(
                    "Span started",
                    operation=operation_name,
                    span_id=span.get_span_id() if span else None,
                    trace_id=span.get_trace_id() if span else None,
                )

            try:
                yield span
            except Exception as e:
                if span:
                    span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
                    span.record_exception(e)
                raise
            finally:
                if span:
                    self.logger.debug(
                        "Span completed",
                        operation=operation_name,
                        span_id=span.get_span_id(),
                        duration_ms=time.time() * 1000 - span.start_time,
                    )

    def shutdown(self) -> None:
        """Shutdown the tracer provider and flush spans."""
        if self._tracer_provider:
            self._tracer_provider.force_flush()
            self.logger.info("OpenTelemetry tracing shutdown completed")


# Global tracing manager instance
_tracing_manager: Optional[TracingManager] = None


def get_tracing_manager(service_name: str = "gpt-computer") -> TracingManager:
    """
    Get the global tracing manager instance.

    Args:
        service_name: Service name

    Returns:
        TracingManager instance
    """
    global _tracing_manager
    if _tracing_manager is None:
        _tracing_manager = TracingManager(service_name)
    return _tracing_manager


def setup_tracing(
    service_name: str = "gpt-computer",
    jaeger_endpoint: Optional[str] = None,
    otlp_endpoint: Optional[str] = None,
    sample_rate: float = 1.0,
) -> bool:
    """
    Initialize OpenTelemetry tracing.

    Args:
        service_name: Service name
        jaeger_endpoint: Jaeger collector endpoint
        otlp_endpoint: OTLP collector endpoint
        sample_rate: Sampling rate

    Returns:
        True if setup was successful
    """
    manager = get_tracing_manager(service_name)
    return manager.setup_tracing(jaeger_endpoint, otlp_endpoint, sample_rate)


def get_tracer(name: str) -> Optional[trace.Tracer]:
    """
    Get a tracer instance.

    Args:
        name: Tracer name

    Returns:
        Tracer instance or None
    """
    manager = get_tracing_manager()
    return manager.get_tracer(name)


def trace_async_function(tracer_name: str = "default", span_name: Optional[str] = None):
    """
    Decorator for tracing async functions.

    Args:
        tracer_name: Name of the tracer
        span_name: Name for the span (defaults to function name)

    Returns:
        Decorator function
    """

    def decorator(func: F) -> F:
        if not OPENTELEMETRY_AVAILABLE:
            return func

        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            manager = get_tracing_manager()
            operation_name = span_name or f"{func.__module__}.{func.__name__}"

            async with manager.trace_async_operation(
                operation_name,
                tracer_name,
                function_name=func.__name__,
                module_name=func.__module__,
                args_count=len(args),
                kwargs_count=len(kwargs),
            ) as span:
                try:
                    result = await func(*args, **kwargs)
                    if span:
                        span.set_attribute("function.success", True)
                    return result
                except Exception as e:
                    if span:
                        span.set_attribute("function.success", False)
                        span.set_attribute("function.error", str(e))
                    raise

        return async_wrapper  # type: ignore

    def sync_decorator(func: F) -> F:
        if not OPENTELEMETRY_AVAILABLE:
            return func

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            manager = get_tracing_manager()
            operation_name = span_name or f"{func.__module__}.{func.__name__}"

            # For sync functions, we need to handle tracing differently
            tracer = manager.get_tracer(tracer_name)
            if not tracer:
                return func(*args, **kwargs)

            with tracer.start_as_current_span(operation_name) as span:
                span.set_attribute("function_name", func.__name__)
                span.set_attribute("module_name", func.__module__)

                try:
                    result = func(*args, **kwargs)
                    span.set_attribute("function.success", True)
                    return result
                except Exception as e:
                    span.set_attribute("function.success", False)
                    span.set_attribute("function.error", str(e))
                    span.record_exception(e)
                    raise

        return sync_wrapper  # type: ignore

    def combined_decorator(func: F) -> F:
        if asyncio.iscoroutinefunction(func):
            return decorator(func)
        else:
            return sync_decorator(func)

    return combined_decorator


class SpanWrapper:
    """
    Utility class for wrapping operations with tracing spans.
    """

    def __init__(self, tracer_name: str = "default"):
        self.tracer_name = tracer_name
        self.manager = get_tracing_manager()

    @asynccontextmanager
    async def wrap_operation(
        self, operation_name: str, **attributes
    ) -> AsyncGenerator[Optional[trace.Span], None]:
        """
        Wrap an operation with tracing.

        Args:
            operation_name: Name of the operation
            **attributes: Span attributes

        Yields:
            Span instance or None
        """
        async with self.manager.trace_async_operation(
            operation_name, self.tracer_name, **attributes
        ) as span:
            yield span

    def add_span_attributes(self, span: Optional[trace.Span], **attributes) -> None:
        """
        Add attributes to a span safely.

        Args:
            span: Span instance (can be None)
            **attributes: Attributes to add
        """
        if span and OPENTELEMETRY_AVAILABLE:
            for key, value in attributes.items():
                span.set_attribute(key, value)
