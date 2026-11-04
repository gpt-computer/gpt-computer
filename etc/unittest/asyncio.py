import asyncio

try:
    import nest_asyncio2 as nest_asyncio

    has_nest_asyncio = True
except Exception:
    has_nest_asyncio = False
import unittest

import gptc

from gptc import ChatCompletion
from gptc.client import Client

from .mocks import AsyncGeneratorProviderMock, AsyncProviderMock, ProviderMock

DEFAULT_MESSAGES = [{"role": "user", "content": "Hello"}]


class TestChatCompletion(unittest.TestCase):
    async def run_exception(self):
        return ChatCompletion.create(
            gptc.models.default, DEFAULT_MESSAGES, AsyncProviderMock
        )

    def test_exception(self):
        if has_nest_asyncio:
            self.skipTest("has nest_asyncio")
        self.assertRaises(
            gptc.errors.NestAsyncioError, asyncio.run, self.run_exception()
        )

    def test_create(self):
        result = ChatCompletion.create(
            gptc.models.default, DEFAULT_MESSAGES, AsyncProviderMock
        )
        self.assertEqual("Mock", result)

    def test_create_generator(self):
        result = ChatCompletion.create(
            gptc.models.default, DEFAULT_MESSAGES, AsyncGeneratorProviderMock
        )
        self.assertEqual("Mock", result)

    def test_await_callback(self):
        client = Client(provider=AsyncGeneratorProviderMock)
        response = client.chat.completions.create(DEFAULT_MESSAGES, "", max_tokens=0)
        if not response.choices or response.choices[0].message is None:
            self.fail("LLM returned empty or filtered response")
        self.assertEqual("Mock", response.choices[0].message.content)


class TestChatCompletionAsync(unittest.IsolatedAsyncioTestCase):
    async def test_base(self):
        result = await ChatCompletion.create_async(
            gptc.models.default, DEFAULT_MESSAGES, ProviderMock
        )
        self.assertEqual("Mock", result)

    async def test_async(self):
        result = await ChatCompletion.create_async(
            gptc.models.default, DEFAULT_MESSAGES, AsyncProviderMock
        )
        self.assertEqual("Mock", result)

    async def test_create_generator(self):
        result = await ChatCompletion.create_async(
            gptc.models.default, DEFAULT_MESSAGES, AsyncGeneratorProviderMock
        )
        self.assertEqual("Mock", result)


class TestChatCompletionNestAsync(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        if not has_nest_asyncio:
            self.skipTest('"nest_asyncio" not installed')
        nest_asyncio.apply()

    async def test_create(self):
        result = await ChatCompletion.create_async(
            gptc.models.default, DEFAULT_MESSAGES, ProviderMock
        )
        self.assertEqual("Mock", result)

    async def _test_nested(self):
        result = ChatCompletion.create(
            gptc.models.default, DEFAULT_MESSAGES, AsyncProviderMock
        )
        self.assertEqual("Mock", result)

    async def _test_nested_generator(self):
        result = ChatCompletion.create(
            gptc.models.default, DEFAULT_MESSAGES, AsyncGeneratorProviderMock
        )
        self.assertEqual("Mock", result)


if __name__ == "__main__":
    unittest.main()
