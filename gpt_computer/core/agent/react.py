import json
import logging
import re
import time

from typing import Dict

from langchain_core.messages import HumanMessage, SystemMessage

from gpt_computer.core.agent_tools.registry import ToolRegistry
from gpt_computer.core.ai import AI

# Import structured logging and tracing if available
try:
    from gpt_computer.core.structured_logging import get_logger
    from gpt_computer.core.tracing import trace_async_function

    STRUCTURED_LOGGING_AVAILABLE = True
    TRACING_AVAILABLE = True
except ImportError:
    STRUCTURED_LOGGING_AVAILABLE = False
    TRACING_AVAILABLE = False

logger = logging.getLogger(__name__)

REACT_SYSTEM_PROMPT = """Answer the following questions as best you can. You have access to the following tools:

{tool_descriptions}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action (json or string)
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!
"""


class ReActAgent:
    def __init__(self, ai: AI, tools: ToolRegistry, max_iterations: int = 10):
        self.ai = ai
        self.tools = tools
        self.max_iterations = max_iterations

        # Initialize structured logger if available
        if STRUCTURED_LOGGING_AVAILABLE:
            self.structured_logger = get_logger("ReActAgent")
        else:
            self.structured_logger = None

    def _format_tool_descriptions(self) -> str:
        tools_data = self.tools.list_tools()
        return "\n".join([f"{t['name']}: {t['description']}" for t in tools_data])

    def _format_tool_names(self) -> str:
        tools_data = self.tools.list_tools()
        return ", ".join([t["name"] for t in tools_data])

    def _parse_output(self, text: str) -> Dict[str, str]:
        """
        Parses the LLM output to find Action and Action Input.
        Returns a dict with action, action_input, or final_answer.
        """
        if "Final Answer:" in text:
            return {"final_answer": text.split("Final Answer:")[-1].strip()}

        # Regex to find Action and Action Input
        action_match = re.search(r"Action:\s*(.*?)\n", text, re.DOTALL)
        action_input_match = re.search(
            r"Action Input:\s*(.*?)(?:\nObservation:|$)", text, re.DOTALL
        )

        if action_match and action_input_match:
            return {
                "action": action_match.group(1).strip(),
                "action_input": action_input_match.group(1).strip(),
            }

        # Fallback if no structured action found but no final answer either
        return {"thought": text}

    @ trace_async_function("ReActAgent", "run") if TRACING_AVAILABLE else lambda x: x
    async def run(self, question: str) -> str:
        start_time = time.time()

        # Log with structured logger if available
        if self.structured_logger:
            self.structured_logger.info(
                "Starting ReAct agent execution",
                question=question,
                max_iterations=self.max_iterations,
                available_tools=len(self.tools.list_tools()),
            )

        # Prepare system prompt
        tool_desc = self._format_tool_descriptions()
        tool_names = self._format_tool_names()

        system_content = REACT_SYSTEM_PROMPT.format(
            tool_descriptions=tool_desc, tool_names=tool_names
        )

        messages = [
            SystemMessage(content=system_content),
            HumanMessage(content=f"Question: {question}"),
        ]

        logger.info(f"Starting ReAct loop for question: {question}")

        for i in range(self.max_iterations):
            time.time()
            logger.debug(f"Iteration {i + 1}/{self.max_iterations}")

            # Get response from LLM
            # AI.next expects a step_name for logging
            messages = await self.ai.next(messages, step_name=f"react_step_{i}")
            response_msg = messages[-1]
            response_text = response_msg.content

            logger.debug(f"LLM Response: {response_text}")

            # Parse response
            parsed = self._parse_output(response_text)

            if "final_answer" in parsed:
                final_answer = parsed["final_answer"]
                total_time = time.time() - start_time

                if self.structured_logger:
                    self.structured_logger.info(
                        "ReAct agent completed successfully",
                        iterations_completed=i + 1,
                        total_time_ms=total_time * 1000,
                        final_answer_length=len(final_answer),
                    )

                logger.info("Final answer found.")
                return final_answer

            if "action" in parsed:
                action = parsed["action"]
                action_input_str = parsed["action_input"]

                logger.info(
                    f"Agent selected action: {action} with input: {action_input_str}"
                )

                # Log action with structured logger
                if self.structured_logger:
                    self.structured_logger.info(
                        "Agent executing tool",
                        iteration=i + 1,
                        action=action,
                        action_input_length=len(action_input_str),
                    )

                # Try to parse input as JSON if possible, otherwise string
                tool_args = {}
                try:
                    tool_args = json.loads(action_input_str)
                    if not isinstance(tool_args, dict):
                        # If valid JSON but not a dict (e.g. "input_string"), treat as single arg 'input'
                        # This assumes tools are standardized to take 'input' if single arg.
                        # However, strictly speaking, arguments should be named.
                        # We'll default to {"input": ...} if it's not a dict.
                        tool_args = {"input": tool_args}
                except json.JSONDecodeError:
                    # Not JSON, treat as raw string input
                    tool_args = {"input": action_input_str}

                # Execute tool
                tool_start_time = time.time()
                try:
                    tool_result = await self.tools.execute(action, **tool_args)
                    tool_execution_time = time.time() - tool_start_time

                    if self.structured_logger:
                        self.structured_logger.info(
                            "Tool execution completed",
                            iteration=i + 1,
                            action=action,
                            tool_execution_time_ms=tool_execution_time * 1000,
                            tool_success=True,
                        )
                except Exception as e:
                    tool_result = f"Error executing tool: {e}"
                    tool_execution_time = time.time() - tool_start_time

                    if self.structured_logger:
                        self.structured_logger.error(
                            "Tool execution failed",
                            iteration=i + 1,
                            action=action,
                            tool_execution_time_ms=tool_execution_time * 1000,
                            tool_success=False,
                            error=str(e),
                        )

                observation = f"Observation: {str(tool_result)}"
                logger.debug(observation)

                # Append observation to history
                messages.append(HumanMessage(content=observation))
            else:
                # Just a thought, or failed parsing. Let the agent continue thinking.
                logger.debug("No action found, continuing conversation.")
                if i == self.max_iterations - 1:
                    total_time = time.time() - start_time

                    if self.structured_logger:
                        self.structured_logger.warning(
                            "ReAct agent reached maximum iterations",
                            total_time_ms=total_time * 1000,
                            iterations_completed=self.max_iterations,
                        )

                    return "Agent reached maximum iterations without a final answer."
                # We don't need to append anything special if it was just a thought,
                # the previous message is already in history.
                pass

        total_time = time.time() - start_time

        if self.structured_logger:
            self.structured_logger.warning(
                "ReAct agent completed without final answer",
                total_time_ms=total_time * 1000,
                iterations_completed=self.max_iterations,
            )

        return "Agent reached maximum iterations."
