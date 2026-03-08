# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from collections.abc import Mapping
from typing import Any

from asyncgateway.resources import ResourceBase


class Resource(ResourceBase):
    """Resource class for managing groups declaratively."""

    name: str = "groups"

    async def ensure(
        self, name: str, variables: Mapping[str, Any] | None = None
    ) -> Mapping[str, Any]:
        """Ensure a group exists. Create if missing."""
        try:
            group = await self.services.groups.get(name)
        except Exception:
            group = await self.services.groups.create(name, variables)
        return group

    async def absent(self, name: str) -> None:
        """Ensure a group does not exist."""
        try:
            await self.services.groups.delete(name)
        except Exception:
            pass

    async def add_device(self, name: str, device_name: str) -> Mapping[str, Any]:
        """Add a device to a group."""
        return await self.services.groups.add_devices(name, [device_name])

    async def remove_device(self, name: str, device_name: str) -> None:
        """Remove a device from a group."""
        await self.services.groups.remove_device(name, device_name)

    async def add_child(self, name: str, child_group: str) -> Mapping[str, Any]:
        """Add a child group to a group."""
        return await self.services.groups.add_children(name, [child_group])

    async def remove_child(self, name: str, child_group: str) -> None:
        """Remove a child group from a group."""
        await self.services.groups.remove_child(name, child_group)
