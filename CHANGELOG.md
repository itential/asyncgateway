# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-03-09

### Added

- TOML support in `serdes` module alongside existing JSON and YAML support (#16)
- `heuristics` module for connection parameter validation and normalization (#9)
- Structured logging module replacing the previous `logger` stub, with configurable log levels (#9)
- 23 async service wrappers covering all IAG 4.x API tag groups (#6)
- 22 declarative resource classes with `ensure`/`absent`/`run`/`dry_run`/`load`/`dump` patterns (#6)
- Comprehensive unit test suite with 686 tests across services and resources (#6)
- Filesystem-based bulk loader via `client.load(path, op)` dispatching to `service.load()` (#6)
- `Operation` string class (`MERGE`, `REPLACE`, `OVERWRITE`) for bulk operations (#6)
- Typed exception hierarchy rooted at `AsyncGatewayError` with HTTP status and transport error mapping (#6)
- Pagination helper `ServiceBase._get_all()` shared across service layer (#6)
- Version derived from git tags via `uv-dynamic-versioning` (#6)
- SPDX license headers across all source files for GPL v3 compliance (#11)
- GitHub Actions CI pipeline with lint, typecheck, security, and tox matrix (py310–py313) (#5, #7, #8)
- GitHub issue and PR templates, CODEOWNERS, CODE_OF_CONDUCT, CONTRIBUTING, SECURITY policy (#11, initial)
- Contributor License Agreement (#initial)

### Fixed

- Pagination infinite loop in services using `_get_all` helper (#13)
- `delete_all` filter bug in `devices` service that incorrectly scoped deletions (#13)
- Minor low-priority issues across services and resources (#14)

### Changed

- Simplified exceptions module from multiple classes to two core exception types (#10)
- Module docstrings added across all source files; stale `Operation` example corrected (#12)

[Unreleased]: https://github.com/itential/asyncgateway/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/itential/asyncgateway/releases/tag/v0.1.0
