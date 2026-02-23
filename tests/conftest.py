"""Shared fixtures for policygate tests."""

from __future__ import annotations

import asyncio
from collections.abc import Callable
from typing import Any

import pytest
from fastmcp import Client

from policygate.entry_points.mcp_server import mcp


@pytest.fixture
def mcp_call() -> Callable[[str, dict[str, Any]], Any]:
    """Call MCP tools through in-memory client transport."""

    def _call(tool_name: str, arguments: dict[str, Any]) -> Any:
        async def _run() -> Any:
            async with Client(mcp) as client:
                result = await client.call_tool(name=tool_name, arguments=arguments)
                if (
                    isinstance(result.structured_content, dict)
                    and "result" in result.structured_content
                ):
                    return result.structured_content["result"]
                return (
                    result.structured_content
                    if result.structured_content is not None
                    else result.data
                )

        return asyncio.run(_run())

    return _call
