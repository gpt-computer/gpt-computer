"""
File Store Module

Manages file storage in a temporary directory for the execution environment.

Classes:
    FileStore: Manages file storage in a temporary directory, allowing for upload and download of files.
"""

import tempfile

from pathlib import Path
from typing import Union

from gpt_computer.infrastructure.files.operations import FilesDict


class FileStore:
    """
    Manages file storage in a temporary directory, allowing for upload and download of files.
    """

    def __init__(self, path: Union[str, Path, None] = None):
        if path is None:
            path = Path(tempfile.mkdtemp(prefix="gpt-computer-"))

        self.working_dir = Path(path)
        self.working_dir.mkdir(parents=True, exist_ok=True)
        self.id = self.working_dir.name.split("-")[-1]

    def _resolve_path(self, name: Union[str, Path]) -> Path:
        root = self.working_dir.resolve()
        path = (root / name).resolve()
        try:
            path.relative_to(root)
        except ValueError as exc:
            raise PermissionError(
                f"File path escapes working directory: {name}"
            ) from exc
        return path

    def push(self, files: FilesDict):
        for name, content in files.items():
            path = self._resolve_path(name)
            path.parent.mkdir(parents=True, exist_ok=True)
            path = self._resolve_path(name)
            with open(path, "w") as f:
                f.write(content)
        return self

    def linting(self, files: FilesDict) -> FilesDict:
        # lint the code
        from gpt_computer.infrastructure.linting.checker import Linting

        linting = Linting()
        return linting.lint_files(files)

    def pull(self) -> FilesDict:
        files = {}
        for path in self.working_dir.glob("**/*"):
            if path.is_file():
                resolved_path = self._resolve_path(path.relative_to(self.working_dir))
                with open(resolved_path, "r") as f:
                    try:
                        content = f.read()
                    except UnicodeDecodeError:
                        content = "binary file"
                    files[str(path.relative_to(self.working_dir))] = content
        return FilesDict(files)
