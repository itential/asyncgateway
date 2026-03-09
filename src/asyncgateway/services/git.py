# Copyright (c) 2025 Itential, Inc
# SPDX-License-Identifier: GPL-3.0-or-later
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Git integration service for asyncgateway.

Provides asynchronous methods for managing Git SSH keys, integrations, and
repositories registered with the IAG, including clone, pull, reset, and
status operations.
"""

from collections.abc import Mapping
from typing import Any

from asyncgateway.services import ServiceBase


class Service(ServiceBase):
    """Service class for Git operations in the Itential Gateway."""

    name: str = "git"

    async def get_keys(self, **params) -> list[Mapping[str, Any]]:
        """Get all Git SSH keys."""
        res = await self.client.get("/git/keys", params=params)
        return res.json()

    async def create_key(self, params: dict[str, Any]) -> Mapping[str, Any]:
        """Create a new Git SSH key."""
        res = await self.client.post("/git/keys", json=params)
        return res.json()

    async def upload_key(self, params: dict[str, Any]) -> Mapping[str, Any]:
        """Upload a Git SSH key."""
        res = await self.client.post("/git/keys/upload", json=params)
        return res.json()

    async def get_key(self, key_id: str) -> Mapping[str, Any]:
        """Get a specific Git SSH key."""
        res = await self.client.get(f"/git/keys/{key_id}")
        return res.json()

    async def delete_key(self, key_id: str) -> None:
        """Delete a Git SSH key."""
        await self.client.delete(f"/git/keys/{key_id}")

    async def update_key(
        self, key_id: str, params: dict[str, Any]
    ) -> Mapping[str, Any]:
        """Update a Git SSH key."""
        res = await self.client.put(f"/git/keys/{key_id}", json=params)
        return res.json()

    async def get_integrations(self, **params) -> list[Mapping[str, Any]]:
        """Get all Git integrations."""
        res = await self.client.get("/git/integrations", params=params)
        return res.json()

    async def create_integration(self, params: dict[str, Any]) -> Mapping[str, Any]:
        """Create a new Git integration."""
        res = await self.client.post("/git/integrations", json=params)
        return res.json()

    async def get_integration(self, int_id: str) -> Mapping[str, Any]:
        """Get a specific Git integration."""
        res = await self.client.get(f"/git/integrations/{int_id}")
        return res.json()

    async def delete_integration(self, int_id: str) -> None:
        """Delete a Git integration."""
        await self.client.delete(f"/git/integrations/{int_id}")

    async def update_integration(
        self, int_id: str, params: dict[str, Any]
    ) -> Mapping[str, Any]:
        """Update a Git integration."""
        res = await self.client.put(f"/git/integrations/{int_id}", json=params)
        return res.json()

    async def get_repositories(self, **params) -> list[Mapping[str, Any]]:
        """Get all Git repositories."""
        res = await self.client.get("/git/repositories", params=params)
        return res.json()

    async def create_repository(self, params: dict[str, Any]) -> Mapping[str, Any]:
        """Create a new Git repository."""
        res = await self.client.post("/git/repositories", json=params)
        return res.json()

    async def get_repository(self, repo_id: str) -> Mapping[str, Any]:
        """Get a specific Git repository."""
        res = await self.client.get(f"/git/repositories/{repo_id}")
        return res.json()

    async def delete_repository(self, repo_id: str) -> None:
        """Delete a Git repository."""
        await self.client.delete(f"/git/repositories/{repo_id}")

    async def update_repository(
        self, repo_id: str, params: dict[str, Any]
    ) -> Mapping[str, Any]:
        """Update a Git repository."""
        res = await self.client.put(f"/git/repositories/{repo_id}", json=params)
        return res.json()

    async def get_repository_status(self, repo_id: str) -> Mapping[str, Any]:
        """Get the status of a Git repository."""
        res = await self.client.get(f"/git/repositories/{repo_id}/status")
        return res.json()

    async def reset_repository(self, repo_id: str) -> Mapping[str, Any]:
        """Reset a Git repository."""
        res = await self.client.post(f"/git/repositories/{repo_id}/reset")
        return res.json()

    async def pull_repository(self, repo_id: str) -> Mapping[str, Any]:
        """Pull updates for a Git repository."""
        res = await self.client.post(f"/git/repositories/{repo_id}/pull")
        return res.json()
