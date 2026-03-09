# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from collections.abc import Mapping
from typing import Any

from asyncgateway.resources import ResourceBase


class Resource(ResourceBase):
    """Resource class for HTTP request operations."""

    name: str = "http_requests"

    async def request(self, params: dict[str, Any]) -> Mapping[str, Any]:
        """Execute an HTTP request."""
        return await self.services.http_requests.execute(params)
