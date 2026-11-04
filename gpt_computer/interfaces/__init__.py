"""
Interfaces Package

Provides user-facing interfaces for the gpt_computer application.

Submodules:
    cli: Command-line interface
    api: REST API (FastAPI)
    gui: GUI components
    tray: System tray
    mcp: MCP protocol support
"""

import importlib

_EXPORTS = {
    "CliAgent": ("gpt_computer.interfaces.cli", "CliAgent"),
    "FileSelector": ("gpt_computer.interfaces.cli", "FileSelector"),
    "collect_and_send_human_review": (
        "gpt_computer.interfaces.cli",
        "collect_and_send_human_review",
    ),
    "app": ("gpt_computer.interfaces.api", "app"),
    "AgentRunRequest": ("gpt_computer.interfaces.api", "AgentRunRequest"),
    "AgentRunResponse": ("gpt_computer.interfaces.api", "AgentRunResponse"),
    "HealthResponse": ("gpt_computer.interfaces.api", "HealthResponse"),
}

__all__ = list(_EXPORTS)


def __getattr__(name):
    export = _EXPORTS.get(name)
    if export is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    module_name, attribute_name = export
    module = importlib.import_module(module_name)
    return getattr(module, attribute_name)
