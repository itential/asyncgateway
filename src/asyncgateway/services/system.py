# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from collections.abc import Mapping
from typing import Any

from asyncgateway.services import ServiceBase


class Service(ServiceBase):
    """Service class for system operations in the Itential Gateway."""

    name: str = "system"

    async def get_status(self) -> Mapping[str, Any]:
        """Get the system status."""
        res = await self.client.get("/system/status")
        return res.json()

    async def poll(self) -> Mapping[str, Any]:
        """Poll the system."""
        res = await self.client.get("/system/poll")
        return res.json()

    async def get_audit(self, **params) -> list[Mapping[str, Any]]:
        """Get system audit log."""
        res = await self.client.get("/system/audit", params=params)
        return res.json()

    async def get_exec_history(self, audit_id: str) -> Mapping[str, Any]:
        """Get execution history for a specific audit entry."""
        res = await self.client.get(f"/system/audit/{audit_id}")
        return res.json()

    async def get_openapi_spec(self) -> Mapping[str, Any]:
        """Get the OpenAPI specification."""
        res = await self.client.get("/system/openapi")
        return res.json()
