# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Tests for execution-oriented resources: modules, roles, scripts, nornir, collections, terraforms.

These resources share a common pattern: run/execute, ensure_schema, remove_schema, refresh.
Collections and terraforms add extra operations on top of that baseline.
"""

from unittest.mock import AsyncMock, Mock

import pytest

from asyncgateway.resources.collections import Resource as CollectionsResource
from asyncgateway.resources.modules import Resource as ModulesResource
from asyncgateway.resources.nornir import Resource as NornirResource
from asyncgateway.resources.roles import Resource as RolesResource
from asyncgateway.resources.scripts import Resource as ScriptsResource
from asyncgateway.resources.terraforms import Resource as TerraformsResource

# ---------------------------------------------------------------------------
# Modules
# ---------------------------------------------------------------------------


class TestModulesResource:
    @pytest.fixture
    def mock_modules_service(self):
        svc = Mock()
        svc.execute = AsyncMock(return_value={"status": "ok", "output": "done"})
        svc.update_schema = AsyncMock(return_value={"schema": "updated"})
        svc.delete_schema = AsyncMock(return_value={"schema": "deleted"})
        svc.refresh = AsyncMock(return_value={"refreshed": True})
        return svc

    @pytest.fixture
    def modules_resource(self, mock_modules_service):
        services = Mock()
        services.modules = mock_modules_service
        return ModulesResource(services)

    def test_resource_name(self, modules_resource):
        assert modules_resource.name == "modules"

    @pytest.mark.asyncio
    async def test_run_with_params(self, modules_resource, mock_modules_service):
        params = {"host": "router1", "command": "show version"}
        result = await modules_resource.run("my_module", params)

        mock_modules_service.execute.assert_called_once_with("my_module", params)
        assert result == {"status": "ok", "output": "done"}

    @pytest.mark.asyncio
    async def test_run_without_params_defaults_to_empty_dict(
        self, modules_resource, mock_modules_service
    ):
        await modules_resource.run("my_module")

        mock_modules_service.execute.assert_called_once_with("my_module", {})

    @pytest.mark.asyncio
    async def test_run_with_none_params_defaults_to_empty_dict(
        self, modules_resource, mock_modules_service
    ):
        await modules_resource.run("my_module", None)

        mock_modules_service.execute.assert_called_once_with("my_module", {})

    @pytest.mark.asyncio
    async def test_ensure_schema(self, modules_resource, mock_modules_service):
        schema = {"type": "object", "properties": {"host": {"type": "string"}}}
        result = await modules_resource.ensure_schema("my_module", schema)

        mock_modules_service.update_schema.assert_called_once_with("my_module", schema)
        assert result == {"schema": "updated"}

    @pytest.mark.asyncio
    async def test_remove_schema(self, modules_resource, mock_modules_service):
        result = await modules_resource.remove_schema("my_module")

        mock_modules_service.delete_schema.assert_called_once_with("my_module")
        assert result == {"schema": "deleted"}

    @pytest.mark.asyncio
    async def test_refresh(self, modules_resource, mock_modules_service):
        result = await modules_resource.refresh()

        mock_modules_service.refresh.assert_called_once_with()
        assert result == {"refreshed": True}


# ---------------------------------------------------------------------------
# Roles
# ---------------------------------------------------------------------------


class TestRolesResource:
    @pytest.fixture
    def mock_roles_service(self):
        svc = Mock()
        svc.execute = AsyncMock(return_value={"status": "ok"})
        svc.update_schema = AsyncMock(return_value={"schema": "updated"})
        svc.delete_schema = AsyncMock(return_value={"schema": "deleted"})
        svc.refresh = AsyncMock(return_value={"refreshed": True})
        return svc

    @pytest.fixture
    def roles_resource(self, mock_roles_service):
        services = Mock()
        services.roles = mock_roles_service
        return RolesResource(services)

    def test_resource_name(self, roles_resource):
        assert roles_resource.name == "roles"

    @pytest.mark.asyncio
    async def test_run_with_params(self, roles_resource, mock_roles_service):
        params = {"hosts": ["router1", "router2"]}
        result = await roles_resource.run("deploy_config", params)

        mock_roles_service.execute.assert_called_once_with("deploy_config", params)
        assert result == {"status": "ok"}

    @pytest.mark.asyncio
    async def test_run_without_params_defaults_to_empty_dict(
        self, roles_resource, mock_roles_service
    ):
        await roles_resource.run("deploy_config")

        mock_roles_service.execute.assert_called_once_with("deploy_config", {})

    @pytest.mark.asyncio
    async def test_run_with_none_params(self, roles_resource, mock_roles_service):
        await roles_resource.run("deploy_config", None)

        mock_roles_service.execute.assert_called_once_with("deploy_config", {})

    @pytest.mark.asyncio
    async def test_ensure_schema(self, roles_resource, mock_roles_service):
        schema = {"type": "object"}
        result = await roles_resource.ensure_schema("deploy_config", schema)

        mock_roles_service.update_schema.assert_called_once_with(
            "deploy_config", schema
        )
        assert result == {"schema": "updated"}

    @pytest.mark.asyncio
    async def test_remove_schema(self, roles_resource, mock_roles_service):
        result = await roles_resource.remove_schema("deploy_config")

        mock_roles_service.delete_schema.assert_called_once_with("deploy_config")
        assert result == {"schema": "deleted"}

    @pytest.mark.asyncio
    async def test_refresh(self, roles_resource, mock_roles_service):
        result = await roles_resource.refresh()

        mock_roles_service.refresh.assert_called_once_with()
        assert result == {"refreshed": True}


# ---------------------------------------------------------------------------
# Scripts
# ---------------------------------------------------------------------------


class TestScriptsResource:
    @pytest.fixture
    def mock_scripts_service(self):
        svc = Mock()
        svc.execute = AsyncMock(return_value={"exit_code": 0, "stdout": "hello"})
        svc.update_schema = AsyncMock(return_value={"schema": "updated"})
        svc.delete_schema = AsyncMock(return_value={"schema": "deleted"})
        svc.refresh = AsyncMock(return_value={"refreshed": True})
        return svc

    @pytest.fixture
    def scripts_resource(self, mock_scripts_service):
        services = Mock()
        services.scripts = mock_scripts_service
        return ScriptsResource(services)

    def test_resource_name(self, scripts_resource):
        assert scripts_resource.name == "scripts"

    @pytest.mark.asyncio
    async def test_run_with_params(self, scripts_resource, mock_scripts_service):
        params = {"arg1": "value1"}
        result = await scripts_resource.run("my_script", params)

        mock_scripts_service.execute.assert_called_once_with("my_script", params)
        assert result == {"exit_code": 0, "stdout": "hello"}

    @pytest.mark.asyncio
    async def test_run_without_params(self, scripts_resource, mock_scripts_service):
        await scripts_resource.run("my_script")

        mock_scripts_service.execute.assert_called_once_with("my_script", {})

    @pytest.mark.asyncio
    async def test_run_with_none_params(self, scripts_resource, mock_scripts_service):
        await scripts_resource.run("my_script", None)

        mock_scripts_service.execute.assert_called_once_with("my_script", {})

    @pytest.mark.asyncio
    async def test_ensure_schema(self, scripts_resource, mock_scripts_service):
        schema = {"type": "object", "properties": {"arg1": {"type": "string"}}}
        result = await scripts_resource.ensure_schema("my_script", schema)

        mock_scripts_service.update_schema.assert_called_once_with("my_script", schema)
        assert result == {"schema": "updated"}

    @pytest.mark.asyncio
    async def test_remove_schema(self, scripts_resource, mock_scripts_service):
        result = await scripts_resource.remove_schema("my_script")

        mock_scripts_service.delete_schema.assert_called_once_with("my_script")
        assert result == {"schema": "deleted"}

    @pytest.mark.asyncio
    async def test_refresh(self, scripts_resource, mock_scripts_service):
        result = await scripts_resource.refresh()

        mock_scripts_service.refresh.assert_called_once_with()
        assert result == {"refreshed": True}


# ---------------------------------------------------------------------------
# Nornir
# ---------------------------------------------------------------------------


class TestNornirResource:
    @pytest.fixture
    def mock_nornir_service(self):
        svc = Mock()
        svc.execute = AsyncMock(return_value={"results": {"router1": "ok"}})
        svc.update_schema = AsyncMock(return_value={"schema": "updated"})
        svc.delete_schema = AsyncMock(return_value={"schema": "deleted"})
        svc.refresh = AsyncMock(return_value={"refreshed": True})
        return svc

    @pytest.fixture
    def nornir_resource(self, mock_nornir_service):
        services = Mock()
        services.nornir = mock_nornir_service
        return NornirResource(services)

    def test_resource_name(self, nornir_resource):
        assert nornir_resource.name == "nornir"

    @pytest.mark.asyncio
    async def test_run_with_params(self, nornir_resource, mock_nornir_service):
        params = {"hosts": ["router1"], "command": "show ip int brief"}
        result = await nornir_resource.run("get_interfaces", params)

        mock_nornir_service.execute.assert_called_once_with("get_interfaces", params)
        assert result == {"results": {"router1": "ok"}}

    @pytest.mark.asyncio
    async def test_run_without_params(self, nornir_resource, mock_nornir_service):
        await nornir_resource.run("get_interfaces")

        mock_nornir_service.execute.assert_called_once_with("get_interfaces", {})

    @pytest.mark.asyncio
    async def test_run_with_none_params(self, nornir_resource, mock_nornir_service):
        await nornir_resource.run("get_interfaces", None)

        mock_nornir_service.execute.assert_called_once_with("get_interfaces", {})

    @pytest.mark.asyncio
    async def test_ensure_schema(self, nornir_resource, mock_nornir_service):
        schema = {"type": "object"}
        result = await nornir_resource.ensure_schema("get_interfaces", schema)

        mock_nornir_service.update_schema.assert_called_once_with(
            "get_interfaces", schema
        )
        assert result == {"schema": "updated"}

    @pytest.mark.asyncio
    async def test_remove_schema(self, nornir_resource, mock_nornir_service):
        result = await nornir_resource.remove_schema("get_interfaces")

        mock_nornir_service.delete_schema.assert_called_once_with("get_interfaces")
        assert result == {"schema": "deleted"}

    @pytest.mark.asyncio
    async def test_refresh(self, nornir_resource, mock_nornir_service):
        result = await nornir_resource.refresh()

        mock_nornir_service.refresh.assert_called_once_with()
        assert result == {"refreshed": True}


# ---------------------------------------------------------------------------
# Collections
# ---------------------------------------------------------------------------


class TestCollectionsResource:
    @pytest.fixture
    def mock_collections_service(self):
        svc = Mock()
        svc.execute_module = AsyncMock(return_value={"module_result": "success"})
        svc.execute_role = AsyncMock(return_value={"role_result": "success"})
        svc.update_module_schema = AsyncMock(return_value={"schema": "module_updated"})
        svc.update_role_schema = AsyncMock(return_value={"schema": "role_updated"})
        svc.refresh = AsyncMock(return_value={"refreshed": True})
        return svc

    @pytest.fixture
    def collections_resource(self, mock_collections_service):
        services = Mock()
        services.collections = mock_collections_service
        return CollectionsResource(services)

    def test_resource_name(self, collections_resource):
        assert collections_resource.name == "collections"

    @pytest.mark.asyncio
    async def test_run_module_with_params(
        self, collections_resource, mock_collections_service
    ):
        params = {"host": "router1"}
        result = await collections_resource.run_module("cisco.ios", "facts", params)

        mock_collections_service.execute_module.assert_called_once_with(
            "cisco.ios", "facts", params
        )
        assert result == {"module_result": "success"}

    @pytest.mark.asyncio
    async def test_run_module_without_params(
        self, collections_resource, mock_collections_service
    ):
        await collections_resource.run_module("cisco.ios", "facts")

        mock_collections_service.execute_module.assert_called_once_with(
            "cisco.ios", "facts", {}
        )

    @pytest.mark.asyncio
    async def test_run_module_with_none_params(
        self, collections_resource, mock_collections_service
    ):
        await collections_resource.run_module("cisco.ios", "facts", None)

        mock_collections_service.execute_module.assert_called_once_with(
            "cisco.ios", "facts", {}
        )

    @pytest.mark.asyncio
    async def test_run_role_with_params(
        self, collections_resource, mock_collections_service
    ):
        params = {"hosts": ["router1"]}
        result = await collections_resource.run_role("cisco.ios", "deploy", params)

        mock_collections_service.execute_role.assert_called_once_with(
            "cisco.ios", "deploy", params
        )
        assert result == {"role_result": "success"}

    @pytest.mark.asyncio
    async def test_run_role_without_params(
        self, collections_resource, mock_collections_service
    ):
        await collections_resource.run_role("cisco.ios", "deploy")

        mock_collections_service.execute_role.assert_called_once_with(
            "cisco.ios", "deploy", {}
        )

    @pytest.mark.asyncio
    async def test_run_role_with_none_params(
        self, collections_resource, mock_collections_service
    ):
        await collections_resource.run_role("cisco.ios", "deploy", None)

        mock_collections_service.execute_role.assert_called_once_with(
            "cisco.ios", "deploy", {}
        )

    @pytest.mark.asyncio
    async def test_ensure_module_schema(
        self, collections_resource, mock_collections_service
    ):
        schema = {"type": "object"}
        result = await collections_resource.ensure_module_schema(
            "cisco.ios", "facts", schema
        )

        mock_collections_service.update_module_schema.assert_called_once_with(
            "cisco.ios", "facts", schema
        )
        assert result == {"schema": "module_updated"}

    @pytest.mark.asyncio
    async def test_ensure_role_schema(
        self, collections_resource, mock_collections_service
    ):
        schema = {"type": "object", "properties": {"hosts": {"type": "array"}}}
        result = await collections_resource.ensure_role_schema(
            "cisco.ios", "deploy", schema
        )

        mock_collections_service.update_role_schema.assert_called_once_with(
            "cisco.ios", "deploy", schema
        )
        assert result == {"schema": "role_updated"}

    @pytest.mark.asyncio
    async def test_refresh(self, collections_resource, mock_collections_service):
        result = await collections_resource.refresh()

        mock_collections_service.refresh.assert_called_once_with()
        assert result == {"refreshed": True}


# ---------------------------------------------------------------------------
# Terraforms
# ---------------------------------------------------------------------------


class TestTerraformsResource:
    @pytest.fixture
    def mock_terraforms_service(self):
        svc = Mock()
        svc.apply = AsyncMock(return_value={"apply_result": "applied"})
        svc.plan = AsyncMock(return_value={"plan_result": "planned"})
        svc.destroy = AsyncMock(return_value={"destroy_result": "destroyed"})
        svc.validate = AsyncMock(return_value={"valid": True})
        svc.init = AsyncMock(return_value={"initialized": True})
        svc.update_schema = AsyncMock(return_value={"schema": "updated"})
        svc.delete_schema = AsyncMock(return_value={"schema": "deleted"})
        svc.refresh = AsyncMock(return_value={"refreshed": True})
        return svc

    @pytest.fixture
    def terraforms_resource(self, mock_terraforms_service):
        services = Mock()
        services.terraforms = mock_terraforms_service
        return TerraformsResource(services)

    def test_resource_name(self, terraforms_resource):
        assert terraforms_resource.name == "terraforms"

    @pytest.mark.asyncio
    async def test_apply_with_params(
        self, terraforms_resource, mock_terraforms_service
    ):
        params = {"var": {"region": "us-east-1"}}
        result = await terraforms_resource.apply("vpc_config", params)

        mock_terraforms_service.apply.assert_called_once_with("vpc_config", params)
        assert result == {"apply_result": "applied"}

    @pytest.mark.asyncio
    async def test_apply_without_params(
        self, terraforms_resource, mock_terraforms_service
    ):
        await terraforms_resource.apply("vpc_config")

        mock_terraforms_service.apply.assert_called_once_with("vpc_config", {})

    @pytest.mark.asyncio
    async def test_apply_with_none_params(
        self, terraforms_resource, mock_terraforms_service
    ):
        await terraforms_resource.apply("vpc_config", None)

        mock_terraforms_service.apply.assert_called_once_with("vpc_config", {})

    @pytest.mark.asyncio
    async def test_plan(self, terraforms_resource, mock_terraforms_service):
        params = {"var": {"region": "us-west-2"}}
        result = await terraforms_resource.plan("vpc_config", params)

        mock_terraforms_service.plan.assert_called_once_with("vpc_config", params)
        assert result == {"plan_result": "planned"}

    @pytest.mark.asyncio
    async def test_plan_without_params(
        self, terraforms_resource, mock_terraforms_service
    ):
        await terraforms_resource.plan("vpc_config")

        mock_terraforms_service.plan.assert_called_once_with("vpc_config", {})

    @pytest.mark.asyncio
    async def test_destroy(self, terraforms_resource, mock_terraforms_service):
        result = await terraforms_resource.destroy("old_vpc")

        mock_terraforms_service.destroy.assert_called_once_with("old_vpc", {})
        assert result == {"destroy_result": "destroyed"}

    @pytest.mark.asyncio
    async def test_destroy_with_params(
        self, terraforms_resource, mock_terraforms_service
    ):
        params = {"target": "aws_vpc.main"}
        result = await terraforms_resource.destroy("old_vpc", params)

        mock_terraforms_service.destroy.assert_called_once_with("old_vpc", params)
        assert result == {"destroy_result": "destroyed"}

    @pytest.mark.asyncio
    async def test_validate(self, terraforms_resource, mock_terraforms_service):
        result = await terraforms_resource.validate("vpc_config")

        mock_terraforms_service.validate.assert_called_once_with("vpc_config", {})
        assert result == {"valid": True}

    @pytest.mark.asyncio
    async def test_validate_with_params(
        self, terraforms_resource, mock_terraforms_service
    ):
        params = {"check_vars": True}
        result = await terraforms_resource.validate("vpc_config", params)

        mock_terraforms_service.validate.assert_called_once_with("vpc_config", params)
        assert result == {"valid": True}

    @pytest.mark.asyncio
    async def test_init(self, terraforms_resource, mock_terraforms_service):
        result = await terraforms_resource.init("vpc_config")

        mock_terraforms_service.init.assert_called_once_with("vpc_config", {})
        assert result == {"initialized": True}

    @pytest.mark.asyncio
    async def test_init_with_params(self, terraforms_resource, mock_terraforms_service):
        params = {"backend": "s3"}
        result = await terraforms_resource.init("vpc_config", params)

        mock_terraforms_service.init.assert_called_once_with("vpc_config", params)
        assert result == {"initialized": True}

    @pytest.mark.asyncio
    async def test_ensure_schema(self, terraforms_resource, mock_terraforms_service):
        schema = {"type": "object", "properties": {"region": {"type": "string"}}}
        result = await terraforms_resource.ensure_schema("vpc_config", schema)

        mock_terraforms_service.update_schema.assert_called_once_with(
            "vpc_config", schema
        )
        assert result == {"schema": "updated"}

    @pytest.mark.asyncio
    async def test_remove_schema(self, terraforms_resource, mock_terraforms_service):
        result = await terraforms_resource.remove_schema("vpc_config")

        mock_terraforms_service.delete_schema.assert_called_once_with("vpc_config")
        assert result == {"schema": "deleted"}

    @pytest.mark.asyncio
    async def test_refresh(self, terraforms_resource, mock_terraforms_service):
        result = await terraforms_resource.refresh()

        mock_terraforms_service.refresh.assert_called_once_with()
        assert result == {"refreshed": True}
