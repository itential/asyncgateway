# Copyright (c) 2025 Itential, Inc
# SPDX-License-Identifier: GPL-3.0-or-later
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

"""gNOI resource for asyncgateway.

Thin resource wrapper over the gNOI service for executing network operations
commands (ping, reboot, traceroute, etc.) against network devices via the IAG.
"""

from collections.abc import Mapping
from typing import Any

from asyncgateway.resources import ResourceBase


class Resource(ResourceBase):
    """Resource class for gNOI operations."""

    name: str = "gnoi"

    async def ping(self, params: dict[str, Any]) -> Mapping[str, Any]:
        """Execute a gNOI ping command."""
        return await self.services.gnoi.ping(params)

    async def reboot(self, params: dict[str, Any]) -> Mapping[str, Any]:
        """Execute a gNOI reboot command."""
        return await self.services.gnoi.reboot(params)

    async def time(self, params: dict[str, Any]) -> Mapping[str, Any]:
        """Execute a gNOI time command."""
        return await self.services.gnoi.time(params)

    async def traceroute(self, params: dict[str, Any]) -> Mapping[str, Any]:
        """Execute a gNOI traceroute command."""
        return await self.services.gnoi.traceroute(params)

    async def switch_cpu(self, params: dict[str, Any]) -> Mapping[str, Any]:
        """Execute a gNOI switch_cpu command."""
        return await self.services.gnoi.switch_cpu(params)

    async def reboot_status(self, params: dict[str, Any]) -> Mapping[str, Any]:
        """Execute a gNOI reboot_status command."""
        return await self.services.gnoi.reboot_status(params)

    async def set_package(self, params: dict[str, Any]) -> Mapping[str, Any]:
        """Execute a gNOI set_package command."""
        return await self.services.gnoi.set_package(params)

    async def cancel_reboot(self, params: dict[str, Any]) -> Mapping[str, Any]:
        """Execute a gNOI cancel_reboot command."""
        return await self.services.gnoi.cancel_reboot(params)

    async def clear_lldp_interface(self, params: dict[str, Any]) -> Mapping[str, Any]:
        """Execute a gNOI clear_lldp_interface command."""
        return await self.services.gnoi.clear_lldp_interface(params)

    async def clear_bgp_neighbor(self, params: dict[str, Any]) -> Mapping[str, Any]:
        """Execute a gNOI clear_bgp_neighbor command."""
        return await self.services.gnoi.clear_bgp_neighbor(params)

    async def clear_interface_counters(
        self, params: dict[str, Any]
    ) -> Mapping[str, Any]:
        """Execute a gNOI clear_interface_counters command."""
        return await self.services.gnoi.clear_interface_counters(params)

    async def clear_neighbor_discovery(
        self, params: dict[str, Any]
    ) -> Mapping[str, Any]:
        """Execute a gNOI clear_neighbor_discovery command."""
        return await self.services.gnoi.clear_neighbor_discovery(params)

    async def clear_spanning_tree(self, params: dict[str, Any]) -> Mapping[str, Any]:
        """Execute a gNOI clear_spanning_tree command."""
        return await self.services.gnoi.clear_spanning_tree(params)

    async def wake_on_lan(self, params: dict[str, Any]) -> Mapping[str, Any]:
        """Execute a gNOI wake_on_lan command."""
        return await self.services.gnoi.wake_on_lan(params)
