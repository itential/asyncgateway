# Copyright (c) 2025 Itential, Inc
# SPDX-License-Identifier: GPL-3.0-or-later
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

"""gNMI service for asyncgateway.

Provides asynchronous methods for executing gNMI get and set operations against
network devices via the IAG, along with execution history retrieval.
"""

from collections.abc import Mapping
from typing import Any

from asyncgateway.services import ServiceBase


class Service(ServiceBase):
    """Service class for gNMI operations in the Itential Gateway."""

    name: str = "gnmi"

    async def get(self, params: dict[str, Any]) -> Mapping[str, Any]:
        """Execute a gNMI get operation."""
        res = await self.client.post("/gnmi/get/execute", json=params)
        return res.json()

    async def set(self, params: dict[str, Any]) -> Mapping[str, Any]:
        """Execute a gNMI set operation."""
        res = await self.client.post("/gnmi/set/execute", json=params)
        return res.json()

    async def get_history(self, command: str, **params) -> list[Mapping[str, Any]]:
        """Get execution history for a gNMI command."""
        res = await self.client.get(f"/gnmi/{command}/history", params=params)
        return res.json()
