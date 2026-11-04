"""MCP (Model Context Protocol) server interface.

Canonical location of the MCP server implementation, migrated from
``gpt_computer.interfaces.mcp``.
"""

from .pa_provider import (
    SAFE_MODULES,
    PaProviderRegistry,
    SafeExecutionResult,
    execute_safe_code,
    get_pa_registry,
    get_workspace_dir,
    list_pa_providers,
    load_pa_provider,
)
from .server import MCPRequest, MCPServer
from .tools import (
    CreateDirectoryTool,
    CreateFileTool,
    FetchWebpageTool,
    FileDeleteTool,
    FileListTool,
    FileReadTool,
    FileSearchGlobTool,
    GithubRepoTool,
    GithubTextSearchTool,
    GrepSearchTool,
    ImageGenerationTool,
    MarkItDownTool,
    PythonExecuteTool,
    TextToAudioTool,
    TokenOptimizerTool,
    WebSearchTool,
)

__all__ = [
    "MCPServer",
    "MCPRequest",
    "MarkItDownTool",
    "TextToAudioTool",
    "WebSearchTool",
    "ImageGenerationTool",
    "PythonExecuteTool",
    "FileReadTool",
    "FileListTool",
    "FileDeleteTool",
    "CreateDirectoryTool",
    "CreateFileTool",
    "FetchWebpageTool",
    "FileSearchGlobTool",
    "GrepSearchTool",
    "GithubRepoTool",
    "GithubTextSearchTool",
    "TokenOptimizerTool",
    "execute_safe_code",
    "load_pa_provider",
    "list_pa_providers",
    "get_workspace_dir",
    "get_pa_registry",
    "SAFE_MODULES",
    "SafeExecutionResult",
    "PaProviderRegistry",
]
