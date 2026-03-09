# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from unittest.mock import AsyncMock, Mock, patch

import pytest

from asyncgateway.exceptions import ValidationError
from asyncgateway.resources.devices import Resource as DevicesResource
from asyncgateway.services import Operation
from asyncgateway.services.devices import Service as DevicesService


class TestDevicesService:
    @pytest.fixture
    def mock_client(self):
        """Create a mock ipsdk client."""
        client = Mock()
        return client

    @pytest.fixture
    def devices_service(self, mock_client):
        """Create a DevicesService instance with a mock client."""
        return DevicesService(mock_client)

    @pytest.fixture
    def mock_services(self, devices_service):
        """Create a mock services namespace with devices service."""
        services = Mock()
        services.devices = devices_service
        return services

    @pytest.fixture
    def devices_resource(self, mock_services):
        """Create a DevicesResource instance with mock services."""
        return DevicesResource(mock_services)

    def test_service_name(self, devices_service):
        """Test that the service has the correct name."""
        assert devices_service.name == "devices"

    @pytest.mark.asyncio
    async def test_get_device_success(self, devices_service, mock_client):
        """Test successfully getting a device by name."""
        device_data = {
            "name": "router1",
            "variables": {"ansible_host": "192.168.1.1", "device_type": "cisco_ios"},
        }

        mock_response = Mock()
        mock_response.json.return_value = device_data
        mock_client.get = AsyncMock(return_value=mock_response)

        result = await devices_service.get("router1")

        mock_client.get.assert_called_once_with("/devices/router1")
        mock_response.json.assert_called_once()
        assert result == device_data

    @pytest.mark.asyncio
    async def test_get_all_devices_single_page(self, devices_service, mock_client):
        """Test getting all devices when they fit in a single page."""
        devices_data = {
            "data": [
                {"name": "router1", "variables": {"ansible_host": "192.168.1.1"}},
                {"name": "router2", "variables": {"ansible_host": "192.168.1.2"}},
            ],
            "meta": {"total_count": 2},
        }

        mock_response = Mock()
        mock_response.json.return_value = devices_data
        mock_client.get = AsyncMock(return_value=mock_response)

        result = await devices_service.get_all()

        mock_client.get.assert_called_once_with(
            "/devices", params={"limit": 100, "offset": 0}
        )
        assert result == devices_data["data"]

    @pytest.mark.asyncio
    async def test_get_all_devices_multiple_pages(self, devices_service, mock_client):
        """Test getting all devices when they span multiple pages."""
        # First page
        page1_data = {
            "data": [{"name": f"router{i}", "variables": {}} for i in range(1, 101)],
            "meta": {"total_count": 150},
        }

        # Second page
        page2_data = {
            "data": [{"name": f"router{i}", "variables": {}} for i in range(101, 151)],
            "meta": {"total_count": 150},
        }

        mock_response_1 = Mock()
        mock_response_1.json.return_value = page1_data
        mock_response_2 = Mock()
        mock_response_2.json.return_value = page2_data

        mock_client.get = AsyncMock(side_effect=[mock_response_1, mock_response_2])

        result = await devices_service.get_all()

        assert mock_client.get.call_count == 2
        # Check that both calls were to /devices
        for call in mock_client.get.call_args_list:
            assert call.args == ("/devices",)
            assert "params" in call.kwargs
            assert call.kwargs["params"]["limit"] == 100
            assert "offset" in call.kwargs["params"]

        assert len(result) == 150
        assert result[0]["name"] == "router1"
        assert result[149]["name"] == "router150"

    @pytest.mark.asyncio
    async def test_get_all_devices_empty(self, devices_service, mock_client):
        """Test getting all devices when no devices exist."""
        devices_data = {"data": [], "meta": {"total_count": 0}}

        mock_response = Mock()
        mock_response.json.return_value = devices_data
        mock_client.get = AsyncMock(return_value=mock_response)

        result = await devices_service.get_all()

        mock_client.get.assert_called_once_with(
            "/devices", params={"limit": 100, "offset": 0}
        )
        assert result == []

    @pytest.mark.asyncio
    async def test_create_device_with_variables(self, devices_service, mock_client):
        """Test creating a device with variables."""
        variables = {
            "ansible_host": "192.168.1.1",
            "ansible_user": "admin",
            "device_type": "cisco_ios",
        }

        mock_client.post = AsyncMock()

        await devices_service.create("router1", variables)

        expected_body = {"name": "router1", "variables": variables}
        mock_client.post.assert_called_once_with("/devices", json=expected_body)

    @pytest.mark.asyncio
    async def test_create_device_without_variables(self, devices_service, mock_client):
        """Test creating a device without variables."""
        mock_client.post = AsyncMock()

        await devices_service.create("router1")

        expected_body = {"name": "router1", "variables": {}}
        mock_client.post.assert_called_once_with("/devices", json=expected_body)

    @pytest.mark.asyncio
    async def test_create_device_with_none_variables(
        self, devices_service, mock_client
    ):
        """Test creating a device with None variables."""
        mock_client.post = AsyncMock()

        await devices_service.create("router1", None)

        expected_body = {"name": "router1", "variables": {}}
        mock_client.post.assert_called_once_with("/devices", json=expected_body)

    @pytest.mark.asyncio
    async def test_delete_device(self, devices_service, mock_client):
        """Test deleting a device by name."""
        mock_client.delete = AsyncMock()

        await devices_service.delete("router1")

        mock_client.delete.assert_called_once_with("/devices/router1")

    @pytest.mark.asyncio
    async def test_delete_all_devices(self, devices_service, mock_client):
        """Test deleting all devices regardless of name."""
        devices_data = [
            {"name": "router1", "variables": {}},
            {"name": "router2", "variables": {}},
            {"name": "switch1", "variables": {}},
            {"name": "router_backup", "variables": {}},
            {"name": "firewall1", "variables": {}},
        ]

        with patch.object(
            devices_service, "get_all", return_value=devices_data
        ) as mock_get_all:
            mock_client.delete = AsyncMock()

            await devices_service.delete_all()

            mock_get_all.assert_called_once()

            # Should delete all devices
            expected_calls = [
                ("/devices/router1",),
                ("/devices/router2",),
                ("/devices/switch1",),
                ("/devices/router_backup",),
                ("/devices/firewall1",),
            ]
            actual_calls = [call.args for call in mock_client.delete.call_args_list]
            assert actual_calls == expected_calls
            assert mock_client.delete.call_count == 5

    @pytest.mark.asyncio
    async def test_delete_all_devices_non_router_names(
        self, devices_service, mock_client
    ):
        """Test delete_all deletes all devices regardless of name prefix."""
        devices_data = [
            {"name": "switch1", "variables": {}},
            {"name": "firewall1", "variables": {}},
            {"name": "server1", "variables": {}},
        ]

        with patch.object(
            devices_service, "get_all", return_value=devices_data
        ) as mock_get_all:
            mock_client.delete = AsyncMock()

            await devices_service.delete_all()

            mock_get_all.assert_called_once()
            assert mock_client.delete.call_count == 3

    @pytest.mark.asyncio
    async def test_delete_all_devices_empty_list(self, devices_service, mock_client):
        """Test delete_all when no devices exist."""
        with patch.object(devices_service, "get_all", return_value=[]) as mock_get_all:
            mock_client.delete = AsyncMock()

            await devices_service.delete_all()

            mock_get_all.assert_called_once()
            mock_client.delete.assert_not_called()

    def test_service_inherits_from_service_base(self):
        """Test that DevicesService inherits from ServiceBase."""
        from asyncgateway.services import ServiceBase

        assert issubclass(DevicesService, ServiceBase)

    def test_service_initialization(self, mock_client):
        """Test that the service initializes correctly with a client."""
        service = DevicesService(mock_client)
        assert service.client is mock_client
        assert service.name == "devices"

    @pytest.mark.asyncio
    async def test_patch_device(self, devices_service, mock_client):
        """Test patching device variables."""
        patch_data = {"ansible_host": "10.0.0.99", "device_type": "cisco_nxos"}
        patched = {"name": "router1", "variables": patch_data}

        mock_response = Mock()
        mock_response.json.return_value = patched
        mock_client.patch = AsyncMock(return_value=mock_response)

        result = await devices_service.patch("router1", patch_data)

        mock_client.patch.assert_called_once_with(
            "/devices/router1", json={"variables": patch_data}
        )
        assert result == patched

    @pytest.mark.asyncio
    async def test_get_variables(self, devices_service, mock_client):
        """Test getting all variables for a device."""
        variables = {"ansible_host": "192.168.1.1", "device_type": "cisco_ios"}

        mock_response = Mock()
        mock_response.json.return_value = variables
        mock_client.get = AsyncMock(return_value=mock_response)

        result = await devices_service.get_variables("router1")

        mock_client.get.assert_called_once_with("/devices/router1/variables")
        assert result == variables

    @pytest.mark.asyncio
    async def test_get_variable(self, devices_service, mock_client):
        """Test getting a specific variable for a device."""
        variable = {"ansible_host": "192.168.1.1"}

        mock_response = Mock()
        mock_response.json.return_value = variable
        mock_client.get = AsyncMock(return_value=mock_response)

        result = await devices_service.get_variable("router1", "ansible_host")

        mock_client.get.assert_called_once_with(
            "/devices/router1/variables/ansible_host"
        )
        assert result == variable

    @pytest.mark.asyncio
    async def test_get_state(self, devices_service, mock_client):
        """Test getting the state of a device."""
        state = {"status": "reachable", "last_seen": "2025-01-01T00:00:00Z"}

        mock_response = Mock()
        mock_response.json.return_value = state
        mock_client.get = AsyncMock(return_value=mock_response)

        result = await devices_service.get_state("router1")

        mock_client.get.assert_called_once_with("/devices/router1/state")
        assert result == state

    @pytest.mark.asyncio
    async def test_load_devices_merge_operation(self, devices_resource, mock_client):
        """Test loading devices with MERGE operation."""
        existing_devices = [
            {"name": "router1", "variables": {"ansible_host": "192.168.1.1"}},
            {"name": "router2", "variables": {"ansible_host": "192.168.1.2"}},
        ]

        new_devices = [
            {"name": "router1", "variables": {"ansible_host": "10.0.0.1"}},  # Existing
            {"name": "router3", "variables": {"ansible_host": "192.168.1.3"}},  # New
        ]

        with patch.object(
            devices_resource.services.devices, "get_all", return_value=existing_devices
        ):
            mock_client.post = AsyncMock()

            result = await devices_resource.load(new_devices, Operation.MERGE)

            assert result["operation"] == Operation.MERGE
            assert result["devices_processed"] == 2
            assert result["devices_created"] == 1  # Only router3 created
            assert result["devices_updated"] == 0
            assert result["devices_deleted"] == 0
            assert len(result["errors"]) == 0

            # Only router3 should be created (router1 skipped in merge mode)
            mock_client.post.assert_called_once_with(
                "/devices",
                json={"name": "router3", "variables": {"ansible_host": "192.168.1.3"}},
            )

    @pytest.mark.asyncio
    async def test_load_devices_overwrite_operation(
        self, devices_resource, mock_client
    ):
        """Test loading devices with OVERWRITE operation."""
        existing_devices = [
            {"name": "router1", "variables": {"ansible_host": "192.168.1.1"}},
        ]

        new_devices = [
            {
                "name": "router1",
                "variables": {"ansible_host": "10.0.0.1"},
            },  # Update existing
            {"name": "router2", "variables": {"ansible_host": "192.168.1.2"}},  # New
        ]

        with patch.object(
            devices_resource.services.devices, "get_all", return_value=existing_devices
        ):
            mock_client.delete = AsyncMock()
            mock_client.post = AsyncMock()

            result = await devices_resource.load(new_devices, Operation.OVERWRITE)

            assert result["operation"] == Operation.OVERWRITE
            assert result["devices_processed"] == 2
            assert result["devices_created"] == 1  # router2
            assert result["devices_updated"] == 1  # router1
            assert result["devices_deleted"] == 0
            assert len(result["errors"]) == 0

            # router1 should be deleted then recreated, router2 should be created
            mock_client.delete.assert_called_once_with("/devices/router1")
            assert mock_client.post.call_count == 2

    @pytest.mark.asyncio
    async def test_load_devices_replace_operation(self, devices_resource, mock_client):
        """Test loading devices with REPLACE operation."""
        existing_devices = [
            {"name": "router1", "variables": {"ansible_host": "192.168.1.1"}},
            {"name": "switch1", "variables": {"ansible_host": "192.168.1.10"}},
        ]

        new_devices = [
            {"name": "router2", "variables": {"ansible_host": "192.168.1.2"}},
        ]

        with patch.object(
            devices_resource.services.devices, "get_all", return_value=existing_devices
        ):
            mock_client.delete = AsyncMock()
            mock_client.post = AsyncMock()

            result = await devices_resource.load(new_devices, Operation.REPLACE)

            assert result["operation"] == Operation.REPLACE
            assert result["devices_processed"] == 1
            assert result["devices_created"] == 1
            assert result["devices_updated"] == 0
            assert result["devices_deleted"] == 2  # Both existing devices deleted
            assert len(result["errors"]) == 0

            # All existing devices should be deleted, then new ones created
            assert mock_client.delete.call_count == 2
            mock_client.post.assert_called_once_with(
                "/devices",
                json={"name": "router2", "variables": {"ansible_host": "192.168.1.2"}},
            )

    @pytest.mark.asyncio
    async def test_load_devices_invalid_operation(self, devices_resource):
        """Test load with invalid operation type."""
        devices = [{"name": "router1", "variables": {}}]

        with pytest.raises(ValidationError, match="Invalid operation 'INVALID'"):
            await devices_resource.load(devices, "INVALID")

    @pytest.mark.asyncio
    async def test_load_devices_missing_name(self, devices_resource, mock_client):
        """Test load with device missing name field."""
        devices = [{"variables": {"ansible_host": "192.168.1.1"}}]  # Missing name

        with patch.object(
            devices_resource.services.devices, "get_all", return_value=[]
        ):
            result = await devices_resource.load(devices, Operation.MERGE)

            assert result["devices_processed"] == 1
            assert result["devices_created"] == 0
            assert len(result["errors"]) == 1
            assert "Device missing name field" in result["errors"][0]

    @pytest.mark.asyncio
    async def test_load_devices_with_errors(self, devices_resource, mock_client):
        """Test load operation with some devices causing errors."""
        devices = [
            {"name": "router1", "variables": {"ansible_host": "192.168.1.1"}},
            {"name": "router2", "variables": {"ansible_host": "192.168.1.2"}},
        ]

        with patch.object(
            devices_resource.services.devices, "get_all", return_value=[]
        ):
            # Mock post to raise an exception for router2
            def mock_post(*args, **kwargs):
                if kwargs.get("json", {}).get("name") == "router2":
                    raise Exception("Network error")
                return None

            mock_client.post = AsyncMock(side_effect=mock_post)

            result = await devices_resource.load(devices, Operation.MERGE)

            assert result["devices_processed"] == 2
            assert result["devices_created"] == 1  # Only router1 succeeded
            assert len(result["errors"]) == 1
            assert "Failed to process router2: Network error" in result["errors"][0]

    @pytest.mark.asyncio
    async def test_dump_devices_single_json_file(
        self, devices_resource, mock_client, tmp_path
    ):
        """Test dumping all devices to a single JSON file."""
        devices_data = [
            {"name": "router1", "variables": {"ansible_host": "192.168.1.1"}},
            {"name": "router2", "variables": {"ansible_host": "192.168.1.2"}},
        ]

        with (
            patch.object(
                devices_resource.services.devices, "get_all", return_value=devices_data
            ),
            patch(
                "asyncgateway.resources.devices.Path", return_value=tmp_path / "devices"
            ),
        ):
            result = await devices_resource.dump()

            assert result["format"] == "json"
            assert result["individual_files"] is False
            assert result["devices_count"] == 2
            assert len(result["files_created"]) == 1
            assert len(result["errors"]) == 0
            assert "all_devices.json" in result["files_created"][0]

    @pytest.mark.asyncio
    async def test_dump_devices_individual_yaml_files(
        self, devices_resource, mock_client, tmp_path
    ):
        """Test dumping devices to individual YAML files."""
        devices_data = [
            {"name": "router1", "variables": {"ansible_host": "192.168.1.1"}},
            {"name": "router2", "variables": {"ansible_host": "192.168.1.2"}},
        ]

        with (
            patch.object(
                devices_resource.services.devices, "get_all", return_value=devices_data
            ),
            patch(
                "asyncgateway.resources.devices.Path", return_value=tmp_path / "devices"
            ),
        ):
            result = await devices_resource.dump(
                individual_files=True, format_type="yaml"
            )

            assert result["format"] == "yaml"
            assert result["individual_files"] is True
            assert result["devices_count"] == 2
            assert len(result["files_created"]) == 2
            assert len(result["errors"]) == 0

            # Check that both device files were created
            created_files = result["files_created"]
            assert any("router1.yaml" in f for f in created_files)
            assert any("router2.yaml" in f for f in created_files)

    @pytest.mark.asyncio
    async def test_dump_devices_no_devices(self, devices_resource, mock_client):
        """Test dump operation when no devices exist."""
        with patch.object(
            devices_resource.services.devices, "get_all", return_value=[]
        ):
            result = await devices_resource.dump()

            assert result["devices_count"] == 0
            assert len(result["files_created"]) == 0
            assert len(result["errors"]) == 0

    @pytest.mark.asyncio
    async def test_dump_devices_invalid_format(self, devices_resource):
        """Test dump with invalid format type."""
        with pytest.raises(ValidationError, match="Invalid format_type 'xml'"):
            await devices_resource.dump(format_type="xml")

    @pytest.mark.asyncio
    async def test_dump_devices_yml_format_normalization(
        self, devices_resource, mock_client
    ):
        """Test that 'yml' format is normalized to 'yaml'."""
        with patch.object(
            devices_resource.services.devices, "get_all", return_value=[]
        ):
            result = await devices_resource.dump(format_type="yml")

            assert result["format"] == "yaml"  # Should be normalized

    @pytest.mark.asyncio
    async def test_dump_devices_custom_folder(
        self, devices_resource, mock_client, tmp_path
    ):
        """Test dump with custom devices folder."""
        devices_data = [{"name": "router1", "variables": {}}]
        custom_folder = "custom_devices"

        with (
            patch.object(
                devices_resource.services.devices, "get_all", return_value=devices_data
            ),
            patch(
                "asyncgateway.resources.devices.Path",
                return_value=tmp_path / custom_folder,
            ),
        ):
            result = await devices_resource.dump(devices_folder=custom_folder)

            assert result["devices_folder"] == custom_folder
            assert len(result["files_created"]) == 1

    @pytest.mark.asyncio
    async def test_dump_devices_sanitize_filename(
        self, devices_resource, mock_client, tmp_path
    ):
        """Test that device names are sanitized for filenames."""
        devices_data = [
            {"name": "router/with:special*chars?", "variables": {}},
            {"name": "router.valid-name_123", "variables": {}},
        ]

        with (
            patch.object(
                devices_resource.services.devices, "get_all", return_value=devices_data
            ),
            patch(
                "asyncgateway.resources.devices.Path", return_value=tmp_path / "devices"
            ),
        ):
            result = await devices_resource.dump(individual_files=True)

            assert len(result["files_created"]) == 2
            created_files = result["files_created"]

            # Check that filenames are sanitized
            assert any("routerwithspecialchars.json" in f for f in created_files)
            assert any("router.valid-name_123.json" in f for f in created_files)
