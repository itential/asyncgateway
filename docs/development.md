# Development Environment Setup

This guide covers setting up a development environment for asyncgateway.

## Prerequisites

- Python 3.10 or higher (dev environment pinned to 3.11 via `.python-version`)
- Git
- [uv](https://github.com/astral-sh/uv) package manager

## Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd asyncgateway
   ```

2. **Install uv (if not already installed):**
   ```bash
   # On macOS and Linux
   curl -LsSf https://astral.sh/uv/install.sh | sh

   # On Windows
   powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```

3. **Set up the development environment:**
   ```bash
   uv sync --group dev
   ```

## Development Workflow

### Package Management
- **Add a dependency:** `uv add <package>`
- **Remove a dependency:** `uv remove <package>`
- **Sync dependencies:** `uv sync --group dev`

### Running Tests
- **Run all tests:** `uv run pytest`
- **Run tests with verbose output:** `uv run pytest -v`
- **Run tests with coverage:** `uv run pytest -v --cov`
- **Run specific test pattern:** `uv run pytest -k <pattern>`

No live IAG instance is required — all tests mock `ipsdk`.

### Multi-version Testing

Tests run across Python 3.10–3.13 via tox:

```bash
tox                # all versions
tox -e py312       # single version
```

### Code Quality
- **Lint:** `uv run ruff check src tests`
- **Format:** `uv run ruff format src tests`
- **Type check:** `uv run mypy src/`
- **Security scan:** `uv run bandit -r src/asyncgateway --configfile pyproject.toml`

### Full Local CI

Run the complete CI suite (lint + typecheck + security + tests) with:

```bash
make ci
```

### Building the Package
- **Build distributions:** `uv build`

## Project Structure

```
asyncgateway/
├── src/asyncgateway/
│   ├── __init__.py         # Public API: client, logging
│   ├── client.py           # Client class with service/resource discovery
│   ├── exceptions.py       # Exception hierarchy (AsyncGatewayError, ValidationError)
│   ├── logging.py          # Logging with sensitive data filtering
│   ├── serdes.py           # JSON / YAML / TOML serialization utilities
│   ├── services/           # 23 thin async wrappers, one per IAG API tag group
│   └── resources/          # 22 declarative resource abstractions
├── tests/                  # Test files (mock ipsdk, no live IAG needed)
├── docs/                   # Documentation
└── pyproject.toml          # Project configuration and tool settings
```

## Optional Dependencies

The core library requires only `ipsdk`.  Additional serialization formats can
be unlocked by installing optional packages:

| Format | Operation | Package | Python version |
|--------|-----------|---------|----------------|
| YAML   | read & write | `PyYAML` | any |
| TOML   | read | *(stdlib `tomllib`)* | 3.11+ |
| TOML   | read | `tomli` | 3.10 only |
| TOML   | write | `tomli-w` | any |

Install a single optional format:

```bash
uv add PyYAML          # YAML support
uv add tomli           # TOML read on Python 3.10
uv add tomli-w         # TOML write (any version)
```

Install all optional serialization extras at once:

```bash
uv add PyYAML tomli-w  # tomli only needed on Python 3.10
```

You can inspect runtime availability from Python:

```python
from asyncgateway.serdes import YAML_AVAILABLE, TOML_AVAILABLE, TOML_WRITE_AVAILABLE
```

Calling a function whose dependency is absent raises `ValidationError` (not
`ImportError`), so callers do not need to guard imports.

## Development Notes

- Services and resources are filesystem-discovered at client init. Adding a file with a `Service` or `Resource` class and a `name` attribute is sufficient for registration — no other wiring required.
- `Operation` (`MERGE`, `REPLACE`, `OVERWRITE`) is a plain string class, not an enum. It lives in `services/__init__.py` and is re-exported from `resources/__init__.py`.
- Logging is silent by default (level `NONE = 100`). Enable with `asyncgateway.logging.set_level(asyncgateway.logging.DEBUG)`.
- `client.load(path, op)` reads files from a directory tree and dispatches to `service.load()`. `client.resources.devices.load(data, op)` takes an in-memory list. These are separate code paths.
- `playbooks.get_all()` uses a manual pagination loop and does not call `_get_all()` — the playbooks endpoint uses `meta["count"]` rather than `meta["total_count"]`.

## Contributing

1. Make your changes following the existing code style.
2. Run the full CI suite before committing:
   ```bash
   make ci
   ```
3. Ensure all tests pass and coverage remains high.
4. Raise typed exceptions from `exceptions.py`. Never raise bare `Exception`.
5. Services must be thin — one method per API operation, return `res.json()`, no logic.
6. Resources catch broad `Exception` for "not found" detection (ipsdk exception types are not part of the public contract).

## Troubleshooting

- If you encounter import errors, ensure all dependencies are installed with `uv sync --group dev`.
- For test failures, run with `-v` for more detailed output.
- If tests mock `os.listdir`, note that `Client.__init__` calls it **twice** — once for `services/` and once for `resources/`. Use `side_effect=[service_files, resource_files]`.
- YAML support is optional. If `PyYAML` is not installed, YAML paths raise `ValidationError` rather than `ImportError`.
- TOML read support is optional on Python 3.10 (install `tomli`); on 3.11+ it uses the stdlib `tomllib`. TOML write always requires `tomli-w`.
