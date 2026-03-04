import logging

from gpt_computer.core.default.disk_memory import DiskMemory
from gpt_computer.core.logging_config import setup_logging


def test_memory_logging(tmp_path):
    # arrange
    memory = DiskMemory(tmp_path)
    setup_logging(verbose=True, memory=memory)
    logger = logging.getLogger("test_logger")

    # act
    logger.info("Test message 1")
    logger.error("Test error message")

    # assert
    log_file = tmp_path / "logs" / "system.log"
    assert log_file.exists()
    log_content = log_file.read_text()
    assert "Test message 1" in log_content
    assert "Test error message" in log_content
    assert "INFO" in log_content
    assert "ERROR" in log_content


def test_console_logging(caplog, tmp_path):
    # arrange
    memory = DiskMemory(tmp_path)
    setup_logging(verbose=True, memory=memory)
    logger = logging.getLogger("test_console")

    # act
    with caplog.at_level(logging.INFO, logger="test_console"):
        logger.info("Console message")

    # assert
    assert "Console message" in caplog.text
