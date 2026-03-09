# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from collections.abc import Mapping
from typing import Any

from asyncgateway.services import ServiceBase


class Service(ServiceBase):
    """Service class for managing accounts in the Itential Gateway."""

    name: str = "accounts"

    async def get(self, name: str) -> Mapping[str, Any]:
        """Retrieve a specific account by name."""
        res = await self.client.get(f"/accounts/{name}")
        return res.json()

    async def get_all(self, **params) -> list[Mapping[str, Any]]:
        """Retrieve all accounts from the Gateway API."""
        return await self._get_all("/accounts", **params)

    async def create(self, params: dict[str, Any]) -> Mapping[str, Any]:
        """Create a new account."""
        res = await self.client.post("/accounts", json=params)
        return res.json()

    async def update(self, name: str, params: dict[str, Any]) -> Mapping[str, Any]:
        """Update an account."""
        res = await self.client.put(f"/accounts/{name}", json=params)
        return res.json()

    async def delete(self, name: str) -> None:
        """Delete an account by name."""
        await self.client.delete(f"/accounts/{name}")

    async def update_password(
        self, name: str, params: dict[str, Any]
    ) -> Mapping[str, Any]:
        """Update the password for an account."""
        res = await self.client.put(f"/accounts/{name}/password", json=params)
        return res.json()
