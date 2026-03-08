# Devices CLI Example

A simple command-line interface script that demonstrates how to use the asyncgateway devices service with argument routing.

## Features

- Get a specific device by name
- List all devices
- Create new devices with optional variables
- Delete devices
- Import devices from JSON files with different operation modes

## Usage

Make sure you're in the examples directory and have the project dependencies installed:

```bash
cd examples
uv run python devices.py --help
```

### Commands

#### Get a specific device
```bash
uv run python devices.py get <device_name>
```

#### Get all devices
```bash
uv run python devices.py get-all
```

#### Create a device
```bash
# Without variables
uv run python devices.py create router1

# With variables (JSON string)
uv run python devices.py create router2 '{"ansible_host": "192.168.1.2", "device_type": "cisco_ios"}'
```

#### Delete a device
```bash
uv run python devices.py delete router1
```

#### Import devices from JSON file
```bash
uv run python devices.py import MERGE sample_devices.json
uv run python devices.py import REPLACE sample_devices.json
uv run python devices.py import OVERWRITE sample_devices.json
```

### Operation Types

- **MERGE**: Only add missing devices, skip existing ones
- **REPLACE**: Delete all existing devices first, then add new ones
- **OVERWRITE**: Add missing devices and replace existing ones

## Sample Data

The `sample_devices.json` file contains example device configurations:

```json
[
  {
    "name": "router1",
    "variables": {
      "ansible_host": "192.168.1.1",
      "ansible_user": "admin",
      "device_type": "cisco_ios",
      "ansible_port": 22
    }
  },
  {
    "name": "router2", 
    "variables": {
      "ansible_host": "192.168.1.2",
      "ansible_user": "admin",
      "device_type": "cisco_ios",
      "ansible_port": 22
    }
  },
  {
    "name": "switch1",
    "variables": {
      "ansible_host": "192.168.1.10",
      "ansible_user": "admin", 
      "device_type": "cisco_ios",
      "ansible_port": 22
    }
  }
]
```

## Configuration

Update the `config` dictionary in the script to match your environment:

```python
config = {
    'host': 'localhost',
    'port': 3000,
    'protocol': 'http',
    # Add authentication parameters as needed
    # 'username': 'your_username',
    # 'password': 'your_password',
}
```

## Error Handling

The script includes comprehensive error handling:
- Connection errors
- Invalid JSON format
- Missing files
- API errors
- Invalid operation types

All errors are displayed with descriptive messages and appropriate exit codes.