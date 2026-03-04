"""
Module for managing the execution environment on the local disk.

This module provides a class that handles the execution of code stored on the local
file system. It includes methods for uploading files to the execution environment,
running commands, and capturing the output.

Classes
-------
DiskExecutionEnv
    An execution environment that runs code on the local file system and captures
    the output of the execution.

Imports
-------
- logging: For logging information about the execution.
- subprocess: For running shell commands.
- time: For timing the execution of commands.
- Path: For handling file system paths.
- Optional, Tuple, Union: For type annotations.
- BaseExecutionEnv: For inheriting the base execution environment interface.
- FileStore: For managing file storage.
- FilesDict: For handling collections of files.
"""

import logging
import subprocess
import time

from pathlib import Path
from typing import Optional, Tuple, Union

from gpt_computer.core.base_execution_env import BaseExecutionEnv
from gpt_computer.core.default.file_store import FileStore
from gpt_computer.core.files_dict import FilesDict

logger = logging.getLogger(__name__)


class DiskExecutionEnv(BaseExecutionEnv):
    """
    An execution environment that runs code on the local file system and captures
    the output of the execution.

    This class is responsible for executing code that is stored on disk. It ensures that
    the necessary entrypoint file exists and then runs the code using a subprocess. If the
    execution is interrupted by the user, it handles the interruption gracefully.

    Attributes
    ----------
    store : FileStore
        An instance of FileStore that manages the storage of files in the execution
        environment.
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
        start = time.time()
        logger.info("\n--- Start of run ---")
        # while running, also print the stdout and stderr
        p = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=self.files.working_dir,
            text=True,
            shell=True,
        )
        logger.info("$ %s", command)
        stdout_full, stderr_full = "", ""

        try:
            while p.poll() is None:
                assert p.stdout is not None
                assert p.stderr is not None
                stdout = p.stdout.readline()
                stderr = p.stderr.readline()
                if stdout:
                    logger.debug(stdout.strip())
                    stdout_full += stdout
                if stderr:
                    logger.debug(stderr.strip())
                    stderr_full += stderr
                if timeout and time.time() - start > timeout:
                    logger.error("Timeout!")
                    p.kill()
                    raise TimeoutError()
        except KeyboardInterrupt:
            logger.info("\nStopping execution.")
            logger.info("Execution stopped.")
            p.kill()
            logger.info("\n--- Finished run ---\n")

        return stdout_full, stderr_full, p.returncode
