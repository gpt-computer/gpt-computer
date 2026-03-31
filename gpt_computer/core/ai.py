"""
AI Module

This module provides an AI class that interfaces with language models to perform various tasks such as
starting a conversation, advancing the conversation, and handling message serialization. It also includes
backoff strategies for handling rate limit errors from the OpenAI API.

Classes:
    AI: A class that interfaces with language models for conversation management and message serialization.

Functions:
    serialize_messages(messages: List[Message]) -> str
        Serialize a list of messages to a JSON string.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os

from pathlib import Path
from typing import Any, List, Optional, Union

import backoff
import openai
import pyperclip

from langchain_anthropic import ChatAnthropic
from langchain_core.callbacks import (
    StdOutCallbackHandler as StreamingStdOutCallbackHandler,
)
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import (
    AIMessage,
    HumanMessage,
    SystemMessage,
    messages_from_dict,
    messages_to_dict,
)
from langchain_openai import AzureChatOpenAI, ChatOpenAI

try:
    from langchain_google_genai import ChatGoogleGenerativeAI
except ImportError:
    ChatGoogleGenerativeAI = None
try:
    from langchain_groq import ChatGroq
except ImportError:
    ChatGroq = None
try:
    from langchain_mistralai import ChatMistralAI
except ImportError:
    ChatMistralAI = None
try:
    from langchain_cohere import ChatCohere
except ImportError:
    ChatCohere = None

from gpt_computer.core.token_usage import TokenUsageLog

# Import structured logging if available
try:
    from gpt_computer.core.structured_logging import get_logger

    STRUCTURED_LOGGING_AVAILABLE = True
except ImportError:
    STRUCTURED_LOGGING_AVAILABLE = False

# Type hint for a chat message
Message = Union[AIMessage, HumanMessage, SystemMessage]

# Set up logging
logger = logging.getLogger(__name__)


class AI:
    """
    A class that interfaces with language models for conversation management and message serialization.

    This class provides methods to start and advance conversations, handle message serialization,
    and implement backoff strategies for rate limit errors when interacting with the OpenAI API.

    Attributes
    ----------
    temperature : float
        The temperature setting for the language model.
    azure_endpoint : str
        The endpoint URL for the Azure-hosted language model.
    model_name : str
        The name of the language model to use.
    streaming : bool
        A flag indicating whether to use streaming for the language model.
    llm : BaseChatModel
        The language model instance for conversation management.
    token_usage_log : TokenUsageLog
        A log for tracking token usage during conversations.

    Methods
    -------
    start(system: str, user: str, step_name: str) -> List[Message]
        Start the conversation with a system message and a user message.
    next(messages: List[Message], prompt: Optional[str], step_name: str) -> List[Message]
        Advances the conversation by sending message history to LLM and updating with the response.
    backoff_inference(messages: List[Message]) -> Any
        Perform inference using the language model with an exponential backoff strategy.
    serialize_messages(messages: List[Message]) -> str
        Serialize a list of messages to a JSON string.
    deserialize_messages(jsondictstr: str) -> List[Message]
        Deserialize a JSON string to a list of messages.
    _create_chat_model() -> BaseChatModel
        Create a chat model with the specified model name and temperature.
    """

    def __init__(
        self,
        model_name="gpt-4-turbo",
        temperature=0.1,
        azure_endpoint=None,
        base_url=None,
        streaming=True,
        vision=False,
    ):
        """
        Initialize the AI class.

        Parameters
        ----------
        model_name : str, optional
            The name of the model to use, by default "gpt-4".
        temperature : float, optional
            The temperature to use for the model, by default 0.1.
        base_url : str, optional
            The base URL for the API (e.g., for local LLMs like Ollama), by default None.
        """
        self.temperature = temperature
        self.azure_endpoint = azure_endpoint
        self.base_url = base_url
        self.model_name = model_name
        self.streaming = streaming
        self.vision = (
            ("vision-preview" in model_name)
            or ("gpt-4-turbo" in model_name and "preview" not in model_name)
            or ("claude" in model_name)
        )
        self.llm = self._create_chat_model()
        self.token_usage_log = TokenUsageLog(model_name)

        # Initialize structured logger if available
        if STRUCTURED_LOGGING_AVAILABLE:
            self.structured_logger = get_logger(f"AI.{model_name}")
        else:
            self.structured_logger = None

        logger.debug(f"Using model {self.model_name}")

    async def start(self, system: str, user: Any, *, step_name: str) -> List[Message]:
        """
        Start the conversation with a system message and a user message.

        Parameters
        ----------
        system : str
            The content of the system message.
        user : str
            The content of the user message.
        step_name : str
            The name of the step.

        Returns
        -------
        List[Message]
            The list of messages in the conversation.
        """

        messages: List[Message] = [
            SystemMessage(content=system),
            HumanMessage(content=user),
        ]

        # Log with structured logger if available
        if self.structured_logger:
            self.structured_logger.info(
                "Starting conversation",
                step_name=step_name,
                model=self.model_name,
                system_length=len(str(system)),
                user_length=len(str(user)),
            )

        return await self.next(messages, step_name=step_name)

    def _extract_content(self, content):
        """
        Extracts text content from a message, supporting both string and list types.
        Parameters
        ----------
        content : Union[str, List[dict]]
            The content of a message, which could be a string or a list.
        Returns
        -------
        str
            The extracted text content.
        """
        if isinstance(content, str):
            return content
        elif isinstance(content, list) and content and "text" in content[0]:
            # Assuming the structure of list content is [{'type': 'text', 'text': 'Some text'}, ...]
            return content[0]["text"]
        else:
            return ""

    def _collapse_text_messages(self, messages: List[Message]):
        """
        Combine consecutive messages of the same type into a single message, where if the message content
        is a list type, the first text element's content is taken. This method keeps `combined_content` as a string.

        This method iterates through the list of messages, combining consecutive messages of the same type
        by joining their content with a newline character. If the content is a list, it extracts text from the first
        text element's content. This reduces the number of messages and simplifies the conversation for processing.

        Parameters
        ----------
        messages : List[Message]
            The list of messages to collapse.

        Returns
        -------
        List[Message]
            The list of messages after collapsing consecutive messages of the same type.
        """
        collapsed_messages = []
        if not messages:
            return collapsed_messages

        previous_message = messages[0]
        combined_content = self._extract_content(previous_message.content)

        for current_message in messages[1:]:
            if current_message.type == previous_message.type:
                combined_content += "\n\n" + self._extract_content(
                    current_message.content
                )
            else:
                collapsed_messages.append(
                    previous_message.__class__(content=combined_content)
                )
                previous_message = current_message
                combined_content = self._extract_content(current_message.content)

        collapsed_messages.append(previous_message.__class__(content=combined_content))
        return collapsed_messages

    async def next(
        self,
        messages: List[Message],
        prompt: Optional[str] = None,
        *,
        step_name: str,
    ) -> List[Message]:
        """
        Advances the conversation by sending message history
        to LLM and updating with the response.

        Parameters
        ----------
        messages : List[Message]
            The list of messages in the conversation.
        prompt : Optional[str], optional
            The prompt to use, by default None.
        step_name : str
            The name of the step.

        Returns
        -------
        List[Message]
            The updated list of messages in the conversation.
        """

        if prompt:
            messages.append(HumanMessage(content=prompt))

        # Log with structured logger if available
        if self.structured_logger:
            self.structured_logger.info(
                "Advancing conversation",
                step_name=step_name,
                model=self.model_name,
                message_count=len(messages),
                has_prompt=prompt is not None,
            )

        logger.debug(
            "Creating a new chat completion: %s",
            "\n".join([m.pretty_repr() for m in messages]),
        )

        if not self.vision:
            messages = self._collapse_text_messages(messages)

        response = await self.backoff_inference(messages)

        self.token_usage_log.update_log(
            messages=messages, answer=response.content, step_name=step_name
        )
        messages.append(response)
        logger.debug(f"Chat completion finished: {messages}")

        return messages

    @backoff.on_exception(backoff.expo, openai.RateLimitError, max_tries=7, max_time=45)
    async def backoff_inference(self, messages):
        """
        Perform inference using the language model while implementing an exponential backoff strategy.

        This function will retry the inference in case of a rate limit error from the OpenAI API.
        It uses an exponential backoff strategy, meaning the wait time between retries increases
        exponentially. The function will attempt to retry up to 7 times within a span of 45 seconds.

        Parameters
        ----------
        messages : List[Message]
            A list of chat messages which will be passed to the language model for processing.

        callbacks : List[Callable]
            A list of callback functions that are triggered after each inference. These functions
            can be used for logging, monitoring, or other auxiliary tasks.

        Returns
        -------
        Any
            The output from the language model after processing the provided messages.

        Raises
        ------
        openai.error.RateLimitError
            If the number of retries exceeds the maximum or if the rate limit persists beyond the
            allotted time, the function will ultimately raise a RateLimitError.

        Example
        -------
        >>> messages = [SystemMessage(content="Hello"), HumanMessage(content="How's the weather?")]
        >>> response = await backoff_inference(messages)
        """
        return await self.llm.ainvoke(messages)  # type: ignore

    @staticmethod
    def serialize_messages(messages: List[Message]) -> str:
        """
        Serialize a list of messages to a JSON string.

        Parameters
        ----------
        messages : List[Message]
            The list of messages to serialize.

        Returns
        -------
        str
            The serialized messages as a JSON string.
        """
        return json.dumps(messages_to_dict(messages))

    @staticmethod
    def deserialize_messages(jsondictstr: str) -> List[Message]:
        """
        Deserialize a JSON string to a list of messages.

        Parameters
        ----------
        jsondictstr : str
            The JSON string to deserialize.

        Returns
        -------
        List[Message]
            The deserialized list of messages.
        """
        data = json.loads(jsondictstr)
        # Modify implicit is_chunk property to ALWAYS false
        # since Langchain's Message schema is stricter
        prevalidated_data = [
            {**item, "tools": {**item.get("tools", {}), "is_chunk": False}}
            for item in data
        ]
        return list(messages_from_dict(prevalidated_data))  # type: ignore

    def _create_chat_model(self) -> BaseChatModel:
        """
        Create a chat model with the specified model name and temperature.

        Parameters
        ----------
        model : str
            The name of the model to create.
        temperature : float
            The temperature to use for the model.

        Returns
        -------
        BaseChatModel
            The created chat model.
        """
        if self.azure_endpoint:
            return AzureChatOpenAI(
                azure_endpoint=self.azure_endpoint,
                openai_api_version=os.getenv(
                    "OPENAI_API_VERSION", "2024-05-01-preview"
                ),
                deployment_name=self.model_name,
                openai_api_type="azure",
                streaming=self.streaming,
                callbacks=[StreamingStdOutCallbackHandler()],
            )
        elif "claude" in self.model_name:
            return ChatAnthropic(
                model=self.model_name,
                temperature=self.temperature,
                callbacks=[StreamingStdOutCallbackHandler()],
                streaming=self.streaming,
                max_tokens_to_sample=4096,
            )
        elif self.vision:
            return ChatOpenAI(
                model=self.model_name,
                temperature=self.temperature,
                streaming=self.streaming,
                callbacks=[StreamingStdOutCallbackHandler()],
                max_tokens=4096,  # vision models default to low max token limits
                openai_api_base=self.base_url,
            )
        elif "gemini" in self.model_name:
            if ChatGoogleGenerativeAI is None:
                raise ImportError("langchain-google-genai is not installed.")
            return ChatGoogleGenerativeAI(
                model=self.model_name,
                temperature=self.temperature,
                streaming=self.streaming,
                convert_system_message_to_human=True,  # Gemini often needs this
                callbacks=[StreamingStdOutCallbackHandler()],
            )
        elif "llama" in self.model_name or "mixtral" in self.model_name:
            # Assume Groq for Llama/Mixtral unless explicitly overridden or handled via base_url (which would be OpenAI class above if user passed base_url)
            # If user passed base_url explictly, we might want to prioritize that via OpenAI class.
            # But here we are inside _create_chat_model.
            # If base_url is set, we might default to OpenAI client?
            # Actually, let's make Groq explicit if no base_url, or if user asked for it.
            # For simplicity, if model name matches Groq patterns and NO base_url is provided, use Groq.
            if not self.base_url and ChatGroq:
                return ChatGroq(
                    model_name=self.model_name,
                    temperature=self.temperature,
                    streaming=self.streaming,
                    callbacks=[StreamingStdOutCallbackHandler()],
                )
            # If base_url is provided, fall through to default OpenAI client which handles generic endpoints.
        elif "mistral" in self.model_name and "mixtral" not in self.model_name:
            # Mistral API (not Groq Mixtral)
            if not self.base_url and ChatMistralAI:
                return ChatMistralAI(
                    model=self.model_name,
                    temperature=self.temperature,
                    streaming=self.streaming,
                    callbacks=[StreamingStdOutCallbackHandler()],
                )
        elif "command" in self.model_name:
            if not self.base_url and ChatCohere:
                return ChatCohere(
                    model=self.model_name,
                    temperature=self.temperature,
                    streaming=self.streaming,
                    callbacks=[StreamingStdOutCallbackHandler()],
                )

        # Default to OpenAI (or compatible)
        return ChatOpenAI(
            model=self.model_name,
            temperature=self.temperature,
            streaming=self.streaming,
            callbacks=[StreamingStdOutCallbackHandler()],
            openai_api_base=self.base_url,
        )


def serialize_messages(messages: List[Message]) -> str:
    return AI.serialize_messages(messages)


class ClipboardAI(AI):
    # Ignore not init superclass
    def __init__(self, **_):  # type: ignore
        self.vision = False
        self.token_usage_log = TokenUsageLog("clipboard_llm")

    @staticmethod
    def serialize_messages(messages: List[Message]) -> str:
        return "\n\n".join([f"{m.type}:\n{m.content}" for m in messages])

    @staticmethod
    def multiline_input():
        print("Enter/Paste your content. Ctrl-D or Ctrl-Z ( windows ) to save it.")
        content = []
        while True:
            try:
                line = input()
            except EOFError:
                break
            content.append(line)
        return "\n".join(content)

    async def next(
        self,
        messages: List[Message],
        prompt: Optional[str] = None,
        *,
        step_name: str,
    ) -> List[Message]:
        """
        Not yet fully supported
        """
        if prompt:
            messages.append(HumanMessage(content=prompt))

        logger.debug(f"Creating a new chat completion: {messages}")

        msgs = self.serialize_messages(messages)
        pyperclip.copy(msgs)
        Path("clipboard.txt").write_text(msgs)
        print(
            "Messages copied to clipboard and written to clipboard.txt,",
            len(msgs),
            "characters in total",
        )

        # Since input() is blocking, we should run it in an executor to avoid blocking the event loop
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(None, self.multiline_input)

        messages.append(AIMessage(content=response))
        logger.debug(f"Chat completion finished: {messages}")

        return messages
