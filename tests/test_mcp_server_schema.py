"""Schema regression tests for policygate MCP tools."""

from __future__ import annotations

import asyncio

from policygate.entry_points.mcp_server import mcp


def test_outline_router_tool_registered() -> None:
    async def _get_tool() -> dict:
        tool = await mcp.get_tool("outline_router")
        return tool.parameters

    parameters = asyncio.run(_get_tool())
    assert parameters["type"] == "object"


def test_sync_repository_tool_registered() -> None:
    async def _get_tool() -> dict:
        tool = await mcp.get_tool("sync_repository")
        return tool.parameters

    parameters = asyncio.run(_get_tool())
    assert parameters["type"] == "object"


def test_read_rules_schema_has_string_items() -> None:
    async def _get_schema() -> dict:
        tool = await mcp.get_tool("read_rules")
        return tool.parameters["properties"]["rule_names"]

    schema = asyncio.run(_get_schema())
    assert schema["type"] == "array"
    assert schema["items"]["type"] == "string"


def test_copy_scripts_schema_has_string_items() -> None:
    async def _get_schema() -> dict:
        tool = await mcp.get_tool("copy_scripts")
        return tool.parameters["properties"]["script_names"]

    schema = asyncio.run(_get_schema())
    assert schema["type"] == "array"
    assert schema["items"]["type"] == "string"
