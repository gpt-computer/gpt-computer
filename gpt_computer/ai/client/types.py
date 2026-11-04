from __future__ import annotations

from typing import AsyncIterator, Iterator, Union

from gpt_computer.infrastructure.config.paths import AppConfig

from .stubs import ChatCompletion, ChatCompletionChunk

Proxies = Union[dict, str]
IterResponse = Iterator[Union[ChatCompletion, ChatCompletionChunk]]
AsyncIterResponse = AsyncIterator[Union[ChatCompletion, ChatCompletionChunk]]


class Client:
    def __init__(
        self,
        api_key: str = None,
        proxies: Proxies = None,
        base_url: str = None,
        **kwargs,
    ) -> None:
        self.api_key: str = api_key
        self.proxies = proxies
        self.proxy: str = self.get_proxy()
        self.base_url: str = base_url

    def get_proxy(self) -> Union[str, None]:
        if isinstance(self.proxies, str):
            return self.proxies
        elif self.proxies is None:
            return AppConfig.proxy
        elif "all" in self.proxies:
            return self.proxies["all"]
        elif "https" in self.proxies:
            return self.proxies["https"]
