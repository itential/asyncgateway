# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

"""RBAC resource for asyncgateway.

Provides declarative operations for managing IAG RBAC groups, including
``ensure_group``/``absent_group`` and helpers for assigning and removing roles
and users from groups.
"""

from collections.abc import Mapping
from typing import Any

from asyncgateway.resources import ResourceBase


class Resource(ResourceBase):
    """Resource class for managing RBAC resources declaratively."""

    name: str = "rbac"

    async def ensure_group(
        self, name: str, params: dict[str, Any] | None = None
    ) -> Mapping[str, Any]:
        """Ensure an RBAC group exists. Create if missing."""
        try:
            group = await self.services.rbac.get_group(name)
        except Exception:
            group = await self.services.rbac.create_group(params or {"name": name})
        return group

    async def absent_group(self, name: str) -> None:
        """Ensure an RBAC group does not exist."""
        try:
            await self.services.rbac.delete_group(name)
        except Exception:
            pass

    async def add_role(self, group_name: str, role_name: str) -> Mapping[str, Any]:
        """Add a role to a group."""
        return await self.services.rbac.add_group_roles(group_name, [role_name])

    async def remove_role(self, group_name: str, role_name: str) -> None:
        """Remove a role from a group."""
        await self.services.rbac.remove_group_role(group_name, role_name)

    async def add_user(self, group_name: str, user_name: str) -> Mapping[str, Any]:
        """Add a user to a group."""
        return await self.services.rbac.add_group_users(group_name, [user_name])

    async def remove_user(self, group_name: str, user_name: str) -> None:
        """Remove a user from a group."""
        await self.services.rbac.remove_group_user(group_name, user_name)
