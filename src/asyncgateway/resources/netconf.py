# Copyright (c) 2025 Itential, Inc
# SPDX-License-Identifier: GPL-3.0-or-later
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

"""NETCONF resource for asyncgateway.

Thin resource wrapper over the netconf service for executing get-config,
set-config, and exec-rpc operations against network devices via the IAG.
"""

from collections.abc import Mapping
from typing import Any

from asyncgateway.resources import ResourceBase


class Resource(ResourceBase):
    """Resource class for netconf operations."""

    name: str = "netconf"

    async def get_config(self, params: dict[str, Any]) -> Mapping[str, Any]:
        """Get configuration via netconf."""
        return await self.services.netconf.get_config(params)

    async def set_config(self, params: dict[str, Any]) -> Mapping[str, Any]:
        """Set configuration via netconf."""
        return await self.services.netconf.set_config(params)

    async def exec_rpc(self, params: dict[str, Any]) -> Mapping[str, Any]:
        """Execute an RPC via netconf."""
        return await self.services.netconf.exec_rpc(params)
