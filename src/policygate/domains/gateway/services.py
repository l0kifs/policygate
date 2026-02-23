"""Application service for policy gateway use-cases."""

from __future__ import annotations

import tempfile
from typing import Protocol

import yaml
from pydantic import ValidationError

from policygate.domains.gateway.exceptions import (
    RepositorySyncError,
    RouterReferenceError,
    RouterValidationError,
)
from policygate.domains.gateway.models import CopiedScriptsResult, RouterConfig


class RepositoryGateway(Protocol):
    """Port for repository synchronization and file access."""

    def refresh_if_needed(self) -> None: ...

    def force_refresh(self) -> None: ...

    def read_text(self, relative_path: str) -> str: ...

    def read_many_texts(self, relative_paths: list[str]) -> dict[str, str]: ...

    def copy_many_files(
        self,
        relative_paths: list[str],
        destination_directory: str,
    ) -> list[str]: ...


class PolicyGatewayService:
    """Use-case service for router outline, rules reading, and scripts copying."""

    def __init__(self, repository_gateway: RepositoryGateway) -> None:
        self._repository_gateway = repository_gateway

    def outline_router(self) -> str:
        """Return parsed and validated router.yaml content as markdown text."""
        router = self._load_router()
        return self._router_to_markdown(router)

    def sync_repository(self) -> dict[str, str]:
        """Force synchronization of remote repository to local cache."""
        self._repository_gateway.force_refresh()
        return {"status": "synced"}

    def read_rules(self, rule_names: list[str]) -> str:
        """Return rule markdown content by aliases from router.yaml as markdown text."""
        if not rule_names:
            return ""

        router = self._load_router()
        missing = [name for name in rule_names if name not in router.rules]
        if missing:
            joined = ", ".join(missing)
            raise RouterReferenceError(f"unknown rule aliases: {joined}")

        names_to_paths = {name: router.rules[name].path for name in rule_names}
        contents_by_path = self._repository_gateway.read_many_texts(
            list(names_to_paths.values())
        )
        sections: list[str] = []
        for name, path in names_to_paths.items():
            if path not in contents_by_path:
                continue
            sections.append(f"<{name}>\n{contents_by_path[path].rstrip()}\n</{name}>")

        return "\n\n".join(sections)

    def copy_scripts(self, script_names: list[str]) -> CopiedScriptsResult:
        """Copy script files by aliases to a temporary directory."""
        if not script_names:
            destination = tempfile.mkdtemp(prefix="policygate-scripts-")
            return CopiedScriptsResult(
                destination_directory=destination,
                copied_files=[],
            )

        router = self._load_router()
        missing = [name for name in script_names if name not in router.scripts]
        if missing:
            joined = ", ".join(missing)
            raise RouterReferenceError(f"unknown script aliases: {joined}")

        destination = tempfile.mkdtemp(prefix="policygate-scripts-")
        paths = [router.scripts[name].path for name in script_names]
        copied_files = self._repository_gateway.copy_many_files(
            relative_paths=paths,
            destination_directory=destination,
        )

        return CopiedScriptsResult(
            destination_directory=destination,
            copied_files=copied_files,
        )

    def _load_router(self) -> RouterConfig:
        try:
            self._repository_gateway.refresh_if_needed()
            router_raw = self._repository_gateway.read_text("router.yaml")
            parsed = yaml.safe_load(router_raw)
            if not isinstance(parsed, dict):
                raise RouterValidationError(
                    "router.yaml must contain a top-level object"
                )
            return RouterConfig.model_validate(parsed)
        except ValidationError as error:
            raise RouterValidationError(str(error)) from error
        except OSError as error:
            raise RepositorySyncError(str(error)) from error

    def _router_to_markdown(self, router: RouterConfig) -> str:
        sections: list[str] = ["# Router"]

        sections.append("## Tasks")
        if not router.tasks:
            sections.append("- _none_")
        else:
            for name, task in router.tasks.items():
                sections.append(f"### {name}")
                sections.append(f"- Description: {task.description}")
                sections.append(
                    f"- Rules: {', '.join(task.rules) if task.rules else '_none_'}"
                )
                sections.append(
                    f"- Scripts: {', '.join(task.scripts) if task.scripts else '_none_'}"
                )

        sections.append("## Rules")
        if not router.rules:
            sections.append("- _none_")
        else:
            for name, rule in router.rules.items():
                sections.append(f"- **{name}**: {rule.description}")

        sections.append("## Scripts")
        if not router.scripts:
            sections.append("- _none_")
        else:
            for name, script in router.scripts.items():
                sections.append(f"- **{name}**: `{script.path}` — {script.description}")

        return "\n".join(sections)
