# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from collections.abc import Mapping
from typing import Any

from asyncgateway.resources import ResourceBase


class Resource(ResourceBase):
    """Resource class for managing inventory declaratively."""

    name: str = "inventory"

    async def refresh(self) -> Mapping[str, Any]:
        """Refresh inventory."""
        return await self.services.inventory.refresh()

    async def ensure_device(
        self,
        integration_type: str,
        inventory_name: str,
        device_name: str,
        params: dict[str, Any],
    ) -> Mapping[str, Any]:
        """Ensure a device exists in an inventory. Try update first, then create."""
        try:
            device = await self.services.inventory.update_device(
                integration_type, inventory_name, device_name, params
            )
        except Exception:
            device = await self.services.inventory.create_device(
                integration_type, inventory_name, params
            )
        return device

    async def absent_device(
        self,
        integration_type: str,
        inventory_name: str,
        device_name: str,
    ) -> None:
        """Ensure a device does not exist in an inventory."""
        try:
            await self.services.inventory.delete_device(
                integration_type, inventory_name, device_name
            )
        except Exception:
            pass
