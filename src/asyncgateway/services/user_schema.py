# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from collections.abc import Mapping
from typing import Any

from asyncgateway.services import ServiceBase


class Service(ServiceBase):
    """Service class for user schema operations in the Itential Gateway."""

    name: str = "user_schema"

    async def upsert(
        self, schema_type: str, schema_name: str, schema: Mapping[str, Any]
    ) -> Mapping[str, Any]:
        """Upsert a user schema."""
        res = await self.client.put(
            f"/user-schema/{schema_type}/{schema_name}", json=schema
        )
        return res.json()

    async def delete(self, schema_type: str, schema_name: str) -> None:
        """Delete a user schema."""
        await self.client.delete(f"/user-schema/{schema_type}/{schema_name}")
