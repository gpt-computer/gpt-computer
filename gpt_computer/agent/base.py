"""
Base Agent Module

Defines the abstract base class for agents that interact with code.

Classes:
    BaseAgent: Abstract base class for an agent that interacts with code.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from gpt_computer.agent.prompt import Prompt
from gpt_computer.infrastructure.files.operations import FilesDict


class BaseAgent(ABC):
    """
    Abstract base class for an agent that interacts with code.

    Defines the interface for agents capable of initializing and improving code
    based on a given prompt.
    """

    @abstractmethod
    async def init(self, prompt: Prompt) -> FilesDict:
        pass

    @abstractmethod
    async def improve(self, files_dict: FilesDict, prompt: Prompt) -> FilesDict:
        pass
