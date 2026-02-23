"""MCP server entry point for policy routing gateway."""

from __future__ import annotations

from dataclasses import asdict, is_dataclass
from typing import Annotated, Any

from fastmcp import FastMCP
from pydantic import Field

from policygate.config.settings import get_settings
from policygate.domains.gateway.services import PolicyGatewayService
from policygate.infrastructure.repository.github_repository_gateway import (
    GitHubRepositoryGateway,
)


def _to_serializable(value: Any) -> Any:
    if isinstance(value, list):
        return [_to_serializable(item) for item in value]
    if isinstance(value, dict):
        return {key: _to_serializable(item) for key, item in value.items()}
    if is_dataclass(value):
        return _to_serializable(asdict(value))
    if hasattr(value, "model_dump"):
        return value.model_dump(mode="json")
    return value


mcp = FastMCP(
    name="policygate",
    instructions=(
        "Policy gateway for task routing. Use router outline first, then read rules, "
        "and copy scripts only for scripts explicitly mapped in router.yaml."
    ),
    version=get_settings().app_version,
    on_duplicate="error",
    mask_error_details=False,
)


def build_service() -> PolicyGatewayService:
    """Build service graph with GitHub-backed repository gateway."""
    settings = get_settings()
    return PolicyGatewayService(
        repository_gateway=GitHubRepositoryGateway(
            repository_url=settings.github_repository_url,
            access_token=settings.github_access_token,
            local_repo_data_dir=settings.local_repo_data_dir,
            refresh_interval_seconds=settings.repository_refresh_interval_seconds,
        )
    )


@mcp.tool(
    annotations={
        "readOnlyHint": True,
        "idempotentHint": True,
        "openWorldHint": False,
    }
)
def outline_router() -> str:
    """Parse and return router.yaml contents as markdown text."""
    return build_service().outline_router()


@mcp.tool(
    annotations={
        "readOnlyHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    }
)
def sync_repository() -> dict[str, str]:
    """Force repository synchronization to refresh local cache now."""
    return build_service().sync_repository()


@mcp.tool(
    annotations={
        "readOnlyHint": True,
        "idempotentHint": True,
        "openWorldHint": False,
    }
)
def read_rules(
    rule_names: Annotated[
        list[str],
        Field(
            description=(
                "Rule aliases from router.yaml rules section. "
                "Example: [\"rule1\", \"rule_security\"]"
            )
        ),
    ],
) -> str:
    """Read selected rules and return a combined markdown document."""
    return build_service().read_rules(rule_names=rule_names)


@mcp.tool(
    annotations={
        "readOnlyHint": False,
        "destructiveHint": False,
        "openWorldHint": False,
    }
)
def copy_scripts(
    script_names: Annotated[
        list[str],
        Field(description="Script aliases from router.yaml scripts section."),
    ],
) -> dict[str, Any]:
    """Copy selected scripts to a temporary directory for execution."""
    return _to_serializable(build_service().copy_scripts(script_names=script_names))


def run() -> None:
    """Run MCP server."""
    mcp.run()
