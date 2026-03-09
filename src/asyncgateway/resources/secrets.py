# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Secret resource for asyncgateway.

Provides declarative ``ensure`` and ``absent`` operations for IAG secrets,
implementing an upsert pattern (try update, then create) for ``ensure``.
"""

from collections.abc import Mapping
from typing import Any

from asyncgateway.resources import ResourceBase


class Resource(ResourceBase):
    """Resource class for managing secrets declaratively."""

    name: str = "secrets"

    async def ensure(self, params: dict[str, Any]) -> Mapping[str, Any]:
        """Ensure a secret exists. Try update first, then create."""
        try:
            result = await self.services.secrets.update(params)
        except Exception:
            try:
                result = await self.services.secrets.create(params)
            except Exception:
                raise
        return result

    async def absent(self, params: dict[str, Any]) -> None:
        """Ensure a secret does not exist."""
        try:
            await self.services.secrets.delete(params)
        except Exception:
            pass
