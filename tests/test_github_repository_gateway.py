"""Unit tests for GitHub repository gateway internals."""

from __future__ import annotations

from pathlib import Path

import pytest

from policygate.domains.gateway.exceptions import RepositorySyncError
from policygate.infrastructure.repository.github_repository_gateway import (
    GitHubRepositoryGateway,
)


def _build_gateway() -> GitHubRepositoryGateway:
    return GitHubRepositoryGateway(
        repository_url="https://github.com/owner/repo",
        access_token="token",
        local_repo_data_dir="~/.policygate/test_repo_data",
        refresh_interval_seconds=60,
    )


def test_resolve_tarball_url_uses_tarball_url_placeholder() -> None:
    gateway = _build_gateway()

    resolved = gateway._resolve_tarball_url(
        repository_payload={
            "tarball_url": "https://api.github.com/repos/owner/repo/tarball{/ref}"
        },
        default_branch="main",
    )

    assert resolved == "https://api.github.com/repos/owner/repo/tarball/main"


def test_resolve_tarball_url_falls_back_to_archive_url() -> None:
    gateway = _build_gateway()

    resolved = gateway._resolve_tarball_url(
        repository_payload={
            "archive_url": "https://api.github.com/repos/owner/repo/{archive_format}{/ref}"
        },
        default_branch="main",
    )

    assert resolved == "https://api.github.com/repos/owner/repo/tarball/main"


def test_resolve_tarball_url_uses_default_when_missing_keys() -> None:
    gateway = _build_gateway()

    resolved = gateway._resolve_tarball_url(
        repository_payload={},
        default_branch="main",
    )

    assert resolved == "https://api.github.com/repos/owner/repo/tarball/main"


def test_copy_repository_entries_allows_missing_scripts(tmp_path: Path) -> None:
    gateway = GitHubRepositoryGateway(
        repository_url="https://github.com/owner/repo",
        access_token="token",
        local_repo_data_dir=str(tmp_path / "cache"),
        refresh_interval_seconds=60,
    )
    source_root = tmp_path / "source"
    source_root.mkdir(parents=True, exist_ok=True)
    (source_root / "router.yaml").write_text("tasks: {}\nrules: {}\n", encoding="utf-8")
    (source_root / "rules").mkdir(parents=True, exist_ok=True)
    (source_root / "rules" / "rule1.md").write_text("# rule\n", encoding="utf-8")

    gateway._copy_repository_entries(source_root)

    assert (tmp_path / "cache" / "router.yaml").exists()
    assert (tmp_path / "cache" / "rules").exists()
    assert not (tmp_path / "cache" / "scripts").exists()


def test_copy_repository_entries_requires_rules(tmp_path: Path) -> None:
    gateway = GitHubRepositoryGateway(
        repository_url="https://github.com/owner/repo",
        access_token="token",
        local_repo_data_dir=str(tmp_path / "cache"),
        refresh_interval_seconds=60,
    )
    source_root = tmp_path / "source"
    source_root.mkdir(parents=True, exist_ok=True)
    (source_root / "router.yaml").write_text("tasks: {}\nrules: {}\n", encoding="utf-8")

    with pytest.raises(RepositorySyncError, match="missing required entry: rules"):
        gateway._copy_repository_entries(source_root)
