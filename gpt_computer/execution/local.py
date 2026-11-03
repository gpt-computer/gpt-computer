"""
Local Disk Execution Environment

Provides an execution environment that runs code on the local file system.

Classes:
    DiskExecutionEnv: Runs code on the local file system and captures output.
"""

from __future__ import annotations

import logging
import os
import signal
import subprocess

from pathlib import Path
from typing import Optional, Tuple, Union

from gpt_computer.execution.base import BaseExecutionEnv
from gpt_computer.infrastructure.files.file_store import FileStore
from gpt_computer.infrastructure.files.operations import FilesDict

logger = logging.getLogger(__name__)


def _kill_process_tree(process: subprocess.Popen) -> None:
    if os.name == "posix":
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
    else:
        process.kill()


class DiskExecutionEnv(BaseExecutionEnv):
    """
    An execution environment that runs code on the local file system and captures
    the output of the execution.

    This class is responsible for executing code that is stored on disk. It ensures that
    the necessary entrypoint file exists and then runs the code using a subprocess.
    """

    def __init__(self, path: Union[str, Path, None] = None):
        self.files = FileStore(path)

    def upload(self, files: FilesDict) -> "DiskExecutionEnv":
        self.files.push(files)
        return self

    def download(self) -> FilesDict:
        return self.files.pull()

    def popen(self, command: str) -> subprocess.Popen:
        p = subprocess.Popen(
            command,
            shell=True,
            cwd=self.files.working_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        return p

    def run(self, command: str, timeout: Optional[int] = None) -> Tuple[str, str, int]:
        logger.info("\n--- Start of run ---")
        p = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=self.files.working_dir,
            text=True,
            shell=True,
            start_new_session=os.name == "posix",
        )
        logger.info("$ %s", command)
        try:
            stdout_full, stderr_full = p.communicate(timeout=timeout)
        except subprocess.TimeoutExpired as exc:
            logger.error("Command timed out after %s seconds", timeout)
            _kill_process_tree(p)
            p.communicate()
            raise TimeoutError(f"Command timed out after {timeout} seconds") from exc
        except KeyboardInterrupt:
            logger.info("\nStopping execution.")
            _kill_process_tree(p)
            stdout_full, stderr_full = p.communicate()
            logger.info("Execution stopped.")
            logger.info("\n--- Finished run ---\n")
        for line in stdout_full.splitlines():
            logger.debug(line)
        for line in stderr_full.splitlines():
            logger.debug(line)

        return stdout_full, stderr_full, p.returncode
