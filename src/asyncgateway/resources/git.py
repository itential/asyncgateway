# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from typing import Any, Dict, Mapping

from asyncgateway.resources import ResourceBase


class Resource(ResourceBase):
    """Resource class for managing git resources declaratively."""

    name: str = "git"

    async def ensure_key(self, params: Dict[str, Any]) -> Mapping[str, Any]:
        """Create or ensure a Git SSH key exists."""
        return await self.services.git.create_key(params)

    async def ensure_integration(self, params: Dict[str, Any]) -> Mapping[str, Any]:
        """Create or ensure a Git integration exists."""
        return await self.services.git.create_integration(params)

    async def ensure_repository(self, params: Dict[str, Any]) -> Mapping[str, Any]:
        """Create or ensure a Git repository exists."""
        return await self.services.git.create_repository(params)
