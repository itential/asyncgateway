# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Netmiko service for asyncgateway.

Provides asynchronous methods for sending CLI commands and configuration sets
to network devices via the Netmiko driver on the IAG, along with execution
history retrieval and schema access.
"""

from collections.abc import Mapping
from typing import Any

from asyncgateway.services import ServiceBase


class Service(ServiceBase):
    """Service class for netmiko operations in the Itential Gateway."""

    name: str = "netmiko"

    async def send_command(self, params: dict[str, Any]) -> Mapping[str, Any]:
        """Send a command via netmiko."""
        res = await self.client.post("/netmiko/send_command/execute", json=params)
        return res.json()

    async def get_send_command_history(self, **params) -> list[Mapping[str, Any]]:
        """Get send_command execution history."""
        res = await self.client.get("/netmiko/send_command/history", params=params)
        return res.json()

    async def send_config(self, params: dict[str, Any]) -> Mapping[str, Any]:
        """Send a config set via netmiko."""
        res = await self.client.post("/netmiko/send_config_set/execute", json=params)
        return res.json()

    async def get_send_config_history(self, **params) -> list[Mapping[str, Any]]:
        """Get send_config_set execution history."""
        res = await self.client.get("/netmiko/send_config_set/history", params=params)
        return res.json()

    async def get_schema(self, command: str) -> Mapping[str, Any]:
        """Get schema for a netmiko command."""
        res = await self.client.get(f"/netmiko/{command}/schema")
        return res.json()
