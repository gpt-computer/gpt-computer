"""
Preprompts Holder Module

Provides a holder for preprompt texts stored on disk.

Classes:
    PrepromptsHolder: Retrieves preprompt texts from a specified directory.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict

from gpt_computer.agent.memory.disk import DiskMemory


class PrepromptsHolder:
    def __init__(self, preprompts_path: Path):
        self.preprompts_path = preprompts_path

    def get_preprompts(self) -> Dict[str, str]:
        preprompts_repo = DiskMemory(self.preprompts_path)
        return {file_name: preprompts_repo[file_name] for file_name in preprompts_repo}
