"""Compatibility facade for invoking synchronous and asynchronous completions."""

from __future__ import annotations

import os

from typing import Any, AsyncIterator, Coroutine, Iterator, Union


class ChatCompletionAPI:
    @staticmethod
    def _prepare_request(
        model: Any,
        messages: list[dict[str, Any]],
        provider: Any,
        stream: bool,
        image: Any,
        image_name: str | None,
        ignore_working: bool,
        ignore_stream: bool,
        **kwargs: Any,
    ) -> tuple[Any, Any, dict[str, Any]]:
        if image is not None:
            kwargs["media"] = [(image, image_name)]
        elif "images" in kwargs:
            kwargs["media"] = kwargs.pop("images")

        from gpt_computer.ai.client.service import get_model_and_provider

        model, provider = get_model_and_provider(
            model,
            provider,
            stream,
            ignore_working,
            ignore_stream,
            has_images="media" in kwargs,
        )

        if "proxy" not in kwargs:
            proxy = os.environ.get("GPTC_PROXY")
            if proxy:
                kwargs["proxy"] = proxy
        if ignore_stream:
            kwargs["ignore_stream"] = True

        return model, provider, kwargs

    @staticmethod
    def create(
        model: Any,
        messages: list[dict[str, Any]],
        provider: Any = None,
        stream: bool = False,
        image: Any = None,
        image_name: str | None = None,
        ignore_working: bool = False,
        ignore_stream: bool = False,
        **kwargs: Any,
    ) -> Union[Iterator[Any], str]:
        from gpt_computer.ai.providers.base_provider import get_provider_method
        from gpt_computer.ai.providers.helper import concat_chunks

        model, provider, kwargs = ChatCompletionAPI._prepare_request(
            model,
            messages,
            provider,
            stream,
            image,
            image_name,
            ignore_working,
            ignore_stream,
            **kwargs,
        )
        result = get_provider_method(provider)(model, messages, stream=stream, **kwargs)
        return result if stream or ignore_stream else concat_chunks(result)

    @staticmethod
    def create_async(
        model: Any,
        messages: list[dict[str, Any]],
        provider: Any = None,
        stream: bool = False,
        image: Any = None,
        image_name: str | None = None,
        ignore_working: bool = False,
        ignore_stream: bool = False,
        **kwargs: Any,
    ) -> Union[AsyncIterator[Any], Coroutine[Any, Any, str]]:
        from gpt_computer.ai.providers.base_provider import get_async_provider_method
        from gpt_computer.ai.providers.helper import async_concat_chunks

        model, provider, kwargs = ChatCompletionAPI._prepare_request(
            model,
            messages,
            provider,
            stream,
            image,
            image_name,
            ignore_working,
            ignore_stream,
            **kwargs,
        )
        result = get_async_provider_method(provider)(
            model, messages, stream=stream, **kwargs
        )
        if not stream and not ignore_stream and hasattr(result, "__aiter__"):
            result = async_concat_chunks(result)
        return result


__all__ = ["ChatCompletionAPI"]
