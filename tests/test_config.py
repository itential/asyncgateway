# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from unittest.mock import AsyncMock, Mock

import pytest

from asyncgateway.services.config import Service as ConfigService


class TestConfigService:
    @pytest.fixture
    def mock_client(self):
        """Create a mock ipsdk client."""
        client = Mock()
        return client

    @pytest.fixture
    def config_service(self, mock_client):
        """Create a ConfigService instance with a mock client."""
        return ConfigService(mock_client)

    def test_service_name(self, config_service):
        """Test that the service has the correct name."""
        assert config_service.name == "config"

    def test_service_inherits_from_service_base(self):
        """Test that ConfigService inherits from ServiceBase."""
        from asyncgateway.services import ServiceBase

        assert issubclass(ConfigService, ServiceBase)

    def test_service_initialization(self, mock_client):
        """Test that the service initializes correctly with a client."""
        service = ConfigService(mock_client)
        assert service.client is mock_client
        assert service.name == "config"

    @pytest.mark.asyncio
    async def test_get_config_success(self, config_service, mock_client):
        """Test successfully getting configuration."""
        config_data = {
            "debug_mode": True,
            "max_concurrent_jobs": 10,
            "default_timeout": 300,
            "advanced_features": True,
        }

        mock_response = Mock()
        mock_response.json.return_value = config_data
        mock_client.get = AsyncMock(return_value=mock_response)

        result = await config_service.get()

        mock_client.get.assert_called_once_with("/config")
        mock_response.json.assert_called_once()
        assert result == config_data

    @pytest.mark.asyncio
    async def test_get_config_empty_response(self, config_service, mock_client):
        """Test getting configuration with empty response."""
        config_data = {}

        mock_response = Mock()
        mock_response.json.return_value = config_data
        mock_client.get = AsyncMock(return_value=mock_response)

        result = await config_service.get()

        mock_client.get.assert_called_once_with("/config")
        mock_response.json.assert_called_once()
        assert result == config_data

    @pytest.mark.asyncio
    async def test_update_config_success(self, config_service, mock_client):
        """Test successfully updating configuration."""
        update_data = {
            "debug_mode": True,
            "max_concurrent_jobs": 15,
            "new_feature_enabled": True,
        }

        updated_config = {
            "debug_mode": True,
            "max_concurrent_jobs": 15,
            "default_timeout": 300,
            "new_feature_enabled": True,
        }

        mock_response = Mock()
        mock_response.json.return_value = updated_config
        mock_client.put = AsyncMock(return_value=mock_response)

        result = await config_service.update(update_data)

        mock_client.put.assert_called_once_with("/config", json=update_data)
        mock_response.json.assert_called_once()
        assert result == updated_config

    @pytest.mark.asyncio
    async def test_update_config_empty_data(self, config_service, mock_client):
        """Test updating configuration with empty data."""
        update_data = {}

        mock_response = Mock()
        mock_response.json.return_value = {"status": "no changes"}
        mock_client.put = AsyncMock(return_value=mock_response)

        result = await config_service.update(update_data)

        mock_client.put.assert_called_once_with("/config", json=update_data)
        mock_response.json.assert_called_once()
        assert result == {"status": "no changes"}

    @pytest.mark.asyncio
    async def test_update_config_single_setting(self, config_service, mock_client):
        """Test updating a single configuration setting."""
        update_data = {"debug_mode": False}

        updated_config = {
            "debug_mode": False,
            "max_concurrent_jobs": 10,
            "default_timeout": 300,
        }

        mock_response = Mock()
        mock_response.json.return_value = updated_config
        mock_client.put = AsyncMock(return_value=mock_response)

        result = await config_service.update(update_data)

        mock_client.put.assert_called_once_with("/config", json=update_data)
        assert result == updated_config

    @pytest.mark.asyncio
    async def test_update_config_with_complex_data(self, config_service, mock_client):
        """Test updating configuration with complex nested data."""
        update_data = {
            "features": {
                "advanced_mode": True,
                "experimental": ["feature1", "feature2"],
            },
            "timeouts": {"default": 300, "long_running": 1800},
        }

        mock_response = Mock()
        mock_response.json.return_value = update_data
        mock_client.put = AsyncMock(return_value=mock_response)

        result = await config_service.update(update_data)

        mock_client.put.assert_called_once_with("/config", json=update_data)
        assert result == update_data
