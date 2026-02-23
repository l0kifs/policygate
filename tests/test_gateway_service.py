"""Unit tests for policy gateway service."""

from __future__ import annotations

from pathlib import Path

import pytest

from policygate.domains.gateway.exceptions import RouterReferenceError
from policygate.domains.gateway.services import PolicyGatewayService


class StubRepositoryGateway:
    """In-memory repository gateway stub for service tests."""

    def __init__(self) -> None:
        self.router = """
tasks:
  task1:
    description: Example task
    rules: [rule1]
    scripts: [script1]
rules:
  rule1:
    path: rules/rule1.md
    description: Rule one
scripts:
  script1:
    path: scripts/script1.py
    description: Script one
""".strip()
        self.files = {
            "rules/rule1.md": "# rule",
            "scripts/script1.py": "print('ok')\n",
        }
        self.refresh_calls = 0
        self.force_refresh_calls = 0

    def refresh_if_needed(self) -> None:
        self.refresh_calls += 1

    def read_text(self, relative_path: str) -> str:
        if relative_path == "router.yaml":
            return self.router
        return self.files[relative_path]

    def force_refresh(self) -> None:
        self.force_refresh_calls += 1

    def read_many_texts(self, relative_paths: list[str]) -> dict[str, str]:
        return {path: self.files[path] for path in relative_paths}

    def copy_many_files(
        self,
        relative_paths: list[str],
        destination_directory: str,
    ) -> list[str]:
        destination = Path(destination_directory)
        destination.mkdir(parents=True, exist_ok=True)
        copied: list[str] = []
        for path in relative_paths:
            target = destination / Path(path).name
            target.write_text(self.files[path], encoding="utf-8")
            copied.append(str(target))
        return copied


def test_outline_router_returns_router_document() -> None:
    gateway = StubRepositoryGateway()
    service = PolicyGatewayService(repository_gateway=gateway)

    outlined = service.outline_router()

    assert "# Router" in outlined
    assert "## Tasks" in outlined
    assert "## Rules" in outlined
    assert "## Scripts" in outlined
    assert "### task1" in outlined
    assert gateway.refresh_calls == 1


def test_read_rules_returns_selected_rule_content() -> None:
    gateway = StubRepositoryGateway()
    service = PolicyGatewayService(repository_gateway=gateway)

    payload = service.read_rules(["rule1"])

    assert "<rule1>" in payload
    assert "</rule1>" in payload
    assert "# rule" in payload


def test_read_rules_raises_for_unknown_alias() -> None:
    gateway = StubRepositoryGateway()
    service = PolicyGatewayService(repository_gateway=gateway)

    with pytest.raises(RouterReferenceError):
        service.read_rules(["missing"])


def test_copy_scripts_creates_temp_destination_with_files() -> None:
    gateway = StubRepositoryGateway()
    service = PolicyGatewayService(repository_gateway=gateway)

    copied = service.copy_scripts(["script1"])

    assert copied.destination_directory
    assert len(copied.copied_files) == 1
    copied_path = Path(copied.copied_files[0])
    assert copied_path.exists()
    assert copied_path.read_text(encoding="utf-8") == "print('ok')\n"


def test_sync_repository_forces_refresh() -> None:
    gateway = StubRepositoryGateway()
    service = PolicyGatewayService(repository_gateway=gateway)

    payload = service.sync_repository()

    assert payload == {"status": "synced"}
    assert gateway.force_refresh_calls == 1
