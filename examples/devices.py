#!/usr/bin/env python3
"""Simple devices management CLI script.

This script demonstrates how to use the asyncgateway devices service
with command-line arguments to route to different methods.

Usage:
    python devices.py get <device_name>
    python devices.py get-all
    python devices.py create <device_name> [variables_json]
    python devices.py delete <device_name>
    python devices.py import <operation> <devices_json_file>

Examples:
    python devices.py get router1
    python devices.py get-all
    python devices.py create router2 '{"ansible_host": "192.168.1.2"}'
    python devices.py delete router1
    python devices.py import MERGE devices.json
"""

import argparse
import asyncio
import json
import sys
from pathlib import Path

import asyncgateway
from asyncgateway.services import Operation


async def get_device(client, device_name: str):
    """Get a specific device by name."""
    try:
        device = await client.devices.get(device_name)
        print(json.dumps(device, indent=2))
    except Exception as e:
        print(f"Error getting device {device_name}: {e}", file=sys.stderr)
        sys.exit(1)


async def get_all_devices(client):
    """Get all devices."""
    try:
        devices = await client.devices.get_all()
        print(f"Found {len(devices)} devices:")
        for device in devices:
            print(f"  - {device['name']}")
        print("\nFull data:")
        print(json.dumps(devices, indent=2))
    except Exception as e:
        print(f"Error getting all devices: {e}", file=sys.stderr)
        sys.exit(1)


async def create_device(client, device_name: str, variables_json: str = None):
    """Create a new device."""
    try:
        variables = {}
        if variables_json:
            variables = json.loads(variables_json)

        await client.devices.create(device_name, variables)
        print(f"Successfully created device: {device_name}")
        if variables:
            print(f"Variables: {json.dumps(variables, indent=2)}")
    except Exception as e:
        print(f"Error creating device {device_name}: {e}", file=sys.stderr)
        sys.exit(1)


async def delete_device(client, device_name: str):
    """Delete a device by name."""
    try:
        await client.devices.delete(device_name)
        print(f"Successfully deleted device: {device_name}")
    except Exception as e:
        print(f"Error deleting device {device_name}: {e}", file=sys.stderr)
        sys.exit(1)


async def import_devices(client, operation: str, devices_file: str):
    """Import devices from a JSON file."""
    try:
        # Validate operation
        operation = operation.upper()
        if operation not in ["MERGE", "REPLACE", "OVERWRITE"]:
            print(
                f"Invalid operation: {operation}. Must be MERGE, REPLACE, or OVERWRITE",
                file=sys.stderr,
            )
            sys.exit(1)

        # Get the operation constant
        op = getattr(Operation, operation)

        # Load devices from file
        devices_path = Path(devices_file)
        if not devices_path.exists():
            print(f"File not found: {devices_file}", file=sys.stderr)
            sys.exit(1)

        with open(devices_path) as f:
            devices_data = json.load(f)

        if not isinstance(devices_data, list):
            print(
                "Devices file must contain a JSON array of device objects",
                file=sys.stderr,
            )
            sys.exit(1)

        # Import devices
        result = await client.devices.import_devices(devices_data, op)

        print(f"Import completed with operation: {operation}")
        print(f"Devices processed: {result['devices_processed']}")
        print(f"Devices created: {result['devices_created']}")
        print(f"Devices updated: {result['devices_updated']}")
        print(f"Devices deleted: {result['devices_deleted']}")

        if result["errors"]:
            print(f"\nErrors encountered ({len(result['errors'])}):")
            for error in result["errors"]:
                print(f"  - {error}")
        else:
            print("\nNo errors encountered.")

    except Exception as e:
        print(f"Error importing devices: {e}", file=sys.stderr)
        sys.exit(1)


async def main():
    """Main function to parse arguments and route to appropriate method."""
    parser = argparse.ArgumentParser(
        description="Simple devices management CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__.split("\n\n")[1],  # Show usage examples
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Get command
    get_parser = subparsers.add_parser("get", help="Get a specific device")
    get_parser.add_argument("device_name", help="Name of the device to retrieve")

    # Get-all command
    subparsers.add_parser("get-all", help="Get all devices")

    # Create command
    create_parser = subparsers.add_parser("create", help="Create a new device")
    create_parser.add_argument("device_name", help="Name of the device to create")
    create_parser.add_argument(
        "variables", nargs="?", help="JSON string of device variables"
    )

    # Delete command
    delete_parser = subparsers.add_parser("delete", help="Delete a device")
    delete_parser.add_argument("device_name", help="Name of the device to delete")

    # Import command
    import_parser = subparsers.add_parser(
        "import", help="Import devices from JSON file"
    )
    import_parser.add_argument(
        "operation",
        choices=["MERGE", "REPLACE", "OVERWRITE"],
        help="Import operation type",
    )
    import_parser.add_argument(
        "devices_file", help="Path to JSON file containing devices"
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Configuration for asyncgateway client
    # You may need to adjust these settings for your environment
    config = {
        "host": "gateway.privateip.dev"
        # "host": "localhost",
        # "port": 3000,
        # "protocol": "http",
        # Add authentication parameters as needed
        # 'username': 'your_username',
        # 'password': 'your_password',
    }

    try:
        async with asyncgateway.client(**config) as client:
            if args.command == "get":
                await get_device(client, args.device_name)
            elif args.command == "get-all":
                await get_all_devices(client)
            elif args.command == "create":
                await create_device(client, args.device_name, args.variables)
            elif args.command == "delete":
                await delete_device(client, args.device_name)
            elif args.command == "import":
                await import_devices(client, args.operation, args.devices_file)
            else:
                print(f"Unknown command: {args.command}", file=sys.stderr)
                sys.exit(1)

    except Exception as e:
        print(f"Connection error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
