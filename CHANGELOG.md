# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.3] - 2026-03-02

### Added
- Centralized logging configuration with outputs to stderr and `~/.policygate/policygate.log`.
- New optional settings: `POLICYGATE__LOG_LEVEL` and `POLICYGATE__LOG_FILE_PATH`.
- Regression test for logging setup to verify log directory and file creation.

### Changed
- Unified runtime logging usage across service, MCP entry point, and repository gateway via shared logger configuration.
- Added operational logging for tool execution, repository synchronization, and router-loading paths.

## [0.1.2] - 2026-02-23

### Changed
- `outline_router` now hides rule file paths and returns only rule aliases with descriptions in the rules section.

### Fixed
- Added regression test coverage to ensure router outline output does not expose rule file paths.

## [0.1.1] - 2026-02-23

### Added
- Regression test to ensure MCP service construction is cached across tool calls.

### Changed
- Reused a single cached service instance in MCP entrypoint to preserve repository refresh interval behavior between requests.
- Updated documentation default for `POLICYGATE__REPOSITORY_REFRESH_INTERVAL_SECONDS` from `60` to `1800` to match runtime settings.

## [0.1.0] - 2026-02-23

### Added
- Initial project scaffolding for `policygate`.
- Business Requirements Document in `docs/BRD.md`.
- MCP server entry point and domain/infrastructure layers.
- GitHub repository integration and synchronized local cache.
- Router parsing and validation support for task/rule/script mapping.
- Threading support and improved repository synchronization behavior.

### Changed
- Renamed project from template to `policygate`.
- Enhanced package metadata in `pyproject.toml` for PyPI publishing.

[0.1.0]: https://github.com/l0kifs/policygate/releases/tag/v0.1.0
[0.1.1]: https://github.com/l0kifs/policygate/compare/v0.1.0...v0.1.1
[0.1.2]: https://github.com/l0kifs/policygate/compare/v0.1.1...v0.1.2
[0.1.3]: https://github.com/l0kifs/policygate/compare/v0.1.2...v0.1.3
