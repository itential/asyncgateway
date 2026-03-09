# Copyright (c) 2025 Itential, Inc
# SPDX-License-Identifier: GPL-3.0-or-later
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from collections.abc import Mapping
from typing import Any

from asyncgateway.services import ServiceBase


class Service(ServiceBase):
    """Service class for LDAP operations in the Itential Gateway."""

    name: str = "ldap"

    async def test_bind(self, params: dict[str, Any]) -> Mapping[str, Any]:
        """Test an LDAP bind."""
        res = await self.client.post("/ldap/test_bind", json=params)
        return res.json()
