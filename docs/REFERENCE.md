# Policygate MCP API Reference

## Server

- Name: `policygate`
- Entry point: `policygate.entry_points.mcp_server:run`
- Run: `uv run policygate-mcp`

## Required Environment Variables

- `POLICYGATE__GITHUB_REPOSITORY_URL`
- `POLICYGATE__GITHUB_ACCESS_TOKEN`

## Optional Environment Variables

- `POLICYGATE__LOCAL_REPO_DATA_DIR` (default: `~/.policygate/repo_data`)
- `POLICYGATE__REPOSITORY_REFRESH_INTERVAL_SECONDS` (default: `1800`)
- `POLICYGATE__LOG_LEVEL` (default: `INFO`)
- `POLICYGATE__LOG_FILE_PATH` (default: `~/.policygate/policygate.log`)

## Tools

### `sync_repository`
Force sync from GitHub to local cache.

- Args: none
- Returns:
  - `status: str` (`"synced"` on success)

### `outline_router`
Parse and return `router.yaml`.

- Args: none
- Returns:
  - `str` (Markdown text)
  - Includes sections: `Tasks`, `Rules`, `Scripts`

### `read_rules`
Read markdown rule files referenced in `router.yaml`.

- Args:
  - `rule_names: list[str]` — aliases from `router.yaml.rules`
  - Example: `rule_names = ["rule1", "rule_security"]`
- Returns:
  - `str` (combined Markdown text)
  - Output format: one section per alias (`<rule_alias> ... </rule_alias>`) + rule content

### `copy_scripts`
Copy script files referenced in `router.yaml` to a temp directory.

- Args:
  - `script_names: list[str]` — aliases from `router.yaml.scripts`
- Returns:
  - `destination_directory: str`
  - `copied_files: list[str]`

## Expected Repository Layout

```text
rules/
scripts/
router.yaml
```
