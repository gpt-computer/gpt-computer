"""
CLI Agent Module

Provides the CliAgent class which manages the lifecycle of code generation and improvement
using an AI model.

Classes:
    CliAgent: Agent that orchestrates code generation and improvement via CLI.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable, Coroutine, Optional, TypeVar

from gpt_computer.agent.base import BaseAgent
from gpt_computer.agent.default.paths import PREPROMPTS_PATH
from gpt_computer.agent.default.steps import (
    execute_entrypoint,
    gen_code,
    gen_entrypoint,
    improve_fn,
)
from gpt_computer.agent.memory.base import BaseMemory
from gpt_computer.agent.memory.disk import DiskMemory
from gpt_computer.agent.pp_holder import PrepromptsHolder
from gpt_computer.agent.prompt import Prompt
from gpt_computer.execution.base import BaseExecutionEnv
from gpt_computer.execution.local import DiskExecutionEnv
from gpt_computer.infrastructure.files.operations import FilesDict

if TYPE_CHECKING:
    from gpt_computer.ai.client import AI
else:
    AI = Any

CodeGenType = TypeVar(
    "CodeGenType",
    bound=Callable[
        [AI, str, BaseMemory, PrepromptsHolder], Coroutine[Any, Any, FilesDict]
    ],
)
CodeProcessor = TypeVar(
    "CodeProcessor",
    bound=Callable[[AI, BaseExecutionEnv, FilesDict], Coroutine[Any, Any, FilesDict]],
)
ImproveType = TypeVar(
    "ImproveType",
    bound=Callable[
        [AI, str, FilesDict, BaseMemory, PrepromptsHolder],
        Coroutine[Any, Any, FilesDict],
    ],
)


class CliAgent(BaseAgent):
    """
    The `CliAgent` class is responsible for managing the lifecycle of code generation and improvement
    using an AI model. It orchestrates the generation of new code and the improvement of existing code
    based on given prompts and utilizes a memory system and execution environment for processing.
    """

    def __init__(
        self,
        memory: BaseMemory,
        execution_env: BaseExecutionEnv,
        ai: AI = None,
        code_gen_fn: CodeGenType = gen_code,
        improve_fn: ImproveType = improve_fn,
        process_code_fn: CodeProcessor = execute_entrypoint,
        preprompts_holder: PrepromptsHolder = None,
    ):
        self.memory = memory
        self.execution_env = execution_env
        if ai is None:
            from gpt_computer.ai.client import AI as AIClient

            ai = AIClient()
        self.ai = ai
        self.code_gen_fn = code_gen_fn
        self.process_code_fn = process_code_fn
        self.improve_fn = improve_fn
        self.preprompts_holder = preprompts_holder or PrepromptsHolder(PREPROMPTS_PATH)

    @classmethod
    def with_default_config(
        cls,
        memory: DiskMemory,
        execution_env: DiskExecutionEnv,
        ai: AI = None,
        code_gen_fn: CodeGenType = gen_code,
        improve_fn: ImproveType = improve_fn,
        process_code_fn: CodeProcessor = execute_entrypoint,
        preprompts_holder: PrepromptsHolder = None,
        diff_timeout=3,
    ):
        return cls(
            memory=memory,
            execution_env=execution_env,
            ai=ai,
            code_gen_fn=code_gen_fn,
            process_code_fn=process_code_fn,
            improve_fn=improve_fn,
            preprompts_holder=preprompts_holder or PrepromptsHolder(PREPROMPTS_PATH),
        )

    async def init(self, prompt: Prompt) -> FilesDict:
        files_dict = await self.code_gen_fn(
            self.ai, prompt, self.memory, self.preprompts_holder
        )
        entrypoint = await gen_entrypoint(
            self.ai, prompt, files_dict, self.memory, self.preprompts_holder
        )
        combined_dict = {**files_dict, **entrypoint}
        files_dict = FilesDict(combined_dict)
        files_dict = await self.process_code_fn(
            self.ai,
            self.execution_env,
            files_dict,
            preprompts_holder=self.preprompts_holder,
            prompt=prompt,
            memory=self.memory,
        )
        return files_dict

    async def improve(
        self,
        files_dict: FilesDict,
        prompt: Prompt,
        execution_command: Optional[str] = None,
        diff_timeout=3,
    ) -> FilesDict:
        files_dict = await self.improve_fn(
            self.ai,
            prompt,
            files_dict,
            self.memory,
            self.preprompts_holder,
            diff_timeout=diff_timeout,
        )
        return files_dict
