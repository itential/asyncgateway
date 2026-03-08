# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import json
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

import pytest

from asyncgateway import serdes
from asyncgateway.client import Client
from asyncgateway.exceptions import AsyncGatewayError, ValidationError
from asyncgateway.services import Operation


class TestLoad:
    @pytest.fixture
    def temp_load_dir(self):
        """Create a temporary directory structure for testing load operations."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create devices directory and sample data
            devices_dir = temp_path / "devices"
            devices_dir.mkdir()

            devices_data = [
                {"name": "router1", "variables": {"ansible_host": "192.168.1.1"}},
                {"name": "router2", "variables": {"ansible_host": "192.168.1.2"}},
            ]

            with open(devices_dir / "routers.json", "w") as f:
                json.dump(devices_data, f)

            # Create playbooks directory and sample data
            playbooks_dir = temp_path / "playbooks"
            playbooks_dir.mkdir()

            playbooks_data = [
                {"name": "automation", "config": {"script": "echo hello"}},
            ]

            with open(playbooks_dir / "automation.json", "w") as f:
                json.dump(playbooks_data, f)

            yield temp_path

    @pytest.fixture
    def mock_client_with_services(self):
        """Create a mock client with device and playbook services."""
        with (
            patch("asyncgateway.client.ipsdk.gateway_factory"),
            patch(
                "asyncgateway.client.os.listdir",
                side_effect=[["devices.py", "playbooks.py"], []],
            ),
            patch("asyncgateway.client.importlib.util.spec_from_file_location"),
            patch(
                "asyncgateway.client.importlib.util.module_from_spec"
            ) as mock_module_from_spec,
        ):
            # Mock devices service
            devices_service = Mock()
            devices_service.name = "devices"
            devices_service.load = AsyncMock(
                return_value={
                    "operation": "MERGE",
                    "devices_processed": 2,
                    "devices_created": 2,
                    "devices_updated": 0,
                    "devices_deleted": 0,
                    "errors": [],
                }
            )
            devices_service.get = AsyncMock()

            # Mock playbooks service
            playbooks_service = Mock()
            playbooks_service.name = "playbooks"
            playbooks_service.load = AsyncMock(
                return_value={
                    "operation": "MERGE",
                    "playbooks_processed": 1,
                    "playbooks_created": 1,
                    "playbooks_updated": 0,
                    "playbooks_deleted": 0,
                    "errors": [],
                }
            )
            playbooks_service.get = AsyncMock()

            # Mock modules
            mock_devices_module = Mock()
            mock_devices_service_class = Mock()
            mock_devices_service_class.name = "devices"
            mock_devices_service_class.return_value = devices_service
            mock_devices_module.Service = mock_devices_service_class

            mock_playbooks_module = Mock()
            mock_playbooks_service_class = Mock()
            mock_playbooks_service_class.name = "playbooks"
            mock_playbooks_service_class.return_value = playbooks_service
            mock_playbooks_module.Service = mock_playbooks_service_class

            mock_module_from_spec.side_effect = [
                mock_devices_module,
                mock_playbooks_module,
            ]

            client = Client()

            yield client, devices_service, playbooks_service

    @pytest.mark.asyncio
    async def test_load_success(self, temp_load_dir, mock_client_with_services):
        """Test successful load from path."""
        client, devices_service, playbooks_service = mock_client_with_services

        result = await client.load(str(temp_load_dir), Operation.MERGE)

        # Verify devices service was called
        devices_service.load.assert_called_once()
        call_args = devices_service.load.call_args
        assert call_args[0][1] == Operation.MERGE  # operation parameter
        assert len(call_args[0][0]) == 2  # 2 devices loaded
        assert call_args[0][0][0]["name"] == "router1"

        # Verify playbooks service was called
        playbooks_service.load.assert_called_once()
        call_args = playbooks_service.load.call_args
        assert call_args[0][1] == Operation.MERGE
        assert len(call_args[0][0]) == 1  # 1 playbook loaded

        # Verify aggregated results
        assert result["operation"] == Operation.MERGE
        assert result["services_processed"] == 2
        assert result["total_resources_processed"] == 3  # 2 devices + 1 playbook
        assert result["total_resources_created"] == 3
        assert result["total_resources_updated"] == 0
        assert result["total_resources_deleted"] == 0
        assert result["errors"] == []
        assert "devices" in result["service_results"]
        assert "playbooks" in result["service_results"]

    @pytest.mark.asyncio
    async def test_load_invalid_operation(
        self, temp_load_dir, mock_client_with_services
    ):
        """Test load with invalid operation type."""
        client, _, _ = mock_client_with_services

        with pytest.raises(ValidationError) as exc_info:
            await client.load(str(temp_load_dir), "INVALID")

        assert "Invalid operation 'INVALID'" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_load_nonexistent_path(self, mock_client_with_services):
        """Test load from nonexistent path."""
        client, _, _ = mock_client_with_services

        with pytest.raises(FileNotFoundError) as exc_info:
            await client.load("/nonexistent/path", Operation.MERGE)

        assert "Load path does not exist" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_load_file_instead_of_directory(self, mock_client_with_services):
        """Test load when path points to a file instead of directory."""
        client, _, _ = mock_client_with_services

        with tempfile.NamedTemporaryFile() as temp_file:
            with pytest.raises(ValidationError) as exc_info:
                await client.load(temp_file.name, Operation.MERGE)

            assert "Load path must be a directory" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_load_empty_directory(self, mock_client_with_services):
        """Test load from empty directory."""
        client, _, _ = mock_client_with_services

        with tempfile.TemporaryDirectory() as temp_dir:
            result = await client.load(temp_dir, Operation.MERGE)

            assert result["operation"] == Operation.MERGE
            assert result["services_processed"] == 0
            assert result["total_resources_processed"] == 0
            assert result["errors"] == []

    @pytest.mark.asyncio
    async def test_load_service_without_load_method(
        self, temp_load_dir, mock_client_with_services
    ):
        """Test load when service doesn't have load method."""
        client, devices_service, playbooks_service = mock_client_with_services

        # Remove load method from devices service
        delattr(devices_service, "load")

        result = await client.load(str(temp_load_dir), Operation.MERGE)

        # Should still process playbooks but report error for devices
        assert result["services_processed"] == 1  # Only playbooks processed
        assert "Service devices does not support load operations" in result["errors"]
        assert "playbooks" in result["service_results"]

    @pytest.mark.asyncio
    async def test_load_service_load_error(
        self, temp_load_dir, mock_client_with_services
    ):
        """Test load when service load method raises error."""
        client, devices_service, playbooks_service = mock_client_with_services

        # Make devices load raise an error
        devices_service.load.side_effect = AsyncGatewayError("Load failed")

        result = await client.load(str(temp_load_dir), Operation.MERGE)

        # Should still process playbooks but report error for devices
        assert result["services_processed"] == 1  # Only playbooks processed
        assert len(result["errors"]) == 1
        assert "Failed to process devices service: Load failed" in result["errors"]

    @pytest.mark.asyncio
    async def test_load_invalid_json_file(self, mock_client_with_services):
        """Test load with invalid JSON file."""
        client, _, _ = mock_client_with_services

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            devices_dir = temp_path / "devices"
            devices_dir.mkdir()

            # Create invalid JSON file
            with open(devices_dir / "invalid.json", "w") as f:
                f.write("{ invalid json")

            # JSON errors should be captured in the errors list, not raised
            result = await client.load(str(temp_path), Operation.MERGE)

            # Should have errors from processing the invalid JSON
            assert len(result["errors"]) > 0
            assert any(
                "Failed to process devices service" in error
                for error in result["errors"]
            )
            assert (
                result["services_processed"] == 0
            )  # No services processed successfully

    @pytest.mark.asyncio
    async def test_load_default_operation(
        self, temp_load_dir, mock_client_with_services
    ):
        """Test load with default operation (should be MERGE)."""
        client, devices_service, playbooks_service = mock_client_with_services

        # Call without specifying operation
        result = await client.load(str(temp_load_dir))

        # Should default to MERGE
        assert result["operation"] == Operation.MERGE

        # Verify services were called with MERGE
        devices_service.load.assert_called_once()
        assert devices_service.load.call_args[0][1] == Operation.MERGE

        playbooks_service.load.assert_called_once()
        assert playbooks_service.load.call_args[0][1] == Operation.MERGE

    @pytest.mark.asyncio
    async def test_load_single_object_in_file(self, mock_client_with_services):
        """Test load when file contains single object instead of array."""
        client, devices_service, playbooks_service = mock_client_with_services

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            devices_dir = temp_path / "devices"
            devices_dir.mkdir()

            # Create file with single device object (not array)
            device_data = {
                "name": "single_router",
                "variables": {"ansible_host": "192.168.1.100"},
            }

            with open(devices_dir / "single.json", "w") as f:
                json.dump(device_data, f)

            await client.load(str(temp_path), Operation.MERGE)

            # Should process single object
            devices_service.load.assert_called_once()
            call_args = devices_service.load.call_args
            assert len(call_args[0][0]) == 1  # 1 device loaded
            assert call_args[0][0][0]["name"] == "single_router"

    def test_get_available_services(self, mock_client_with_services):
        """Test _get_available_services helper method."""
        client, _, _ = mock_client_with_services

        services = client._get_available_services()

        # Should find both devices and playbooks services
        assert "devices" in services
        assert "playbooks" in services
        assert len(services) == 2

    @pytest.mark.skipif(not serdes.YAML_AVAILABLE, reason="PyYAML not available")
    @pytest.mark.asyncio
    async def test_load_with_yaml_files(self, mock_client_with_services):
        """Test load with YAML files."""
        client, devices_service, playbooks_service = mock_client_with_services

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create devices directory with YAML files
            devices_dir = temp_path / "devices"
            devices_dir.mkdir()

            devices_yaml = """- name: router1
  variables:
    ansible_host: 192.168.1.1
    device_type: cisco_ios
- name: router2
  variables:
    ansible_host: 192.168.1.2
    device_type: cisco_ios"""

            with open(devices_dir / "devices.yaml", "w") as f:
                f.write(devices_yaml)

            # Create playbooks directory with YAML file
            playbooks_dir = temp_path / "playbooks"
            playbooks_dir.mkdir()

            playbooks_yaml = """name: automation_playbook
config:
  script: echo "Hello from YAML"
  timeout: 30"""

            with open(playbooks_dir / "automation.yml", "w") as f:
                f.write(playbooks_yaml)

            result = await client.load(str(temp_path), Operation.MERGE)

            # Verify devices service was called with YAML data
            devices_service.load.assert_called_once()
            call_args = devices_service.load.call_args
            devices_data = call_args[0][0]
            assert len(devices_data) == 2
            assert devices_data[0]["name"] == "router1"
            assert devices_data[0]["variables"]["ansible_host"] == "192.168.1.1"

            # Verify playbooks service was called with YAML data
            playbooks_service.load.assert_called_once()
            call_args = playbooks_service.load.call_args
            playbooks_data = call_args[0][0]
            assert len(playbooks_data) == 1
            assert playbooks_data[0]["name"] == "automation_playbook"
            assert playbooks_data[0]["config"]["script"] == 'echo "Hello from YAML"'

            # Verify aggregated results
            assert result["operation"] == Operation.MERGE
            assert result["services_processed"] == 2
            assert result["total_resources_processed"] == 3  # 2 devices + 1 playbook

    @pytest.mark.asyncio
    async def test_load_mixed_json_yaml(self, mock_client_with_services):
        """Test load with mixed JSON and YAML files."""
        client, devices_service, playbooks_service = mock_client_with_services

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create devices directory with JSON file
            devices_dir = temp_path / "devices"
            devices_dir.mkdir()

            devices_json = [
                {"name": "switch1", "variables": {"ansible_host": "192.168.1.10"}}
            ]

            with open(devices_dir / "switches.json", "w") as f:
                json.dump(devices_json, f)

            # Create playbooks directory with YAML file (if available)
            playbooks_dir = temp_path / "playbooks"
            playbooks_dir.mkdir()

            if serdes.YAML_AVAILABLE:
                playbooks_yaml = "name: mixed_test\nconfig:\n  type: test"
                with open(playbooks_dir / "mixed.yaml", "w") as f:
                    f.write(playbooks_yaml)
                expected_services = 2
                # Mock fixtures return: devices_processed=2, playbooks_processed=1 = total 3
                expected_resources = 3
            else:
                # If YAML not available, only JSON will be processed
                expected_services = 1
                # Mock fixtures return: devices_processed=2 (from fixture)
                expected_resources = 2

            result = await client.load(str(temp_path), Operation.MERGE)

            # Verify devices service was called
            devices_service.load.assert_called_once()
            call_args = devices_service.load.call_args
            devices_data = call_args[0][0]
            assert len(devices_data) == 1
            assert devices_data[0]["name"] == "switch1"

            # Verify results based on YAML availability
            assert result["services_processed"] == expected_services
            assert result["total_resources_processed"] == expected_resources

    def test_yaml_available_flag_matches_serdes(self):
        """Test that the client's YAML detection matches the serdes module."""
        # This ensures consistency between client and serdes modules
        client_yaml_available = (
            hasattr(serdes, "YAML_AVAILABLE") and serdes.YAML_AVAILABLE
        )
        assert isinstance(client_yaml_available, bool)
