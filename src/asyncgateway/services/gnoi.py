# Copyright (c) 2025 Itential, Inc
# SPDX-License-Identifier: GPL-3.0-or-later
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

"""gNOI service for asyncgateway.

Provides asynchronous methods for executing gNOI operations against network
devices via the IAG, including ping, reboot, traceroute, time, package
management, and interface/protocol clear commands.
"""

from collections.abc import Mapping
from typing import Any

from asyncgateway.services import ServiceBase


class Service(ServiceBase):
    """Service class for gNOI operations in the Itential Gateway."""

    name: str = "gnoi"

    async def ping(self, params: dict[str, Any]) -> Mapping[str, Any]:
        """Execute a gNOI ping command."""
        res = await self.client.post("/gnoi/ping/execute", json=params)
        return res.json()

    async def reboot(self, params: dict[str, Any]) -> Mapping[str, Any]:
        """Execute a gNOI reboot command."""
        res = await self.client.post("/gnoi/reboot/execute", json=params)
        return res.json()

    async def time(self, params: dict[str, Any]) -> Mapping[str, Any]:
        """Execute a gNOI time command."""
        res = await self.client.post("/gnoi/time/execute", json=params)
        return res.json()

    async def traceroute(self, params: dict[str, Any]) -> Mapping[str, Any]:
        """Execute a gNOI traceroute command."""
        res = await self.client.post("/gnoi/traceroute/execute", json=params)
        return res.json()

    async def switch_cpu(self, params: dict[str, Any]) -> Mapping[str, Any]:
        """Execute a gNOI switch_cpu command."""
        res = await self.client.post("/gnoi/switch_cpu/execute", json=params)
        return res.json()

    async def reboot_status(self, params: dict[str, Any]) -> Mapping[str, Any]:
        """Execute a gNOI reboot_status command."""
        res = await self.client.post("/gnoi/reboot_status/execute", json=params)
        return res.json()

    async def set_package(self, params: dict[str, Any]) -> Mapping[str, Any]:
        """Execute a gNOI set_package command."""
        res = await self.client.post("/gnoi/set_package/execute", json=params)
        return res.json()

    async def cancel_reboot(self, params: dict[str, Any]) -> Mapping[str, Any]:
        """Execute a gNOI cancel_reboot command."""
        res = await self.client.post("/gnoi/cancel_reboot/execute", json=params)
        return res.json()

    async def clear_lldp_interface(self, params: dict[str, Any]) -> Mapping[str, Any]:
        """Execute a gNOI clear_lldp_interface command."""
        res = await self.client.post("/gnoi/clear_lldp_interface/execute", json=params)
        return res.json()

    async def clear_bgp_neighbor(self, params: dict[str, Any]) -> Mapping[str, Any]:
        """Execute a gNOI clear_bgp_neighbor command."""
        res = await self.client.post("/gnoi/clear_bgp_neighbor/execute", json=params)
        return res.json()

    async def clear_interface_counters(
        self, params: dict[str, Any]
    ) -> Mapping[str, Any]:
        """Execute a gNOI clear_interface_counters command."""
        res = await self.client.post(
            "/gnoi/clear_interface_counters/execute", json=params
        )
        return res.json()

    async def clear_neighbor_discovery(
        self, params: dict[str, Any]
    ) -> Mapping[str, Any]:
        """Execute a gNOI clear_neighbor_discovery command."""
        res = await self.client.post(
            "/gnoi/clear_neighbor_discovery/execute", json=params
        )
        return res.json()

    async def clear_spanning_tree(self, params: dict[str, Any]) -> Mapping[str, Any]:
        """Execute a gNOI clear_spanning_tree command."""
        res = await self.client.post("/gnoi/clear_spanning_tree/execute", json=params)
        return res.json()

    async def wake_on_lan(self, params: dict[str, Any]) -> Mapping[str, Any]:
        """Execute a gNOI wake_on_lan command."""
        res = await self.client.post("/gnoi/wake_on_lan/execute", json=params)
        return res.json()

    async def get_history(self, command: str, **params) -> list[Mapping[str, Any]]:
        """Get execution history for a gNOI command."""
        res = await self.client.get(f"/gnoi/{command}/history", params=params)
        return res.json()
