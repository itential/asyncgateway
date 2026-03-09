# Copyright (c) 2025 Itential, Inc
# SPDX-License-Identifier: GPL-3.0-or-later
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Device group management service for asyncgateway.

Provides asynchronous methods for creating, reading, updating, and deleting
device groups on the IAG, including membership management for devices, child
groups, and group variables.
"""

from collections.abc import Mapping
from typing import Any

from asyncgateway.services import ServiceBase


class Service(ServiceBase):
    """Service class for managing groups in the Itential Gateway."""

    name: str = "groups"

    async def get(self, name: str) -> Mapping[str, Any]:
        """Retrieve a specific group by name."""
        res = await self.client.get(f"/groups/{name}")
        return res.json()

    async def get_all(self, **params) -> list[Mapping[str, Any]]:
        """Retrieve all groups from the Gateway API."""
        return await self._get_all("/groups", **params)

    async def create(
        self, name: str, variables: Mapping[str, Any] | None = None
    ) -> Mapping[str, Any]:
        """Create a new group."""
        body = {"name": name, "variables": variables or {}}
        res = await self.client.post("/groups", json=body)
        return res.json()

    async def update(
        self, name: str, variables: Mapping[str, Any]
    ) -> Mapping[str, Any]:
        """Update a group's variables."""
        res = await self.client.put(f"/groups/{name}", json={"variables": variables})
        return res.json()

    async def delete(self, name: str) -> None:
        """Delete a group by name."""
        await self.client.delete(f"/groups/{name}")

    async def get_devices(self, name: str, **params) -> list[Mapping[str, Any]]:
        """Get devices in a group."""
        res = await self.client.get(f"/groups/{name}/devices", params=params)
        return res.json()

    async def add_devices(self, name: str, devices: list[str]) -> Mapping[str, Any]:
        """Add devices to a group."""
        res = await self.client.post(
            f"/groups/{name}/devices", json={"devices": devices}
        )
        return res.json()

    async def remove_device(self, name: str, device_name: str) -> None:
        """Remove a device from a group."""
        await self.client.delete(f"/groups/{name}/devices/{device_name}")

    async def get_children(self, name: str) -> list[Mapping[str, Any]]:
        """Get child groups of a group."""
        res = await self.client.get(f"/groups/{name}/children")
        return res.json()

    async def add_children(self, name: str, children: list[str]) -> Mapping[str, Any]:
        """Add child groups to a group."""
        res = await self.client.post(
            f"/groups/{name}/children", json={"children": children}
        )
        return res.json()

    async def remove_child(self, name: str, child_group: str) -> None:
        """Remove a child group from a group."""
        await self.client.delete(f"/groups/{name}/children/{child_group}")

    async def get_variables(self, name: str) -> Mapping[str, Any]:
        """Get all variables for a group."""
        res = await self.client.get(f"/groups/{name}/variables")
        return res.json()

    async def get_variable(self, name: str, variable_name: str) -> Mapping[str, Any]:
        """Get a specific variable for a group."""
        res = await self.client.get(f"/groups/{name}/variables/{variable_name}")
        return res.json()
