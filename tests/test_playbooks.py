# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from unittest.mock import AsyncMock, Mock, patch

import pytest

from asyncgateway.resources.playbooks import Resource as PlaybooksResource
from asyncgateway.services import Operation
from asyncgateway.services.playbooks import Service as PlaybooksService


class TestPlaybooksService:
    @pytest.fixture
    def mock_client(self):
        """Create a mock ipsdk client."""
        client = Mock()
        return client

    @pytest.fixture
    def playbooks_service(self, mock_client):
        """Create a PlaybooksService instance with a mock client."""
        return PlaybooksService(mock_client)

    @pytest.fixture
    def mock_services(self, playbooks_service):
        """Create a mock services namespace with playbooks service."""
        services = Mock()
        services.playbooks = playbooks_service
        return services

    @pytest.fixture
    def playbooks_resource(self, mock_services):
        """Create a PlaybooksResource instance with mock services."""
        return PlaybooksResource(mock_services)

    def test_service_name(self, playbooks_service):
        """Test that the service has the correct name."""
        assert playbooks_service.name == "playbooks"

    def test_service_inherits_from_service_base(self):
        """Test that PlaybooksService inherits from ServiceBase."""
        from asyncgateway.services import ServiceBase

        assert issubclass(PlaybooksService, ServiceBase)

    def test_service_initialization(self, mock_client):
        """Test that the service initializes correctly with a client."""
        service = PlaybooksService(mock_client)
        assert service.client is mock_client
        assert service.name == "playbooks"

    @pytest.mark.asyncio
    async def test_get_playbook_success(self, playbooks_service, mock_client):
        """Test successfully getting a playbook by name."""
        playbook_data = {
            "name": "network_config",
            "description": "Configure network devices",
            "variables": ["hostname", "config_template"],
            "tasks": ["configure", "validate"],
        }

        mock_response = Mock()
        mock_response.json.return_value = playbook_data
        mock_client.get = AsyncMock(return_value=mock_response)

        result = await playbooks_service.get("network_config")

        mock_client.get.assert_called_once_with("/playbooks/network_config")
        mock_response.json.assert_called_once()
        assert result == playbook_data

    @pytest.mark.asyncio
    async def test_get_all_playbooks_single_page(self, playbooks_service, mock_client):
        """Test getting all playbooks when they fit in a single page."""
        playbooks_data = {
            "data": [
                {"name": "playbook1", "description": "First playbook"},
                {"name": "playbook2", "description": "Second playbook"},
            ],
            "meta": {"count": 2},
        }

        mock_response = Mock()
        mock_response.json.return_value = playbooks_data
        mock_client.get = AsyncMock(return_value=mock_response)

        result = await playbooks_service.get_all()

        mock_client.get.assert_called_once_with(
            "/playbooks", params={"limit": 100, "offset": 0}
        )
        assert result == playbooks_data["data"]
        assert len(result) == 2

    @pytest.mark.asyncio
    async def test_get_all_playbooks_multiple_pages(
        self, playbooks_service, mock_client
    ):
        """Test getting all playbooks when they span multiple pages."""
        # First page
        page1_data = {
            "data": [
                {"name": f"playbook{i}", "description": f"Playbook {i}"}
                for i in range(1, 101)
            ],
            "meta": {"count": 150},
        }

        # Second page
        page2_data = {
            "data": [
                {"name": f"playbook{i}", "description": f"Playbook {i}"}
                for i in range(101, 151)
            ],
            "meta": {"count": 150},
        }

        mock_response_1 = Mock()
        mock_response_1.json.return_value = page1_data
        mock_response_2 = Mock()
        mock_response_2.json.return_value = page2_data

        mock_client.get = AsyncMock(side_effect=[mock_response_1, mock_response_2])

        result = await playbooks_service.get_all()

        assert mock_client.get.call_count == 2
        # Check that both calls were to /playbooks
        for call in mock_client.get.call_args_list:
            assert call.args == ("/playbooks",)
            assert "params" in call.kwargs
            assert call.kwargs["params"]["limit"] == 100
            assert "offset" in call.kwargs["params"]

        assert len(result) == 150
        assert result[0]["name"] == "playbook1"
        assert result[149]["name"] == "playbook150"

    @pytest.mark.asyncio
    async def test_get_all_playbooks_empty(self, playbooks_service, mock_client):
        """Test getting all playbooks when no playbooks exist."""
        playbooks_data = {"data": [], "meta": {"count": 0}}

        mock_response = Mock()
        mock_response.json.return_value = playbooks_data
        mock_client.get = AsyncMock(return_value=mock_response)

        result = await playbooks_service.get_all()

        mock_client.get.assert_called_once_with(
            "/playbooks", params={"limit": 100, "offset": 0}
        )
        assert result == []

    @pytest.mark.asyncio
    async def test_refresh_success(self, playbooks_service, mock_client):
        """Test successfully refreshing playbooks."""
        refresh_result = {
            "success": True,
            "updated_count": 5,
            "message": "Playbooks refreshed successfully",
        }

        mock_response = Mock()
        mock_response.json.return_value = refresh_result
        mock_client.post = AsyncMock(return_value=mock_response)

        result = await playbooks_service.refresh()

        mock_client.post.assert_called_once_with("/playbooks/refresh")
        mock_response.json.assert_called_once()
        assert result == refresh_result

    @pytest.mark.asyncio
    async def test_refresh_failure(self, playbooks_service, mock_client):
        """Test playbook refresh with failure result."""
        refresh_result = {
            "success": False,
            "error": "Repository connection failed",
            "updated_count": 0,
        }

        mock_response = Mock()
        mock_response.json.return_value = refresh_result
        mock_client.post = AsyncMock(return_value=mock_response)

        result = await playbooks_service.refresh()

        mock_client.post.assert_called_once_with("/playbooks/refresh")
        assert result == refresh_result

    @pytest.mark.asyncio
    async def test_get_schema_success(self, playbooks_service, mock_client):
        """Test successfully getting a playbook schema."""
        schema_data = {
            "type": "object",
            "properties": {
                "hostname": {"type": "string", "description": "Target device hostname"},
                "config_template": {
                    "type": "string",
                    "description": "Configuration template to apply",
                },
            },
            "required": ["hostname"],
        }

        mock_response = Mock()
        mock_response.json.return_value = schema_data
        mock_client.get = AsyncMock(return_value=mock_response)

        result = await playbooks_service.get_schema("network_config")

        mock_client.get.assert_called_once_with("/playbooks/network_config/schema")
        mock_response.json.assert_called_once()
        assert result == schema_data

    @pytest.mark.asyncio
    async def test_update_schema_success(self, playbooks_service, mock_client):
        """Test successfully updating a playbook schema."""
        new_schema = {
            "type": "object",
            "properties": {
                "hostname": {"type": "string", "description": "Target device hostname"},
                "config_template": {
                    "type": "string",
                    "description": "Configuration template to apply",
                },
                "backup_enabled": {
                    "type": "boolean",
                    "description": "Enable configuration backup",
                    "default": True,
                },
            },
            "required": ["hostname", "config_template"],
        }

        updated_schema = new_schema.copy()
        updated_schema["updated_at"] = "2025-01-01T00:00:00Z"

        mock_response = Mock()
        mock_response.json.return_value = updated_schema
        mock_client.put = AsyncMock(return_value=mock_response)

        result = await playbooks_service.update_schema("network_config", new_schema)

        mock_client.put.assert_called_once_with(
            "/playbooks/network_config/schema", json=new_schema
        )
        mock_response.json.assert_called_once()
        assert result == updated_schema

    @pytest.mark.asyncio
    async def test_update_schema_empty_schema(self, playbooks_service, mock_client):
        """Test updating a playbook schema with empty schema."""
        empty_schema = {}

        mock_response = Mock()
        mock_response.json.return_value = {"message": "Schema cleared"}
        mock_client.put = AsyncMock(return_value=mock_response)

        result = await playbooks_service.update_schema("network_config", empty_schema)

        mock_client.put.assert_called_once_with(
            "/playbooks/network_config/schema", json=empty_schema
        )
        assert result == {"message": "Schema cleared"}

    @pytest.mark.asyncio
    async def test_delete_schema_success(self, playbooks_service, mock_client):
        """Test successfully deleting a playbook schema."""
        delete_result = {"success": True, "message": "Schema deleted successfully"}

        mock_response = Mock()
        mock_response.json.return_value = delete_result
        mock_client.delete = AsyncMock(return_value=mock_response)

        result = await playbooks_service.delete_schema("old_playbook")

        mock_client.delete.assert_called_once_with("/playbooks/old_playbook/schema")
        mock_response.json.assert_called_once()
        assert result == delete_result

    @pytest.mark.asyncio
    async def test_delete_schema_not_found(self, playbooks_service, mock_client):
        """Test deleting a playbook schema that doesn't exist."""
        delete_result = {"success": False, "error": "Schema not found"}

        mock_response = Mock()
        mock_response.json.return_value = delete_result
        mock_client.delete = AsyncMock(return_value=mock_response)

        result = await playbooks_service.delete_schema("nonexistent_playbook")

        mock_client.delete.assert_called_once_with(
            "/playbooks/nonexistent_playbook/schema"
        )
        assert result == delete_result

    @pytest.mark.asyncio
    async def test_get_all_pagination_edge_case(self, playbooks_service, mock_client):
        """Test pagination edge case where total equals limit exactly."""
        playbooks_data = {
            "data": [
                {"name": f"playbook{i}", "description": f"Playbook {i}"}
                for i in range(1, 101)
            ],
            "meta": {"count": 100},
        }

        mock_response = Mock()
        mock_response.json.return_value = playbooks_data
        mock_client.get = AsyncMock(return_value=mock_response)

        result = await playbooks_service.get_all()

        # Should only make one call since total equals limit
        mock_client.get.assert_called_once_with(
            "/playbooks", params={"limit": 100, "offset": 0}
        )
        assert len(result) == 100

    @pytest.mark.asyncio
    async def test_get_playbook_with_special_characters(
        self, playbooks_service, mock_client
    ):
        """Test getting a playbook with special characters in name."""
        playbook_name = "network-config_v2.1"
        playbook_data = {
            "name": playbook_name,
            "description": "Network configuration v2.1",
            "version": "2.1.0",
        }

        mock_response = Mock()
        mock_response.json.return_value = playbook_data
        mock_client.get = AsyncMock(return_value=mock_response)

        result = await playbooks_service.get(playbook_name)

        mock_client.get.assert_called_once_with(f"/playbooks/{playbook_name}")
        assert result == playbook_data

    @pytest.mark.asyncio
    async def test_create_playbook(self, playbooks_service, mock_client):
        """Test creating a new playbook."""
        playbook_data = {
            "description": "Network configuration playbook",
            "tasks": ["configure", "validate"],
        }

        mock_client.post = AsyncMock()

        await playbooks_service.create("network_config", playbook_data)

        expected_body = {"name": "network_config", **playbook_data}
        mock_client.post.assert_called_once_with("/playbooks", json=expected_body)

    @pytest.mark.asyncio
    async def test_delete_playbook(self, playbooks_service, mock_client):
        """Test deleting a playbook by name."""
        mock_client.delete = AsyncMock()

        await playbooks_service.delete("old_playbook")

        mock_client.delete.assert_called_once_with("/playbooks/old_playbook")

    @pytest.mark.asyncio
    async def test_load_playbooks_merge_operation(
        self, playbooks_resource, mock_client
    ):
        """Test load with MERGE operation."""
        load_data = [
            {"name": "playbook1", "description": "First playbook", "tasks": ["task1"]},
            {"name": "playbook2", "description": "Second playbook", "tasks": ["task2"]},
            {"name": "playbook3", "description": "Third playbook", "tasks": ["task3"]},
        ]

        # Mock existing playbooks - playbook1 already exists
        existing_playbooks = [
            {"name": "playbook1", "description": "Existing playbook"},
        ]

        with patch.object(
            playbooks_resource.services.playbooks,
            "get_all",
            return_value=existing_playbooks,
        ):
            mock_client.post = AsyncMock()

            result = await playbooks_resource.load(load_data, Operation.MERGE)

            # Should only create playbook2 and playbook3 (skip existing playbook1)
            assert mock_client.post.call_count == 2
            expected_calls = [
                {
                    "name": "playbook2",
                    "description": "Second playbook",
                    "tasks": ["task2"],
                },
                {
                    "name": "playbook3",
                    "description": "Third playbook",
                    "tasks": ["task3"],
                },
            ]
            actual_calls = [
                call.kwargs["json"] for call in mock_client.post.call_args_list
            ]
            assert actual_calls == expected_calls

            assert result["operation"] == Operation.MERGE
            assert result["playbooks_processed"] == 3
            assert result["playbooks_created"] == 2
            assert result["playbooks_updated"] == 0
            assert result["playbooks_deleted"] == 0

    @pytest.mark.asyncio
    async def test_load_playbooks_replace_operation(
        self, playbooks_resource, mock_client
    ):
        """Test load with REPLACE operation."""
        load_data = [
            {"name": "playbook1", "description": "First playbook", "tasks": ["task1"]},
            {"name": "playbook2", "description": "Second playbook", "tasks": ["task2"]},
        ]

        # Mock existing playbooks
        existing_playbooks = [
            {"name": "playbook3", "description": "Existing playbook"},
            {"name": "playbook4", "description": "Another existing playbook"},
        ]

        with patch.object(
            playbooks_resource.services.playbooks,
            "get_all",
            return_value=existing_playbooks,
        ):
            mock_client.delete = AsyncMock()
            mock_client.post = AsyncMock()

            result = await playbooks_resource.load(load_data, Operation.REPLACE)

            # Should delete all existing playbooks first
            assert mock_client.delete.call_count == 2
            delete_calls = [call.args[0] for call in mock_client.delete.call_args_list]
            assert "/playbooks/playbook3" in delete_calls
            assert "/playbooks/playbook4" in delete_calls

            # Then create new playbooks
            assert mock_client.post.call_count == 2
            expected_calls = [
                {
                    "name": "playbook1",
                    "description": "First playbook",
                    "tasks": ["task1"],
                },
                {
                    "name": "playbook2",
                    "description": "Second playbook",
                    "tasks": ["task2"],
                },
            ]
            actual_calls = [
                call.kwargs["json"] for call in mock_client.post.call_args_list
            ]
            assert actual_calls == expected_calls

            assert result["operation"] == Operation.REPLACE
            assert result["playbooks_processed"] == 2
            assert result["playbooks_created"] == 2
            assert result["playbooks_updated"] == 0
            assert result["playbooks_deleted"] == 2

    @pytest.mark.asyncio
    async def test_load_playbooks_overwrite_operation(
        self, playbooks_resource, mock_client
    ):
        """Test load with OVERWRITE operation."""
        load_data = [
            {
                "name": "playbook1",
                "description": "Updated playbook",
                "tasks": ["new_task"],
            },
            {"name": "playbook2", "description": "New playbook", "tasks": ["task2"]},
        ]

        # Mock existing playbooks - playbook1 already exists
        existing_playbooks = [
            {"name": "playbook1", "description": "Old description"},
            {"name": "playbook3", "description": "Unrelated playbook"},
        ]

        with patch.object(
            playbooks_resource.services.playbooks,
            "get_all",
            return_value=existing_playbooks,
        ):
            mock_client.delete = AsyncMock()
            mock_client.post = AsyncMock()

            result = await playbooks_resource.load(load_data, Operation.OVERWRITE)

            # Should delete playbook1 (existing playbook to be overwritten) and create both playbooks
            assert mock_client.delete.call_count == 1
            mock_client.delete.assert_called_with("/playbooks/playbook1")

            # Should create playbook1 (after deletion) and playbook2 (new playbook)
            assert mock_client.post.call_count == 2
            expected_calls = [
                {
                    "name": "playbook1",
                    "description": "Updated playbook",
                    "tasks": ["new_task"],
                },
                {
                    "name": "playbook2",
                    "description": "New playbook",
                    "tasks": ["task2"],
                },
            ]
            actual_calls = [
                call.kwargs["json"] for call in mock_client.post.call_args_list
            ]
            assert actual_calls == expected_calls

            assert result["operation"] == Operation.OVERWRITE
            assert result["playbooks_processed"] == 2
            assert result["playbooks_created"] == 1  # playbook2 is new
            assert result["playbooks_updated"] == 1  # playbook1 was overwritten
            assert result["playbooks_deleted"] == 0

    @pytest.mark.asyncio
    async def test_load_playbooks_empty_data(self, playbooks_resource, mock_client):
        """Test load with empty data."""
        with patch.object(
            playbooks_resource.services.playbooks, "get_all", return_value=[]
        ):
            result = await playbooks_resource.load([], Operation.MERGE)

            assert result["operation"] == Operation.MERGE
            assert result["playbooks_processed"] == 0
            assert result["playbooks_created"] == 0
            assert result["playbooks_updated"] == 0
            assert result["playbooks_deleted"] == 0
            assert result["errors"] == []

    @pytest.mark.asyncio
    async def test_load_playbooks_invalid_operation(
        self, playbooks_resource, mock_client
    ):
        """Test load with invalid operation."""
        load_data = [{"name": "playbook1", "description": "Test playbook"}]

        with pytest.raises(Exception) as exc_info:
            await playbooks_resource.load(load_data, "invalid_operation")

        assert "Invalid operation 'invalid_operation'" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_load_playbooks_missing_name(self, playbooks_resource, mock_client):
        """Test load with playbook data missing name."""
        load_data = [
            {
                "description": "Missing name playbook",
                "tasks": ["task1"],
            },  # Missing name
            {"name": "playbook2", "description": "Valid playbook", "tasks": ["task2"]},
        ]

        with patch.object(
            playbooks_resource.services.playbooks, "get_all", return_value=[]
        ):
            mock_client.post = AsyncMock()

            result = await playbooks_resource.load(load_data, Operation.MERGE)

            # Should only create playbook2, skip the playbook without name
            assert mock_client.post.call_count == 1
            mock_client.post.assert_called_with(
                "/playbooks",
                json={
                    "name": "playbook2",
                    "description": "Valid playbook",
                    "tasks": ["task2"],
                },
            )

            assert result["playbooks_processed"] == 2
            assert result["playbooks_created"] == 1
            assert len(result["errors"]) == 1
            assert "Playbook missing name field" in result["errors"][0]

    @pytest.mark.asyncio
    async def test_load_playbooks_with_create_errors(
        self, playbooks_resource, mock_client
    ):
        """Test load with errors during playbook creation."""
        load_data = [
            {"name": "playbook1", "description": "First playbook"},
            {"name": "playbook2", "description": "Second playbook"},
        ]

        with patch.object(
            playbooks_resource.services.playbooks, "get_all", return_value=[]
        ):
            # Mock client.post to fail for playbook2
            def post_side_effect(*args, **kwargs):
                if kwargs.get("json", {}).get("name") == "playbook2":
                    raise Exception("Creation failed")
                return AsyncMock()

            mock_client.post = AsyncMock(side_effect=post_side_effect)

            result = await playbooks_resource.load(load_data, Operation.MERGE)

            assert result["playbooks_processed"] == 2
            assert result["playbooks_created"] == 1  # Only playbook1 succeeded
            assert len(result["errors"]) == 1
            assert "Failed to process playbook2: Creation failed" in result["errors"][0]
