"""
End-to-End Tests with Fake Providers

These tests validate the AI client layer end-to-end using fake/deterministic
providers (no live API calls). They cover the vertical slice from CLI →
AI client → provider invocation.

Tests verify:
- Client works with a fake provider (sync)
- AsyncClient works with a fake provider (async)
- ClientFactory creates clients correctly
- Legacy gptc imports still work with deprecation warnings
- API identity preserved between legacy and new imports
"""

import subprocess
import sys

import pytest

from gpt_computer.ai.client import AsyncClient, Client, ClientFactory
from gpt_computer.ai.providers.base import BaseProvider


class FakeProvider(BaseProvider):
    """Deterministic fake provider for testing."""

    url = "https://fake.example.com"
    working = True
    supports_stream = True
    supports_message_history = True
    supports_system_message = True

    def __init__(self, response="fake response"):
        self._response = response
        self.call_count = 0

    def create_completion(self, model="", messages=None, stream=False, **kwargs):
        self.call_count += 1
        if stream:
            for chunk in self._response.split():
                yield chunk + " "
        else:
            yield self._response

    def get_dict(self):
        return {"name": "FakeProvider", "url": self.url, "label": None}


def _run_subprocess(script: str) -> subprocess.CompletedProcess:
    """Run a Python subprocess with deprecation warnings enabled."""
    return subprocess.run(
        [sys.executable, "-W", "all", "-c", script],
        capture_output=True,
        text=True,
    )


# ---------------------------------------------------------------------------
# Client tests
# ---------------------------------------------------------------------------


def test_client_with_fake_provider():
    """Test Client.generate with a fake provider."""
    fake = FakeProvider("hello world")
    client = Client(provider=fake)
    response = client.generate("test prompt", model="fake-model")
    assert response == "hello world"
    assert fake.call_count == 1


def test_client_streaming_with_fake_provider():
    """Test Client.generate with streaming."""
    fake = FakeProvider("streaming response")
    client = Client(provider=fake)
    result = client.generate("test prompt", stream=True)
    chunks = list(result)
    assert "".join(chunks).strip() == "streaming response"


def test_client_no_provider_raises():
    """Test Client.generate raises without a provider."""
    client = Client()
    with pytest.raises(ValueError, match="No provider configured"):
        client.generate("test prompt")


def test_client_factory_creates_client():
    """Test ClientFactory.create_client."""
    fake = FakeProvider("factory response")
    client = ClientFactory.create_client(provider=fake, api_key="sk-test")
    assert isinstance(client, Client)
    assert client.api_key == "sk-test"
    response = client.generate("hello")
    assert response == "factory response"


def test_client_factory_creates_async_client():
    """Test ClientFactory.create_async_client."""
    fake = FakeProvider("async factory response")
    client = ClientFactory.create_async_client(provider=fake)
    assert isinstance(client, AsyncClient)


# ---------------------------------------------------------------------------
# AsyncClient tests
# ---------------------------------------------------------------------------


def test_async_client_with_fake_provider():
    """Test AsyncClient.generate with a fake provider."""
    import asyncio

    fake = FakeProvider("async hello")
    client = AsyncClient(provider=fake)
    response = asyncio.run(client.generate("test prompt"))
    assert response == "async hello"
    assert fake.call_count == 1


# ---------------------------------------------------------------------------
# Legacy import compatibility tests (subprocess-based)
# ---------------------------------------------------------------------------


def test_legacy_gptc_imports_with_warning():
    """Test that legacy gptc imports work with deprecation warnings (subprocess)."""
    script = """
import warnings
warnings.simplefilter("always")
from gptc import Client, AsyncClient, ChatCompletion, Model
print("SUCCESS")
"""
    result = _run_subprocess(script)
    assert result.returncode == 0
    assert "SUCCESS" in result.stdout
    assert "deprecated" in result.stderr.lower()


def test_legacy_gptc_providers_import_with_warning():
    """Test that legacy gptc.providers imports work with deprecation warnings."""
    script = """
import warnings
warnings.simplefilter("always")
from gptc.providers import BaseProvider
print("SUCCESS")
"""
    result = _run_subprocess(script)
    assert result.returncode == 0
    assert "SUCCESS" in result.stdout
    assert "deprecated" in result.stderr.lower()


def test_legacy_core_imports_with_warning():
    """Test that legacy gpt_computer.core imports work with deprecation warnings."""
    script = """
import warnings
warnings.simplefilter("always")
from gpt_computer.core import BaseAgent
print("SUCCESS")
"""
    result = _run_subprocess(script)
    assert result.returncode == 0
    assert "SUCCESS" in result.stdout
    assert "deprecated" in result.stderr.lower()


# ---------------------------------------------------------------------------
# API identity tests
# ---------------------------------------------------------------------------


def test_client_api_identity():
    """Test that legacy Client and new Client are the same class."""
    from gpt_computer.ai.client import Client as NewClient
    from gptc import Client as LegacyClient

    assert LegacyClient is NewClient, "Client class identity not preserved"


def test_async_client_api_identity():
    """Test that legacy AsyncClient and new AsyncClient are the same class."""
    from gpt_computer.ai.client import AsyncClient as NewAsyncClient
    from gptc import AsyncClient as LegacyAsyncClient

    assert (
        LegacyAsyncClient is NewAsyncClient
    ), "AsyncClient class identity not preserved"


def test_model_api_identity():
    """Test that legacy Model and new Model are the same class."""
    from gpt_computer.ai.models import Model as NewModel
    from gptc import Model as LegacyModel

    assert LegacyModel is NewModel, "Model class identity not preserved"


# ---------------------------------------------------------------------------
# Fake provider end-to-end test
# ---------------------------------------------------------------------------


def test_e2e_client_generate_returns_provider_response():
    """End-to-end: Client.generate returns the provider's response."""
    fake = FakeProvider("e2e success")
    client = Client(provider=fake)
    response = client.generate("generate something", model="test-model")
    assert response == "e2e success"


def test_e2e_async_client_generate_returns_provider_response():
    """End-to-end: AsyncClient.generate returns the provider's response."""
    import asyncio

    fake = FakeProvider("async e2e success")
    client = AsyncClient(provider=fake)
    response = asyncio.run(client.generate("generate something", model="test-model"))
    assert response == "async e2e success"


def test_chat_completion_api_with_fake_provider():
    """The migrated ChatCompletion facade preserves synchronous provider calls."""
    from gpt_computer.ai.chat_completion import ChatCompletionAPI

    fake = FakeProvider("facade response")
    response = ChatCompletionAPI.create(
        "fake-model",
        [{"role": "user", "content": "hello"}],
        provider=fake,
    )
    assert response == "facade response"


def test_chat_completion_api_async_with_fake_provider():
    """The migrated ChatCompletion facade preserves asynchronous provider calls."""
    import asyncio

    from gpt_computer.ai.chat_completion import ChatCompletionAPI

    fake = FakeProvider("async facade response")
    response = asyncio.run(
        ChatCompletionAPI.create_async(
            "fake-model",
            [{"role": "user", "content": "hello"}],
            provider=fake,
        )
    )
    assert response == "async facade response"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
