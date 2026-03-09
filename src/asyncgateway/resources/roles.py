# Copyright (c) 2025 Itential, Inc
# SPDX-License-Identifier: GPL-3.0-or-later
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible role resource for asyncgateway.

Provides operations for running Ansible roles and managing their schemas on the
IAG.
"""

from collections.abc import Mapping
from typing import Any

from asyncgateway.resources import ResourceBase


class Resource(ResourceBase):
    """Resource class for managing roles declaratively."""

    name: str = "roles"

    async def run(
        self, name: str, params: dict[str, Any] | None = None
    ) -> Mapping[str, Any]:
        """Run a role."""
        return await self.services.roles.execute(name, params or {})

    async def ensure_schema(
        self, name: str, schema: Mapping[str, Any]
    ) -> Mapping[str, Any]:
        """Ensure a role schema is set."""
        return await self.services.roles.update_schema(name, schema)

    async def remove_schema(self, name: str) -> Mapping[str, Any]:
        """Remove a role schema."""
        return await self.services.roles.delete_schema(name)

    async def refresh(self) -> Mapping[str, Any]:
        """Refresh roles."""
        return await self.services.roles.refresh()
