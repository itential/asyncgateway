# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from typing import Any, Dict, List, Mapping

from asyncgateway.services import ServiceBase


class Service(ServiceBase):
    """Service class for managing secrets in the Itential Gateway."""

    name: str = "secrets"

    async def get_all(self, **params) -> List[Mapping[str, Any]]:
        """Retrieve all secrets from the Gateway API."""
        return await self._get_all("/secrets", **params)

    async def create(self, params: Dict[str, Any]) -> Mapping[str, Any]:
        """Create a new secret."""
        res = await self.client.post("/secrets", json=params)
        return res.json()

    async def update(self, params: Dict[str, Any]) -> Mapping[str, Any]:
        """Update a secret."""
        res = await self.client.put("/secrets", json=params)
        return res.json()

    async def delete(self, params: Dict[str, Any]) -> None:
        """Delete a secret."""
        await self.client.delete("/secrets", json=params)
