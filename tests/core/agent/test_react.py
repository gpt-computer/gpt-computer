import sys

from unittest.mock import AsyncMock, MagicMock

import pytest

from langchain_core.messages import AIMessage
from pydantic import BaseModel

from gpt_computer.agent.react import ReActAgent as MigratedReActAgent
from gpt_computer.agent.tools.registry import ToolRegistry as MigratedToolRegistry
from gpt_computer.core.agent.react import ReActAgent
from gpt_computer.core.agent_tools.registry import ToolRegistry
from gpt_computer.core.ai import AI
from gpt_computer.execution.local import DiskExecutionEnv
from gpt_computer.infrastructure.files.operations import FilesDict


class AddArgs(BaseModel):
    a: int
    b: int


class RunArgs(BaseModel):
    command: str
    timeout: int


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


@pytest.mark.asyncio
async def test_react_agent_continues_after_tool_failure():
    def failing_tool(a: int, b: int):
        raise RuntimeError("tool unavailable")

    tools = ToolRegistry()
    tools.register(
        name="add",
        description="Adds two numbers",
        args_schema=AddArgs,
        func=failing_tool,
    )
    ai = MagicMock(spec=AI)
    ai.next = AsyncMock(
        side_effect=[
            [
                AIMessage(
                    content='Thought: calculate.\nAction: add\nAction Input: {"a": 2, "b": 2}'
                )
            ],
            [
                AIMessage(
                    content="Thought: handle the error.\nFinal Answer: unavailable"
                )
            ],
        ]
    )

    agent = ReActAgent(ai=ai, tools=tools)
    result = await agent.run("What is 2 + 2?")

    assert result == "unavailable"
    second_call_messages = ai.next.await_args_list[1][0][0]
    assert "tool unavailable" in second_call_messages[-1].content


@pytest.mark.asyncio
async def test_react_agent_surfaces_execution_timeout_to_ai(tmp_path):
    env = DiskExecutionEnv(tmp_path)
    env.files.push(
        FilesDict(
            {
                "infinite.py": (
                    "import time\n"
                    "while True:\n"
                    "    print('tick', flush=True)\n"
                    "    time.sleep(0.05)\n"
                )
            }
        )
    )
    tools = MigratedToolRegistry()
    tools.register(
        name="run_command",
        description="Run a command with a timeout",
        args_schema=RunArgs,
        func=env.run,
    )
    ai = MagicMock(spec=AI)
    ai.next = AsyncMock(
        side_effect=[
            [
                AIMessage(
                    content=(
                        "Thought: run it.\nAction: run_command\nAction Input: "
                        f'{{"command": "\\"{sys.executable}\\" infinite.py", "timeout": 1}}'
                    )
                )
            ],
            [AIMessage(content="Thought: it timed out.\nFinal Answer: timed out")],
        ]
    )

    agent = MigratedReActAgent(ai=ai, tools=tools)
    result = await agent.run("Run the infinite command")

    assert result == "timed out"
    second_call_messages = ai.next.await_args_list[1][0][0]
    assert "Command timed out after 1 seconds" in second_call_messages[-1].content
