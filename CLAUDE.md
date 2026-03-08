# CLAUDE.md

## Purpose & Architecture

`asyncgateway` is an async Python client library for the Itential Automation Gateway (IAG) 4.x REST API. It is structured in two layers: a **services layer** of thin async wrappers that map 1:1 to API endpoints, and a **resources layer** of declarative abstractions that compose services into atomic, idempotent operations. Both are exposed through a single `Client` instance as `client.services.{name}` and `client.resources.{name}`.

**Module responsibilities:**

- `client.py` — `Client` class with two `_Namespace` containers (`services`, `resources`). On init, scans `services/` and `resources/` directories via `importlib`, instantiates each `Service`/`Resource` class, and attaches it to the appropriate namespace by its `.name` attribute. All `**kwargs` pass through to `ipsdk.gateway_factory(want_async=True, **kwargs)`. `client.load(path, op)` is a filesystem bulk loader that dispatches to `service.load(data, op)` for any service that exposes one.
- `services/` — 23 files covering all IAG API tag groups. Each file has one `Service(ServiceBase)` class. Methods call `self.client.{verb}(path)` and return `res.json()` — no logic. Pagination handled by the shared `ServiceBase._get_all(path, **params)` helper.
- `resources/` — 22 files. Each has one `Resource(ResourceBase)` class that receives the `services` namespace as `self.services`. Implements declarative patterns: `ensure`/`absent` for CRUD, `run`/`dry_run` for execution, `load`/`dump` for bulk operations.
- `serdes.py` — JSON/YAML serialization. JSON is tried first; YAML requires optional `PyYAML`. The `YAML_AVAILABLE` bool controls runtime behavior.
- `exceptions.py` — Exception hierarchy rooted at `AsyncGatewayError`. `classify_httpx_error` and `classify_http_status` map transport errors to typed exceptions. Aliases (`HTTPError`, `TimeoutError`, etc.) exist for backward compatibility.
- `logger.py` — stdlib `logging` wrapper. **Default level is 100 (silent).** Enable with `asyncgateway.logger.set_level(logging.DEBUG)`.
- `metadata.py` — Reads version from installed package metadata via `importlib.metadata`.

**Data flow — service layer:** `async with asyncgateway.client(**kwargs)` → `client.services.devices.get_all()` → `ipsdk.get("/devices", params=...)` → list of dicts.

**Data flow — resource layer:** `client.resources.devices.ensure("router1", {...})` → tries `services.devices.get("router1")`; on exception calls `services.devices.create(...)` → returns device dict.

**Data flow — bulk load:** `client.load("/data", Operation.MERGE)` → reads JSON/YAML files from `/data/{service_name}/` → calls `service.load(data_list, op)` for each service that has a `load()` method.

**Non-obvious design decisions:**
- `services/` and `resources/` are both filesystem-discovered at init. Adding a file with a `Service` or `Resource` class and a `name` attribute is all registration requires.
- `client.load()` dispatches to `service.load()`, not `resource.load()`. The resource `load()` methods (on `devices`, `playbooks`) accept in-memory data lists; `client.load()` handles file I/O.
- `Operation` is a plain string class (`"MERGE"`, `"REPLACE"`, `"OVERWRITE"`), not an `Enum`. It lives in `services/__init__.py` and is re-exported from `resources/__init__.py`.
- Resources use a broad `except Exception` for "not found" detection because `ipsdk` exception types are not part of the public contract.
- `playbooks.get_all()` uses a manual pagination loop checking `meta["count"]`, not the shared `_get_all` helper, because the playbooks endpoint uses a different metadata key than all other list endpoints.
- Version is derived from git tags via `uv-dynamic-versioning`.

## Tech Stack

- **Python 3.10+** (pyproject.toml `requires-python`); dev environment pinned to **3.11** (`.python-version`)
- **ipsdk** — the only runtime dependency; provides `gateway_factory()` and the actual async HTTP transport
- **httpx** — used internally by `ipsdk`; exposed in `exceptions.py` for error type-checking
- **PyYAML** — optional runtime dep; absence degrades YAML paths to `ValidationError` rather than breaking
- **uv** — package manager, venv, and build runner. Use `uv` for all package operations.
- **hatchling + uv-dynamic-versioning** — build backend; version comes from git tags (PEP 440)
- **tox + tox-uv** — multi-version test runner; tests py310–py313
- **Dev tools:** `pytest`, `pytest-asyncio`, `pytest-cov`, `ruff`, `mypy`, `bandit`, `pre-commit`

## Development Workflow

```bash
uv sync --group dev              # install all deps including tox
uv run pytest                    # run tests (all 200, ~0.4s)
uv run pytest -v --cov           # with coverage
tox                              # test across py310–py313
tox -e py312                     # single version
uv run ruff check src tests      # lint
uv run ruff format src tests     # format
uv run mypy src/                 # type check
uv run bandit -r src/asyncgateway --configfile pyproject.toml  # security
make premerge                    # lint + security + tests (full local CI)
```

CI runs on GitHub Actions (`.github/workflows/premerge.yaml`) on push/PR to `main`/`devel`: lint → typecheck → security in parallel, then test matrix (py310–py313 via tox), plus a coverage job. Releases are published to PyPI via OIDC trusted publishing on `v*` tags.

**First-run verification:** `uv run pytest` passes without a live IAG instance — all tests mock `ipsdk`.

## Code Standards

- All service and resource methods are `async`. Use `async with asyncgateway.client(**config) as client:` always.
- **Services**: one method per API operation, call `self.client.{verb}(path)`, return `res.json()`. No logic, no error handling, no side effects.
- **Resources**: compose service calls. Use `self.services.{name}.method()`. For ensure/absent patterns, catch broad `Exception` (not specific types) because ipsdk's exception contract is not guaranteed.
- Raise typed exceptions from `exceptions.py`. Never raise bare `Exception`.
- Pagination: use `self._get_all(path, **params)` in services. Exception: `playbooks.get_all()` uses its own loop for `meta["count"]` compatibility.
- `serdes.loads/dumps` are the canonical serialization functions. Low-level `json_loads/yaml_loads` variants are internal.
- Logging: `asyncgateway.logger.*` only inside the package. No `print()` except in `logger.fatal()`.

## Known Technical Debt

1. **`__aexit__` is a no-op** (`pass`). `ipsdk` connections are not explicitly closed. Impact unknown without ipsdk internals, but critical risk in long-running processes.
2. **`client.load()` dispatches to `service.load()`**, not `resource.load()`. This is an architectural inconsistency — the load/dump logic lives in resources but the bulk file loader bypasses the resource layer entirely.
3. **`devices.delete_all()` in `services/devices.py` only deletes devices starting with `"router"`** — leftover test code that is still in the public API.
4. **`__main__.py` is a stub** — prints a message and exits. No CLI.
5. **`pyproject.toml` still lists `requires-python = ">=3.10"`** but `docs/development.md` says 3.8+. The latter is stale.
6. **No resource-level tests** for the 22 new resource files. Current tests cover services and infrastructure only. All resource logic (ensure, absent, run, load) is untested.
7. **YAML errors raise `JSONError`** — intentional for consistency but confusing.
8. **`Operation` docstring still refers to `client.devices.import_devices()`** — a method that no longer exists.

## New Developer Entry Points

1. **Read first:** `src/asyncgateway/client.py` (service + resource discovery), then `src/asyncgateway/services/devices.py` (canonical service example), then `src/asyncgateway/resources/devices.py` (canonical resource example with load/dump/ensure/absent).
2. **Run first:** `uv sync --group dev && uv run pytest`
3. **Likely to trip you up:**
   - Logging is silent by default. Call `asyncgateway.logger.set_level(logging.DEBUG)` to see anything.
   - `client.load(path, op)` reads files and calls `service.load()`. `client.resources.devices.load(data, op)` takes an in-memory list. These are separate code paths.
   - `Operation.MERGE` is a plain string `"MERGE"`, not an enum member.
   - Both `services/` and `resources/` are scanned at client init via `os.listdir`. Tests that mock `os.listdir` must handle **two calls** — use `side_effect=[service_files, resource_files]`.
   - `playbooks.get_all()` does not use `_get_all` (different meta key). Don't refactor it without checking the IAG API response format.
   - YAML support is optional; missing `PyYAML` raises `ValidationError`, not `ImportError`.
