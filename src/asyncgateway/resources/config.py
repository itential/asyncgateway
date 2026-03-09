# Copyright (c) 2025 Itential, Inc
# SPDX-License-Identifier: GPL-3.0-or-later
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Gateway configuration resource for asyncgateway.

Thin resource wrapper over the config service for reading and updating IAG
system-wide configuration settings.
"""

from collections.abc import Mapping
from typing import Any

from asyncgateway.resources import ResourceBase


class Resource(ResourceBase):
    """Resource class for managing gateway configuration."""

    name: str = "config"

    async def get(self) -> Mapping[str, Any]:
        """Get the current gateway configuration."""
        return await self.services.config.get()

    async def update(self, config: Mapping[str, Any]) -> Mapping[str, Any]:
        """Update the gateway configuration."""
        return await self.services.config.update(config)
