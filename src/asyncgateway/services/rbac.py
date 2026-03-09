# Copyright (c) 2025 Itential, Inc
# SPDX-License-Identifier: GPL-3.0-or-later
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Role-based access control (RBAC) service for asyncgateway.

Provides asynchronous methods for managing RBAC groups and their role and user
memberships on the IAG, along with read access to roles and per-user role/group
lookups.
"""

from collections.abc import Mapping
from typing import Any

from asyncgateway.services import ServiceBase


class Service(ServiceBase):
    """Service class for RBAC operations in the Itential Gateway."""

    name: str = "rbac"

    async def get_roles(self, **params) -> list[Mapping[str, Any]]:
        """Get all RBAC roles."""
        res = await self.client.get("/rbac/roles", params=params)
        return res.json()

    async def get_role(self, name: str) -> Mapping[str, Any]:
        """Get a specific RBAC role."""
        res = await self.client.get(f"/rbac/roles/{name}")
        return res.json()

    async def get_groups(self, **params) -> list[Mapping[str, Any]]:
        """Get all RBAC groups."""
        res = await self.client.get("/rbac/groups", params=params)
        return res.json()

    async def get_group(self, name: str) -> Mapping[str, Any]:
        """Get a specific RBAC group."""
        res = await self.client.get(f"/rbac/groups/{name}")
        return res.json()

    async def create_group(self, params: dict[str, Any]) -> Mapping[str, Any]:
        """Create a new RBAC group."""
        res = await self.client.post("/rbac/groups", json=params)
        return res.json()

    async def update_group(
        self, name: str, params: dict[str, Any]
    ) -> Mapping[str, Any]:
        """Update an RBAC group."""
        res = await self.client.put(f"/rbac/groups/{name}", json=params)
        return res.json()

    async def delete_group(self, name: str) -> None:
        """Delete an RBAC group."""
        await self.client.delete(f"/rbac/groups/{name}")

    async def get_group_roles(self, name: str) -> list[Mapping[str, Any]]:
        """Get roles assigned to a group."""
        res = await self.client.get(f"/rbac/groups/{name}/roles")
        return res.json()

    async def add_group_roles(self, name: str, roles: list[str]) -> Mapping[str, Any]:
        """Add roles to a group."""
        res = await self.client.post(
            f"/rbac/groups/{name}/roles", json={"roles": roles}
        )
        return res.json()

    async def remove_group_role(self, name: str, role_name: str) -> None:
        """Remove a role from a group."""
        await self.client.delete(f"/rbac/groups/{name}/roles/{role_name}")

    async def get_group_users(self, name: str) -> list[Mapping[str, Any]]:
        """Get users in a group."""
        res = await self.client.get(f"/rbac/groups/{name}/users")
        return res.json()

    async def add_group_users(self, name: str, users: list[str]) -> Mapping[str, Any]:
        """Add users to a group."""
        res = await self.client.post(
            f"/rbac/groups/{name}/users", json={"users": users}
        )
        return res.json()

    async def remove_group_user(self, name: str, user_name: str) -> None:
        """Remove a user from a group."""
        await self.client.delete(f"/rbac/groups/{name}/users/{user_name}")

    async def get_user_roles(self, user_name: str) -> list[Mapping[str, Any]]:
        """Get roles assigned to a user."""
        res = await self.client.get(f"/rbac/users/{user_name}/roles")
        return res.json()

    async def get_user_groups(self, user_name: str) -> list[Mapping[str, Any]]:
        """Get groups a user belongs to."""
        res = await self.client.get(f"/rbac/users/{user_name}/groups")
        return res.json()
