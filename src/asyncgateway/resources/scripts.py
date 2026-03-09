# Copyright (c) 2025 Itential, Inc
# SPDX-License-Identifier: GPL-3.0-or-later
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Script resource for asyncgateway.

Provides operations for running IAG scripts and managing their schemas.
"""

from collections.abc import Mapping
from typing import Any

from asyncgateway.resources import ResourceBase


class Resource(ResourceBase):
    """Resource class for managing scripts declaratively."""

    name: str = "scripts"

    async def run(
        self, name: str, params: dict[str, Any] | None = None
    ) -> Mapping[str, Any]:
        """Run a script."""
        return await self.services.scripts.execute(name, params or {})

    async def ensure_schema(
        self, name: str, schema: Mapping[str, Any]
    ) -> Mapping[str, Any]:
        """Ensure a script schema is set."""
        return await self.services.scripts.update_schema(name, schema)

    async def remove_schema(self, name: str) -> Mapping[str, Any]:
        """Remove a script schema."""
        return await self.services.scripts.delete_schema(name)

    async def refresh(self) -> Mapping[str, Any]:
        """Refresh scripts."""
        return await self.services.scripts.refresh()
