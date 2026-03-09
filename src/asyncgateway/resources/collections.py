# Copyright (c) 2025 Itential, Inc
# SPDX-License-Identifier: GPL-3.0-or-later
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible collection resource for asyncgateway.

Provides operations for executing collection modules and roles and managing
their schemas on the IAG.
"""

from collections.abc import Mapping
from typing import Any

from asyncgateway.resources import ResourceBase


class Resource(ResourceBase):
    """Resource class for managing collections declaratively."""

    name: str = "collections"

    async def run_module(
        self, collection: str, module: str, params: dict[str, Any] | None = None
    ) -> Mapping[str, Any]:
        """Run a collection module."""
        return await self.services.collections.execute_module(
            collection, module, params or {}
        )

    async def run_role(
        self, collection: str, role: str, params: dict[str, Any] | None = None
    ) -> Mapping[str, Any]:
        """Run a collection role."""
        return await self.services.collections.execute_role(
            collection, role, params or {}
        )

    async def ensure_module_schema(
        self, collection: str, module: str, schema: Mapping[str, Any]
    ) -> Mapping[str, Any]:
        """Ensure a collection module schema is set."""
        return await self.services.collections.update_module_schema(
            collection, module, schema
        )

    async def ensure_role_schema(
        self, collection: str, role: str, schema: Mapping[str, Any]
    ) -> Mapping[str, Any]:
        """Ensure a collection role schema is set."""
        return await self.services.collections.update_role_schema(
            collection, role, schema
        )

    async def refresh(self) -> Mapping[str, Any]:
        """Refresh collections."""
        return await self.services.collections.refresh()
