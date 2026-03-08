# Architecture Review: asyncgateway
**Language:** python  |  **Reviewed:** 2026-03-08T17:25:00Z

## 🟡 Summary

Well-structured async client library with solid test coverage and clean error hierarchy, but carrying several reliability risks: an unbounded pagination loop, a hardcoded filter in a destructive operation, shadowing of builtins, missing type annotations on public interfaces, deferred inline imports, and no pytest-asyncio mode pinned.

**11 findings:** 🔴 0 critical  🟠 3 high  🟡 5 medium  ⚪ 3 low

## Architecture

**Layers observed:** client → service → serdes → exceptions → logger

**Dependency direction:** clean

```
asyncgateway (public API)
  └── Client
        ├── services/devices.py   ──┐
        ├── services/playbooks.py ──┤──> asyncgateway.serdes
        ├── services/config.py    ──┘    asyncgateway.exceptions
        └── load() / _load_service_data()

ipsdk (external gateway SDK) <── Client.__init_services__
httpx (HTTP)               <── exceptions.py (classify helpers)
```

Services are dynamically loaded from the filesystem at client construction via importlib, which is creative but fragile (no error recovery when a module fails to load). Dependency direction is clean: exceptions and serdes are shared utilities with no upward imports. The services themselves import from asyncgateway (absolute) rather than using relative imports, which is acceptable but slightly unusual inside a src-layout package.

## Findings

### 🟠 P1 — High

#### [F01] Pagination loop can hang indefinitely if API returns fewer items than declared total
**Location:** `src/asyncgateway/services/devices.py:110-124`  |  **Category:** concurrency

**Problem:** The `get_all()` loop breaks only when `len(results) == total`. If the API ever returns fewer items than `total_count` (server-side bug, concurrent deletion, or an off-by-one in the API's pagination), the condition is never satisfied and the loop runs forever, pegging the event loop.

**Risk:** Infinite loop in any caller that uses `get_all()`, including `load()` and `delete_all()`. In a coroutine environment this blocks all other work on the event loop until the process is killed.

**Before:**
```
while True:
    params["offset"] = offset
    res = await self.client.get("/devices", params=params)
    json_data = res.json()
    total = json_data["meta"]["total_count"]
    results.extend(json_data["data"])
    if len(results) == total:
        break
    offset += limit
```
**After:**
```
while True:
    params["offset"] = offset
    res = await self.client.get("/devices", params=params)
    json_data = res.json()
    page = json_data["data"]
    total = json_data["meta"]["total_count"]
    results.extend(page)
    if not page or len(results) >= total:
        break
    offset += limit
```

#### [F02] Playbooks get_all() has the same unbounded pagination loop with a different meta key
**Location:** `src/asyncgateway/services/playbooks.py:99-113`  |  **Category:** concurrency

**Problem:** Identical pagination pattern as F01, but uses `json_data["meta"]["count"]` rather than `json_data["meta"]["total_count"]`. This is also a latent KeyError if the API returns a different shape, and carries the same infinite loop risk.

**Risk:** Infinite loop or KeyError crashing the coroutine. The inconsistent meta key (`count` vs `total_count`) suggests the two services were written against different API versions or documentation and one of them is wrong.

**Before:**
```
total = json_data["meta"]["count"]
```
**After:**
```
# Align with devices.py and fix the loop guard:
total = json_data["meta"]["total_count"]  # or "count" — pick one key and use it consistently
# Also apply the same break guard as F01
```

#### [F03] delete_all() deletes only devices whose names start with 'router' — hardcoded filter on a destructive method
**Location:** `src/asyncgateway/services/devices.py:222-225`  |  **Category:** structure

**Problem:** `delete_all()` silently applies a `startswith("router")` filter. The method name and docstring imply it deletes all devices, but it actually deletes only a hardcoded subset. A caller who reads only the method signature will delete far fewer devices than expected — or none at all in an environment without devices named 'router*'.

**Risk:** Operational correctness risk: callers that expect a full wipe for cleanup or REPLACE-like workflows will leave stale devices behind. The filter appears to be a copy-paste artifact from a test environment.

**Before:**
```
async def delete_all(self) -> None:
    devices = await self.get_all()
    for ele in devices:
        if ele["name"].startswith("router"):
            await self.delete(ele["name"])
```
**After:**
```
async def delete_all(self) -> None:
    devices = await self.get_all()
    for device in devices:
        await self.delete(device["name"])
```

### 🟡 P2 — Medium

#### [F04] exceptions.py defines ConnectionError and TimeoutError, shadowing Python builtins
**Location:** `src/asyncgateway/exceptions.py:23,60`  |  **Category:** structure

**Problem:** `class ConnectionError(AsyncGatewayError)` shadows the built-in `ConnectionError`. `TimeoutError = ConnectionError` also shadows the built-in `TimeoutError`. Any file that imports `from asyncgateway.exceptions import *` (or does `from asyncgateway import exceptions`) and then uses the bare name gets the library class instead of the builtin, which can mask real network exceptions at the Python level.

**Risk:** Subtle bugs in callers that rely on catching the builtin `ConnectionError` or `TimeoutError` from standard library code. The `classify_httpx_error` function itself is insulated because it uses the local `ConnectionError` name, but library consumers may be confused.

**Before:**
```
class ConnectionError(AsyncGatewayError):
    ...
TimeoutError = ConnectionError
```
**After:**
```
class GatewayConnectionError(AsyncGatewayError):
    ...
TimeoutError = GatewayConnectionError  # or GatewayTimeoutError
# provide backward-compat aliases in __init__.py if needed
```

#### [F05] Deferred inline imports of ValidationError inside service methods
**Location:** `src/asyncgateway/services/devices.py:257,365 | src/asyncgateway/services/playbooks.py:325`  |  **Category:** structure

**Problem:** `ValidationError` is imported inline inside `load()` and `dump()` methods rather than at the module top level. There is no circular-import reason to do this: `devices.py` already imports `AsyncGatewayError` from the same module at the top. The inline imports are inconsistent and add latency on first call.

**Risk:** Code quality issue that confuses readers into thinking there is a circular-import constraint that doesn't exist. If the exception path is hot it adds repeated import overhead.

**Before:**
```
# Inside devices.py load():
from asyncgateway.exceptions import ValidationError
raise ValidationError(...)
```
**After:**
```
# At top of devices.py:
from asyncgateway.exceptions import AsyncGatewayError, ValidationError
# remove inline imports
```

#### [F06] No pytest-asyncio mode configured; relies on implicit deprecated auto-detection
**Location:** `pyproject.toml (missing [tool.pytest.ini_options])`  |  **Category:** testing

**Problem:** pytest-asyncio requires an explicit `asyncio_mode` setting (`auto`, `strict`, or `loose`). Without it, the library uses its deprecated auto-detection, which will break in pytest-asyncio 0.22+ and is already emitting deprecation warnings. The project has no `[tool.pytest.ini_options]` section in `pyproject.toml` at all.

**Risk:** Test suite will start failing silently or with hard errors when pytest-asyncio is upgraded. In CI with unpinned dev deps this can break builds without a clear cause.

**Before:**
```
# pyproject.toml has no [tool.pytest.ini_options] section
```
**After:**
```
[tool.pytest.ini_options]
asyncio_mode = "auto"
addopts = "--tb=short"
```

#### [F07] Missing type annotations on all public Client and ServiceBase signatures
**Location:** `src/asyncgateway/client.py:17,20,37 | src/asyncgateway/services/__init__.py:56`  |  **Category:** structure

**Problem:** `Client.__init__(**kwargs)`, `__aenter__`, `__aexit__`, and `ServiceBase.__init__(client)` all lack return type annotations and parameter types. The project classifies itself as `Typing :: Typed` in pyproject.toml classifiers, and mypy is in the dev toolchain, but these core public interfaces are untyped.

**Risk:** mypy provides no type coverage over the entry point into the library. Callers using the library with mypy will get `Any` for the client instance, defeating the purpose of the typed annotation.

**Before:**
```
def __init__(self, **kwargs):
    ...
async def __aenter__(self):
    ...
async def __aexit__(self, exc_type, exc_value, traceback):
    pass
```
**After:**
```
from typing import Any, Optional, Type
from types import TracebackType

def __init__(self, **kwargs: Any) -> None:
    ...
async def __aenter__(self) -> "Client":
    ...
async def __aexit__(self, exc_type: Optional[Type[BaseException]], exc_value: Optional[BaseException], traceback: Optional[TracebackType]) -> None:
    pass
```

#### [F08] Runtime dependency on ipsdk has no version pin; PyYAML is a soft dep with no declared optional extra
**Location:** `pyproject.toml:9-11`  |  **Category:** dependencies

**Problem:** `ipsdk` is listed without a version constraint (`ipsdk` with no specifier). If ipsdk releases a breaking change, all builds and deploys will start silently using the incompatible version. Additionally, `PyYAML` is used in `serdes.py` with a try/except import but is not declared as a dependency — not even as an optional extra — so `uv add PyYAML` is required manually.

**Risk:** Non-reproducible installs. A fresh `uv sync` on a CI runner or in production can pull a broken ipsdk version. YAML support appears to work in practice only if the user's environment happens to have PyYAML installed.

**Before:**
```
dependencies = [
    "ipsdk",
]
```
**After:**
```
dependencies = [
    "ipsdk>=<minimum-known-good-version>",
]

[project.optional-dependencies]
yaml = ["PyYAML>=6.0"]
```

### ⚪ P3 — Low

#### [F09] logger.fatal() calls sys.exit(1), making it unsuitable for use inside a library
**Location:** `src/asyncgateway/logger.py:87`  |  **Category:** observability

**Problem:** `logger.fatal()` logs a message and then calls `sys.exit(1)`. A library should never call `sys.exit()`; that decision belongs to the application consuming the library. If a caller is running a long-lived service and hits a transient error that triggers this path, the entire process is killed.

**Risk:** If any service method surfaces an error and a caller wraps it in `logger.fatal()`, the whole process exits. Library consumers have no way to recover from this.

**Before:**
```
def fatal(msg: str) -> None:
    log(logging.FATAL, msg)
    print(f"ERROR: {msg}")
    sys.exit(1)
```
**After:**
```
# Either remove fatal() entirely or raise an exception instead of sys.exit:
def fatal(msg: str) -> None:
    log(logging.FATAL, msg)
    raise SystemExit(1)  # at minimum; ideally just raise AsyncGatewayError
```

#### [F10] __main__.py uses print() instead of sys.stdout or logging, and calls it a placeholder
**Location:** `src/asyncgateway/__main__.py:11-12`  |  **Category:** structure

**Problem:** The module entry point uses bare `print()` calls. The module docstring says it is a placeholder for future CLI. This is fine for a placeholder, but if a CLI is ever added the prints will need to be replaced with proper output handling.

**Risk:** Low. Nit for now, but worth flagging before CLI work begins.

#### [F11] dump() in devices.py writes files to cwd-relative path with no configurable base directory
**Location:** `src/asyncgateway/services/devices.py:393`  |  **Category:** structure

**Problem:** `folder_path = Path(devices_folder)` uses a relative path by default (`"devices"`), which resolves against whatever the current working directory is at call time. Library code that writes to relative paths is unpredictable when called from different working directories.

**Risk:** Files land in an unexpected location depending on where the caller's process started. Low risk for now since the method is optional, but will surprise users.

## What's Working Well

- 200 tests pass, 93% overall line coverage. Error paths, pagination edge cases, and all three load operation modes are tested.
- Custom exception hierarchy is well-designed: AsyncGatewayError as the base, specific subclasses for connection/auth/validation, plus classify_httpx_error() that maps httpx exceptions to domain types. classify_httpx_error and classify_http_status are both tested thoroughly.
- serdes module is a good single-responsibility abstraction: JSON/YAML parsing isolated in one place, graceful degradation when PyYAML is absent, YAML_AVAILABLE flag used consistently across client and serdes.
- Pre-commit hooks configured for linting, security (bandit), and formatting with pre-push test enforcement — strong quality gate for a library.
- The dynamic service loader pattern is clean: adding a new service requires only dropping a .py file with a Service class into services/. No manual registration in __init__ needed.
- bandit reports zero security findings across all source files.
- load() in client.py properly aggregates per-service errors into a results dict rather than raising on the first failure, allowing partial success and detailed reporting.
- CI matrix covers Python 3.10–3.13 with fail-fast disabled, ensuring broad compatibility.

## Refactor Plan

Each step is independently mergeable and must not break existing behavior.

### Step 1: Fix pagination infinite loop in get_all() for both devices and playbooks
*Addresses: F01, F02*

**What:** In `devices.py` and `playbooks.py`, change the `while True` break condition from `len(results) == total` to `not page or len(results) >= total`. Also align the meta key (`total_count` vs `count`) across both services — decide which one the API actually returns and use it consistently.

**Why now:** This is the highest-reliability risk in the codebase. An API quirk or concurrent deletion can cause an infinite async loop. Fixing it is a one-line change per service with clear test coverage already in place.

**Safe when:** Existing pagination tests still pass. Add a new test with a mock that returns `total_count=5` but only 3 items; confirm `get_all()` returns after one call.

### Step 2: Remove hardcoded 'router' filter from delete_all()
*Addresses: F03*

**What:** Delete the `if ele["name"].startswith("router"):` guard in `devices.py:delete_all()`. Update the docstring to accurately describe that all devices are deleted.

**Why now:** The method is dangerous in its current form — a caller reading the signature gets a false contract. This is a one-line fix.

**Safe when:** Existing test `test_delete_all_devices_with_router_prefix` is updated to expect all listed devices to be deleted, and a new test confirms non-router devices are also deleted.

### Step 3: Add pytest.ini_options with asyncio_mode=auto and pin ipsdk version
*Addresses: F06, F08*

**What:** Add `[tool.pytest.ini_options]` with `asyncio_mode = "auto"` to pyproject.toml. Pin `ipsdk` to a minimum known-good version. Optionally add a `[project.optional-dependencies]` yaml extra for PyYAML.

**Why now:** The pytest-asyncio deprecation will silently break tests on next minor upgrade. The ipsdk pin prevents a broken CI from a dependency update. Both are config-only changes with no code impact.

**Safe when:** Test suite passes without deprecation warnings. `uv sync` produces the same resolved ipsdk version across two independent environments.

### Step 4: Fix inline imports of ValidationError and add top-level type annotations
*Addresses: F05, F07*

**What:** Move the `from asyncgateway.exceptions import ValidationError` inline imports in `devices.py` and `playbooks.py` to module-level. Add return and parameter type annotations to `Client.__init__`, `__aenter__`, `__aexit__`, and `ServiceBase.__init__`.

**Why now:** These are cleanup items that make the codebase consistent and unlock mypy coverage over the public interface. No logic changes required.

**Safe when:** `uv run mypy src/` reports zero new errors. All 200 tests still pass.

### Step 5: Rename ConnectionError and TimeoutError to avoid shadowing builtins
*Addresses: F04*

**What:** Rename `class ConnectionError` to `class GatewayConnectionError` (and update `TimeoutError = GatewayConnectionError`). Add backward-compat aliases `ConnectionError = GatewayConnectionError` if this is a published API, but mark them deprecated.

**Why now:** Lower urgency than the above steps since the shadowing only affects code that mixes asyncgateway exceptions with builtins in the same scope, but it's a correctness hazard worth addressing before the 1.0 API surface is locked.

**Safe when:** All exception tests pass. Verify via `python -c 'from asyncgateway.exceptions import ConnectionError; import builtins; assert ConnectionError is not builtins.ConnectionError'` prints the correct class.
