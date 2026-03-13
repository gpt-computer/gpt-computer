from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Union


class BaseMemory(ABC):
    @property
    @abstractmethod
    def path(self) -> Path:
        pass

    @abstractmethod
    def __contains__(self, key: str) -> bool:
        pass

    @abstractmethod
    def __getitem__(self, key: str) -> str:
        pass

    @abstractmethod
    def get(self, key: str, default: Optional[Any] = None) -> Any:
        pass

    @abstractmethod
    def __setitem__(self, key: Union[str, Path], val: str) -> None:
        pass

    @abstractmethod
    def __delitem__(self, key: Union[str, Path]) -> None:
        pass

    @abstractmethod
    def __iter__(self) -> Iterator[str]:
        pass

    @abstractmethod
    def __len__(self) -> int:
        pass

    @abstractmethod
    def to_path_list_string(self, supported_code_files_only: bool = False) -> str:
        pass

    @abstractmethod
    def to_dict(self) -> Dict[Union[str, Path], str]:
        pass

    @abstractmethod
    def to_json(self) -> str:
        pass

    @abstractmethod
    def log(self, key: Union[str, Path], val: str) -> None:
        pass

    @abstractmethod
    def archive_logs(self):
        pass

    @abstractmethod
    def index(self, texts: List[str], metadatas: List[Dict[str, Any]]):
        pass

    @abstractmethod
    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        pass
