from unittest.mock import AsyncMock, MagicMock

import pytest

from langchain.schema import AIMessage
from pydantic import BaseModel

from gpt_computer.core.agent.react import ReActAgent
from gpt_computer.core.agent_tools.registry import ToolRegistry
from gpt_computer.core.ai import AI


class AddArgs(BaseModel):
    a: int
    b: int


def add(a: int, b: int):
    return a + b


@pytest.mark.asyncio
async def test_react_agent_loop():
    # 1. Setup ToolRegistry
    tools = ToolRegistry()
    tools.register(
        name="add", description="Adds two numbers", args_schema=AddArgs, func=add
    )

    # 2. Mock AI
    ai = MagicMock(spec=AI)
    ai.next = AsyncMock()

    # Define the sequence of LLM responses
    # First response: Decide to use the tool
    response_1 = AIMessage(
        content='Thought: I need to calculate 2 + 2.\nAction: add\nAction Input: {"a": 2, "b": 2}'
    )
    # Second response: After observing result "4", provide final answer
    response_2 = AIMessage(content="Thought: The result is 4.\nFinal Answer: 4")

    # Mock return values for ai.next. It returns a list of messages (history + new response)
    # We only care about the last message in the return for the agent's logic
    ai.next.side_effect = [[response_1], [response_2]]  # Iteration 1  # Iteration 2

    # 3. Run Agent
    agent = ReActAgent(ai=ai, tools=tools)
    result = await agent.run("What is 2 + 2?")

    # 4. Assertions
    assert result == "4"
    assert ai.next.call_count == 2

    # Verify tool was executed
    # We can't easily spy on the inner tool function unless we wrapped it,
    # but the fact that the second prompt (implied) would have contained "Observation: 4"
    # and the agent finished suggests success.
    # To be sure, let's verify the tool execution directly if possible or trust the flow.
    # Actually, we can check if ai.next was called with the observation in the history for the second call.

    # The second call to ai.next receives the message history.
    # The history passed to second call should contain:
    # [System, Human(Question), AI(Thought/Action), Human(Observation)]

    second_call_args = ai.next.await_args_list[1]
    message_history = second_call_args[0][0]  # first arg is messages list

    # Check if Observation is in the last message passed to LLM
    assert "Observation: 4" in message_history[-1].content


@pytest.mark.asyncio
async def test_react_agent_max_iterations():
    tools = ToolRegistry()
    ai = MagicMock(spec=AI)
    ai.next = AsyncMock()

    # Always return a thought without action or final answer
    ai.next.return_value = [AIMessage(content="Thought: I am thinking...")]

    agent = ReActAgent(ai=ai, tools=tools, max_iterations=2)
    result = await agent.run("Run forever?")

    assert result == "Agent reached maximum iterations without a final answer."
    assert ai.next.call_count == 2
