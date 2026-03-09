# Usage Guide

asyncgateway is an async Python client for the Itential Automation Gateway (IAG) 4.x REST API. It has two layers:

- **Services** — thin async wrappers that map 1:1 to IAG API endpoints (`client.services.<name>`)
- **Resources** — declarative abstractions that compose services into idempotent operations (`client.resources.<name>`)

## Installation

```bash
pip install asyncgateway
```

YAML support is optional. Install `PyYAML` to enable YAML file loading and output:

```bash
pip install asyncgateway[yaml]
```

## Quick Start

All interaction with IAG goes through a `Client` instance used as an async context manager:

```python
import asyncio
import asyncgateway

config = {
    "host": "https://iag.example.com",
    "username": "admin",
    "password": "secret",
}

async def main():
    async with asyncgateway.client(**config) as client:
        devices = await client.services.devices.get_all()
        print(devices)

asyncio.run(main())
```

All `**kwargs` are forwarded to `ipsdk.gateway_factory()`. Refer to the ipsdk documentation for the full list of connection parameters.

## Services Layer

Services expose the raw IAG API. Each method maps to a single endpoint and returns the parsed JSON response. There is no added logic — use services when you need direct API access.

### Devices

```python
async with asyncgateway.client(**config) as client:
    # List all devices (paginated automatically)
    devices = await client.services.devices.get_all()

    # Get a single device
    device = await client.services.devices.get("router1")

    # Create a device
    await client.services.devices.create("router1", {"ansible_host": "10.0.0.1"})

    # Update device variables
    await client.services.devices.patch("router1", {"ansible_host": "10.0.0.2"})

    # Delete a device
    await client.services.devices.delete("router1")

    # Get device variables
    variables = await client.services.devices.get_variables("router1")

    # Get a specific variable
    var = await client.services.devices.get_variable("router1", "ansible_host")

    # Get device state
    state = await client.services.devices.get_state("router1")
```

### Playbooks

```python
async with asyncgateway.client(**config) as client:
    # List all playbooks
    playbooks = await client.services.playbooks.get_all()

    # Execute a playbook
    result = await client.services.playbooks.execute("site.yml", {"limit": "routers"})

    # Dry run a playbook
    result = await client.services.playbooks.dry_run("site.yml", {})
```

### Available Services

| Name | Description |
|------|-------------|
| `accounts` | User account management |
| `ansible_venv` | Ansible virtual environment management |
| `collections` | Ansible collection management |
| `config` | Gateway configuration |
| `devices` | Device inventory |
| `git` | Git repository management |
| `gnmi` | gNMI operations |
| `gnoi` | gNOI operations |
| `groups` | Device group management |
| `http_requests` | HTTP request execution |
| `inventory` | Inventory management |
| `ldap` | LDAP configuration |
| `modules` | Ansible module management |
| `netconf` | NETCONF operations |
| `netmiko` | Netmiko operations |
| `nornir` | Nornir operations |
| `playbooks` | Ansible playbook execution |
| `pronghorn` | Pronghorn integration |
| `python_venv` | Python virtual environment management |
| `rbac` | Role-based access control |
| `roles` | Ansible role management |
| `scripts` | Script execution |
| `secrets` | Secret management |
| `system` | System operations |
| `terraforms` | Terraform execution |
| `user_schema` | User schema management |

## Resources Layer

Resources provide declarative, idempotent operations. Use resources when you want "ensure this state exists" semantics rather than direct CRUD.

### ensure / absent

`ensure` creates a resource if it is missing, or updates it if variables are provided. `absent` deletes a resource if it exists, and is a no-op otherwise.

```python
async with asyncgateway.client(**config) as client:
    # Ensure a device exists with the given variables
    device = await client.resources.devices.ensure(
        "router1",
        {"ansible_host": "10.0.0.1", "ansible_user": "admin"}
    )

    # Ensure a device exists without changing its variables
    device = await client.resources.devices.ensure("router1")

    # Delete a device if it exists (no error if already gone)
    await client.resources.devices.absent("router1")
```

### Running Playbooks

```python
async with asyncgateway.client(**config) as client:
    # Run a playbook
    result = await client.resources.playbooks.run(
        "site.yml",
        {"limit": "routers", "tags": "deploy"}
    )

    # Dry run a playbook
    result = await client.resources.playbooks.dry_run("site.yml")

    # Manage playbook schemas
    await client.resources.playbooks.ensure_schema("site.yml", {...})
    await client.resources.playbooks.remove_schema("site.yml")

    # Refresh playbooks from external sources
    await client.resources.playbooks.refresh()
```

### Available Resources

| Name | Operations |
|------|------------|
| `accounts` | ensure, absent |
| `collections` | ensure, absent |
| `config` | ensure |
| `devices` | ensure, absent, load, dump |
| `git` | ensure, absent |
| `gnmi` | run |
| `gnoi` | run |
| `groups` | ensure, absent |
| `http_requests` | run |
| `inventory` | ensure, absent |
| `modules` | ensure, absent |
| `netconf` | run |
| `netmiko` | run |
| `nornir` | run |
| `playbooks` | run, dry_run, ensure_schema, remove_schema, load, refresh |
| `rbac` | ensure, absent |
| `roles` | ensure, absent |
| `scripts` | run |
| `secrets` | ensure, absent |
| `system` | run |
| `terraforms` | run |

## Bulk Operations

### Loading from Files

`client.load()` reads JSON or YAML files from a directory tree and imports them into IAG. The directory must contain subdirectories named after each service:

```
/data/
  devices/
    routers.json
    switches.yaml
  playbooks/
    site.json
```

```python
from asyncgateway.services import Operation

async with asyncgateway.client(**config) as client:
    results = await client.load("/data", Operation.MERGE)
    print(results["services_processed"])
    print(results["total_resources_created"])
    if results["errors"]:
        print(results["errors"])
```

**Operations:**

| Operation | Behavior |
|-----------|----------|
| `Operation.MERGE` | Add missing resources; skip existing ones |
| `Operation.OVERWRITE` | Add missing resources; replace existing ones |
| `Operation.REPLACE` | Delete all existing resources; add all from files |

`Operation.MERGE` is the default and the safest choice. File contents must be a JSON/YAML object or array of objects, each with a `name` field.

### Exporting to Files

The `devices` resource supports dumping the current device inventory to files:

```python
async with asyncgateway.client(**config) as client:
    # Single file with all devices
    results = await client.resources.devices.dump(
        format_type="json",
        devices_folder="./backup"
    )

    # One file per device
    results = await client.resources.devices.dump(
        individual_files=True,
        format_type="yaml",
        devices_folder="./backup"
    )

    print(results["files_created"])
    print(results["devices_count"])
```

### In-memory Bulk Load

Resources also support loading from an in-memory list directly:

```python
async with asyncgateway.client(**config) as client:
    devices = [
        {"name": "router1", "variables": {"ansible_host": "10.0.0.1"}},
        {"name": "router2", "variables": {"ansible_host": "10.0.0.2"}},
    ]
    results = await client.resources.devices.load(devices, Operation.MERGE)
```

## Error Handling

All exceptions inherit from `AsyncGatewayError`:

```python
from asyncgateway.exceptions import AsyncGatewayError, ValidationError

async with asyncgateway.client(**config) as client:
    try:
        device = await client.services.devices.get("nonexistent")
    except AsyncGatewayError as e:
        print(f"Gateway error: {e}")
    except ValidationError as e:
        print(f"Invalid input: {e}")
```

| Exception | Raised for |
|-----------|-----------|
| `AsyncGatewayError` | Base class; all gateway errors |
| `ValidationError` | Invalid input, JSON/YAML parsing errors |

## Logging

Logging is disabled by default (level `NONE = 100`). Enable it before creating the client:

```python
import asyncgateway

# Enable debug logging
asyncgateway.logging.set_level(asyncgateway.logging.DEBUG)

# Enable info logging only
asyncgateway.logging.set_level(asyncgateway.logging.INFO)

# Also enable httpx/httpcore transport logging
asyncgateway.logging.set_level(asyncgateway.logging.DEBUG, propagate=True)

# Disable logging
asyncgateway.logging.set_level(asyncgateway.logging.NONE)
```

Available levels: `TRACE (5)`, `DEBUG (10)`, `INFO (20)`, `WARNING (30)`, `ERROR (40)`, `CRITICAL (50)`, `FATAL (90)`, `NONE (100)`.

### Sensitive Data Filtering

Enable automatic redaction of credentials and tokens in log output:

```python
asyncgateway.logging.enable_sensitive_data_filtering()

# Add a custom pattern
asyncgateway.logging.add_sensitive_data_pattern(
    "my_token",
    r"my_token=(\S+)"
)

asyncgateway.logging.disable_sensitive_data_filtering()
```

## YAML Support

YAML file loading requires `PyYAML`. If it is not installed, any operation that reads a YAML file raises `ValidationError`. JSON always works with no optional dependencies.

Check availability at runtime:

```python
from asyncgateway import serdes
if serdes.YAML_AVAILABLE:
    print("YAML support enabled")
```
