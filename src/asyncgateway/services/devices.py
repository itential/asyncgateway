# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Device management service for asyncgateway.

This module provides asynchronous methods for managing devices in the Itential Gateway,
including operations for creating, reading, updating, and deleting device configurations.
"""

from collections.abc import Mapping
from typing import Any

from asyncgateway.services import ServiceBase


class Service(ServiceBase):
    """Service class for managing devices in the Itential Gateway.

    This service provides methods to interact with device resources including
    retrieving device information, creating new devices, and managing device
    configurations through the Gateway API.

    Attributes:
        name (str): Service identifier used by the client for service discovery
        client: ipsdk client instance for API communication

    Example:
        ```python
        async with asyncgateway.client(**config) as client:
            # Get a specific device
            device = await client.services.devices.get("router1")

            # Create a new device
            await client.services.devices.create("router2", {"ansible_host": "192.168.1.1"})

            # Get all devices
            all_devices = await client.services.devices.get_all()
        ```

    """

    name: str = "devices"

    async def get(self, name: str) -> Mapping[str, Any]:
        """Retrieve a specific device by name."""
        res = await self.client.get(f"/devices/{name}")
        return res.json()

    async def get_all(self) -> list[Mapping[str, Any]]:
        """Retrieve all devices from the Gateway API."""
        return await self._get_all("/devices")

    async def create(
        self, name: str, variables: Mapping[str, Any] | None = None
    ) -> None:
        """Create a new device in the Gateway."""
        body = {"name": name, "variables": variables or {}}
        await self.client.post("/devices", json=body)

    async def delete(self, name: str) -> None:
        """Delete a specific device by name."""
        await self.client.delete(f"/devices/{name}")

    async def delete_all(self) -> None:
        """Delete all devices that have names starting with 'router'."""
        devices = await self.get_all()
        for ele in devices:
            if ele["name"].startswith("router"):
                await self.delete(ele["name"])

    async def patch(self, name: str, variables: Mapping[str, Any]) -> Mapping[str, Any]:
        """Patch variables for a specific device."""
        res = await self.client.patch(f"/devices/{name}", json={"variables": variables})
        return res.json()

    async def get_variables(self, name: str) -> Mapping[str, Any]:
        """Get all variables for a specific device."""
        res = await self.client.get(f"/devices/{name}/variables")
        return res.json()

    async def get_variable(self, name: str, variable_name: str) -> Mapping[str, Any]:
        """Get a specific variable for a device."""
        res = await self.client.get(f"/devices/{name}/variables/{variable_name}")
        return res.json()

    async def get_state(self, name: str) -> Mapping[str, Any]:
        """Get the state of a specific device."""
        res = await self.client.get(f"/devices/{name}/state")
        return res.json()
