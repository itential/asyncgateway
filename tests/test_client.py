# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from unittest.mock import Mock, patch

import pytest

from asyncgateway.client import Client


class TestClient:
    @patch("ipsdk.gateway_factory")
    @patch("os.listdir")
    @patch("importlib.util.spec_from_file_location")
    @patch("importlib.util.module_from_spec")
    def test_init_services_basic(
        self,
        mock_module_from_spec,
        mock_spec_from_file,
        mock_listdir,
        mock_gateway_factory,
    ):
        # Mock the directory listing - called twice: once for services, once for resources
        mock_listdir.side_effect = [
            ["devices.py", "config.py", "__init__.py", "_private.py"],
            [],
        ]

        # Mock the ipsdk client
        mock_client = Mock()
        mock_gateway_factory.return_value = mock_client

        # Mock the importlib functionality
        mock_spec = Mock()
        mock_spec_from_file.return_value = mock_spec

        mock_module = Mock()
        mock_module_from_spec.return_value = mock_module

        # Mock the service class
        mock_service_class = Mock()
        mock_service_class.name = "devices"
        mock_service_instance = Mock()
        mock_service_instance.name = "devices"
        mock_service_class.return_value = mock_service_instance
        mock_module.Service = mock_service_class

        # Create client
        client = Client(host="localhost", port=3000)

        # Verify ipsdk factory was called with correct args
        mock_gateway_factory.assert_called_once_with(
            want_async=True, host="localhost", port=3000
        )

        # Verify only non-underscore .py files were processed
        expected_files = [
            "devices",
            "config",
        ]  # __init__.py and _private.py should be excluded
        actual_calls = [call[0][0] for call in mock_spec_from_file.call_args_list]
        assert set(actual_calls) == set(expected_files)

        # Verify service was attached to client.services
        assert hasattr(client.services, "devices")
        assert client.services.devices == mock_service_instance
        mock_service_class.assert_called_with(mock_client)

    @patch("ipsdk.gateway_factory")
    @patch("os.listdir")
    def test_init_services_empty_directory(self, mock_listdir, mock_gateway_factory):
        mock_listdir.side_effect = [[], []]
        mock_gateway_factory.return_value = Mock()

        client = Client()

        # Should not fail with empty directory
        assert isinstance(client, Client)

    @patch("ipsdk.gateway_factory")
    @patch("os.listdir")
    def test_init_services_no_py_files(self, mock_listdir, mock_gateway_factory):
        mock_listdir.side_effect = [["README.md", "data.json", "script.sh"], []]
        mock_gateway_factory.return_value = Mock()

        client = Client()

        # Should not fail with no .py files
        assert isinstance(client, Client)

    @patch("ipsdk.gateway_factory")
    @patch("os.listdir")
    @patch("importlib.util.spec_from_file_location")
    @patch("importlib.util.module_from_spec")
    def test_init_services_service_with_no_service_class(
        self,
        mock_module_from_spec,
        mock_spec_from_file,
        mock_listdir,
        mock_gateway_factory,
    ):
        mock_listdir.side_effect = [["broken.py"], []]
        mock_gateway_factory.return_value = Mock()

        mock_spec = Mock()
        mock_spec_from_file.return_value = mock_spec

        mock_module = Mock()
        mock_module_from_spec.return_value = mock_module
        mock_module.Service = None  # No Service class

        client = Client()

        # Should handle missing Service class gracefully
        assert isinstance(client, Client)

    @patch("ipsdk.gateway_factory")
    @patch("os.listdir")
    @patch("importlib.util.spec_from_file_location")
    @patch("importlib.util.module_from_spec")
    def test_init_services_multiple_services(
        self,
        mock_module_from_spec,
        mock_spec_from_file,
        mock_listdir,
        mock_gateway_factory,
    ):
        mock_listdir.side_effect = [["devices.py", "config.py", "playbooks.py"], []]
        mock_client = Mock()
        mock_gateway_factory.return_value = mock_client

        mock_spec = Mock()
        mock_spec_from_file.return_value = mock_spec

        # Create different mock modules for each service
        services_data = [
            ("devices", "devices"),
            ("config", "config"),
            ("playbooks", "playbooks"),
        ]

        mock_modules = []
        for _service_name, service_attr in services_data:
            mock_module = Mock()
            mock_service_class = Mock()
            mock_service_class.name = service_attr
            mock_service_instance = Mock()
            mock_service_instance.name = service_attr
            mock_service_class.return_value = mock_service_instance
            mock_module.Service = mock_service_class
            mock_modules.append(mock_module)

        mock_module_from_spec.side_effect = mock_modules

        client = Client()

        # Verify all services were attached to client.services
        assert hasattr(client.services, "devices")
        assert hasattr(client.services, "config")
        assert hasattr(client.services, "playbooks")

    def test_services_directory_path(self):
        # Test that the services path is constructed correctly using os.path functions
        with (
            patch("os.path.dirname") as mock_dirname,
            patch("os.path.realpath") as mock_realpath,
            patch("os.path.join") as mock_join,
            patch("ipsdk.gateway_factory"),
            patch("os.listdir", side_effect=[[], []]),
        ):
            mock_realpath.return_value = "/path/to/asyncgateway/client.py"
            mock_dirname.return_value = "/path/to/asyncgateway"
            mock_join.return_value = "/path/to/asyncgateway/services"

            Client()

            # realpath is called at least once (once for services path, once for resources path)
            assert mock_realpath.call_count >= 1
            # dirname is called with the realpath result
            mock_dirname.assert_called_with("/path/to/asyncgateway/client.py")
            # os.path.join is called for both services and resources paths
            assert mock_join.call_count >= 1

    @pytest.mark.asyncio
    async def test_aenter(self):
        with (
            patch("ipsdk.gateway_factory"),
            patch("os.listdir", side_effect=[[], []]),
        ):
            client = Client()
            result = await client.__aenter__()

            assert result is client

    @pytest.mark.asyncio
    async def test_aexit(self):
        with (
            patch("ipsdk.gateway_factory"),
            patch("os.listdir", side_effect=[[], []]),
        ):
            client = Client()
            # Should not raise any exceptions
            await client.__aexit__(None, None, None)

    @pytest.mark.asyncio
    async def test_aexit_with_exception(self):
        with (
            patch("ipsdk.gateway_factory"),
            patch("os.listdir", side_effect=[[], []]),
        ):
            client = Client()
            # Should handle exceptions gracefully
            await client.__aexit__(ValueError, ValueError("test"), None)

    @pytest.mark.asyncio
    async def test_async_context_manager_usage(self):
        with (
            patch("ipsdk.gateway_factory"),
            patch("os.listdir", side_effect=[[], []]),
        ):
            async with Client() as client:
                assert isinstance(client, Client)

    @patch("ipsdk.gateway_factory")
    @patch("os.listdir")
    @patch("importlib.util.spec_from_file_location")
    @patch("importlib.util.module_from_spec")
    def test_init_passes_kwargs_to_gateway_factory(
        self,
        mock_module_from_spec,
        mock_spec_from_file,
        mock_listdir,
        mock_gateway_factory,
    ):
        mock_listdir.side_effect = [[], []]
        mock_gateway_factory.return_value = Mock()

        kwargs = {
            "host": "example.com",
            "port": 8080,
            "username": "testuser",
            "password": "testpass",
            "ssl_verify": False,
        }

        Client(**kwargs)

        mock_gateway_factory.assert_called_once_with(want_async=True, **kwargs)

    @patch("ipsdk.gateway_factory")
    @patch("os.listdir")
    @patch("importlib.util.spec_from_file_location")
    @patch("importlib.util.module_from_spec")
    def test_service_loader_exception_handling(
        self,
        mock_module_from_spec,
        mock_spec_from_file,
        mock_listdir,
        mock_gateway_factory,
    ):
        mock_listdir.side_effect = [["broken.py"], []]
        mock_gateway_factory.return_value = Mock()

        # Simulate an exception during module loading
        mock_spec_from_file.side_effect = Exception("Module loading failed")

        # Should not raise exception, but handle it gracefully
        with pytest.raises(Exception, match="Module loading failed"):
            Client()

    @patch("ipsdk.gateway_factory")
    @patch("os.listdir")
    @patch("importlib.util.spec_from_file_location")
    @patch("importlib.util.module_from_spec")
    def test_service_with_invalid_name_attribute(
        self,
        mock_module_from_spec,
        mock_spec_from_file,
        mock_listdir,
        mock_gateway_factory,
    ):
        mock_listdir.side_effect = [["test.py"], []]
        mock_client = Mock()
        mock_gateway_factory.return_value = mock_client

        mock_spec = Mock()
        mock_spec_from_file.return_value = mock_spec

        mock_module = Mock()
        mock_module_from_spec.return_value = mock_module

        # Service class with invalid name attribute (None will cause TypeError in setattr)
        mock_service_class = Mock()
        mock_service_class.name = None
        mock_service_instance = Mock()
        mock_service_class.return_value = mock_service_instance
        mock_module.Service = mock_service_class

        # setattr with None as attribute name should raise TypeError
        with pytest.raises(TypeError):
            Client()
