"""
Disk Memory Module

Provides a file-based key-value database system where keys correspond to filenames
and values to file contents.

Classes:
    DiskMemory: File-based key-value store for agent memory.
"""

from __future__ import annotations

import base64
import json
import shutil

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Union

from gpt_computer.agent.memory.base import BaseMemory
from gpt_computer.agent.memory.vector_store import VectorStore
from gpt_computer.tools.supported_languages import SUPPORTED_LANGUAGES


class DiskMemory(BaseMemory):
    """
    A file-based key-value store where keys correspond to filenames and values
    to file contents.
    """

    def __init__(self, path: Union[str, Path]):
        self._path: Path = Path(path).absolute()
        self._path.mkdir(parents=True, exist_ok=True)
        self.id = self._path.name.split("-")[-1] if "-" in self._path.name else ""
        self._vector_store = None

    @property
    def path(self) -> Path:
        return self._path

    @property
    def vector_store(self):
        if self._vector_store is None:
            self._vector_store = VectorStore(self.path)
        return self._vector_store

    def __contains__(self, key: str) -> bool:
        return (self.path / key).is_file()

    def __getitem__(self, key: str) -> str:
        full_path = self.path / key

        if not full_path.is_file():
            raise KeyError(f"File '{key}' could not be found in '{self.path}'")

        if full_path.suffix in [".png", ".jpeg", ".jpg"]:
            with full_path.open("rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
            mime_type = "image/png" if full_path.suffix == ".png" else "image/jpeg"
            return f"data:{mime_type};base64,{encoded_string}"
        else:
            with full_path.open("r", encoding="utf-8") as f:
                return f.read()

    def get(self, key: str, default: Optional[Any] = None) -> Any:
        item_path = self.path / key
        try:
            if item_path.is_file():
                return self[key]
            elif item_path.is_dir():
                return DiskMemory(item_path)
            else:
                return default
        except Exception:
            return default

    def __setitem__(self, key: Union[str, Path], val: str) -> None:
        if str(key).startswith("../"):
            raise ValueError(f"File name {key} attempted to access parent path.")

        if not isinstance(val, str):
            raise TypeError("val must be str")

        full_path = self.path / key
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(val, encoding="utf-8")

    def __delitem__(self, key: Union[str, Path]) -> None:
        item_path = self.path / key
        if not item_path.exists():
            raise KeyError(f"Item '{key}' could not be found in '{self.path}'")

        if item_path.is_file():
            item_path.unlink()
        elif item_path.is_dir():
            shutil.rmtree(item_path)

    def __iter__(self) -> Iterator[str]:
        return iter(
            sorted(
                str(item.relative_to(self.path))
                for item in sorted(self.path.rglob("*"))
                if item.is_file()
            )
        )

    def __len__(self) -> int:
        return len(list(self.__iter__()))

    def _supported_files(self) -> str:
        valid_extensions = {
            ext for lang in SUPPORTED_LANGUAGES for ext in lang["extensions"]
        }
        file_paths = [
            str(item)
            for item in self
            if Path(item).is_file() and Path(item).suffix in valid_extensions
        ]
        return "\n".join(file_paths)

    def _all_files(self) -> str:
        file_paths = [str(item) for item in self if Path(item).is_file()]
        return "\n".join(file_paths)

    def to_path_list_string(self, supported_code_files_only: bool = False) -> str:
        if supported_code_files_only:
            return self._supported_files()
        else:
            return self._all_files()

    def to_dict(self) -> Dict[Union[str, Path], str]:
        return {file_path: self[file_path] for file_path in self}

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    def log(self, key: Union[str, Path], val: str) -> None:
        if str(key).startswith("../"):
            raise ValueError(f"File name {key} attempted to access parent path.")

        if not isinstance(val, str):
            raise TypeError("val must be str")

        full_path = self.path / "logs" / key
        full_path.parent.mkdir(parents=True, exist_ok=True)

        if not full_path.exists():
            full_path.touch()

        with open(full_path, "a", encoding="utf-8") as file:
            file.write(f"\n{datetime.now().isoformat()}\n")
            file.write(val + "\n")

    def archive_logs(self):
        if (self.path / "logs").is_dir():
            archive_dir = (
                self.path / f"logs_{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}"
            )
            shutil.move(self.path / "logs", archive_dir)

    def index(self, texts: List[str], metadatas: List[Dict[str, Any]]):
        self.vector_store.add_texts(texts, metadatas)

    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        return self.vector_store.search(query, top_k)
