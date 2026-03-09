# Copyright (c) 2025 Itential, Inc
# SPDX-License-Identifier: GPL-3.0-or-later
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from collections.abc import Mapping
from typing import Any

from asyncgateway.resources import ResourceBase


class Resource(ResourceBase):
    """Resource class for managing terraform configurations declaratively."""

    name: str = "terraforms"

    async def apply(
        self, name: str, params: dict[str, Any] | None = None
    ) -> Mapping[str, Any]:
        """Apply a terraform configuration."""
        return await self.services.terraforms.apply(name, params or {})

    async def plan(
        self, name: str, params: dict[str, Any] | None = None
    ) -> Mapping[str, Any]:
        """Plan a terraform configuration."""
        return await self.services.terraforms.plan(name, params or {})

    async def destroy(
        self, name: str, params: dict[str, Any] | None = None
    ) -> Mapping[str, Any]:
        """Destroy a terraform configuration."""
        return await self.services.terraforms.destroy(name, params or {})

    async def validate(
        self, name: str, params: dict[str, Any] | None = None
    ) -> Mapping[str, Any]:
        """Validate a terraform configuration."""
        return await self.services.terraforms.validate(name, params or {})

    async def init(
        self, name: str, params: dict[str, Any] | None = None
    ) -> Mapping[str, Any]:
        """Initialize a terraform configuration."""
        return await self.services.terraforms.init(name, params or {})

    async def ensure_schema(
        self, name: str, schema: Mapping[str, Any]
    ) -> Mapping[str, Any]:
        """Ensure a terraform schema is set."""
        return await self.services.terraforms.update_schema(name, schema)

    async def remove_schema(self, name: str) -> Mapping[str, Any]:
        """Remove a terraform schema."""
        return await self.services.terraforms.delete_schema(name)

    async def refresh(self) -> Mapping[str, Any]:
        """Refresh terraform configurations."""
        return await self.services.terraforms.refresh()
