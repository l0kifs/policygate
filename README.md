<p align="center">
	<img src="https://capsule-render.vercel.app/api?type=waving&color=0:4F46E5,100:06B6D4&height=200&section=header&text=policygate&fontSize=56&fontColor=ffffff&animation=fadeIn&fontAlignY=38&desc=MCP%20server%20gateway%20for%20task-specific%20AI%20rules%20and%20scripts&descAlignY=58&descSize=16" alt="policygate banner" />
</p>

<p align="center">
	<a href="https://github.com/l0kifs/policygate/actions/workflows/publish-to-pypi.yml"><img src="https://img.shields.io/github/actions/workflow/status/l0kifs/policygate/publish-to-pypi.yml?branch=main&label=publish" alt="Publish workflow" /></a>
	<a href="https://pypi.org/project/policygate/"><img src="https://img.shields.io/pypi/v/policygate" alt="PyPI version" /></a>
	<a href="https://pypi.org/project/policygate/"><img src="https://img.shields.io/pypi/pyversions/policygate" alt="Python versions" /></a>
	<a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="MIT license" /></a>
</p>

# policygate

Policygate is an MCP server gateway for task-specific AI rules and scripts stored in a GitHub repository.

## Features

- Syncs repository content into a local cache at `~/.policygate/repo_data`
- Parses and validates `router.yaml`
- Exposes MCP tools:
	- `sync_repository`
	- `outline_router`
	- `read_rules`
	- `copy_scripts`

Detailed usage reference: [docs/REFERENCE.md](docs/REFERENCE.md)

## Required repository structure

```text
rules/
scripts/
router.yaml
```

## Configuration

Set environment variables:

- `POLICYGATE__GITHUB_REPOSITORY_URL`
- `POLICYGATE__GITHUB_ACCESS_TOKEN`
- `POLICYGATE__LOCAL_REPO_DATA_DIR` (optional, default `~/.policygate/repo_data`)
- `POLICYGATE__REPOSITORY_REFRESH_INTERVAL_SECONDS` (optional, default `60`)

## Run MCP server

Run with:

```bash
uv run policygate-mcp
```

VS Code workspace MCP config example (`.vscode/mcp.json`):

```json
{
    "inputs": [
		{
			"id": "POLICYGATE__GITHUB_REPOSITORY_URL",
			"type": "promptString",
			"description": "GitHub repository URL",
			"password": false
		},
		{
			"id": "POLICYGATE__GITHUB_ACCESS_TOKEN",
			"type": "promptString",
			"description": "GitHub access token",
			"password": true
		}
	],
	"servers": {
		"policygate": {
			"type": "stdio",
			"command": "uvx",
			"args": ["--from", "policygate:latest", "policygate-mcp"],
            "env": {
				"POLICYGATE__GITHUB_REPOSITORY_URL": "${input:POLICYGATE__GITHUB_REPOSITORY_URL}",
				"POLICYGATE__GITHUB_ACCESS_TOKEN": "${input:POLICYGATE__GITHUB_ACCESS_TOKEN}"
			},
		}
	}
}
```

For local testing from the current workspace (after `uv sync --all-groups`):

```json
{
    "inputs": [
		{
			"id": "POLICYGATE__GITHUB_REPOSITORY_URL",
			"type": "promptString",
			"description": "GitHub repository URL",
			"password": false
		},
		{
			"id": "POLICYGATE__GITHUB_ACCESS_TOKEN",
			"type": "promptString",
			"description": "GitHub access token",
			"password": true
		}
	],
	"servers": {
		"policygate-local": {
			"type": "stdio",
			"command": "uv",
			"args": ["run", "policygate-mcp"],
            "env": {
				"POLICYGATE__GITHUB_REPOSITORY_URL": "${input:POLICYGATE__GITHUB_REPOSITORY_URL}",
				"POLICYGATE__GITHUB_ACCESS_TOKEN": "${input:POLICYGATE__GITHUB_ACCESS_TOKEN}"
			},
			"cwd": "${workspaceFolder}"
		}
	}
}
```

## Testing

Run feature-organized end-to-end suites:

```bash
uv run pytest --maxfail=1 --tb=short
```
