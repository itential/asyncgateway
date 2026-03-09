# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from collections.abc import Mapping
from pathlib import Path
from typing import Any

from asyncgateway import serdes
from asyncgateway.exceptions import AsyncGatewayError
from asyncgateway.resources import Operation, ResourceBase


class Resource(ResourceBase):
    """Resource class for managing devices declaratively."""

    name: str = "devices"

    async def ensure(
        self, name: str, variables: Mapping[str, Any] | None = None
    ) -> Mapping[str, Any]:
        """Ensure a device exists. Create if missing, optionally update variables."""
        try:
            device = await self.services.devices.get(name)
        except Exception:
            await self.services.devices.create(name, variables)
            device = await self.services.devices.get(name)
        else:
            if variables is not None:
                await self.services.devices.patch(name, variables)
                device = await self.services.devices.get(name)
        return device

    async def absent(self, name: str) -> None:
        """Ensure a device does not exist."""
        try:
            await self.services.devices.delete(name)
        except Exception:
            pass

    async def load(self, data: list[Mapping[str, Any]], op: str) -> dict[str, Any]:
        """Load all devices from data based on the operation.

        Args:
            data: List of device configurations to load
            op: Load operation type from Operation enum
                - Operation.MERGE: Only add missing devices, skip existing ones
                - Operation.OVERWRITE: Add missing devices and replace existing ones
                - Operation.REPLACE: Delete all existing devices and add new devices

        Returns:
            dict: Load results with statistics and any errors
        """
        valid_operations = {Operation.MERGE, Operation.REPLACE, Operation.OVERWRITE}

        if op not in valid_operations:
            from asyncgateway.exceptions import ValidationError

            raise ValidationError(
                f"Invalid operation '{op}'. Must be one of: {valid_operations}"
            )

        results: dict[str, Any] = {
            "operation": op,
            "devices_processed": 0,
            "devices_created": 0,
            "devices_updated": 0,
            "devices_deleted": 0,
            "errors": [],
        }

        try:
            existing_devices = await self.services.devices.get_all()
            existing_names = {device["name"] for device in existing_devices}

            # REPLACE: Delete all existing devices first
            if op == Operation.REPLACE:
                for device in existing_devices:
                    try:
                        await self.services.devices.delete(device["name"])
                        results["devices_deleted"] += 1
                    except Exception as e:
                        results["errors"].append(
                            f"Failed to delete {device['name']}: {str(e)}"
                        )

                existing_names = set()  # No existing devices after deletion

            # Process each device in the load data
            for device_data in data:
                results["devices_processed"] += 1
                device_name = device_data.get("name")

                if not device_name:
                    results["errors"].append("Device missing name field")
                    continue

                device_variables = device_data.get("variables", {})

                try:
                    if device_name in existing_names:
                        if op == Operation.MERGE:
                            # Skip existing devices in merge mode
                            continue
                        elif op == Operation.OVERWRITE:
                            # Replace existing device
                            await self.services.devices.delete(device_name)
                            await self.services.devices.create(
                                device_name, device_variables
                            )
                            results["devices_updated"] += 1
                    else:
                        # Create new device
                        await self.services.devices.create(
                            device_name, device_variables
                        )
                        results["devices_created"] += 1

                except Exception as e:
                    results["errors"].append(
                        f"Failed to process {device_name}: {str(e)}"
                    )

            return results

        except Exception as e:
            raise AsyncGatewayError(f"Load operation failed: {str(e)}") from e

    async def dump(
        self,
        individual_files: bool = False,
        format_type: str = "json",
        devices_folder: str = "devices",
    ) -> dict[str, Any]:
        """Dump all devices to files in the devices folder.

        Args:
            individual_files (bool): If True, create separate files for each device.
            format_type (str): Output format ('json' or 'yaml'). Defaults to 'json'.
            devices_folder (str): Folder name to create/use for output files.

        Returns:
            dict: Results with file paths created and statistics
        """
        # Validate format
        format_type = format_type.lower()
        if format_type not in ["json", "yaml", "yml"]:
            from asyncgateway.exceptions import ValidationError

            raise ValidationError(
                f"Invalid format_type '{format_type}'. Must be 'json', 'yaml', or 'yml'"
            )

        # Normalize yaml format
        if format_type == "yml":
            format_type = "yaml"

        results: dict[str, Any] = {
            "format": format_type,
            "individual_files": individual_files,
            "devices_folder": devices_folder,
            "files_created": [],
            "devices_count": 0,
            "errors": [],
        }

        try:
            # Get all devices
            devices = await self.services.devices.get_all()
            results["devices_count"] = len(devices)

            if not devices:
                return results

            # Create devices folder if it doesn't exist
            folder_path = Path(devices_folder)
            folder_path.mkdir(exist_ok=True)

            file_extension = f".{format_type}"

            if individual_files:
                # Create individual files for each device
                for device in devices:
                    device_name = device.get("name", "unknown")

                    # Sanitize filename
                    safe_filename = "".join(
                        c for c in device_name if c.isalnum() or c in "._-"
                    )
                    if not safe_filename:
                        safe_filename = f"device_{results['devices_count']}"

                    file_path = folder_path / f"{safe_filename}{file_extension}"

                    try:
                        content = serdes.dumps(device, format_type=format_type)
                        file_path.write_text(content, encoding="utf-8")
                        results["files_created"].append(str(file_path))
                    except Exception as e:
                        results["errors"].append(
                            f"Failed to write {device_name} to {file_path}: {str(e)}"
                        )
            else:
                # Create single file with all devices
                filename = f"all_devices{file_extension}"
                file_path = folder_path / filename

                try:
                    content = serdes.dumps(devices, format_type=format_type)
                    file_path.write_text(content, encoding="utf-8")
                    results["files_created"].append(str(file_path))
                except Exception as e:
                    results["errors"].append(
                        f"Failed to write all devices to {file_path}: {str(e)}"
                    )

            return results

        except Exception as e:
            raise AsyncGatewayError(f"Dump operation failed: {str(e)}") from e
