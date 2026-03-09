# Copyright (c) 2025 Itential, Inc
# SPDX-License-Identifier: GPL-3.0-or-later
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from collections.abc import Mapping
from typing import Any

from asyncgateway.resources import ResourceBase


class Resource(ResourceBase):
    """Resource class for managing accounts declaratively."""

    name: str = "accounts"

    async def ensure(self, name: str, params: dict[str, Any]) -> Mapping[str, Any]:
        """Ensure an account exists. Create if missing."""
        try:
            account = await self.services.accounts.get(name)
        except Exception:
            account = await self.services.accounts.create(params)
        return account

    async def absent(self, name: str) -> None:
        """Ensure an account does not exist."""
        try:
            await self.services.accounts.delete(name)
        except Exception:
            pass
