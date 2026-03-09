# Copyright (c) 2025 Itential, Inc
# SPDX-License-Identifier: GPL-3.0-or-later
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Secret management service for asyncgateway.

Provides asynchronous methods for creating, listing, updating, and deleting
secrets stored in the IAG.
"""

from collections.abc import Mapping
from typing import Any

from asyncgateway.services import ServiceBase


class Service(ServiceBase):
    """Service class for managing secrets in the Itential Gateway."""

    name: str = "secrets"

    async def get_all(self, **params) -> list[Mapping[str, Any]]:
        """Retrieve all secrets from the Gateway API."""
        return await self._get_all("/secrets", **params)

    async def create(self, params: dict[str, Any]) -> Mapping[str, Any]:
        """Create a new secret."""
        res = await self.client.post("/secrets", json=params)
        return res.json()

    async def update(self, params: dict[str, Any]) -> Mapping[str, Any]:
        """Update a secret."""
        res = await self.client.put("/secrets", json=params)
        return res.json()

    async def delete(self, params: dict[str, Any]) -> None:
        """Delete a secret."""
        await self.client.delete("/secrets", json=params)
