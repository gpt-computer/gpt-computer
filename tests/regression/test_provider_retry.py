"""Provider failure and retry regression tests."""

import asyncio

import pytest

from gpt_computer.ai.providers.retry_provider import (
    ProviderCircuitBreaker,
    RetryProvider,
)
from gpt_computer.ai.providers.types import BaseProvider
from gptc.errors import RetryProviderError


class FirstFailingProvider(BaseProvider):
    url = "https://first.example.test"
    working = True
    calls = 0

    @classmethod
    async def create_async_generator(cls, model, messages, **kwargs):
        cls.calls += 1
        if False:
            yield ""
        raise RuntimeError("first provider failed")


class SecondFailingProvider(BaseProvider):
    url = "https://second.example.test"
    working = True
    calls = 0

    @classmethod
    async def create_async_generator(cls, model, messages, **kwargs):
        cls.calls += 1
        if False:
            yield ""
        raise ValueError("second provider failed")


class SucceedingProvider(BaseProvider):
    url = "https://success.example.test"
    working = True
    calls = 0

    @classmethod
    async def create_async_generator(cls, model, messages, **kwargs):
        cls.calls += 1
        yield "recovered response"


@pytest.fixture(autouse=True)
def reset_provider_state():
    ProviderCircuitBreaker.reset()
    FirstFailingProvider.calls = 0
    SecondFailingProvider.calls = 0
    SucceedingProvider.calls = 0
    yield
    ProviderCircuitBreaker.reset()


def _collect(provider):
    async def collect():
        return [
            chunk
            async for chunk in provider.create_async_generator(
                model="test-model",
                messages=[{"role": "user", "content": "hello"}],
                api_key="test-key",
            )
        ]

    return asyncio.run(collect())


def test_retry_provider_falls_back_after_provider_error():
    retry = RetryProvider(
        [FirstFailingProvider, SucceedingProvider],
        shuffle=False,
    )

    chunks = _collect(retry)

    assert chunks[-1] == "recovered response"
    assert FirstFailingProvider.calls == 1
    assert SucceedingProvider.calls == 1


def test_retry_provider_reports_errors_when_all_providers_fail():
    retry = RetryProvider(
        [FirstFailingProvider, SecondFailingProvider],
        shuffle=False,
    )

    with pytest.raises(RetryProviderError, match="first provider failed") as error:
        _collect(retry)

    assert "second provider failed" in str(error.value)
    assert FirstFailingProvider.calls == 1
    assert SecondFailingProvider.calls == 1
