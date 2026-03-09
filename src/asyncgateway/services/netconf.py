# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

"""NETCONF service for asyncgateway.

Provides asynchronous methods for executing NETCONF get-config, set-config,
and exec-rpc operations against network devices via the IAG, along with
execution history retrieval.
"""

from collections.abc import Mapping
from typing import Any

from asyncgateway.services import ServiceBase


class Service(ServiceBase):
    """Service class for netconf operations in the Itential Gateway."""

    name: str = "netconf"

    async def get_config(self, params: dict[str, Any]) -> Mapping[str, Any]:
        """Get configuration via netconf."""
        res = await self.client.post("/netconf/get_config/execute", json=params)
        return res.json()

    async def set_config(self, params: dict[str, Any]) -> Mapping[str, Any]:
        """Set configuration via netconf."""
        res = await self.client.post("/netconf/set_config/execute", json=params)
        return res.json()

    async def exec_rpc(self, params: dict[str, Any]) -> Mapping[str, Any]:
        """Execute an RPC via netconf."""
        res = await self.client.post("/netconf/exec_rpc/execute", json=params)
        return res.json()

    async def get_history(self, command: str, **params) -> list[Mapping[str, Any]]:
        """Get execution history for a netconf command."""
        res = await self.client.get(f"/netconf/{command}/history", params=params)
        return res.json()
