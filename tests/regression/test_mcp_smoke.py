"""MCP startup and protocol smoke tests."""

import asyncio

from gpt_computer.interfaces.mcp import MCPServer
from gpt_computer.interfaces.mcp.server import MCPRequest


def test_mcp_server_initializes_and_lists_tools():
    server = MCPServer(safe_mode=True)

    response = asyncio.run(server.handle_request(MCPRequest(id=1, method="initialize")))

    assert response.error is None
    assert response.result["serverInfo"]["name"] == "gpt-computer-mcp-server"
    assert response.result["protocolVersion"] == "2024-11-05"
    assert "tools" in response.result["capabilities"]

    tools_response = asyncio.run(
        server.handle_request(MCPRequest(id=2, method="tools/list"))
    )
    tool_names = {tool["name"] for tool in tools_response.result["tools"]}
    assert "file_read" in tool_names
    assert "python_execute" in tool_names
