# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Inventory integration service for asyncgateway.

Provides asynchronous methods for managing devices and groups within external
inventory sources connected to the IAG, supporting full CRUD operations and
inventory refresh.
"""

from collections.abc import Mapping
from typing import Any

from asyncgateway.services import ServiceBase


class Service(ServiceBase):
    """Service class for inventory operations in the Itential Gateway."""

    name: str = "inventory"

    async def refresh(self) -> Mapping[str, Any]:
        """Refresh inventory."""
        res = await self.client.post("/inventory/refresh")
        return res.json()

    async def get_devices(
        self, integration_type: str, inventory_name: str, **params
    ) -> list[Mapping[str, Any]]:
        """Get all devices from an inventory."""
        res = await self.client.get(
            f"/inventory/{integration_type}/{inventory_name}/devices",
            params=params,
        )
        return res.json()

    async def get_device(
        self, integration_type: str, inventory_name: str, device_name: str
    ) -> Mapping[str, Any]:
        """Get a specific device from an inventory."""
        res = await self.client.get(
            f"/inventory/{integration_type}/{inventory_name}/devices/{device_name}"
        )
        return res.json()

    async def create_device(
        self, integration_type: str, inventory_name: str, params: dict[str, Any]
    ) -> Mapping[str, Any]:
        """Create a device in an inventory."""
        res = await self.client.post(
            f"/inventory/{integration_type}/{inventory_name}/devices",
            json=params,
        )
        return res.json()

    async def update_device(
        self,
        integration_type: str,
        inventory_name: str,
        device_name: str,
        params: dict[str, Any],
    ) -> Mapping[str, Any]:
        """Update a device in an inventory."""
        res = await self.client.put(
            f"/inventory/{integration_type}/{inventory_name}/devices/{device_name}",
            json=params,
        )
        return res.json()

    async def patch_device(
        self,
        integration_type: str,
        inventory_name: str,
        device_name: str,
        params: dict[str, Any],
    ) -> Mapping[str, Any]:
        """Patch a device in an inventory."""
        res = await self.client.patch(
            f"/inventory/{integration_type}/{inventory_name}/devices/{device_name}",
            json=params,
        )
        return res.json()

    async def delete_device(
        self, integration_type: str, inventory_name: str, device_name: str
    ) -> None:
        """Delete a device from an inventory."""
        await self.client.delete(
            f"/inventory/{integration_type}/{inventory_name}/devices/{device_name}"
        )

    async def get_groups(
        self, integration_type: str, inventory_name: str, **params
    ) -> list[Mapping[str, Any]]:
        """Get all groups from an inventory."""
        res = await self.client.get(
            f"/inventory/{integration_type}/{inventory_name}/groups",
            params=params,
        )
        return res.json()

    async def get_group(
        self, integration_type: str, inventory_name: str, group_name: str
    ) -> Mapping[str, Any]:
        """Get a specific group from an inventory."""
        res = await self.client.get(
            f"/inventory/{integration_type}/{inventory_name}/groups/{group_name}"
        )
        return res.json()

    async def get_group_devices(
        self, integration_type: str, inventory_name: str, group_name: str
    ) -> list[Mapping[str, Any]]:
        """Get devices in a group from an inventory."""
        res = await self.client.get(
            f"/inventory/{integration_type}/{inventory_name}/groups/{group_name}/devices"
        )
        return res.json()

    async def get_group_children(
        self, integration_type: str, inventory_name: str, group_name: str
    ) -> list[Mapping[str, Any]]:
        """Get child groups of a group from an inventory."""
        res = await self.client.get(
            f"/inventory/{integration_type}/{inventory_name}/groups/{group_name}/children"
        )
        return res.json()
