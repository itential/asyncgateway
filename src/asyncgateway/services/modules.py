# Copyright (c) 2025 Itential, Inc
# SPDX-License-Identifier: GPL-3.0-or-later
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Module management service for asyncgateway.

Provides asynchronous methods for managing IAG modules, including retrieval,
execution, schema management, execution history, and refresh from external
sources.
"""

from collections.abc import Mapping
from typing import Any

from asyncgateway.services import ServiceBase


class Service(ServiceBase):
    """Service class for managing modules in the Itential Gateway."""

    name: str = "modules"

    async def get(self, name: str) -> Mapping[str, Any]:
        """Retrieve a specific module by name."""
        res = await self.client.get(f"/modules/{name}")
        return res.json()

    async def get_all(self, **params) -> list[Mapping[str, Any]]:
        """Retrieve all modules from the Gateway API."""
        return await self._get_all("/modules", **params)

    async def get_schema(self, name: str) -> Mapping[str, Any]:
        """Retrieve the schema for a specific module."""
        res = await self.client.get(f"/modules/{name}/schema")
        return res.json()

    async def update_schema(
        self, name: str, schema: Mapping[str, Any]
    ) -> Mapping[str, Any]:
        """Update the schema for a specific module."""
        res = await self.client.put(f"/modules/{name}/schema", json=schema)
        return res.json()

    async def delete_schema(self, name: str) -> Mapping[str, Any]:
        """Delete the schema for a specific module."""
        res = await self.client.delete(f"/modules/{name}/schema")
        return res.json()

    async def execute(self, name: str, params: dict[str, Any]) -> Mapping[str, Any]:
        """Execute a module."""
        res = await self.client.post(f"/modules/{name}/execute", json=params)
        return res.json()

    async def get_history(self, name: str, **params) -> list[Mapping[str, Any]]:
        """Get execution history for a module."""
        res = await self.client.get(f"/modules/{name}/history", params=params)
        return res.json()

    async def refresh(self) -> Mapping[str, Any]:
        """Refresh modules from their external sources."""
        res = await self.client.post("/modules/refresh")
        return res.json()
