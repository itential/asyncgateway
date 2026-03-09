# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from collections.abc import Mapping
from typing import Any

from asyncgateway.services import ServiceBase


class Service(ServiceBase):
    """Service class for Python virtual environment operations in the Itential Gateway."""

    name: str = "python_venv"

    async def get_list(self) -> list[Mapping[str, Any]]:
        """Get list of Python virtual environments."""
        res = await self.client.get("/pythonvenv/list")
        return res.json()

    async def refresh(self) -> Mapping[str, Any]:
        """Refresh Python virtual environments."""
        res = await self.client.get("/pythonvenv/refresh")
        return res.json()
