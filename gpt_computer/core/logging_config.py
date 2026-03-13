import logging
import sys
import traceback

from typing import Any, Optional


class MemoryLogHandler(logging.Handler):
    """
    A logging handler that redirects logs to the BaseMemory log method.
    """

    def __init__(self, memory: Any, log_file_name: str = "system.log"):
        super().__init__()
        self.memory = memory
        self.log_file_name = log_file_name

    def emit(self, record):
        try:
            msg = self.format(record)
            self.memory.log(self.log_file_name, msg)
        except Exception:
            self.handleError(record)


def setup_logging(
    verbose: bool = False, memory: Optional[Any] = None, log_file: Optional[str] = None
):
    """
    Configures the logging system for the application.
    """
    try:
        level = logging.DEBUG if verbose else logging.INFO

        # Root logger configuration
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)  # Catch all, filter at handlers

        # Remove existing handlers, but keep pytest's if running tests
        for handler in root_logger.handlers[:]:
            if not type(handler).__name__.startswith("_pytest") and not isinstance(
                handler, MemoryLogHandler
            ):
                root_logger.removeHandler(handler)

        # Console Handler (User facing)
        console_formatter = logging.Formatter("%(message)s")
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(console_formatter)
        root_logger.addHandler(console_handler)

        # File Handler (System debug)
        if log_file:
            file_formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(file_formatter)
            root_logger.addHandler(file_handler)

        # Memory Handler (Project specific logs)
        if memory is not None:
            memory_formatter = logging.Formatter(
                "%(name)s - %(levelname)s - %(message)s"
            )
            memory_handler = MemoryLogHandler(memory)
            memory_handler.setLevel(logging.DEBUG)
            memory_handler.setFormatter(memory_formatter)
            root_logger.addHandler(memory_handler)

        # Silence some noisy loggers
        logging.getLogger("openai").setLevel(logging.WARNING)
        logging.getLogger("httpx").setLevel(logging.WARNING)
        logging.getLogger("httpcore").setLevel(logging.WARNING)
    except Exception:
        traceback.print_exc()
