import importlib

from typing import TYPE_CHECKING

from gpt_computer.agent.default.constants import MAX_EDIT_REFINEMENT_STEPS
from gpt_computer.agent.default.paths import (
    CODE_GEN_LOG_FILE,
    DEBUG_LOG_FILE,
    DIFF_LOG_FILE,
    ENTRYPOINT_FILE,
    ENTRYPOINT_LOG_FILE,
    IMPROVE_LOG_FILE,
    MEMORY_REL_PATH,
    META_DATA_REL_PATH,
    PREPROMPTS_PATH,
    memory_path,
    metadata_path,
)

if TYPE_CHECKING:
    from gpt_computer.agent.default.simple_agent import (
        SimpleAgent,
        default_config_agent,
    )


def __getattr__(name):
    if name not in {"SimpleAgent", "default_config_agent"}:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    module = importlib.import_module("gpt_computer.agent.default.simple_agent")
    return getattr(module, name)


__all__ = [
    "MAX_EDIT_REFINEMENT_STEPS",
    "CODE_GEN_LOG_FILE",
    "DEBUG_LOG_FILE",
    "DIFF_LOG_FILE",
    "ENTRYPOINT_FILE",
    "ENTRYPOINT_LOG_FILE",
    "IMPROVE_LOG_FILE",
    "MEMORY_REL_PATH",
    "META_DATA_REL_PATH",
    "PREPROMPTS_PATH",
    "memory_path",
    "metadata_path",
    "SimpleAgent",
    "default_config_agent",
]
