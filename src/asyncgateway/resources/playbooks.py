# Copyright (c) 2025 Itential, Inc
# SPDX-License-Identifier: GPL-3.0-or-later
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Ansible playbook resource for asyncgateway.

Provides operations for running and dry-running Ansible playbooks, managing
their schemas, and bulk loading (MERGE/OVERWRITE/REPLACE) playbook configurations
from in-memory data into the IAG.
"""

from collections.abc import Mapping
from typing import Any

from asyncgateway.exceptions import AsyncGatewayError
from asyncgateway.resources import Operation, ResourceBase


class Resource(ResourceBase):
    """Resource class for managing playbooks declaratively."""

    name: str = "playbooks"

    async def run(
        self, name: str, params: dict[str, Any] | None = None
    ) -> Mapping[str, Any]:
        """Run a playbook."""
        return await self.services.playbooks.execute(name, params or {})

    async def dry_run(
        self, name: str, params: dict[str, Any] | None = None
    ) -> Mapping[str, Any]:
        """Dry run a playbook."""
        return await self.services.playbooks.dry_run(name, params or {})

    async def ensure_schema(
        self, name: str, schema: Mapping[str, Any]
    ) -> Mapping[str, Any]:
        """Ensure a playbook schema is set."""
        return await self.services.playbooks.update_schema(name, schema)

    async def remove_schema(self, name: str) -> Mapping[str, Any]:
        """Remove a playbook schema."""
        return await self.services.playbooks.delete_schema(name)

    async def load(self, data: list[Mapping[str, Any]], op: str) -> dict[str, Any]:
        """Load all playbooks from data based on the operation.

        Args:
            data: List of playbook configurations to load
            op: Load operation type from Operation enum
                - Operation.MERGE: Only add missing playbooks, skip existing ones
                - Operation.OVERWRITE: Add missing playbooks and replace existing ones
                - Operation.REPLACE: Delete all existing playbooks and add new playbooks

        Returns:
            dict: Load results with statistics and any errors
        """
        valid_operations = {Operation.MERGE, Operation.REPLACE, Operation.OVERWRITE}

        if op not in valid_operations:
            from asyncgateway.exceptions import ValidationError

            raise ValidationError(
                f"Invalid operation '{op}'. Must be one of: {valid_operations}"
            )

        results: dict[str, Any] = {
            "operation": op,
            "playbooks_processed": 0,
            "playbooks_created": 0,
            "playbooks_updated": 0,
            "playbooks_deleted": 0,
            "errors": [],
        }

        try:
            existing_playbooks = await self.services.playbooks.get_all()
            existing_names = {playbook["name"] for playbook in existing_playbooks}

            # REPLACE: Delete all existing playbooks first
            if op == Operation.REPLACE:
                for playbook in existing_playbooks:
                    try:
                        await self.services.playbooks.delete(playbook["name"])
                        results["playbooks_deleted"] += 1
                    except Exception as e:
                        results["errors"].append(
                            f"Failed to delete {playbook['name']}: {str(e)}"
                        )

                existing_names = set()  # No existing playbooks after deletion

            # Process each playbook in the load data
            for playbook_data in data:
                results["playbooks_processed"] += 1
                playbook_name = playbook_data.get("name")

                if not playbook_name:
                    results["errors"].append("Playbook missing name field")
                    continue

                # Extract name from the data for create call
                playbook_config = {
                    k: v for k, v in playbook_data.items() if k != "name"
                }

                try:
                    if playbook_name in existing_names:
                        if op == Operation.MERGE:
                            # Skip existing playbooks in merge mode
                            continue
                        elif op == Operation.OVERWRITE:
                            # Replace existing playbook
                            await self.services.playbooks.delete(playbook_name)
                            await self.services.playbooks.create(
                                playbook_name, playbook_config
                            )
                            results["playbooks_updated"] += 1
                    else:
                        # Create new playbook
                        await self.services.playbooks.create(
                            playbook_name, playbook_config
                        )
                        results["playbooks_created"] += 1

                except Exception as e:
                    results["errors"].append(
                        f"Failed to process {playbook_name}: {str(e)}"
                    )

            return results

        except Exception as e:
            raise AsyncGatewayError(f"Load operation failed: {str(e)}") from e

    async def refresh(self) -> Mapping[str, Any]:
        """Refresh playbooks from their external sources."""
        return await self.services.playbooks.refresh()
