# Copyright (c) 2025 Itential, Inc
# SPDX-License-Identifier: GPL-3.0-or-later
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from collections.abc import Mapping
from typing import Any

from asyncgateway.resources import ResourceBase


class Resource(ResourceBase):
    """Resource class for gNMI operations."""

    name: str = "gnmi"

    async def get(self, params: dict[str, Any]) -> Mapping[str, Any]:
        """Execute a gNMI get operation."""
        return await self.services.gnmi.get(params)

    async def set(self, params: dict[str, Any]) -> Mapping[str, Any]:
        """Execute a gNMI set operation."""
        return await self.services.gnmi.set(params)
