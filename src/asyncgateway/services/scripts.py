# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Script management service for asyncgateway.

Provides asynchronous methods for managing scripts on the IAG, including
retrieval, execution, schema management, execution history, and refresh from
external sources.
"""

from collections.abc import Mapping
from typing import Any

from asyncgateway.services import ServiceBase


class Service(ServiceBase):
    """Service class for managing scripts in the Itential Gateway."""

    name: str = "scripts"

    async def get(self, name: str) -> Mapping[str, Any]:
        """Retrieve a specific script by name."""
        res = await self.client.get(f"/scripts/{name}")
        return res.json()

    async def get_all(self, **params) -> list[Mapping[str, Any]]:
        """Retrieve all scripts from the Gateway API."""
        return await self._get_all("/scripts", **params)

    async def get_schema(self, name: str) -> Mapping[str, Any]:
        """Retrieve the schema for a specific script."""
        res = await self.client.get(f"/scripts/{name}/schema")
        return res.json()

    async def update_schema(
        self, name: str, schema: Mapping[str, Any]
    ) -> Mapping[str, Any]:
        """Update the schema for a specific script."""
        res = await self.client.put(f"/scripts/{name}/schema", json=schema)
        return res.json()

    async def delete_schema(self, name: str) -> Mapping[str, Any]:
        """Delete the schema for a specific script."""
        res = await self.client.delete(f"/scripts/{name}/schema")
        return res.json()

    async def execute(self, name: str, params: dict[str, Any]) -> Mapping[str, Any]:
        """Execute a script."""
        res = await self.client.post(f"/scripts/{name}/execute", json=params)
        return res.json()

    async def get_history(self, name: str, **params) -> list[Mapping[str, Any]]:
        """Get execution history for a script."""
        res = await self.client.get(f"/scripts/{name}/history", params=params)
        return res.json()

    async def refresh(self) -> Mapping[str, Any]:
        """Refresh scripts from their external sources."""
        res = await self.client.post("/scripts/refresh")
        return res.json()
