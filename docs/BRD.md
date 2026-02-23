# Business Requirements Document: AI Agent Rules Gateway

## Overview

An MCP server that acts as a gateway for AI agent task-specific rules and scripts stored in a GitHub repository. The server fetches and caches the repository locally, then exposes its contents to AI agents via MCP tools.

## Stack

- Python, FastMCP, Pydantic, pydantic-settings, httpx

## Functional Requirements

### 1. Repository Integration

- Connect to a user-specified GitHub repository using a provided access token.
- Clone/fetch the repository to local storage: `~/.gateway_name/repo_data`.
- Monitor the repository for changes and keep local data up-to-date.

### 2. Repository Structure (Expected)

```
rules/        # Markdown files defining AI agent rules
scripts/      # Python scripts implementing task logic
router.yaml   # Routing configuration
```

### 3. `router.yaml` Schema

```yaml
tasks:
  task1:
    description: "Short description of task 1"
    rules:
      - rule1
    scripts:
      - script1
rules:
  rule1:
    path: rules/rule1.md
    description: "Short description of rule 1"
scripts:
  script1:
    path: scripts/script1.py
    description: "Short description of script 1"
```

### 4. MCP Server Tools

| Tool           | Description                                             |
| -------------- | ------------------------------------------------------- |
| Outline router | Parse and return the contents of `router.yaml`          |
| Read rules     | Return the content of specified rule `.md` files        |
| Copy scripts   | Copy specified scripts to a temp location for execution |

## Configuration

User must supply:
- GitHub repository URL
- GitHub access token
