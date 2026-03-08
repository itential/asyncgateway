# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from typing import Any, Dict, Mapping

from asyncgateway.services import ServiceBase


class Service(ServiceBase):
    """Service class for LDAP operations in the Itential Gateway."""

    name: str = "ldap"

    async def test_bind(self, params: Dict[str, Any]) -> Mapping[str, Any]:
        """Test an LDAP bind."""
        res = await self.client.post("/ldap/test_bind", json=params)
        return res.json()
