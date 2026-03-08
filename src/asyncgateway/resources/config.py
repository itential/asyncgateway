# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from typing import Any, Mapping

from asyncgateway.resources import ResourceBase


class Resource(ResourceBase):
    """Resource class for managing gateway configuration."""

    name: str = "config"

    async def get(self) -> Mapping[str, Any]:
        """Get the current gateway configuration."""
        return await self.services.config.get()

    async def update(self, config: Mapping[str, Any]) -> Mapping[str, Any]:
        """Update the gateway configuration."""
        return await self.services.config.update(config)
