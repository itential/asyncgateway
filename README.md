# AsyncGateway

> Async Python client for the Itential Automation Gateway (IAG) 4.x API.

## Overview

`asyncgateway` provides async/await access to IAG 4.x across two layers:

- **Services** (`client.services.*`) — thin async wrappers, one method per API endpoint, returning raw dicts.
- **Resources** (`client.resources.*`) — declarative abstractions that compose service calls into idempotent operations (`ensure`, `absent`, `run`, `load`, `dump`).

Use services when you need direct API access. Use resources when you want declarative, state-based control.

## Installation

```bash
pip install asyncgateway
```

```bash
uv add asyncgateway
```

**Requires:** Python 3.10+, `ipsdk`

## Usage

### Client initialization

```python
import asyncio
import asyncgateway

config = {
    "host": "gateway.example.com",
    # "port": 3000,
    # "protocol": "https",
    # "username": "admin",
    # "password": "secret",
}

async def main():
    async with asyncgateway.client(**config) as client:
        ...

asyncio.run(main())
```

All `**kwargs` are passed through to `ipsdk.gateway_factory()`.

### Services layer

Direct, one-to-one wrappers around IAG API endpoints.

```python
# Devices
devices = await client.services.devices.get_all()
device  = await client.services.devices.get("router1")
await client.services.devices.create("router1", {"ansible_host": "192.168.1.1"})
await client.services.devices.patch("router1", {"ansible_user": "admin"})
await client.services.devices.delete("router1")

# Playbooks
playbooks = await client.services.playbooks.get_all()
playbook  = await client.services.playbooks.get("network_config")
await client.services.playbooks.refresh()
schema = await client.services.playbooks.get_schema("network_config")
await client.services.playbooks.update_schema("network_config", schema)
await client.services.playbooks.delete_schema("network_config")

# Gateway configuration
config = await client.services.config.get()
await client.services.config.update({"max_concurrent_jobs": 10})
```

### Resources layer

Declarative, idempotent operations that compose service calls.

```python
from asyncgateway.services import Operation

# Ensure a device exists; create if missing, patch variables if present
device = await client.resources.devices.ensure("router1", {"ansible_host": "192.168.1.1"})

# Ensure a device does not exist (no-op if already absent)
await client.resources.devices.absent("router1")

# Bulk load devices from an in-memory list
data = [{"name": "router1", "variables": {"ansible_host": "192.168.1.1"}}]
result = await client.resources.devices.load(data, Operation.MERGE)

# Dump all devices to files
result = await client.resources.devices.dump(format_type="yaml", individual_files=True)

# Run a playbook
result = await client.resources.playbooks.run("network_config", {"target": "router1"})

# Dry run a playbook
result = await client.resources.playbooks.dry_run("network_config", {"target": "router1"})
```

**Load operations:**

| Operation | Behavior |
|-----------|----------|
| `Operation.MERGE` | Add missing resources; skip existing |
| `Operation.OVERWRITE` | Add missing; replace existing |
| `Operation.REPLACE` | Delete all existing, then add from data |

### Bulk file load

`client.load(path, op)` reads JSON/YAML files from `{path}/{service_name}/` and dispatches to each service that supports `load()`:

```python
result = await client.load("/data", Operation.MERGE)
```

YAML support requires `PyYAML` (`uv add PyYAML`). Without it, YAML paths raise `ValidationError`.

## Development

```bash
git clone https://github.com/itential/asyncgateway
cd asyncgateway
uv sync --group dev
uv run pytest          # all tests pass without a live IAG instance
make ci                # lint + typecheck + security + tests (full local CI)
```

See [docs/development.md](docs/development.md) for the full contributor guide and [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines.

## License

GPL-3.0-or-later. See [LICENSE](LICENSE).
