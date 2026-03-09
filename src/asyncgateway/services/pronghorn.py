# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Pronghorn service for asyncgateway.

Provides an asynchronous method for retrieving Pronghorn platform information
from the IAG.
"""

from collections.abc import Mapping
from typing import Any

from asyncgateway.services import ServiceBase


class Service(ServiceBase):
    """Service class for pronghorn operations in the Itential Gateway."""

    name: str = "pronghorn"

    async def get(self) -> Mapping[str, Any]:
        """Get pronghorn information."""
        res = await self.client.get("/pronghorn")
        return res.json()
