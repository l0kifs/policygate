"""GitHub repository gateway with local caching for policy assets."""

from __future__ import annotations

import json
import shutil
import tarfile
import tempfile
import threading
import time
from io import BytesIO
from pathlib import Path
from urllib.parse import urlparse

import httpx

from policygate.domains.gateway.exceptions import RepositorySyncError


class GitHubRepositoryGateway:
    """Synchronize a GitHub repository and expose files from local cache."""

    def __init__(
        self,
        repository_url: str,
        access_token: str,
        local_repo_data_dir: str,
        refresh_interval_seconds: int = 60,
    ) -> None:
        if not repository_url:
            raise RepositorySyncError("github_repository_url is not configured")
        if not access_token:
            raise RepositorySyncError("github_access_token is not configured")

        self._repository_url = repository_url
        self._access_token = access_token
        self._local_repo_data_dir = Path(local_repo_data_dir).expanduser().resolve()
        self._refresh_interval_seconds = max(refresh_interval_seconds, 1)
        self._last_refresh_check_at = 0.0
        self._refresh_lock = threading.Lock()

        self._owner, self._repo = self._parse_owner_repo(repository_url)
        self._metadata_file = self._local_repo_data_dir / ".policygate_sync.json"

    def refresh_if_needed(self) -> None:
        """Refresh local cache if check interval elapsed and commit changed."""
        with self._refresh_lock:
            now = time.time()
            if (
                now - self._last_refresh_check_at < self._refresh_interval_seconds
                and self._local_repo_data_dir.exists()
            ):
                return

            self._last_refresh_check_at = now
            self._refresh(force=not self._local_repo_data_dir.exists())

    def force_refresh(self) -> None:
        """Force synchronization regardless of refresh interval and cached SHA."""
        with self._refresh_lock:
            self._refresh(force=True)
            self._last_refresh_check_at = time.time()

    def read_text(self, relative_path: str) -> str:
        """Read text file from synchronized local repository cache."""
        target = self._resolve_relative_path(relative_path)
        return target.read_text(encoding="utf-8")

    def read_many_texts(self, relative_paths: list[str]) -> dict[str, str]:
        """Read multiple files from local repository cache."""
        content_by_path: dict[str, str] = {}
        for relative_path in relative_paths:
            target = self._resolve_relative_path(relative_path)
            content_by_path[relative_path] = target.read_text(encoding="utf-8")
        return content_by_path

    def copy_many_files(
        self,
        relative_paths: list[str],
        destination_directory: str,
    ) -> list[str]:
        """Copy files from local cache to destination directory."""
        destination = Path(destination_directory).resolve()
        destination.mkdir(parents=True, exist_ok=True)

        copied: list[str] = []
        for relative_path in relative_paths:
            source = self._resolve_relative_path(relative_path)
            target = destination / Path(relative_path).name
            shutil.copy2(source, target)
            copied.append(str(target))
        return copied

    def _refresh(self, force: bool = False) -> None:
        default_branch, latest_sha, tarball_url = self._get_repository_state()
        cached_sha = self._read_cached_sha()

        if not force and cached_sha == latest_sha:
            return

        self._download_and_extract(tarball_url=tarball_url)
        self._write_metadata(
            {
                "repository": f"{self._owner}/{self._repo}",
                "default_branch": default_branch,
                "sha": latest_sha,
                "synced_at": int(time.time()),
            }
        )

    def _get_repository_state(self) -> tuple[str, str, str]:
        headers = self._build_headers()

        with httpx.Client(timeout=30.0, headers=headers) as client:
            repository_response = client.get(
                f"https://api.github.com/repos/{self._owner}/{self._repo}"
            )
            repository_response.raise_for_status()
            repository_payload = repository_response.json()

            default_branch = repository_payload["default_branch"]
            tarball_url = self._resolve_tarball_url(
                repository_payload=repository_payload,
                default_branch=default_branch,
            )

            commit_response = client.get(
                f"https://api.github.com/repos/{self._owner}/{self._repo}/commits/{default_branch}"
            )
            commit_response.raise_for_status()
            latest_sha = commit_response.json()["sha"]

        return default_branch, latest_sha, tarball_url

    def _resolve_tarball_url(
        self,
        repository_payload: dict,
        default_branch: str,
    ) -> str:
        tarball_url = repository_payload.get("tarball_url")
        if isinstance(tarball_url, str) and tarball_url:
            if "{/ref}" in tarball_url:
                return tarball_url.replace("{/ref}", f"/{default_branch}")
            return tarball_url

        archive_url = repository_payload.get("archive_url")
        if isinstance(archive_url, str) and archive_url:
            url = archive_url.replace("{/archive_format}", "/tarball")
            url = url.replace("{archive_format}", "tarball")
            if "{/ref}" in url:
                return url.replace("{/ref}", f"/{default_branch}")
            return url.rstrip("/") + f"/{default_branch}"

        return f"https://api.github.com/repos/{self._owner}/{self._repo}/tarball/{default_branch}"

    def _download_and_extract(self, tarball_url: str) -> None:
        headers = self._build_headers()
        with httpx.Client(
            timeout=60.0, headers=headers, follow_redirects=True
        ) as client:
            archive_response = client.get(tarball_url)
            archive_response.raise_for_status()
            archive_bytes = archive_response.content

        with tempfile.TemporaryDirectory(prefix="policygate-sync-") as temp_dir:
            temp_path = Path(temp_dir)
            with tarfile.open(fileobj=BytesIO(archive_bytes), mode="r:gz") as archive:
                archive.extractall(path=temp_path)

            extracted_roots = [child for child in temp_path.iterdir() if child.is_dir()]
            if not extracted_roots:
                raise RepositorySyncError("unable to extract repository archive")

            source_root = extracted_roots[0]
            self._copy_repository_entries(source_root)

    def _copy_repository_entries(self, source_root: Path) -> None:
        required_entries = ["router.yaml", "rules"]
        optional_entries = ["scripts"]

        self._local_repo_data_dir.mkdir(parents=True, exist_ok=True)
        for child in list(self._local_repo_data_dir.iterdir()):
            if child.name == self._metadata_file.name:
                continue
            if child.is_dir():
                shutil.rmtree(child)
            else:
                child.unlink()

        for entry in required_entries:
            source_path = source_root / entry
            if not source_path.exists():
                raise RepositorySyncError(
                    f"repository is missing required entry: {entry}"
                )
            self._copy_entry(source_path=source_path, target_name=entry)

        for entry in optional_entries:
            source_path = source_root / entry
            if not source_path.exists():
                continue
            self._copy_entry(source_path=source_path, target_name=entry)

    def _copy_entry(self, source_path: Path, target_name: str) -> None:
        target_path = self._local_repo_data_dir / target_name
        if source_path.is_dir():
            shutil.copytree(source_path, target_path, dirs_exist_ok=True)
        else:
            shutil.copy2(source_path, target_path)

    def _resolve_relative_path(self, relative_path: str) -> Path:
        if not relative_path:
            raise RepositorySyncError("relative path cannot be empty")

        candidate = (self._local_repo_data_dir / relative_path).resolve()
        base = self._local_repo_data_dir.resolve()
        if base not in candidate.parents and candidate != base:
            raise RepositorySyncError("path traversal is not allowed")
        if not candidate.exists() or not candidate.is_file():
            raise RepositorySyncError(f"file not found: {relative_path}")
        return candidate

    def _read_cached_sha(self) -> str | None:
        if not self._metadata_file.exists():
            return None
        try:
            payload = json.loads(self._metadata_file.read_text(encoding="utf-8"))
            return payload.get("sha")
        except (json.JSONDecodeError, OSError):
            return None

    def _write_metadata(self, payload: dict[str, str | int]) -> None:
        self._metadata_file.parent.mkdir(parents=True, exist_ok=True)
        self._metadata_file.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def _parse_owner_repo(self, repository_url: str) -> tuple[str, str]:
        parsed = urlparse(repository_url)
        path = parsed.path.strip("/")
        if path.endswith(".git"):
            path = path[:-4]

        segments = path.split("/")
        if len(segments) < 2:
            raise RepositorySyncError(
                "github_repository_url must include owner and repository name"
            )
        return segments[0], segments[1]

    def _build_headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self._access_token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
