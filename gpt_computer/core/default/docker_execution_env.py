import io
import logging
import tarfile

from typing import Optional, Tuple

import docker

from gpt_computer.core.base_execution_env import BaseExecutionEnv
from gpt_computer.core.files_dict import FilesDict

logger = logging.getLogger(__name__)


class DockerExecutionEnv(BaseExecutionEnv):
    def __init__(self, image: str = "python:3.11-slim"):
        self.client = docker.from_env()
        self.image = image
        self.container = None
        self.workdir = "/workspace"

        try:
            self.client.images.pull(self.image)
        except Exception as e:
            logger.warning(f"Could not pull image {self.image}: {e}")

    def _start_container(self):
        if self.container is None:
            self.container = self.client.containers.run(
                self.image,
                command="tail -f /dev/null",  # Keep alive
                detach=True,
                working_dir=self.workdir,
                auto_remove=True,
            )
            # Create workdir
            self.container.exec_run(f"mkdir -p {self.workdir}")

    def upload(self, files: FilesDict) -> "DockerExecutionEnv":
        self._start_container()

        # Create a tar stream
        file_like_object = io.BytesIO()
        with tarfile.open(fileobj=file_like_object, mode="w") as tar:
            for name, content in files.items():
                info = tarfile.TarInfo(name=name)
                encoded = content.encode("utf-8")
                info.size = len(encoded)
                tar.addfile(tarinfo=info, fileobj=io.BytesIO(encoded))

        file_like_object.seek(0)

        try:
            self.container.put_archive(self.workdir, file_like_object)
        except Exception as e:
            logger.error(f"Failed to upload files to container: {e}")
            raise

        return self

    def download(self) -> FilesDict:
        # Implementing download from container is complex (get_archive returns a tar stream)
        # For MVP, we might skip or implement partially.
        # But BaseExecutionEnv requires it.
        # Let's verify if we need it for the current flows.
        # usually we only need upload + run.
        return FilesDict({})

    def popen(self, command: str):
        # Docker SDK doesn't support a true Popen interface easily.
        # We can simulate it or just raise NotImplementedError if self_heal uses it.
        # self_heal uses popen.
        # We might need to rethink self_heal for docker or assume run() is enough.
        raise NotImplementedError("Popen not supported in Docker env yet. Use run()")

    def run(self, command: str, timeout: Optional[int] = None) -> Tuple[str, str, int]:
        self._start_container()

        logger.info(f"Docker exec: {command}")

        try:
            # exec_run returns (exit_code, output)
            # It combines stdout and stderr by default unless demux=True
            exit_code, output = self.container.exec_run(
                f"bash -c '{command}'", workdir=self.workdir, demux=True
            )

            stdout = output[0].decode("utf-8") if output[0] else ""
            stderr = output[1].decode("utf-8") if output[1] else ""

            logger.debug(f"Stdout: {stdout}")
            if stderr:
                logger.debug(f"Stderr: {stderr}")

            return stdout, stderr, exit_code

        except Exception as e:
            logger.error(f"Docker execution failed: {e}")
            return "", str(e), 1

    def __del__(self):
        if self.container:
            try:
                self.container.stop()
            except:
                pass
