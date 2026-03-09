# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

"""System resource for asyncgateway.

Thin resource wrapper over the system service for checking IAG status,
polling availability, and retrieving the system audit log.
"""

from collections.abc import Mapping
from typing import Any

from asyncgateway.resources import ResourceBase


class Resource(ResourceBase):
    """Resource class for system operations."""

    name: str = "system"

    async def get_status(self) -> Mapping[str, Any]:
        """Get the system status."""
        return await self.services.system.get_status()

    async def poll(self) -> Mapping[str, Any]:
        """Poll the system."""
        return await self.services.system.poll()

    async def get_audit(self, **params) -> list[Mapping[str, Any]]:
        """Get system audit log."""
        return await self.services.system.get_audit(**params)
