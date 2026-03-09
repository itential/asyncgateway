# Copyright (c) 2025 Itential, Inc
# SPDX-License-Identifier: GPL-3.0-or-later
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Service module for asyncgateway.

This module provides the base class for all asyncgateway services and defines
the common interface that services must implement.
"""


class Operation:
    """Enumeration of supported import operations for device management.

    This class defines the available operation modes for importing devices,
    each with different behavior for handling existing devices.

    Attributes:
        MERGE (str): Only add missing devices, skip existing ones
        REPLACE (str): Delete all existing devices and add new devices
        OVERWRITE (str): Add missing devices and replace existing ones

    Example:
        ```python
        await client.devices.import_devices(device_list, Operation.MERGE)
        ```
    """

    MERGE = "MERGE"
    REPLACE = "REPLACE"
    OVERWRITE = "OVERWRITE"


class ServiceBase:
    """Base class for all asyncgateway services.

    This class provides the foundation for service implementations and manages
    the connection to the underlying ipsdk client. All service classes should
    inherit from this base class.

    Attributes:
        client: The ipsdk client instance for making HTTP requests to the Gateway API
        name: Class attribute that defines the service name (must be set by subclasses)

    Example:
        ```python
        class MyService(ServiceBase):
            name = "myservice"

            async def get_data(self):
                response = await self.client.get("/myservice/data")
                return response.json()
        ```

    """

    def __init__(self, client):
        """Initialize the service with an ipsdk client.

        Args:
            client: The ipsdk client instance for making HTTP requests

        Returns:
            None

        Raises:
            None

        """
        self.client = client

    async def _get_all(self, path: str, **params) -> list:
        """Paginate through all results for a given path.

        Args:
            path: API path to GET
            **params: Additional query parameters

        Returns:
            list: All results collected across all pages
        """
        limit = 100
        offset = 0
        results = []
        while True:
            res = await self.client.get(
                path, params={**params, "limit": limit, "offset": offset}
            )
            body = res.json()
            results.extend(body.get("data", []))
            meta = body.get("meta", {})
            total = meta.get("total_count", meta.get("count", len(results)))
            if len(results) >= total:
                break
            offset += limit
        return results
