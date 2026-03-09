# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible playbook service for asyncgateway.

Provides asynchronous methods for managing Ansible playbooks on the IAG,
including CRUD operations, execution, dry-run, schema management, execution
history, and refresh from external sources.

Note: ``get_all`` uses manual pagination with ``meta["count"]`` rather than the
shared ``_get_all`` helper because the playbooks endpoint uses a different
metadata key from all other list endpoints.
"""

from collections.abc import Mapping
from typing import Any

from asyncgateway.services import ServiceBase


class Service(ServiceBase):
    """Service class for managing playbooks in the Itential Gateway."""

    name: str = "playbooks"

    async def get(self, name: str) -> Mapping[str, Any]:
        """Retrieve a specific playbook by name."""
        res = await self.client.get(f"/playbooks/{name}")
        return res.json()

    async def get_all(self) -> list[Mapping[str, Any]]:
        """Retrieve all playbooks from the Gateway API using manual pagination."""
        limit = 100
        offset = 0

        params = {"limit": limit}

        results = []

        while True:
            params["offset"] = offset

            res = await self.client.get("/playbooks", params=params)

            json_data = res.json()

            total = json_data["meta"]["count"]

            results.extend(json_data["data"])

            if len(results) == total:
                break

            offset += limit

        return results

    async def refresh(self) -> Mapping[str, Any]:
        """Refresh playbooks from their external sources."""
        res = await self.client.post("/playbooks/refresh")
        return res.json()

    async def get_schema(self, pb: str) -> Mapping[str, Any]:
        """Retrieve the schema for a specific playbook."""
        res = await self.client.get(f"/playbooks/{pb}/schema")
        return res.json()

    async def update_schema(
        self, name: str, schema: Mapping[str, Any]
    ) -> Mapping[str, Any]:
        """Update the schema for a specific playbook."""
        res = await self.client.put(f"/playbooks/{name}/schema", json=schema)
        return res.json()

    async def delete_schema(self, name: str) -> Mapping[str, Any]:
        """Delete the schema for a specific playbook."""
        res = await self.client.delete(f"/playbooks/{name}/schema")
        return res.json()

    async def create(self, name: str, data: Mapping[str, Any]) -> None:
        """Create a new playbook in the Gateway."""
        body = {"name": name, **data}
        await self.client.post("/playbooks", json=body)

    async def delete(self, name: str) -> None:
        """Delete a specific playbook by name."""
        await self.client.delete(f"/playbooks/{name}")

    async def execute(self, name: str, params: dict[str, Any]) -> Mapping[str, Any]:
        """Execute a playbook."""
        res = await self.client.post(f"/playbooks/{name}/execute", json=params)
        return res.json()

    async def dry_run(self, name: str, params: dict[str, Any]) -> Mapping[str, Any]:
        """Dry run a playbook."""
        res = await self.client.post(f"/playbooks/{name}/dry_run", json=params)
        return res.json()

    async def get_history(self, name: str, **params) -> list[Mapping[str, Any]]:
        """Get execution history for a playbook."""
        res = await self.client.get(f"/playbooks/{name}/history", params=params)
        return res.json()
