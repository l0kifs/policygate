"""Schema regression tests for policygate MCP tools."""

from __future__ import annotations

import asyncio
from types import SimpleNamespace

import pytest

from policygate.entry_points import mcp_server

mcp = mcp_server.mcp


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


def test_build_service_reuses_cached_instance(monkeypatch: pytest.MonkeyPatch) -> None:
    gateway_init_calls = 0

    class FakeGateway:
        def __init__(self, **_: object) -> None:
            nonlocal gateway_init_calls
            gateway_init_calls += 1

    fake_settings = SimpleNamespace(
        github_repository_url="https://github.com/owner/repo",
        github_access_token="token",
        local_repo_data_dir="~/.policygate/repo_data",
        repository_refresh_interval_seconds=1800,
    )

    monkeypatch.setattr(mcp_server, "get_settings", lambda: fake_settings)
    monkeypatch.setattr(mcp_server, "GitHubRepositoryGateway", FakeGateway)
    mcp_server.build_service.cache_clear()

    first = mcp_server.build_service()
    second = mcp_server.build_service()

    assert first is second
    assert gateway_init_calls == 1

    mcp_server.build_service.cache_clear()
