# Copyright (c) 2025 Itential, Inc
# SPDX-License-Identifier: GPL-3.0-or-later
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from collections.abc import Mapping
from typing import Any

from asyncgateway.services import ServiceBase


class Service(ServiceBase):
    """Service class for managing terraform configurations in the Itential Gateway."""

    name: str = "terraforms"

    async def get(self, name: str) -> Mapping[str, Any]:
        """Retrieve a specific terraform configuration by name."""
        res = await self.client.get(f"/terraforms/{name}")
        return res.json()

    async def get_all(self, **params) -> list[Mapping[str, Any]]:
        """Retrieve all terraform configurations from the Gateway API."""
        return await self._get_all("/terraforms", **params)

    async def get_schema(self, name: str) -> Mapping[str, Any]:
        """Retrieve the schema for a specific terraform configuration."""
        res = await self.client.get(f"/terraforms/{name}/schema")
        return res.json()

    async def update_schema(
        self, name: str, schema: Mapping[str, Any]
    ) -> Mapping[str, Any]:
        """Update the schema for a specific terraform configuration."""
        res = await self.client.put(f"/terraforms/{name}/schema", json=schema)
        return res.json()

    async def delete_schema(self, name: str) -> Mapping[str, Any]:
        """Delete the schema for a specific terraform configuration."""
        res = await self.client.delete(f"/terraforms/{name}/schema")
        return res.json()

    async def init(self, name: str, params: dict[str, Any]) -> Mapping[str, Any]:
        """Initialize a terraform configuration."""
        res = await self.client.post(f"/terraforms/{name}/init", json=params)
        return res.json()

    async def apply(self, name: str, params: dict[str, Any]) -> Mapping[str, Any]:
        """Apply a terraform configuration."""
        res = await self.client.post(f"/terraforms/{name}/apply", json=params)
        return res.json()

    async def plan(self, name: str, params: dict[str, Any]) -> Mapping[str, Any]:
        """Plan a terraform configuration."""
        res = await self.client.post(f"/terraforms/{name}/plan", json=params)
        return res.json()

    async def validate(self, name: str, params: dict[str, Any]) -> Mapping[str, Any]:
        """Validate a terraform configuration."""
        res = await self.client.post(f"/terraforms/{name}/validate", json=params)
        return res.json()

    async def destroy(self, name: str, params: dict[str, Any]) -> Mapping[str, Any]:
        """Destroy a terraform configuration."""
        res = await self.client.post(f"/terraforms/{name}/destroy", json=params)
        return res.json()

    async def get_history(self, name: str, **params) -> list[Mapping[str, Any]]:
        """Get execution history for a terraform configuration."""
        res = await self.client.get(f"/terraforms/{name}/history", params=params)
        return res.json()

    async def refresh(self) -> Mapping[str, Any]:
        """Refresh terraform configurations."""
        res = await self.client.post("/terraforms/refresh")
        return res.json()
