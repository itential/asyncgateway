# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Nornir task service for asyncgateway.

Provides asynchronous methods for managing and executing Nornir tasks on the
IAG, including schema management, execution history, and refresh from external
sources.
"""

from collections.abc import Mapping
from typing import Any

from asyncgateway.services import ServiceBase


class Service(ServiceBase):
    """Service class for managing nornir tasks in the Itential Gateway."""

    name: str = "nornir"

    async def get(self, name: str) -> Mapping[str, Any]:
        """Retrieve a specific nornir task by name."""
        res = await self.client.get(f"/nornir/{name}")
        return res.json()

    async def get_all(self, **params) -> list[Mapping[str, Any]]:
        """Retrieve all nornir tasks from the Gateway API."""
        return await self._get_all("/nornir", **params)

    async def get_schema(self, name: str) -> Mapping[str, Any]:
        """Retrieve the schema for a specific nornir task."""
        res = await self.client.get(f"/nornir/{name}/schema")
        return res.json()

    async def update_schema(
        self, name: str, schema: Mapping[str, Any]
    ) -> Mapping[str, Any]:
        """Update the schema for a specific nornir task."""
        res = await self.client.put(f"/nornir/{name}/schema", json=schema)
        return res.json()

    async def delete_schema(self, name: str) -> Mapping[str, Any]:
        """Delete the schema for a specific nornir task."""
        res = await self.client.delete(f"/nornir/{name}/schema")
        return res.json()

    async def execute(self, name: str, params: dict[str, Any]) -> Mapping[str, Any]:
        """Execute a nornir task."""
        res = await self.client.post(f"/nornir/{name}/execute", json=params)
        return res.json()

    async def get_history(self, name: str, **params) -> list[Mapping[str, Any]]:
        """Get execution history for a nornir task."""
        res = await self.client.get(f"/nornir/{name}/history", params=params)
        return res.json()

    async def refresh(self) -> Mapping[str, Any]:
        """Refresh nornir tasks from their external sources."""
        res = await self.client.post("/nornir/refresh")
        return res.json()
