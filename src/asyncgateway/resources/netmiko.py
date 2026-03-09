# Copyright (c) 2025 Itential, Inc
# SPDX-License-Identifier: GPL-3.0-or-later
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Netmiko resource for asyncgateway.

Thin resource wrapper over the netmiko service for sending CLI commands and
configuration sets to network devices via the IAG.
"""

from collections.abc import Mapping
from typing import Any

from asyncgateway.resources import ResourceBase


class Resource(ResourceBase):
    """Resource class for netmiko operations."""

    name: str = "netmiko"

    async def send_command(self, params: dict[str, Any]) -> Mapping[str, Any]:
        """Send a command via netmiko."""
        return await self.services.netmiko.send_command(params)

    async def send_config(self, params: dict[str, Any]) -> Mapping[str, Any]:
        """Send a config set via netmiko."""
        return await self.services.netmiko.send_config(params)
