# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from unittest.mock import AsyncMock, Mock, patch

import pytest

from asyncgateway.client import Client


class TestResourceCleanup:
    @patch("asyncgateway.client.ipsdk.gateway_factory")
    @patch("asyncgateway.client.os.listdir")
    def test_client_creates_ipsdk_client(self, mock_listdir, mock_gateway_factory):
        """Test that the client properly creates an ipsdk client."""
        mock_listdir.side_effect = [[], []]
        mock_client = Mock()
        mock_gateway_factory.return_value = mock_client

        client = Client(host="test.example.com")

        # Verify the ipsdk factory was called with correct parameters
        mock_gateway_factory.assert_called_once_with(
            want_async=True, host="test.example.com"
        )
        # Verify client was created successfully
        assert isinstance(client, Client)

    @pytest.mark.asyncio
    @patch("asyncgateway.client.ipsdk.gateway_factory")
    @patch("asyncgateway.client.os.listdir")
    async def test_client_as_async_context_manager(
        self, mock_listdir, mock_gateway_factory
    ):
        """Test client can be used as an async context manager."""
        mock_listdir.side_effect = [[], []]
        mock_client = AsyncMock()
        mock_gateway_factory.return_value = mock_client

        async with Client() as client:
            # Verify client is accessible and properly initialized
            assert isinstance(client, Client)

        # Test should complete without errors

    @pytest.mark.asyncio
    @patch("asyncgateway.client.ipsdk.gateway_factory")
    @patch("asyncgateway.client.os.listdir")
    async def test_aenter_returns_client(self, mock_listdir, mock_gateway_factory):
        """Test that __aenter__ returns the client instance."""
        mock_listdir.side_effect = [[], []]
        mock_client = Mock()
        mock_gateway_factory.return_value = mock_client

        client = Client()
        result = await client.__aenter__()

        # __aenter__ should return the client instance itself
        assert result is client

    @pytest.mark.asyncio
    @patch("asyncgateway.client.ipsdk.gateway_factory")
    @patch("asyncgateway.client.os.listdir")
    async def test_aexit_no_exceptions(self, mock_listdir, mock_gateway_factory):
        """Test that __aexit__ completes without raising exceptions."""
        mock_listdir.side_effect = [[], []]
        mock_client = Mock()
        mock_gateway_factory.return_value = mock_client

        client = Client()

        # Should not raise any exceptions
        await client.__aexit__(None, None, None)

    @pytest.mark.asyncio
    @patch("asyncgateway.client.ipsdk.gateway_factory")
    @patch("asyncgateway.client.os.listdir")
    async def test_aexit_with_exception_info(self, mock_listdir, mock_gateway_factory):
        """Test that __aexit__ handles exception info properly."""
        mock_listdir.side_effect = [[], []]
        mock_client = Mock()
        mock_gateway_factory.return_value = mock_client

        client = Client()

        # Should handle exception info without raising
        await client.__aexit__(ValueError, ValueError("test"), None)

    @pytest.mark.asyncio
    @patch("asyncgateway.client.ipsdk.gateway_factory")
    @patch("asyncgateway.client.os.listdir")
    async def test_multiple_aexit_calls(self, mock_listdir, mock_gateway_factory):
        """Test that multiple __aexit__ calls don't cause issues."""
        mock_listdir.side_effect = [[], []]
        mock_client = Mock()
        mock_gateway_factory.return_value = mock_client

        client = Client()

        # First exit call
        await client.__aexit__(None, None, None)

        # Second exit call should not raise any exceptions
        await client.__aexit__(None, None, None)

    @pytest.mark.asyncio
    @patch("asyncgateway.client.ipsdk.gateway_factory")
    @patch("asyncgateway.client.os.listdir")
    async def test_client_without_context_manager(
        self, mock_listdir, mock_gateway_factory
    ):
        """Test that clients can be created without using context manager."""
        mock_listdir.side_effect = [[], []]
        mock_client = Mock()
        mock_gateway_factory.return_value = mock_client

        client = Client(host="test.example.com")

        # Client should work normally
        assert isinstance(client, Client)

        # Manual exit call should work without issues
        await client.__aexit__(None, None, None)

    @pytest.mark.asyncio
    @patch("asyncgateway.client.ipsdk.gateway_factory")
    @patch("asyncgateway.client.os.listdir")
    @patch("asyncgateway.client.importlib.util.spec_from_file_location")
    @patch("asyncgateway.client.importlib.util.module_from_spec")
    async def test_services_initialized_with_ipsdk_client(
        self,
        mock_module_from_spec,
        mock_spec_from_file,
        mock_listdir,
        mock_gateway_factory,
    ):
        """Test that services are properly initialized with the ipsdk client."""
        mock_listdir.side_effect = [["devices.py"], []]
        mock_client = Mock()
        mock_gateway_factory.return_value = mock_client

        mock_spec = Mock()
        mock_spec_from_file.return_value = mock_spec

        mock_module = Mock()
        mock_module_from_spec.return_value = mock_module

        mock_service_class = Mock()
        mock_service_class.name = "devices"
        mock_service_instance = Mock()
        mock_service_instance.name = "devices"
        mock_service_class.return_value = mock_service_instance
        mock_module.Service = mock_service_class

        async with Client() as client:
            # Verify service was initialized on client.services
            assert hasattr(client.services, "devices")
            mock_service_class.assert_called_once_with(mock_client)

    @pytest.mark.asyncio
    @patch("asyncgateway.client.ipsdk.gateway_factory")
    @patch("asyncgateway.client.os.listdir")
    async def test_client_parameters_passed_to_ipsdk(
        self, mock_listdir, mock_gateway_factory
    ):
        """Test that client parameters are properly passed to ipsdk factory."""
        mock_listdir.side_effect = [[], []]
        mock_client = Mock()
        mock_gateway_factory.return_value = mock_client

        client_kwargs = {
            "host": "example.com",
            "port": 8080,
            "username": "testuser",
            "password": "testpass",
            "ssl_verify": False,
        }

        Client(**client_kwargs)

        mock_gateway_factory.assert_called_once_with(want_async=True, **client_kwargs)

    @pytest.mark.asyncio
    @patch("asyncgateway.client.ipsdk.gateway_factory")
    @patch("asyncgateway.client.os.listdir")
    async def test_context_manager_exception_handling(
        self, mock_listdir, mock_gateway_factory
    ):
        """Test that context manager properly handles exceptions in user code."""
        mock_listdir.side_effect = [[], []]
        mock_client = Mock()
        mock_gateway_factory.return_value = mock_client

        test_exception = ValueError("User code error")

        # Exception in user code should still propagate
        with pytest.raises(ValueError, match="User code error"):
            async with Client():
                raise test_exception
