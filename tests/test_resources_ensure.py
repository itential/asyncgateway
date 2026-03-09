# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Tests for declarative (ensure/absent) resources: groups, accounts, secrets, rbac, inventory, git.

These resources implement idempotent CRUD patterns:
  - ensure: create-or-get (or create-or-update for secrets/inventory)
  - absent: delete, swallow NotFound
  - Membership management (groups, rbac)
  - Pure-create wrappers (git)
"""

from unittest.mock import AsyncMock, Mock

import pytest

from asyncgateway.resources.accounts import Resource as AccountsResource
from asyncgateway.resources.git import Resource as GitResource
from asyncgateway.resources.groups import Resource as GroupsResource
from asyncgateway.resources.inventory import Resource as InventoryResource
from asyncgateway.resources.rbac import Resource as RbacResource
from asyncgateway.resources.secrets import Resource as SecretsResource

# ---------------------------------------------------------------------------
# Groups
# ---------------------------------------------------------------------------


class TestGroupsResource:
    @pytest.fixture
    def mock_groups_service(self):
        svc = Mock()
        svc.get = AsyncMock(return_value={"name": "datacenter", "devices": []})
        svc.create = AsyncMock(return_value={"name": "datacenter", "devices": []})
        svc.delete = AsyncMock(return_value=None)
        svc.add_devices = AsyncMock(
            return_value={"name": "datacenter", "devices": ["router1"]}
        )
        svc.remove_device = AsyncMock(return_value=None)
        svc.add_children = AsyncMock(
            return_value={"name": "datacenter", "children": ["rack1"]}
        )
        svc.remove_child = AsyncMock(return_value=None)
        return svc

    @pytest.fixture
    def groups_resource(self, mock_groups_service):
        services = Mock()
        services.groups = mock_groups_service
        return GroupsResource(services)

    def test_resource_name(self, groups_resource):
        assert groups_resource.name == "groups"

    @pytest.mark.asyncio
    async def test_ensure_creates_group_when_not_found(
        self, groups_resource, mock_groups_service
    ):
        mock_groups_service.get.side_effect = Exception("not found")
        mock_groups_service.create.return_value = {"name": "new_group", "devices": []}

        result = await groups_resource.ensure("new_group")

        mock_groups_service.get.assert_called_once_with("new_group")
        mock_groups_service.create.assert_called_once_with("new_group", None)
        assert result == {"name": "new_group", "devices": []}

    @pytest.mark.asyncio
    async def test_ensure_creates_group_with_variables(
        self, groups_resource, mock_groups_service
    ):
        mock_groups_service.get.side_effect = Exception("not found")
        variables = {"description": "My group"}
        mock_groups_service.create.return_value = {
            "name": "new_group",
            "description": "My group",
        }

        result = await groups_resource.ensure("new_group", variables)

        mock_groups_service.create.assert_called_once_with("new_group", variables)
        assert result["description"] == "My group"

    @pytest.mark.asyncio
    async def test_ensure_returns_existing_group(
        self, groups_resource, mock_groups_service
    ):
        existing = {"name": "datacenter", "devices": ["router1"]}
        mock_groups_service.get.return_value = existing

        result = await groups_resource.ensure("datacenter")

        mock_groups_service.get.assert_called_once_with("datacenter")
        mock_groups_service.create.assert_not_called()
        assert result == existing

    @pytest.mark.asyncio
    async def test_absent_deletes_existing_group(
        self, groups_resource, mock_groups_service
    ):
        await groups_resource.absent("datacenter")

        mock_groups_service.delete.assert_called_once_with("datacenter")

    @pytest.mark.asyncio
    async def test_absent_swallows_exception_when_group_not_found(
        self, groups_resource, mock_groups_service
    ):
        mock_groups_service.delete.side_effect = Exception("group not found")

        # Should not raise
        await groups_resource.absent("nonexistent_group")

        mock_groups_service.delete.assert_called_once_with("nonexistent_group")

    @pytest.mark.asyncio
    async def test_add_device(self, groups_resource, mock_groups_service):
        result = await groups_resource.add_device("datacenter", "router1")

        mock_groups_service.add_devices.assert_called_once_with(
            "datacenter", ["router1"]
        )
        assert result == {"name": "datacenter", "devices": ["router1"]}

    @pytest.mark.asyncio
    async def test_add_device_wraps_single_name_in_list(
        self, groups_resource, mock_groups_service
    ):
        await groups_resource.add_device("grp", "switch99")

        call_args = mock_groups_service.add_devices.call_args
        assert call_args[0][1] == ["switch99"]

    @pytest.mark.asyncio
    async def test_remove_device(self, groups_resource, mock_groups_service):
        await groups_resource.remove_device("datacenter", "router1")

        mock_groups_service.remove_device.assert_called_once_with(
            "datacenter", "router1"
        )

    @pytest.mark.asyncio
    async def test_add_child(self, groups_resource, mock_groups_service):
        result = await groups_resource.add_child("datacenter", "rack1")

        mock_groups_service.add_children.assert_called_once_with(
            "datacenter", ["rack1"]
        )
        assert result == {"name": "datacenter", "children": ["rack1"]}

    @pytest.mark.asyncio
    async def test_add_child_wraps_single_name_in_list(
        self, groups_resource, mock_groups_service
    ):
        await groups_resource.add_child("parent", "child_group")

        call_args = mock_groups_service.add_children.call_args
        assert call_args[0][1] == ["child_group"]

    @pytest.mark.asyncio
    async def test_remove_child(self, groups_resource, mock_groups_service):
        await groups_resource.remove_child("datacenter", "rack1")

        mock_groups_service.remove_child.assert_called_once_with("datacenter", "rack1")


# ---------------------------------------------------------------------------
# Accounts
# ---------------------------------------------------------------------------


class TestAccountsResource:
    @pytest.fixture
    def mock_accounts_service(self):
        svc = Mock()
        svc.get = AsyncMock(return_value={"username": "admin", "role": "admin"})
        svc.create = AsyncMock(return_value={"username": "admin", "role": "admin"})
        svc.delete = AsyncMock(return_value=None)
        return svc

    @pytest.fixture
    def accounts_resource(self, mock_accounts_service):
        services = Mock()
        services.accounts = mock_accounts_service
        return AccountsResource(services)

    def test_resource_name(self, accounts_resource):
        assert accounts_resource.name == "accounts"

    @pytest.mark.asyncio
    async def test_ensure_returns_existing_account(
        self, accounts_resource, mock_accounts_service
    ):
        existing = {"username": "admin", "role": "admin"}
        mock_accounts_service.get.return_value = existing

        result = await accounts_resource.ensure("admin", {"role": "admin"})

        mock_accounts_service.get.assert_called_once_with("admin")
        mock_accounts_service.create.assert_not_called()
        assert result == existing

    @pytest.mark.asyncio
    async def test_ensure_creates_account_when_not_found(
        self, accounts_resource, mock_accounts_service
    ):
        mock_accounts_service.get.side_effect = Exception("account not found")
        params = {"username": "newuser", "role": "viewer"}
        mock_accounts_service.create.return_value = {
            "username": "newuser",
            "role": "viewer",
        }

        result = await accounts_resource.ensure("newuser", params)

        mock_accounts_service.get.assert_called_once_with("newuser")
        mock_accounts_service.create.assert_called_once_with(params)
        assert result == {"username": "newuser", "role": "viewer"}

    @pytest.mark.asyncio
    async def test_ensure_passes_full_params_to_create(
        self, accounts_resource, mock_accounts_service
    ):
        mock_accounts_service.get.side_effect = Exception("not found")
        params = {"username": "op_user", "role": "operator", "email": "op@example.com"}

        await accounts_resource.ensure("op_user", params)

        mock_accounts_service.create.assert_called_once_with(params)

    @pytest.mark.asyncio
    async def test_absent_deletes_existing_account(
        self, accounts_resource, mock_accounts_service
    ):
        await accounts_resource.absent("admin")

        mock_accounts_service.delete.assert_called_once_with("admin")

    @pytest.mark.asyncio
    async def test_absent_swallows_exception_when_not_found(
        self, accounts_resource, mock_accounts_service
    ):
        mock_accounts_service.delete.side_effect = Exception("account not found")

        # Should not raise
        await accounts_resource.absent("nonexistent_user")

        mock_accounts_service.delete.assert_called_once_with("nonexistent_user")


# ---------------------------------------------------------------------------
# Secrets
# ---------------------------------------------------------------------------


class TestSecretsResource:
    @pytest.fixture
    def mock_secrets_service(self):
        svc = Mock()
        svc.update = AsyncMock(return_value={"id": "secret1", "updated": True})
        svc.create = AsyncMock(return_value={"id": "secret1", "created": True})
        svc.delete = AsyncMock(return_value=None)
        return svc

    @pytest.fixture
    def secrets_resource(self, mock_secrets_service):
        services = Mock()
        services.secrets = mock_secrets_service
        return SecretsResource(services)

    def test_resource_name(self, secrets_resource):
        assert secrets_resource.name == "secrets"

    @pytest.mark.asyncio
    async def test_ensure_updates_when_secret_exists(
        self, secrets_resource, mock_secrets_service
    ):
        params = {"name": "db_password", "value": "new_pass"}
        result = await secrets_resource.ensure(params)

        mock_secrets_service.update.assert_called_once_with(params)
        mock_secrets_service.create.assert_not_called()
        assert result == {"id": "secret1", "updated": True}

    @pytest.mark.asyncio
    async def test_ensure_creates_when_update_fails(
        self, secrets_resource, mock_secrets_service
    ):
        mock_secrets_service.update.side_effect = Exception("secret not found")
        params = {"name": "new_secret", "value": "my_value"}

        result = await secrets_resource.ensure(params)

        mock_secrets_service.update.assert_called_once_with(params)
        mock_secrets_service.create.assert_called_once_with(params)
        assert result == {"id": "secret1", "created": True}

    @pytest.mark.asyncio
    async def test_ensure_propagates_create_exception(
        self, secrets_resource, mock_secrets_service
    ):
        mock_secrets_service.update.side_effect = Exception("not found")
        mock_secrets_service.create.side_effect = Exception("validation error")
        params = {"name": "bad_secret"}

        with pytest.raises(Exception, match="validation error"):
            await secrets_resource.ensure(params)

    @pytest.mark.asyncio
    async def test_absent_deletes_secret(self, secrets_resource, mock_secrets_service):
        params = {"name": "db_password"}
        await secrets_resource.absent(params)

        mock_secrets_service.delete.assert_called_once_with(params)

    @pytest.mark.asyncio
    async def test_absent_swallows_exception_when_not_found(
        self, secrets_resource, mock_secrets_service
    ):
        mock_secrets_service.delete.side_effect = Exception("secret not found")
        params = {"name": "nonexistent_secret"}

        # Should not raise
        await secrets_resource.absent(params)

        mock_secrets_service.delete.assert_called_once_with(params)

    @pytest.mark.asyncio
    async def test_ensure_passes_params_unchanged_to_update(
        self, secrets_resource, mock_secrets_service
    ):
        params = {"name": "my_secret", "value": "abc123"}
        await secrets_resource.ensure(params)

        assert mock_secrets_service.update.call_args[0][0] is params


# ---------------------------------------------------------------------------
# RBAC
# ---------------------------------------------------------------------------


class TestRbacResource:
    @pytest.fixture
    def mock_rbac_service(self):
        svc = Mock()
        svc.get_group = AsyncMock(return_value={"name": "admins", "roles": []})
        svc.create_group = AsyncMock(return_value={"name": "admins", "roles": []})
        svc.delete_group = AsyncMock(return_value=None)
        svc.add_group_roles = AsyncMock(
            return_value={"name": "admins", "roles": ["admin"]}
        )
        svc.remove_group_role = AsyncMock(return_value=None)
        svc.add_group_users = AsyncMock(
            return_value={"name": "admins", "users": ["alice"]}
        )
        svc.remove_group_user = AsyncMock(return_value=None)
        return svc

    @pytest.fixture
    def rbac_resource(self, mock_rbac_service):
        services = Mock()
        services.rbac = mock_rbac_service
        return RbacResource(services)

    def test_resource_name(self, rbac_resource):
        assert rbac_resource.name == "rbac"

    @pytest.mark.asyncio
    async def test_ensure_group_returns_existing(
        self, rbac_resource, mock_rbac_service
    ):
        existing = {"name": "admins", "roles": ["admin"]}
        mock_rbac_service.get_group.return_value = existing

        result = await rbac_resource.ensure_group("admins")

        mock_rbac_service.get_group.assert_called_once_with("admins")
        mock_rbac_service.create_group.assert_not_called()
        assert result == existing

    @pytest.mark.asyncio
    async def test_ensure_group_creates_when_not_found(
        self, rbac_resource, mock_rbac_service
    ):
        mock_rbac_service.get_group.side_effect = Exception("group not found")
        mock_rbac_service.create_group.return_value = {"name": "editors", "roles": []}

        result = await rbac_resource.ensure_group("editors")

        mock_rbac_service.create_group.assert_called_once_with({"name": "editors"})
        assert result == {"name": "editors", "roles": []}

    @pytest.mark.asyncio
    async def test_ensure_group_creates_with_provided_params(
        self, rbac_resource, mock_rbac_service
    ):
        mock_rbac_service.get_group.side_effect = Exception("not found")
        params = {"name": "viewers", "description": "Read-only group"}
        mock_rbac_service.create_group.return_value = params

        await rbac_resource.ensure_group("viewers", params)

        mock_rbac_service.create_group.assert_called_once_with(params)

    @pytest.mark.asyncio
    async def test_ensure_group_uses_name_as_default_params(
        self, rbac_resource, mock_rbac_service
    ):
        mock_rbac_service.get_group.side_effect = Exception("not found")

        await rbac_resource.ensure_group("operators")

        mock_rbac_service.create_group.assert_called_once_with({"name": "operators"})

    @pytest.mark.asyncio
    async def test_absent_group_deletes_group(self, rbac_resource, mock_rbac_service):
        await rbac_resource.absent_group("old_group")

        mock_rbac_service.delete_group.assert_called_once_with("old_group")

    @pytest.mark.asyncio
    async def test_absent_group_swallows_exception(
        self, rbac_resource, mock_rbac_service
    ):
        mock_rbac_service.delete_group.side_effect = Exception("group not found")

        # Should not raise
        await rbac_resource.absent_group("nonexistent_group")

        mock_rbac_service.delete_group.assert_called_once_with("nonexistent_group")

    @pytest.mark.asyncio
    async def test_add_role(self, rbac_resource, mock_rbac_service):
        result = await rbac_resource.add_role("admins", "admin")

        mock_rbac_service.add_group_roles.assert_called_once_with("admins", ["admin"])
        assert result == {"name": "admins", "roles": ["admin"]}

    @pytest.mark.asyncio
    async def test_add_role_wraps_role_name_in_list(
        self, rbac_resource, mock_rbac_service
    ):
        await rbac_resource.add_role("grp", "my_role")

        call_args = mock_rbac_service.add_group_roles.call_args
        assert call_args[0][1] == ["my_role"]

    @pytest.mark.asyncio
    async def test_remove_role(self, rbac_resource, mock_rbac_service):
        await rbac_resource.remove_role("admins", "admin")

        mock_rbac_service.remove_group_role.assert_called_once_with("admins", "admin")

    @pytest.mark.asyncio
    async def test_add_user(self, rbac_resource, mock_rbac_service):
        result = await rbac_resource.add_user("admins", "alice")

        mock_rbac_service.add_group_users.assert_called_once_with("admins", ["alice"])
        assert result == {"name": "admins", "users": ["alice"]}

    @pytest.mark.asyncio
    async def test_add_user_wraps_user_name_in_list(
        self, rbac_resource, mock_rbac_service
    ):
        await rbac_resource.add_user("grp", "bob")

        call_args = mock_rbac_service.add_group_users.call_args
        assert call_args[0][1] == ["bob"]

    @pytest.mark.asyncio
    async def test_remove_user(self, rbac_resource, mock_rbac_service):
        await rbac_resource.remove_user("admins", "alice")

        mock_rbac_service.remove_group_user.assert_called_once_with("admins", "alice")


# ---------------------------------------------------------------------------
# Inventory
# ---------------------------------------------------------------------------


class TestInventoryResource:
    @pytest.fixture
    def mock_inventory_service(self):
        svc = Mock()
        svc.refresh = AsyncMock(return_value={"refreshed": True, "count": 10})
        svc.update_device = AsyncMock(
            return_value={"name": "router1", "status": "updated"}
        )
        svc.create_device = AsyncMock(
            return_value={"name": "router1", "status": "created"}
        )
        svc.delete_device = AsyncMock(return_value=None)
        return svc

    @pytest.fixture
    def inventory_resource(self, mock_inventory_service):
        services = Mock()
        services.inventory = mock_inventory_service
        return InventoryResource(services)

    def test_resource_name(self, inventory_resource):
        assert inventory_resource.name == "inventory"

    @pytest.mark.asyncio
    async def test_refresh(self, inventory_resource, mock_inventory_service):
        result = await inventory_resource.refresh()

        mock_inventory_service.refresh.assert_called_once_with()
        assert result == {"refreshed": True, "count": 10}

    @pytest.mark.asyncio
    async def test_ensure_device_updates_existing(
        self, inventory_resource, mock_inventory_service
    ):
        params = {"ip": "10.0.0.1", "type": "router"}
        result = await inventory_resource.ensure_device(
            "netbox", "primary_inventory", "router1", params
        )

        mock_inventory_service.update_device.assert_called_once_with(
            "netbox", "primary_inventory", "router1", params
        )
        mock_inventory_service.create_device.assert_not_called()
        assert result == {"name": "router1", "status": "updated"}

    @pytest.mark.asyncio
    async def test_ensure_device_creates_when_update_fails(
        self, inventory_resource, mock_inventory_service
    ):
        mock_inventory_service.update_device.side_effect = Exception("device not found")
        params = {"name": "router1", "ip": "10.0.0.1"}
        mock_inventory_service.create_device.return_value = {
            "name": "router1",
            "status": "created",
        }

        result = await inventory_resource.ensure_device(
            "netbox", "primary_inventory", "router1", params
        )

        mock_inventory_service.update_device.assert_called_once_with(
            "netbox", "primary_inventory", "router1", params
        )
        mock_inventory_service.create_device.assert_called_once_with(
            "netbox", "primary_inventory", params
        )
        assert result == {"name": "router1", "status": "created"}

    @pytest.mark.asyncio
    async def test_ensure_device_passes_all_args(
        self, inventory_resource, mock_inventory_service
    ):
        params = {"ip": "192.168.1.1", "site": "dc1"}
        await inventory_resource.ensure_device("servicenow", "cmdb", "switch1", params)

        mock_inventory_service.update_device.assert_called_once_with(
            "servicenow", "cmdb", "switch1", params
        )

    @pytest.mark.asyncio
    async def test_absent_device_deletes(
        self, inventory_resource, mock_inventory_service
    ):
        await inventory_resource.absent_device("netbox", "primary_inventory", "router1")

        mock_inventory_service.delete_device.assert_called_once_with(
            "netbox", "primary_inventory", "router1"
        )

    @pytest.mark.asyncio
    async def test_absent_device_swallows_exception(
        self, inventory_resource, mock_inventory_service
    ):
        mock_inventory_service.delete_device.side_effect = Exception("device not found")

        # Should not raise
        await inventory_resource.absent_device(
            "netbox", "primary_inventory", "nonexistent"
        )

        mock_inventory_service.delete_device.assert_called_once_with(
            "netbox", "primary_inventory", "nonexistent"
        )

    @pytest.mark.asyncio
    async def test_absent_device_passes_all_args(
        self, inventory_resource, mock_inventory_service
    ):
        await inventory_resource.absent_device("cmdb", "production", "firewall1")

        mock_inventory_service.delete_device.assert_called_once_with(
            "cmdb", "production", "firewall1"
        )


# ---------------------------------------------------------------------------
# Git
# ---------------------------------------------------------------------------


class TestGitResource:
    @pytest.fixture
    def mock_git_service(self):
        svc = Mock()
        svc.create_key = AsyncMock(
            return_value={"id": "key1", "public_key": "ssh-rsa AAAA..."}
        )
        svc.create_integration = AsyncMock(
            return_value={"id": "integration1", "type": "github"}
        )
        svc.create_repository = AsyncMock(
            return_value={"id": "repo1", "url": "https://github.com/org/repo"}
        )
        return svc

    @pytest.fixture
    def git_resource(self, mock_git_service):
        services = Mock()
        services.git = mock_git_service
        return GitResource(services)

    def test_resource_name(self, git_resource):
        assert git_resource.name == "git"

    @pytest.mark.asyncio
    async def test_ensure_key(self, git_resource, mock_git_service):
        params = {"name": "deploy_key", "private_key": "-----BEGIN OPENSSH..."}
        result = await git_resource.ensure_key(params)

        mock_git_service.create_key.assert_called_once_with(params)
        assert result == {"id": "key1", "public_key": "ssh-rsa AAAA..."}

    @pytest.mark.asyncio
    async def test_ensure_key_passes_params_unchanged(
        self, git_resource, mock_git_service
    ):
        params = {"name": "my_key"}
        await git_resource.ensure_key(params)

        assert mock_git_service.create_key.call_args[0][0] is params

    @pytest.mark.asyncio
    async def test_ensure_integration(self, git_resource, mock_git_service):
        params = {
            "type": "github",
            "token": "ghp_...",
            "base_url": "https://api.github.com",
        }
        result = await git_resource.ensure_integration(params)

        mock_git_service.create_integration.assert_called_once_with(params)
        assert result == {"id": "integration1", "type": "github"}

    @pytest.mark.asyncio
    async def test_ensure_integration_passes_params_unchanged(
        self, git_resource, mock_git_service
    ):
        params = {"type": "gitlab", "token": "glpat-..."}
        await git_resource.ensure_integration(params)

        assert mock_git_service.create_integration.call_args[0][0] is params

    @pytest.mark.asyncio
    async def test_ensure_repository(self, git_resource, mock_git_service):
        params = {
            "name": "network-configs",
            "integration_id": "integration1",
            "branch": "main",
        }
        result = await git_resource.ensure_repository(params)

        mock_git_service.create_repository.assert_called_once_with(params)
        assert result == {"id": "repo1", "url": "https://github.com/org/repo"}

    @pytest.mark.asyncio
    async def test_ensure_repository_passes_params_unchanged(
        self, git_resource, mock_git_service
    ):
        params = {"name": "configs", "branch": "develop"}
        await git_resource.ensure_repository(params)

        assert mock_git_service.create_repository.call_args[0][0] is params
