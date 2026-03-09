# Copyright (c) 2025 Itential, Inc
# SPDX-License-Identifier: GPL-3.0-or-later
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible collection management service for asyncgateway.

Provides asynchronous methods for managing Ansible collections installed on the
IAG, including CRUD operations on collections and the execution, schema
management, and history retrieval of their modules and roles.
"""

from collections.abc import Mapping
from typing import Any

from asyncgateway.services import ServiceBase


class Service(ServiceBase):
    """Service class for managing collections in the Itential Gateway."""

    name: str = "collections"

    async def get(self, name: str) -> Mapping[str, Any]:
        """Retrieve a specific collection by name."""
        res = await self.client.get(f"/collections/{name}")
        return res.json()

    async def get_all(self, **params) -> list[Mapping[str, Any]]:
        """Retrieve all collections from the Gateway API."""
        return await self._get_all("/collections", **params)

    async def install(self, params: dict[str, Any]) -> Mapping[str, Any]:
        """Install a collection."""
        res = await self.client.post("/collections/install", json=params)
        return res.json()

    async def refresh(self) -> Mapping[str, Any]:
        """Refresh collections."""
        res = await self.client.post("/collections/refresh")
        return res.json()

    async def get_module(self, collection: str, module: str) -> Mapping[str, Any]:
        """Get a specific module from a collection."""
        res = await self.client.get(f"/collections/{collection}/modules/{module}")
        return res.json()

    async def get_modules(self, collection: str, **params) -> list[Mapping[str, Any]]:
        """Get all modules from a collection."""
        res = await self.client.get(f"/collections/{collection}/modules", params=params)
        return res.json()

    async def get_module_schema(
        self, collection: str, module: str
    ) -> Mapping[str, Any]:
        """Get the schema for a collection module."""
        res = await self.client.get(
            f"/collections/{collection}/modules/{module}/schema"
        )
        return res.json()

    async def update_module_schema(
        self, collection: str, module: str, schema: Mapping[str, Any]
    ) -> Mapping[str, Any]:
        """Update the schema for a collection module."""
        res = await self.client.put(
            f"/collections/{collection}/modules/{module}/schema", json=schema
        )
        return res.json()

    async def delete_module_schema(
        self, collection: str, module: str
    ) -> Mapping[str, Any]:
        """Delete the schema for a collection module."""
        res = await self.client.delete(
            f"/collections/{collection}/modules/{module}/schema"
        )
        return res.json()

    async def execute_module(
        self, collection: str, module: str, params: dict[str, Any]
    ) -> Mapping[str, Any]:
        """Execute a collection module."""
        res = await self.client.post(
            f"/collections/{collection}/modules/{module}/execute", json=params
        )
        return res.json()

    async def get_module_history(
        self, collection: str, module: str, **params
    ) -> list[Mapping[str, Any]]:
        """Get execution history for a collection module."""
        res = await self.client.get(
            f"/collections/{collection}/modules/{module}/history", params=params
        )
        return res.json()

    async def get_role(self, collection: str, role: str) -> Mapping[str, Any]:
        """Get a specific role from a collection."""
        res = await self.client.get(f"/collections/{collection}/roles/{role}")
        return res.json()

    async def get_roles(self, collection: str, **params) -> list[Mapping[str, Any]]:
        """Get all roles from a collection."""
        res = await self.client.get(f"/collections/{collection}/roles", params=params)
        return res.json()

    async def get_role_schema(self, collection: str, role: str) -> Mapping[str, Any]:
        """Get the schema for a collection role."""
        res = await self.client.get(f"/collections/{collection}/roles/{role}/schema")
        return res.json()

    async def update_role_schema(
        self, collection: str, role: str, schema: Mapping[str, Any]
    ) -> Mapping[str, Any]:
        """Update the schema for a collection role."""
        res = await self.client.put(
            f"/collections/{collection}/roles/{role}/schema", json=schema
        )
        return res.json()

    async def delete_role_schema(self, collection: str, role: str) -> Mapping[str, Any]:
        """Delete the schema for a collection role."""
        res = await self.client.delete(f"/collections/{collection}/roles/{role}/schema")
        return res.json()

    async def execute_role(
        self, collection: str, role: str, params: dict[str, Any]
    ) -> Mapping[str, Any]:
        """Execute a collection role."""
        res = await self.client.post(
            f"/collections/{collection}/roles/{role}/execute", json=params
        )
        return res.json()

    async def get_role_history(
        self, collection: str, role: str, **params
    ) -> list[Mapping[str, Any]]:
        """Get execution history for a collection role."""
        res = await self.client.get(
            f"/collections/{collection}/roles/{role}/history", params=params
        )
        return res.json()
