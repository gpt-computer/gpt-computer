import pytest

from langchain_community.chat_models.fake import FakeListChatModel
from langchain_core.language_models.chat_models import BaseChatModel

from gpt_computer.core.ai import AI


class AsyncFakeListChatModel(FakeListChatModel):
    async def ainvoke(self, *args, **kwargs):
        return self.invoke(*args, **kwargs)


def mock_create_chat_model(self) -> BaseChatModel:
    return AsyncFakeListChatModel(responses=["response1", "response2", "response3"])


@pytest.mark.asyncio
async def test_start(monkeypatch):
    monkeypatch.setattr(AI, "_create_chat_model", mock_create_chat_model)

    ai = AI("gpt-4")

    # act
    response_messages = await ai.start(
        "system prompt", "user prompt", step_name="test_start"
    )

    # assert
    assert response_messages[-1].content == "response1"


@pytest.mark.asyncio
async def test_next(monkeypatch):
    # arrange
    monkeypatch.setattr(AI, "_create_chat_model", mock_create_chat_model)

    ai = AI("gpt-4")
    response_messages = await ai.start(
        "system prompt", "user prompt", step_name="test_next"
    )

    # act
    response_messages = await ai.next(
        response_messages, "next user prompt", step_name="test_next"
    )

    # assert
    assert response_messages[-1].content == "response2"


@pytest.mark.asyncio
async def test_token_logging(monkeypatch):
    # arrange
    monkeypatch.setattr(AI, "_create_chat_model", mock_create_chat_model)

    ai = AI("gpt-4")

    # act
    response_messages = await ai.start(
        "system prompt", "user prompt", step_name="test_token_logging"
    )
    usageCostAfterStart = ai.token_usage_log.usage_cost()
    await ai.next(response_messages, "next user prompt", step_name="test_token_logging")
    usageCostAfterNext = ai.token_usage_log.usage_cost()

    # assert
    assert usageCostAfterStart > 0
    assert usageCostAfterNext > usageCostAfterStart


def test_base_url_support(monkeypatch):
    # Tests that base_url is correctly passed to the LLM constructor
    mock_calls = []

    class MockChatOpenAI:
        def __init__(self, **kwargs):
            mock_calls.append(kwargs)
            self.model = ""  # minimal mock

    # Mock the import in the ai module
    monkeypatch.setattr("gpt_computer.core.ai.ChatOpenAI", MockChatOpenAI)

    ai = AI(base_url="http://localhost:11434/v1")

    assert ai.base_url == "http://localhost:11434/v1"
    assert len(mock_calls) > 0
    assert mock_calls[0].get("openai_api_base") == "http://localhost:11434/v1"


def test_gemini_support(monkeypatch):
    # Tests that gemini models use ChatGoogleGenerativeAI
    mock_calls = []

    class MockChatGoogleGenerativeAI:
        def __init__(self, **kwargs):
            mock_calls.append(kwargs)
            self.model = ""

    # Mock the imports
    monkeypatch.setattr(
        "gpt_computer.core.ai.ChatGoogleGenerativeAI", MockChatGoogleGenerativeAI
    )

    AI(model_name="gemini-1.5-pro")

    assert len(mock_calls) > 0
    assert mock_calls[0].get("model") == "gemini-1.5-pro"
    assert mock_calls[0].get("convert_system_message_to_human") is True


def test_groq_support(monkeypatch):
    # Tests that llama models use ChatGroq by default if no base_url
    mock_calls = []

    class MockChatGroq:
        def __init__(self, **kwargs):
            mock_calls.append(kwargs)
            self.model_name = kwargs.get("model_name", "")

    monkeypatch.setattr("gpt_computer.core.ai.ChatGroq", MockChatGroq)

    AI(model_name="llama3-8b-8192")

    assert len(mock_calls) > 0
    assert mock_calls[0].get("model_name") == "llama3-8b-8192"


def test_mistral_support(monkeypatch):
    # Tests that mistral models use ChatMistralAI by default if no base_url
    mock_calls = []

    class MockChatMistralAI:
        def __init__(self, **kwargs):
            mock_calls.append(kwargs)
            self.model = kwargs.get("model", "")

    monkeypatch.setattr("gpt_computer.core.ai.ChatMistralAI", MockChatMistralAI)

    AI(model_name="mistral-large-latest")

    assert len(mock_calls) > 0
    assert mock_calls[0].get("model") == "mistral-large-latest"


def test_cohere_support(monkeypatch):
    # Tests that command models use ChatCohere by default if no base_url
    mock_calls = []

    class MockChatCohere:
        def __init__(self, **kwargs):
            mock_calls.append(kwargs)
            self.model = kwargs.get("model", "")

    monkeypatch.setattr("gpt_computer.core.ai.ChatCohere", MockChatCohere)

    AI(model_name="command-r-plus")

    assert len(mock_calls) > 0
    assert mock_calls[0].get("model") == "command-r-plus"


def test_base_url_with_other_model(monkeypatch):
    # Tests that if base_url is provided, it uses ChatOpenAI regardless of model name (except for Gemini which might need specific handler)
    mock_calls = []

    class MockChatOpenAI:
        def __init__(self, **kwargs):
            mock_calls.append(kwargs)
            self.model = ""

    monkeypatch.setattr("gpt_computer.core.ai.ChatOpenAI", MockChatOpenAI)

    # Llama on local endpoint
    AI(model_name="llama3", base_url="http://localhost:11434/v1")

    assert len(mock_calls) > 0
    assert mock_calls[0].get("openai_api_base") == "http://localhost:11434/v1"
    # It should use ChatOpenAI, not ChatGroq
