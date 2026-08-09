"""
Module for defining a simple agent that uses AI to manage code generation and improvement.

This module provides a class that represents an agent capable of initializing and improving
a codebase using AI. It handles interactions with the AI model, memory, and execution
environment to generate and refine code based on user prompts.

"""

import tempfile
import time

from typing import Optional

from gpt_computer.core.ai import AI
from gpt_computer.core.base_agent import BaseAgent
from gpt_computer.core.base_execution_env import BaseExecutionEnv
from gpt_computer.core.base_memory import BaseMemory
from gpt_computer.core.default.disk_execution_env import DiskExecutionEnv
from gpt_computer.core.default.disk_memory import DiskMemory
from gpt_computer.core.default.paths import PREPROMPTS_PATH, memory_path
from gpt_computer.core.default.steps import gen_code, gen_entrypoint, improve_fn
from gpt_computer.core.files_dict import FilesDict
from gpt_computer.core.preprompts_holder import PrepromptsHolder
from gpt_computer.core.prompt import Prompt

# Import structured logging and tracing if available
try:
    from gpt_computer.core.structured_logging import get_logger
    from gpt_computer.core.tracing import trace_async_function

    STRUCTURED_LOGGING_AVAILABLE = True
    TRACING_AVAILABLE = True
except ImportError:
    STRUCTURED_LOGGING_AVAILABLE = False
    TRACING_AVAILABLE = False


class SimpleAgent(BaseAgent):
    """
    An agent that uses AI to generate and improve code based on a given prompt.

    This agent is capable of initializing a codebase from a prompt and improving an existing
    codebase based on user input. It uses an AI model to generate and refine code, and it
    interacts with a repository and an execution environment to manage and execute the code.

    Attributes
    ----------
    memory : BaseMemory
        The memory interface where the code and related data are stored.
    execution_env : BaseExecutionEnv
        The execution environment in which the code is executed.
    ai : AI
        The AI model used for generating and improving code.
    preprompts_holder : PrepromptsHolder
        The holder for preprompt messages that guide the AI model.
    """

    def __init__(
        self,
        memory: BaseMemory,
        execution_env: BaseExecutionEnv,
        ai: AI = None,
        preprompts_holder: PrepromptsHolder = None,
    ):
        self.preprompts_holder = preprompts_holder or PrepromptsHolder(PREPROMPTS_PATH)
        self.memory = memory
        self.execution_env = execution_env
        self.ai = ai or AI()

        # Initialize structured logger if available
        if STRUCTURED_LOGGING_AVAILABLE:
            self.structured_logger = get_logger("SimpleAgent")
        else:
            self.structured_logger = None

    @classmethod
    def with_default_config(
        cls, path: str, ai: AI = None, preprompts_holder: PrepromptsHolder = None
    ):
        return cls(
            memory=DiskMemory(memory_path(path)),
            execution_env=DiskExecutionEnv(),
            ai=ai,
            preprompts_holder=preprompts_holder or PrepromptsHolder(PREPROMPTS_PATH),
        )

    @ trace_async_function("SimpleAgent", "init") if TRACING_AVAILABLE else lambda x: x
    async def init(self, prompt: Prompt) -> FilesDict:
        start_time = time.time()

        # Log with structured logger if available
        if self.structured_logger:
            self.structured_logger.info(
                "Starting SimpleAgent initialization",
                prompt_length=len(str(prompt)),
                model=self.ai.model_name,
            )

        try:
            files_dict = await gen_code(
                self.ai, prompt, self.memory, self.preprompts_holder
            )
            entrypoint = await gen_entrypoint(
                self.ai, prompt, files_dict, self.memory, self.preprompts_holder
            )
            combined_dict = {**files_dict, **entrypoint}
            files_dict = FilesDict(combined_dict)

            total_time = time.time() - start_time

            if self.structured_logger:
                self.structured_logger.info(
                    "SimpleAgent initialization completed",
                    total_time_ms=total_time * 1000,
                    files_generated=len(files_dict),
                    success=True,
                )

            return files_dict

        except Exception as e:
            total_time = time.time() - start_time

            if self.structured_logger:
                self.structured_logger.error(
                    "SimpleAgent initialization failed",
                    total_time_ms=total_time * 1000,
                    error=str(e),
                    success=False,
                )
            raise

    @(
        trace_async_function("SimpleAgent", "improve")
        if TRACING_AVAILABLE
        else lambda x: x
    )
    async def improve(
        self,
        files_dict: FilesDict,
        prompt: Prompt,
        execution_command: Optional[str] = None,
    ) -> FilesDict:
        start_time = time.time()

        # Log with structured logger if available
        if self.structured_logger:
            self.structured_logger.info(
                "Starting SimpleAgent improvement",
                prompt_length=len(str(prompt)),
                files_count=len(files_dict),
                model=self.ai.model_name,
                has_execution_command=execution_command is not None,
            )

        try:
            files_dict = await improve_fn(
                self.ai, prompt, files_dict, self.memory, self.preprompts_holder
            )

            total_time = time.time() - start_time

            if self.structured_logger:
                self.structured_logger.info(
                    "SimpleAgent improvement completed",
                    total_time_ms=total_time * 1000,
                    final_files_count=len(files_dict),
                    success=True,
                )

            return files_dict

        except Exception as e:
            total_time = time.time() - start_time

            if self.structured_logger:
                self.structured_logger.error(
                    "SimpleAgent improvement failed",
                    total_time_ms=total_time * 1000,
                    error=str(e),
                    success=False,
                )
            raise


def default_config_agent():
    """
    Creates an instance of SimpleAgent with default configuration.

    Returns
    -------
    SimpleAgent
        An instance of SimpleAgent with a temporary directory as its base path.
    """
    return SimpleAgent.with_default_config(tempfile.mkdtemp())
