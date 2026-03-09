# Copyright (c) 2025 Itential, Inc
# SPDX-License-Identifier: GPL-3.0-or-later
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Module resource for asyncgateway.

Provides operations for running IAG modules and managing their schemas,
composing the modules service into a consistent execution interface.
"""

from collections.abc import Mapping
from typing import Any

from asyncgateway.resources import ResourceBase


class Resource(ResourceBase):
    """Resource class for managing modules declaratively."""

    name: str = "modules"

    async def run(
        self, name: str, params: dict[str, Any] | None = None
    ) -> Mapping[str, Any]:
        """Run a module."""
        return await self.services.modules.execute(name, params or {})

    async def ensure_schema(
        self, name: str, schema: Mapping[str, Any]
    ) -> Mapping[str, Any]:
        """Ensure a module schema is set."""
        return await self.services.modules.update_schema(name, schema)

    async def remove_schema(self, name: str) -> Mapping[str, Any]:
        """Remove a module schema."""
        return await self.services.modules.delete_schema(name)

    async def refresh(self) -> Mapping[str, Any]:
        """Refresh modules."""
        return await self.services.modules.refresh()
