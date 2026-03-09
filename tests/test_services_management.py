# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Tests for management/infrastructure services:
accounts, groups, secrets, rbac, git, inventory, system,
ldap, pronghorn, ansible_venv, python_venv, user_schema.
"""

from unittest.mock import AsyncMock, Mock

import pytest

from asyncgateway.services import ServiceBase
from asyncgateway.services.accounts import Service as AccountsService
from asyncgateway.services.ansible_venv import Service as AnsibleVenvService
from asyncgateway.services.git import Service as GitService
from asyncgateway.services.groups import Service as GroupsService
from asyncgateway.services.inventory import Service as InventoryService
from asyncgateway.services.ldap import Service as LdapService
from asyncgateway.services.pronghorn import Service as PronghornService
from asyncgateway.services.python_venv import Service as PythonVenvService
from asyncgateway.services.rbac import Service as RbacService
from asyncgateway.services.secrets import Service as SecretsService
from asyncgateway.services.system import Service as SystemService
from asyncgateway.services.user_schema import Service as UserSchemaService


def _resp(data):
    r = Mock()
    r.json.return_value = data
    return r


def _paginated(items, total=None):
    return {"data": items, "meta": {"total_count": total or len(items)}}


# ===========================================================================
# Accounts
# ===========================================================================


class TestAccountsService:
    @pytest.fixture
    def client(self):
        return Mock()

    @pytest.fixture
    def svc(self, client):
        return AccountsService(client)

    def test_name(self, svc):
        assert svc.name == "accounts"

    def test_inherits_service_base(self):
        assert issubclass(AccountsService, ServiceBase)

    def test_init(self, client):
        s = AccountsService(client)
        assert s.client is client

    @pytest.mark.asyncio
    async def test_get(self, svc, client):
        data = {"username": "alice", "role": "admin"}
        client.get = AsyncMock(return_value=_resp(data))
        result = await svc.get("alice")
        client.get.assert_called_once_with("/accounts/alice")
        assert result == data

    @pytest.mark.asyncio
    async def test_get_all(self, svc, client):
        items = [{"username": "alice"}, {"username": "bob"}]
        client.get = AsyncMock(return_value=_resp(_paginated(items)))
        result = await svc.get_all()
        assert result == items

    @pytest.mark.asyncio
    async def test_get_all_with_params(self, svc, client):
        client.get = AsyncMock(return_value=_resp(_paginated([])))
        await svc.get_all(role="admin")
        args = client.get.call_args
        assert args[1]["params"]["role"] == "admin"

    @pytest.mark.asyncio
    async def test_create(self, svc, client):
        params = {"username": "charlie", "password": "s3cr3t", "role": "viewer"}
        created = {"username": "charlie", "role": "viewer", "id": "c1"}
        client.post = AsyncMock(return_value=_resp(created))
        result = await svc.create(params)
        client.post.assert_called_once_with("/accounts", json=params)
        assert result == created

    @pytest.mark.asyncio
    async def test_update(self, svc, client):
        params = {"role": "editor"}
        updated = {"username": "alice", "role": "editor"}
        client.put = AsyncMock(return_value=_resp(updated))
        result = await svc.update("alice", params)
        client.put.assert_called_once_with("/accounts/alice", json=params)
        assert result == updated

    @pytest.mark.asyncio
    async def test_delete(self, svc, client):
        client.delete = AsyncMock()
        await svc.delete("alice")
        client.delete.assert_called_once_with("/accounts/alice")

    @pytest.mark.asyncio
    async def test_update_password(self, svc, client):
        params = {"current_password": "old", "new_password": "new"}
        result_data = {"updated": True}
        client.put = AsyncMock(return_value=_resp(result_data))
        result = await svc.update_password("alice", params)
        client.put.assert_called_once_with("/accounts/alice/password", json=params)
        assert result == result_data


# ===========================================================================
# Groups
# ===========================================================================


class TestGroupsService:
    @pytest.fixture
    def client(self):
        return Mock()

    @pytest.fixture
    def svc(self, client):
        return GroupsService(client)

    def test_name(self, svc):
        assert svc.name == "groups"

    def test_inherits_service_base(self):
        assert issubclass(GroupsService, ServiceBase)

    def test_init(self, client):
        s = GroupsService(client)
        assert s.client is client

    @pytest.mark.asyncio
    async def test_get(self, svc, client):
        data = {"name": "datacenter", "devices": []}
        client.get = AsyncMock(return_value=_resp(data))
        result = await svc.get("datacenter")
        client.get.assert_called_once_with("/groups/datacenter")
        assert result == data

    @pytest.mark.asyncio
    async def test_get_all(self, svc, client):
        items = [{"name": "dc1"}, {"name": "dc2"}]
        client.get = AsyncMock(return_value=_resp(_paginated(items)))
        result = await svc.get_all()
        assert result == items

    @pytest.mark.asyncio
    async def test_create_with_variables(self, svc, client):
        variables = {"location": "ny", "environment": "prod"}
        created = {"name": "dc1", "variables": variables}
        client.post = AsyncMock(return_value=_resp(created))
        result = await svc.create("dc1", variables)
        client.post.assert_called_once_with(
            "/groups", json={"name": "dc1", "variables": variables}
        )
        assert result == created

    @pytest.mark.asyncio
    async def test_create_without_variables(self, svc, client):
        client.post = AsyncMock(return_value=_resp({"name": "dc1", "variables": {}}))
        await svc.create("dc1")
        client.post.assert_called_once_with(
            "/groups", json={"name": "dc1", "variables": {}}
        )

    @pytest.mark.asyncio
    async def test_create_with_none_variables(self, svc, client):
        client.post = AsyncMock(return_value=_resp({"name": "dc1", "variables": {}}))
        await svc.create("dc1", None)
        client.post.assert_called_once_with(
            "/groups", json={"name": "dc1", "variables": {}}
        )

    @pytest.mark.asyncio
    async def test_update(self, svc, client):
        variables = {"location": "la"}
        client.put = AsyncMock(
            return_value=_resp({"name": "dc1", "variables": variables})
        )
        result = await svc.update("dc1", variables)
        client.put.assert_called_once_with("/groups/dc1", json={"variables": variables})
        assert result["variables"]["location"] == "la"

    @pytest.mark.asyncio
    async def test_delete(self, svc, client):
        client.delete = AsyncMock()
        await svc.delete("dc1")
        client.delete.assert_called_once_with("/groups/dc1")

    @pytest.mark.asyncio
    async def test_get_devices(self, svc, client):
        devices = [{"name": "router1"}, {"name": "router2"}]
        client.get = AsyncMock(return_value=_resp(devices))
        result = await svc.get_devices("dc1")
        client.get.assert_called_once_with("/groups/dc1/devices", params={})
        assert result == devices

    @pytest.mark.asyncio
    async def test_get_devices_with_params(self, svc, client):
        client.get = AsyncMock(return_value=_resp([]))
        await svc.get_devices("dc1", limit=10)
        client.get.assert_called_once_with("/groups/dc1/devices", params={"limit": 10})

    @pytest.mark.asyncio
    async def test_add_devices(self, svc, client):
        devices = ["router1", "router2"]
        result_data = {"name": "dc1", "devices": devices}
        client.post = AsyncMock(return_value=_resp(result_data))
        result = await svc.add_devices("dc1", devices)
        client.post.assert_called_once_with(
            "/groups/dc1/devices", json={"devices": devices}
        )
        assert result == result_data

    @pytest.mark.asyncio
    async def test_remove_device(self, svc, client):
        client.delete = AsyncMock()
        await svc.remove_device("dc1", "router1")
        client.delete.assert_called_once_with("/groups/dc1/devices/router1")

    @pytest.mark.asyncio
    async def test_get_children(self, svc, client):
        children = [{"name": "rack1"}, {"name": "rack2"}]
        client.get = AsyncMock(return_value=_resp(children))
        result = await svc.get_children("dc1")
        client.get.assert_called_once_with("/groups/dc1/children")
        assert result == children

    @pytest.mark.asyncio
    async def test_add_children(self, svc, client):
        children = ["rack1", "rack2"]
        result_data = {"name": "dc1", "children": children}
        client.post = AsyncMock(return_value=_resp(result_data))
        result = await svc.add_children("dc1", children)
        client.post.assert_called_once_with(
            "/groups/dc1/children", json={"children": children}
        )
        assert result == result_data

    @pytest.mark.asyncio
    async def test_remove_child(self, svc, client):
        client.delete = AsyncMock()
        await svc.remove_child("dc1", "rack1")
        client.delete.assert_called_once_with("/groups/dc1/children/rack1")

    @pytest.mark.asyncio
    async def test_get_variables(self, svc, client):
        variables = {"location": "ny", "environment": "prod"}
        client.get = AsyncMock(return_value=_resp(variables))
        result = await svc.get_variables("dc1")
        client.get.assert_called_once_with("/groups/dc1/variables")
        assert result == variables

    @pytest.mark.asyncio
    async def test_get_variable(self, svc, client):
        variable = {"location": "ny"}
        client.get = AsyncMock(return_value=_resp(variable))
        result = await svc.get_variable("dc1", "location")
        client.get.assert_called_once_with("/groups/dc1/variables/location")
        assert result == variable


# ===========================================================================
# Secrets
# ===========================================================================


class TestSecretsService:
    @pytest.fixture
    def client(self):
        return Mock()

    @pytest.fixture
    def svc(self, client):
        return SecretsService(client)

    def test_name(self, svc):
        assert svc.name == "secrets"

    def test_inherits_service_base(self):
        assert issubclass(SecretsService, ServiceBase)

    def test_init(self, client):
        s = SecretsService(client)
        assert s.client is client

    @pytest.mark.asyncio
    async def test_get_all(self, svc, client):
        items = [{"name": "db_password"}, {"name": "api_key"}]
        client.get = AsyncMock(return_value=_resp(_paginated(items)))
        result = await svc.get_all()
        assert result == items

    @pytest.mark.asyncio
    async def test_get_all_with_params(self, svc, client):
        client.get = AsyncMock(return_value=_resp(_paginated([])))
        await svc.get_all(type="password")
        args = client.get.call_args
        assert args[1]["params"]["type"] == "password"

    @pytest.mark.asyncio
    async def test_create(self, svc, client):
        params = {"name": "db_password", "value": "s3cr3t", "type": "password"}
        created = {"id": "s1", "name": "db_password"}
        client.post = AsyncMock(return_value=_resp(created))
        result = await svc.create(params)
        client.post.assert_called_once_with("/secrets", json=params)
        assert result == created

    @pytest.mark.asyncio
    async def test_update(self, svc, client):
        params = {"name": "db_password", "value": "new_secret"}
        updated = {"id": "s1", "name": "db_password", "updated": True}
        client.put = AsyncMock(return_value=_resp(updated))
        result = await svc.update(params)
        client.put.assert_called_once_with("/secrets", json=params)
        assert result == updated

    @pytest.mark.asyncio
    async def test_delete(self, svc, client):
        params = {"name": "db_password"}
        client.delete = AsyncMock()
        await svc.delete(params)
        client.delete.assert_called_once_with("/secrets", json=params)


# ===========================================================================
# RBAC
# ===========================================================================


class TestRbacService:
    @pytest.fixture
    def client(self):
        return Mock()

    @pytest.fixture
    def svc(self, client):
        return RbacService(client)

    def test_name(self, svc):
        assert svc.name == "rbac"

    def test_inherits_service_base(self):
        assert issubclass(RbacService, ServiceBase)

    def test_init(self, client):
        s = RbacService(client)
        assert s.client is client

    @pytest.mark.asyncio
    async def test_get_roles(self, svc, client):
        roles = [{"name": "admin"}, {"name": "viewer"}]
        client.get = AsyncMock(return_value=_resp(roles))
        result = await svc.get_roles()
        client.get.assert_called_once_with("/rbac/roles", params={})
        assert result == roles

    @pytest.mark.asyncio
    async def test_get_roles_with_params(self, svc, client):
        client.get = AsyncMock(return_value=_resp([]))
        await svc.get_roles(limit=5)
        client.get.assert_called_once_with("/rbac/roles", params={"limit": 5})

    @pytest.mark.asyncio
    async def test_get_role(self, svc, client):
        role = {"name": "admin", "permissions": ["read", "write"]}
        client.get = AsyncMock(return_value=_resp(role))
        result = await svc.get_role("admin")
        client.get.assert_called_once_with("/rbac/roles/admin")
        assert result == role

    @pytest.mark.asyncio
    async def test_get_groups(self, svc, client):
        groups = [{"name": "admins"}, {"name": "viewers"}]
        client.get = AsyncMock(return_value=_resp(groups))
        result = await svc.get_groups()
        client.get.assert_called_once_with("/rbac/groups", params={})
        assert result == groups

    @pytest.mark.asyncio
    async def test_get_groups_with_params(self, svc, client):
        client.get = AsyncMock(return_value=_resp([]))
        await svc.get_groups(limit=10)
        client.get.assert_called_once_with("/rbac/groups", params={"limit": 10})

    @pytest.mark.asyncio
    async def test_get_group(self, svc, client):
        group = {"name": "admins", "roles": ["admin"]}
        client.get = AsyncMock(return_value=_resp(group))
        result = await svc.get_group("admins")
        client.get.assert_called_once_with("/rbac/groups/admins")
        assert result == group

    @pytest.mark.asyncio
    async def test_create_group(self, svc, client):
        params = {"name": "editors", "description": "Content editors"}
        created = {"name": "editors", "id": "g1"}
        client.post = AsyncMock(return_value=_resp(created))
        result = await svc.create_group(params)
        client.post.assert_called_once_with("/rbac/groups", json=params)
        assert result == created

    @pytest.mark.asyncio
    async def test_update_group(self, svc, client):
        params = {"description": "Updated description"}
        client.put = AsyncMock(return_value=_resp({"name": "admins", "updated": True}))
        result = await svc.update_group("admins", params)
        client.put.assert_called_once_with("/rbac/groups/admins", json=params)
        assert result["updated"] is True

    @pytest.mark.asyncio
    async def test_delete_group(self, svc, client):
        client.delete = AsyncMock()
        await svc.delete_group("old_group")
        client.delete.assert_called_once_with("/rbac/groups/old_group")

    @pytest.mark.asyncio
    async def test_get_group_roles(self, svc, client):
        roles = [{"name": "admin"}, {"name": "editor"}]
        client.get = AsyncMock(return_value=_resp(roles))
        result = await svc.get_group_roles("admins")
        client.get.assert_called_once_with("/rbac/groups/admins/roles")
        assert result == roles

    @pytest.mark.asyncio
    async def test_add_group_roles(self, svc, client):
        roles = ["admin", "editor"]
        result_data = {"name": "admins", "roles": roles}
        client.post = AsyncMock(return_value=_resp(result_data))
        result = await svc.add_group_roles("admins", roles)
        client.post.assert_called_once_with(
            "/rbac/groups/admins/roles", json={"roles": roles}
        )
        assert result == result_data

    @pytest.mark.asyncio
    async def test_remove_group_role(self, svc, client):
        client.delete = AsyncMock()
        await svc.remove_group_role("admins", "editor")
        client.delete.assert_called_once_with("/rbac/groups/admins/roles/editor")

    @pytest.mark.asyncio
    async def test_get_group_users(self, svc, client):
        users = [{"username": "alice"}, {"username": "bob"}]
        client.get = AsyncMock(return_value=_resp(users))
        result = await svc.get_group_users("admins")
        client.get.assert_called_once_with("/rbac/groups/admins/users")
        assert result == users

    @pytest.mark.asyncio
    async def test_add_group_users(self, svc, client):
        users = ["alice", "bob"]
        result_data = {"name": "admins", "users": users}
        client.post = AsyncMock(return_value=_resp(result_data))
        result = await svc.add_group_users("admins", users)
        client.post.assert_called_once_with(
            "/rbac/groups/admins/users", json={"users": users}
        )
        assert result == result_data

    @pytest.mark.asyncio
    async def test_remove_group_user(self, svc, client):
        client.delete = AsyncMock()
        await svc.remove_group_user("admins", "alice")
        client.delete.assert_called_once_with("/rbac/groups/admins/users/alice")

    @pytest.mark.asyncio
    async def test_get_user_roles(self, svc, client):
        roles = [{"name": "admin"}]
        client.get = AsyncMock(return_value=_resp(roles))
        result = await svc.get_user_roles("alice")
        client.get.assert_called_once_with("/rbac/users/alice/roles")
        assert result == roles

    @pytest.mark.asyncio
    async def test_get_user_groups(self, svc, client):
        groups = [{"name": "admins"}, {"name": "ops"}]
        client.get = AsyncMock(return_value=_resp(groups))
        result = await svc.get_user_groups("alice")
        client.get.assert_called_once_with("/rbac/users/alice/groups")
        assert result == groups


# ===========================================================================
# Git
# ===========================================================================


class TestGitService:
    @pytest.fixture
    def client(self):
        return Mock()

    @pytest.fixture
    def svc(self, client):
        return GitService(client)

    def test_name(self, svc):
        assert svc.name == "git"

    def test_inherits_service_base(self):
        assert issubclass(GitService, ServiceBase)

    def test_init(self, client):
        s = GitService(client)
        assert s.client is client

    # --- Keys ---

    @pytest.mark.asyncio
    async def test_get_keys(self, svc, client):
        keys = [{"id": "k1", "name": "deploy_key"}]
        client.get = AsyncMock(return_value=_resp(keys))
        result = await svc.get_keys()
        client.get.assert_called_once_with("/git/keys", params={})
        assert result == keys

    @pytest.mark.asyncio
    async def test_get_keys_with_params(self, svc, client):
        client.get = AsyncMock(return_value=_resp([]))
        await svc.get_keys(limit=5)
        client.get.assert_called_once_with("/git/keys", params={"limit": 5})

    @pytest.mark.asyncio
    async def test_create_key(self, svc, client):
        params = {"name": "deploy_key", "private_key": "-----BEGIN OPENSSH..."}
        created = {"id": "k1", "name": "deploy_key", "public_key": "ssh-rsa AAAA"}
        client.post = AsyncMock(return_value=_resp(created))
        result = await svc.create_key(params)
        client.post.assert_called_once_with("/git/keys", json=params)
        assert result == created

    @pytest.mark.asyncio
    async def test_upload_key(self, svc, client):
        params = {"name": "uploaded_key", "private_key": "-----BEGIN OPENSSH..."}
        result_data = {"id": "k2", "name": "uploaded_key"}
        client.post = AsyncMock(return_value=_resp(result_data))
        result = await svc.upload_key(params)
        client.post.assert_called_once_with("/git/keys/upload", json=params)
        assert result == result_data

    @pytest.mark.asyncio
    async def test_get_key(self, svc, client):
        key = {"id": "k1", "name": "deploy_key"}
        client.get = AsyncMock(return_value=_resp(key))
        result = await svc.get_key("k1")
        client.get.assert_called_once_with("/git/keys/k1")
        assert result == key

    @pytest.mark.asyncio
    async def test_delete_key(self, svc, client):
        client.delete = AsyncMock()
        await svc.delete_key("k1")
        client.delete.assert_called_once_with("/git/keys/k1")

    @pytest.mark.asyncio
    async def test_update_key(self, svc, client):
        params = {"name": "renamed_key"}
        updated = {"id": "k1", "name": "renamed_key"}
        client.put = AsyncMock(return_value=_resp(updated))
        result = await svc.update_key("k1", params)
        client.put.assert_called_once_with("/git/keys/k1", json=params)
        assert result == updated

    # --- Integrations ---

    @pytest.mark.asyncio
    async def test_get_integrations(self, svc, client):
        integrations = [{"id": "i1", "type": "github"}]
        client.get = AsyncMock(return_value=_resp(integrations))
        result = await svc.get_integrations()
        client.get.assert_called_once_with("/git/integrations", params={})
        assert result == integrations

    @pytest.mark.asyncio
    async def test_get_integrations_with_params(self, svc, client):
        client.get = AsyncMock(return_value=_resp([]))
        await svc.get_integrations(type="github")
        client.get.assert_called_once_with(
            "/git/integrations", params={"type": "github"}
        )

    @pytest.mark.asyncio
    async def test_create_integration(self, svc, client):
        params = {
            "type": "github",
            "token": "ghp_abc",
            "base_url": "https://api.github.com",
        }
        created = {"id": "i1", "type": "github"}
        client.post = AsyncMock(return_value=_resp(created))
        result = await svc.create_integration(params)
        client.post.assert_called_once_with("/git/integrations", json=params)
        assert result == created

    @pytest.mark.asyncio
    async def test_get_integration(self, svc, client):
        integration = {"id": "i1", "type": "github"}
        client.get = AsyncMock(return_value=_resp(integration))
        result = await svc.get_integration("i1")
        client.get.assert_called_once_with("/git/integrations/i1")
        assert result == integration

    @pytest.mark.asyncio
    async def test_delete_integration(self, svc, client):
        client.delete = AsyncMock()
        await svc.delete_integration("i1")
        client.delete.assert_called_once_with("/git/integrations/i1")

    @pytest.mark.asyncio
    async def test_update_integration(self, svc, client):
        params = {"token": "ghp_new"}
        updated = {"id": "i1", "type": "github", "token": "ghp_new"}
        client.put = AsyncMock(return_value=_resp(updated))
        result = await svc.update_integration("i1", params)
        client.put.assert_called_once_with("/git/integrations/i1", json=params)
        assert result == updated

    # --- Repositories ---

    @pytest.mark.asyncio
    async def test_get_repositories(self, svc, client):
        repos = [{"id": "r1", "url": "https://github.com/org/repo"}]
        client.get = AsyncMock(return_value=_resp(repos))
        result = await svc.get_repositories()
        client.get.assert_called_once_with("/git/repositories", params={})
        assert result == repos

    @pytest.mark.asyncio
    async def test_get_repositories_with_params(self, svc, client):
        client.get = AsyncMock(return_value=_resp([]))
        await svc.get_repositories(integration_id="i1")
        client.get.assert_called_once_with(
            "/git/repositories", params={"integration_id": "i1"}
        )

    @pytest.mark.asyncio
    async def test_create_repository(self, svc, client):
        params = {
            "name": "network-configs",
            "integration_id": "i1",
            "branch": "main",
        }
        created = {"id": "r1", "url": "https://github.com/org/network-configs"}
        client.post = AsyncMock(return_value=_resp(created))
        result = await svc.create_repository(params)
        client.post.assert_called_once_with("/git/repositories", json=params)
        assert result == created

    @pytest.mark.asyncio
    async def test_get_repository(self, svc, client):
        repo = {"id": "r1", "name": "network-configs"}
        client.get = AsyncMock(return_value=_resp(repo))
        result = await svc.get_repository("r1")
        client.get.assert_called_once_with("/git/repositories/r1")
        assert result == repo

    @pytest.mark.asyncio
    async def test_delete_repository(self, svc, client):
        client.delete = AsyncMock()
        await svc.delete_repository("r1")
        client.delete.assert_called_once_with("/git/repositories/r1")

    @pytest.mark.asyncio
    async def test_update_repository(self, svc, client):
        params = {"branch": "develop"}
        updated = {"id": "r1", "branch": "develop"}
        client.put = AsyncMock(return_value=_resp(updated))
        result = await svc.update_repository("r1", params)
        client.put.assert_called_once_with("/git/repositories/r1", json=params)
        assert result == updated

    @pytest.mark.asyncio
    async def test_get_repository_status(self, svc, client):
        status = {"status": "clean", "ahead": 0, "behind": 0}
        client.get = AsyncMock(return_value=_resp(status))
        result = await svc.get_repository_status("r1")
        client.get.assert_called_once_with("/git/repositories/r1/status")
        assert result == status

    @pytest.mark.asyncio
    async def test_reset_repository(self, svc, client):
        result_data = {"reset": True, "ref": "main"}
        client.post = AsyncMock(return_value=_resp(result_data))
        result = await svc.reset_repository("r1")
        client.post.assert_called_once_with("/git/repositories/r1/reset")
        assert result == result_data

    @pytest.mark.asyncio
    async def test_pull_repository(self, svc, client):
        result_data = {"pulled": True, "commits": 3}
        client.post = AsyncMock(return_value=_resp(result_data))
        result = await svc.pull_repository("r1")
        client.post.assert_called_once_with("/git/repositories/r1/pull")
        assert result == result_data


# ===========================================================================
# Inventory
# ===========================================================================


class TestInventoryService:
    @pytest.fixture
    def client(self):
        return Mock()

    @pytest.fixture
    def svc(self, client):
        return InventoryService(client)

    def test_name(self, svc):
        assert svc.name == "inventory"

    def test_inherits_service_base(self):
        assert issubclass(InventoryService, ServiceBase)

    def test_init(self, client):
        s = InventoryService(client)
        assert s.client is client

    @pytest.mark.asyncio
    async def test_refresh(self, svc, client):
        client.post = AsyncMock(return_value=_resp({"refreshed": True, "count": 5}))
        result = await svc.refresh()
        client.post.assert_called_once_with("/inventory/refresh")
        assert result["refreshed"] is True

    @pytest.mark.asyncio
    async def test_get_devices(self, svc, client):
        devices = [{"name": "router1"}, {"name": "switch1"}]
        client.get = AsyncMock(return_value=_resp(devices))
        result = await svc.get_devices("netbox", "primary")
        client.get.assert_called_once_with(
            "/inventory/netbox/primary/devices", params={}
        )
        assert result == devices

    @pytest.mark.asyncio
    async def test_get_devices_with_params(self, svc, client):
        client.get = AsyncMock(return_value=_resp([]))
        await svc.get_devices("netbox", "primary", site="dc1")
        client.get.assert_called_once_with(
            "/inventory/netbox/primary/devices", params={"site": "dc1"}
        )

    @pytest.mark.asyncio
    async def test_get_device(self, svc, client):
        device = {"name": "router1", "ip": "10.0.0.1"}
        client.get = AsyncMock(return_value=_resp(device))
        result = await svc.get_device("netbox", "primary", "router1")
        client.get.assert_called_once_with("/inventory/netbox/primary/devices/router1")
        assert result == device

    @pytest.mark.asyncio
    async def test_create_device(self, svc, client):
        params = {"name": "router2", "ip": "10.0.0.2", "site": "dc1"}
        created = {"id": "d2", "name": "router2"}
        client.post = AsyncMock(return_value=_resp(created))
        result = await svc.create_device("netbox", "primary", params)
        client.post.assert_called_once_with(
            "/inventory/netbox/primary/devices", json=params
        )
        assert result == created

    @pytest.mark.asyncio
    async def test_update_device(self, svc, client):
        params = {"ip": "10.0.0.99"}
        updated = {"name": "router1", "ip": "10.0.0.99"}
        client.put = AsyncMock(return_value=_resp(updated))
        result = await svc.update_device("netbox", "primary", "router1", params)
        client.put.assert_called_once_with(
            "/inventory/netbox/primary/devices/router1", json=params
        )
        assert result == updated

    @pytest.mark.asyncio
    async def test_patch_device(self, svc, client):
        params = {"description": "Core router"}
        patched = {"name": "router1", "description": "Core router"}
        client.patch = AsyncMock(return_value=_resp(patched))
        result = await svc.patch_device("netbox", "primary", "router1", params)
        client.patch.assert_called_once_with(
            "/inventory/netbox/primary/devices/router1", json=params
        )
        assert result == patched

    @pytest.mark.asyncio
    async def test_delete_device(self, svc, client):
        client.delete = AsyncMock()
        await svc.delete_device("netbox", "primary", "router1")
        client.delete.assert_called_once_with(
            "/inventory/netbox/primary/devices/router1"
        )

    @pytest.mark.asyncio
    async def test_get_groups(self, svc, client):
        groups = [{"name": "routers"}, {"name": "switches"}]
        client.get = AsyncMock(return_value=_resp(groups))
        result = await svc.get_groups("netbox", "primary")
        client.get.assert_called_once_with(
            "/inventory/netbox/primary/groups", params={}
        )
        assert result == groups

    @pytest.mark.asyncio
    async def test_get_groups_with_params(self, svc, client):
        client.get = AsyncMock(return_value=_resp([]))
        await svc.get_groups("netbox", "primary", site="dc1")
        client.get.assert_called_once_with(
            "/inventory/netbox/primary/groups", params={"site": "dc1"}
        )

    @pytest.mark.asyncio
    async def test_get_group(self, svc, client):
        group = {"name": "routers", "devices": ["router1"]}
        client.get = AsyncMock(return_value=_resp(group))
        result = await svc.get_group("netbox", "primary", "routers")
        client.get.assert_called_once_with("/inventory/netbox/primary/groups/routers")
        assert result == group

    @pytest.mark.asyncio
    async def test_get_group_devices(self, svc, client):
        devices = [{"name": "router1"}, {"name": "router2"}]
        client.get = AsyncMock(return_value=_resp(devices))
        result = await svc.get_group_devices("netbox", "primary", "routers")
        client.get.assert_called_once_with(
            "/inventory/netbox/primary/groups/routers/devices"
        )
        assert result == devices

    @pytest.mark.asyncio
    async def test_get_group_children(self, svc, client):
        children = [{"name": "core_routers"}]
        client.get = AsyncMock(return_value=_resp(children))
        result = await svc.get_group_children("netbox", "primary", "routers")
        client.get.assert_called_once_with(
            "/inventory/netbox/primary/groups/routers/children"
        )
        assert result == children


# ===========================================================================
# System
# ===========================================================================


class TestSystemService:
    @pytest.fixture
    def client(self):
        return Mock()

    @pytest.fixture
    def svc(self, client):
        return SystemService(client)

    def test_name(self, svc):
        assert svc.name == "system"

    def test_inherits_service_base(self):
        assert issubclass(SystemService, ServiceBase)

    def test_init(self, client):
        s = SystemService(client)
        assert s.client is client

    @pytest.mark.asyncio
    async def test_get_status(self, svc, client):
        status = {"status": "running", "version": "4.5.0", "uptime": 86400}
        client.get = AsyncMock(return_value=_resp(status))
        result = await svc.get_status()
        client.get.assert_called_once_with("/system/status")
        assert result == status

    @pytest.mark.asyncio
    async def test_poll(self, svc, client):
        poll_data = {"alive": True, "timestamp": "2025-01-01T00:00:00Z"}
        client.get = AsyncMock(return_value=_resp(poll_data))
        result = await svc.poll()
        client.get.assert_called_once_with("/system/poll")
        assert result == poll_data

    @pytest.mark.asyncio
    async def test_get_audit(self, svc, client):
        audit = [
            {"event": "login", "user": "admin", "timestamp": "2025-01-01"},
            {"event": "create_device", "user": "alice", "timestamp": "2025-01-02"},
        ]
        client.get = AsyncMock(return_value=_resp(audit))
        result = await svc.get_audit()
        client.get.assert_called_once_with("/system/audit", params={})
        assert len(result) == 2

    @pytest.mark.asyncio
    async def test_get_audit_with_params(self, svc, client):
        client.get = AsyncMock(return_value=_resp([]))
        await svc.get_audit(user="admin", limit=10)
        client.get.assert_called_once_with(
            "/system/audit", params={"user": "admin", "limit": 10}
        )

    @pytest.mark.asyncio
    async def test_get_exec_history(self, svc, client):
        exec_history = {"audit_id": "a1", "steps": [{"step": 1, "status": "ok"}]}
        client.get = AsyncMock(return_value=_resp(exec_history))
        result = await svc.get_exec_history("a1")
        client.get.assert_called_once_with("/system/audit/a1")
        assert result == exec_history

    @pytest.mark.asyncio
    async def test_get_openapi_spec(self, svc, client):
        spec = {"openapi": "3.0.0", "info": {"title": "IAG API", "version": "4.5"}}
        client.get = AsyncMock(return_value=_resp(spec))
        result = await svc.get_openapi_spec()
        client.get.assert_called_once_with("/system/openapi")
        assert result["openapi"] == "3.0.0"


# ===========================================================================
# LDAP
# ===========================================================================


class TestLdapService:
    @pytest.fixture
    def client(self):
        return Mock()

    @pytest.fixture
    def svc(self, client):
        return LdapService(client)

    def test_name(self, svc):
        assert svc.name == "ldap"

    def test_inherits_service_base(self):
        assert issubclass(LdapService, ServiceBase)

    def test_init(self, client):
        s = LdapService(client)
        assert s.client is client

    @pytest.mark.asyncio
    async def test_test_bind_success(self, svc, client):
        params = {
            "host": "ldap.example.com",
            "port": 389,
            "bind_dn": "cn=admin,dc=example,dc=com",
            "bind_password": "secret",
        }
        result_data = {"success": True, "message": "Bind successful"}
        client.post = AsyncMock(return_value=_resp(result_data))
        result = await svc.test_bind(params)
        client.post.assert_called_once_with("/ldap/test_bind", json=params)
        assert result == result_data

    @pytest.mark.asyncio
    async def test_test_bind_failure(self, svc, client):
        params = {"host": "ldap.example.com", "bind_dn": "bad_dn"}
        failure = {"success": False, "message": "Invalid credentials"}
        client.post = AsyncMock(return_value=_resp(failure))
        result = await svc.test_bind(params)
        client.post.assert_called_once_with("/ldap/test_bind", json=params)
        assert result["success"] is False

    @pytest.mark.asyncio
    async def test_test_bind_returns_json(self, svc, client):
        client.post = AsyncMock(return_value=_resp({"success": True}))
        result = await svc.test_bind({"host": "ldap.corp"})
        assert isinstance(result, dict)
        assert "success" in result


# ===========================================================================
# Pronghorn
# ===========================================================================


class TestPronghornService:
    @pytest.fixture
    def client(self):
        return Mock()

    @pytest.fixture
    def svc(self, client):
        return PronghornService(client)

    def test_name(self, svc):
        assert svc.name == "pronghorn"

    def test_inherits_service_base(self):
        assert issubclass(PronghornService, ServiceBase)

    def test_init(self, client):
        s = PronghornService(client)
        assert s.client is client

    @pytest.mark.asyncio
    async def test_get(self, svc, client):
        data = {
            "version": "1.2.3",
            "adapters": ["cisco_ios", "arista_eos"],
            "status": "healthy",
        }
        client.get = AsyncMock(return_value=_resp(data))
        result = await svc.get()
        client.get.assert_called_once_with("/pronghorn")
        assert result == data

    @pytest.mark.asyncio
    async def test_get_returns_json(self, svc, client):
        client.get = AsyncMock(return_value=_resp({"version": "2.0.0"}))
        result = await svc.get()
        assert result == {"version": "2.0.0"}

    @pytest.mark.asyncio
    async def test_get_empty_response(self, svc, client):
        client.get = AsyncMock(return_value=_resp({}))
        result = await svc.get()
        assert result == {}


# ===========================================================================
# Ansible Venv
# ===========================================================================


class TestAnsibleVenvService:
    @pytest.fixture
    def client(self):
        return Mock()

    @pytest.fixture
    def svc(self, client):
        return AnsibleVenvService(client)

    def test_name(self, svc):
        assert svc.name == "ansible_venv"

    def test_inherits_service_base(self):
        assert issubclass(AnsibleVenvService, ServiceBase)

    def test_init(self, client):
        s = AnsibleVenvService(client)
        assert s.client is client

    @pytest.mark.asyncio
    async def test_get_list(self, svc, client):
        venvs = [
            {"name": "default", "ansible_version": "2.14.0"},
            {"name": "custom", "ansible_version": "2.13.0"},
        ]
        client.get = AsyncMock(return_value=_resp(venvs))
        result = await svc.get_list()
        client.get.assert_called_once_with("/ansible_venv/list")
        assert result == venvs

    @pytest.mark.asyncio
    async def test_get_list_empty(self, svc, client):
        client.get = AsyncMock(return_value=_resp([]))
        result = await svc.get_list()
        assert result == []

    @pytest.mark.asyncio
    async def test_refresh(self, svc, client):
        result_data = {"refreshed": True, "count": 2}
        client.get = AsyncMock(return_value=_resp(result_data))
        result = await svc.refresh()
        client.get.assert_called_once_with("/ansible_venv/refresh")
        assert result == result_data


# ===========================================================================
# Python Venv
# ===========================================================================


class TestPythonVenvService:
    @pytest.fixture
    def client(self):
        return Mock()

    @pytest.fixture
    def svc(self, client):
        return PythonVenvService(client)

    def test_name(self, svc):
        assert svc.name == "python_venv"

    def test_inherits_service_base(self):
        assert issubclass(PythonVenvService, ServiceBase)

    def test_init(self, client):
        s = PythonVenvService(client)
        assert s.client is client

    @pytest.mark.asyncio
    async def test_get_list(self, svc, client):
        venvs = [
            {"name": "default", "python_version": "3.11.0"},
            {"name": "legacy", "python_version": "3.10.0"},
        ]
        client.get = AsyncMock(return_value=_resp(venvs))
        result = await svc.get_list()
        client.get.assert_called_once_with("/pythonvenv/list")
        assert result == venvs

    @pytest.mark.asyncio
    async def test_get_list_empty(self, svc, client):
        client.get = AsyncMock(return_value=_resp([]))
        result = await svc.get_list()
        assert result == []

    @pytest.mark.asyncio
    async def test_refresh(self, svc, client):
        result_data = {"refreshed": True, "count": 1}
        client.get = AsyncMock(return_value=_resp(result_data))
        result = await svc.refresh()
        client.get.assert_called_once_with("/pythonvenv/refresh")
        assert result == result_data


# ===========================================================================
# User Schema
# ===========================================================================


class TestUserSchemaService:
    @pytest.fixture
    def client(self):
        return Mock()

    @pytest.fixture
    def svc(self, client):
        return UserSchemaService(client)

    def test_name(self, svc):
        assert svc.name == "user_schema"

    def test_inherits_service_base(self):
        assert issubclass(UserSchemaService, ServiceBase)

    def test_init(self, client):
        s = UserSchemaService(client)
        assert s.client is client

    @pytest.mark.asyncio
    async def test_upsert(self, svc, client):
        schema = {
            "type": "object",
            "properties": {"hostname": {"type": "string"}},
            "required": ["hostname"],
        }
        result_data = {
            "schema_type": "device",
            "schema_name": "cisco",
            "schema": schema,
        }
        client.put = AsyncMock(return_value=_resp(result_data))
        result = await svc.upsert("device", "cisco", schema)
        client.put.assert_called_once_with("/user-schema/device/cisco", json=schema)
        assert result == result_data

    @pytest.mark.asyncio
    async def test_upsert_empty_schema(self, svc, client):
        client.put = AsyncMock(return_value=_resp({"schema": {}}))
        result = await svc.upsert("playbook", "my_playbook", {})
        client.put.assert_called_once_with("/user-schema/playbook/my_playbook", json={})
        assert result == {"schema": {}}

    @pytest.mark.asyncio
    async def test_upsert_nested_schema(self, svc, client):
        schema = {
            "type": "object",
            "properties": {
                "config": {
                    "type": "object",
                    "properties": {"vlan": {"type": "integer"}},
                }
            },
        }
        client.put = AsyncMock(return_value=_resp({"created": True}))
        await svc.upsert("device", "complex_device", schema)
        client.put.assert_called_once_with(
            "/user-schema/device/complex_device", json=schema
        )

    @pytest.mark.asyncio
    async def test_delete(self, svc, client):
        client.delete = AsyncMock()
        await svc.delete("device", "cisco")
        client.delete.assert_called_once_with("/user-schema/device/cisco")

    @pytest.mark.asyncio
    async def test_delete_different_type(self, svc, client):
        client.delete = AsyncMock()
        await svc.delete("playbook", "network_config")
        client.delete.assert_called_once_with("/user-schema/playbook/network_config")

    @pytest.mark.asyncio
    async def test_delete_returns_none(self, svc, client):
        client.delete = AsyncMock()
        result = await svc.delete("device", "cisco")
        assert result is None
