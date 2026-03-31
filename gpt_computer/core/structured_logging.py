"""
Structured Logging Module

This module provides structured logging capabilities with JSON formatting,
correlation IDs, and enhanced observability features for the gpt-computer project.

Classes:
    StructuredLogger: A logger that outputs structured JSON logs
    CorrelationContext: Manages correlation IDs for request tracing
    LogFormatter: Formats log records as structured JSON

Functions:
    get_logger(name: str) -> StructuredLogger
        Get a structured logger instance.
    setup_structured_logging() -> None
        Configure the root logger with structured formatting.
"""

from __future__ import annotations

import json
import logging
import threading
import time
import traceback

from contextlib import contextmanager
from contextvars import ContextVar
from datetime import datetime
from typing import Any, Dict, Optional

# Context variable for correlation ID
correlation_id: ContextVar[Optional[str]] = ContextVar("correlation_id", default=None)


class CorrelationContext:
    """
    Manages correlation IDs for request tracing across async boundaries.
    """

    @staticmethod
    def get_correlation_id() -> Optional[str]:
        """Get the current correlation ID from context."""
        return correlation_id.get()

    @staticmethod
    def set_correlation_id(correlation_id_value: str) -> None:
        """Set the correlation ID in the current context."""
        correlation_id.set(correlation_id_value)

    @staticmethod
    @contextmanager
    def with_correlation_id(correlation_id_value: str):
        """Context manager for setting correlation ID."""
        token = correlation_id.set(correlation_id_value)
        try:
            yield
        finally:
            correlation_id.reset(token)


class StructuredFormatter(logging.Formatter):
    """
    Formats log records as structured JSON with enhanced fields.
    """

    def __init__(self, service_name: str = "gpt-computer"):
        super().__init__()
        self.service_name = service_name

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as structured JSON."""
        # Base log structure
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "service": self.service_name,
            "thread": threading.current_thread().name,
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add correlation ID if available
        if correlation_id.get():
            log_entry["correlation_id"] = correlation_id.get()

        # Add exception information if present
        if record.exc_info:
            log_entry["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": traceback.format_exception(*record.exc_info),
            }

        # Add extra fields from record
        for key, value in record.__dict__.items():
            if key not in {
                "name",
                "msg",
                "args",
                "levelname",
                "levelno",
                "pathname",
                "filename",
                "module",
                "lineno",
                "funcName",
                "created",
                "msecs",
                "relativeCreated",
                "thread",
                "threadName",
                "processName",
                "process",
                "getMessage",
                "exc_info",
                "exc_text",
                "stack_info",
                "message",
            }:
                log_entry[key] = value

        return json.dumps(log_entry, default=str)


class StructuredLogger:
    """
    A logger wrapper that provides structured logging capabilities.
    """

    def __init__(self, name: str, service_name: str = "gpt-computer"):
        self.logger = logging.getLogger(name)
        self.service_name = service_name

    def _log_with_context(self, level: int, message: str, **kwargs):
        """Log a message with additional structured context."""
        extra = kwargs
        self.logger.log(level, message, extra=extra)

    def debug(self, message: str, **kwargs):
        """Log a debug message."""
        self._log_with_context(logging.DEBUG, message, **kwargs)

    def info(self, message: str, **kwargs):
        """Log an info message."""
        self._log_with_context(logging.INFO, message, **kwargs)

    def warning(self, message: str, **kwargs):
        """Log a warning message."""
        self._log_with_context(logging.WARNING, message, **kwargs)

    def error(self, message: str, **kwargs):
        """Log an error message."""
        self._log_with_context(logging.ERROR, message, **kwargs)

    def critical(self, message: str, **kwargs):
        """Log a critical message."""
        self._log_with_context(logging.CRITICAL, message, **kwargs)

    def log_api_call(
        self, model: str, tokens_used: int, response_time: float, **kwargs
    ):
        """Log an API call with structured metrics."""
        self.info(
            "API call completed",
            event_type="api_call",
            model=model,
            tokens_used=tokens_used,
            response_time_ms=response_time * 1000,
            **kwargs,
        )

    def log_agent_action(self, agent_type: str, action: str, duration: float, **kwargs):
        """Log an agent action with timing."""
        self.info(
            "Agent action completed",
            event_type="agent_action",
            agent_type=agent_type,
            action=action,
            duration_ms=duration * 1000,
            **kwargs,
        )

    def log_error_with_context(
        self, error: Exception, context: Dict[str, Any], **kwargs
    ):
        """Log an error with rich context information."""
        self.error(
            f"Error occurred: {str(error)}",
            error_type=type(error).__name__,
            error_message=str(error),
            context=context,
            **kwargs,
        )


# Global logger registry
_loggers: Dict[str, StructuredLogger] = {}


def get_logger(name: str, service_name: str = "gpt-computer") -> StructuredLogger:
    """
    Get a structured logger instance.

    Args:
        name: Logger name
        service_name: Service name for log entries

    Returns:
        StructuredLogger instance
    """
    if name not in _loggers:
        _loggers[name] = StructuredLogger(name, service_name)
    return _loggers[name]


def setup_structured_logging(
    level: str = "INFO",
    service_name: str = "gpt-computer",
    log_file: Optional[str] = None,
    console_output: bool = True,
) -> None:
    """
    Configure the root logger with structured formatting.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        service_name: Service name for log entries
        log_file: Optional file to write logs to
        console_output: Whether to output to console
    """
    # Clear existing handlers
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Set log level
    log_level = getattr(logging, level.upper(), logging.INFO)
    root_logger.setLevel(log_level)

    # Create structured formatter
    formatter = StructuredFormatter(service_name)

    # Console handler
    if console_output:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)

    # File handler
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)  # Always debug for files
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

    # Configure third-party loggers
    logging.getLogger("openai").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("langchain").setLevel(logging.WARNING)


# Performance monitoring decorator
def log_performance(logger: StructuredLogger, operation_name: str):
    """
    Decorator to log function performance.
    """

    def decorator(func):
        if hasattr(func, "__call__"):
            # Handle regular functions
            def wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    duration = time.time() - start_time
                    logger.log_agent_action(
                        agent_type=func.__module__,
                        action=operation_name,
                        duration=duration,
                        success=True,
                    )
                    return result
                except Exception as e:
                    duration = time.time() - start_time
                    logger.log_agent_action(
                        agent_type=func.__module__,
                        action=operation_name,
                        duration=duration,
                        success=False,
                        error=str(e),
                    )
                    raise

            return wrapper
        else:
            # Handle async functions
            async def async_wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = await func(*args, **kwargs)
                    duration = time.time() - start_time
                    logger.log_agent_action(
                        agent_type=func.__module__,
                        action=operation_name,
                        duration=duration,
                        success=True,
                    )
                    return result
                except Exception as e:
                    duration = time.time() - start_time
                    logger.log_agent_action(
                        agent_type=func.__module__,
                        action=operation_name,
                        duration=duration,
                        success=False,
                        error=str(e),
                    )
                    raise

            return async_wrapper

    return decorator
