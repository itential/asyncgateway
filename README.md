# AsyncGateway

> Async Python client for the Itential Automation Gateway (IAG) API.

## Overview

`asyncgateway` provides an async/await interface to IAG 4.x, covering device inventory, playbook management, and gateway configuration. It is built on top of `ipsdk` and uses `httpx` for HTTP transport.

## Installation

```bash
pip install asyncgateway
```

Or with uv:

```bash
uv add asyncgateway
```

**Requires:** Python 3.8+, `ipsdk`

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

### Devices

```python
# List all devices (auto-paginated)
devices = await client.devices.get_all()

# Get a single device
device = await client.devices.get("router1")

# Create a device
await client.devices.create("router1", {
    "ansible_host": "192.168.1.1",
    "ansible_user": "admin",
})

# Delete a device
await client.devices.delete("router1")

# Bulk load from a list
from asyncgateway.services import Operation

data = [{"name": "router1", "variables": {"ansible_host": "192.168.1.1"}}]
result = await client.devices.load(data, Operation.MERGE)

# Dump to files
result = await client.devices.dump(format_type="yaml", individual_files=True)
```

**Load operations:**

| Operation | Behavior |
|-----------|----------|
| `MERGE` | Add only missing devices; skip existing |
| `OVERWRITE` | Add missing; replace existing |
| `REPLACE` | Delete all existing, then add from data |

### Playbooks

```python
# List all playbooks (auto-paginated)
playbooks = await client.playbooks.get_all()

# Get a single playbook
playbook = await client.playbooks.get("network_config")

# Refresh playbooks from external source
await client.playbooks.refresh()

# Manage schemas
schema = await client.playbooks.get_schema("network_config")
await client.playbooks.update_schema("network_config", schema)
await client.playbooks.delete_schema("network_config")

# Bulk load (same Operation enum as devices)
result = await client.playbooks.load(data, Operation.REPLACE)
```

### Configuration

```python
# Get gateway configuration
config = await client.config.get()

# Update configuration
await client.config.update({"max_concurrent_jobs": 10})
```

## Development

```bash
git clone https://github.com/itential/asyncgateway
cd asyncgateway
uv sync --group dev
```

Run checks:

```bash
uv run pytest
uv run ruff check && uv run ruff format
uv run mypy src/
uv run bandit -r src/
```

See [docs/development.md](docs/development.md) for full contributor guide and [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines.

## License

GPL-3.0-or-later. See [LICENSE](LICENSE).
