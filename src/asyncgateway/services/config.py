# Copyright (c) 2025 Itential, Inc
# SPDX-License-Identifier: GPL-3.0-or-later
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Configuration management service for asyncgateway.

This module provides asynchronous methods for managing Gateway configuration
settings, allowing retrieval and updates of system-wide configuration parameters.
"""

from collections.abc import Mapping
from typing import Any

from asyncgateway.services import ServiceBase


class Service(ServiceBase):
    """Service class for managing Gateway configuration.

    This service provides methods to retrieve and update Gateway system configuration.
    The configuration typically includes system settings, feature flags, and other
    administrative parameters that control Gateway behavior.

    Attributes:
        name (str): Service identifier used by the client for service discovery
        client: ipsdk client instance for API communication

    Example:
        ```python
        async with asyncgateway.client(**config) as client:
            # Get current configuration
            current_config = await client.config.get()

            # Update configuration
            new_config = {"feature_enabled": True}
            updated_config = await client.config.update(new_config)
        ```

    """

    name: str = "config"

    async def get(self) -> Mapping[str, Any]:
        """Retrieve the current Gateway configuration.

        Fetches the complete system configuration from the Gateway API.
        This includes all configurable settings and parameters.

        Returns:
            dict: Current configuration data including all system settings

        Raises:
            AsyncGatewayError: If configuration retrieval fails
            ConnectionError: If there are network connectivity issues
            AuthenticationError: If authentication/authorization fails

        Example:
            ```python
            config = await client.config.get()
            print(f"Current settings: {config}")

            # Check if a specific feature is enabled
            if config.get("advanced_features", False):
                print("Advanced features are enabled")
            ```

        """
        res = await self.client.get("/config")
        return res.json()

    async def update(self, config: Mapping[str, Any]) -> Mapping[str, Any]:
        """Update the Gateway configuration.

        Updates the system configuration with the provided settings. This method
        allows modification of various Gateway parameters and feature flags.

        Args:
            config (dict): Configuration data to update. Should contain key-value
                pairs of configuration parameters. Common parameters include:
                - feature flags (boolean values)
                - timeout settings (numeric values)
                - system preferences (string values)

        Returns:
            dict: Updated configuration data reflecting the applied changes

        Raises:
            AsyncGatewayError: If configuration update fails
            ConnectionError: If there are network connectivity issues
            AuthenticationError: If authentication/authorization fails
            ValidationError: If the configuration data is invalid

        Example:
            ```python
            # Update multiple configuration settings
            new_config = {
                "debug_mode": True,
                "max_concurrent_jobs": 10,
                "default_timeout": 300
            }
            result = await client.config.update(new_config)
            print(f"Configuration updated: {result}")
            ```

        """
        res = await self.client.put("/config", json=config)
        return res.json()
