# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from typing import Any, Dict, List, Mapping

from asyncgateway.services import ServiceBase


class Service(ServiceBase):
    """Service class for HTTP request operations in the Itential Gateway."""

    name: str = "http_requests"

    async def get_schema(self) -> Mapping[str, Any]:
        """Get schema for HTTP requests."""
        res = await self.client.get("/http_requests/request/schema")
        return res.json()

    async def execute(self, params: Dict[str, Any]) -> Mapping[str, Any]:
        """Execute an HTTP request."""
        res = await self.client.post("/http_requests/request/execute", json=params)
        return res.json()

    async def get_history(self, **params) -> List[Mapping[str, Any]]:
        """Get HTTP request execution history."""
        res = await self.client.get("/http_requests/request/history", params=params)
        return res.json()
