# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Tests for execution-oriented services: modules, roles, scripts, nornir, collections, terraforms.

These services share a common pattern:
  get, get_all (paginated), get_schema, update_schema, delete_schema,
  execute, get_history, refresh.
Collections adds module+role sub-resource variants.
Terraforms replaces execute with apply/plan/validate/destroy/init.
"""

from unittest.mock import AsyncMock, Mock

import pytest

from asyncgateway.services import ServiceBase
from asyncgateway.services.collections import Service as CollectionsService
from asyncgateway.services.modules import Service as ModulesService
from asyncgateway.services.nornir import Service as NornirService
from asyncgateway.services.roles import Service as RolesService
from asyncgateway.services.scripts import Service as ScriptsService
from asyncgateway.services.terraforms import Service as TerraformsService


def _make_response(data):
    """Helper: return a Mock response whose .json() returns data."""
    resp = Mock()
    resp.json.return_value = data
    return resp


def _make_paginated(items, total=None):
    """Helper: return paginated response body matching _get_all expectations."""
    if total is None:
        total = len(items)
    return {"data": items, "meta": {"total_count": total}}


# ===========================================================================
# Modules
# ===========================================================================


class TestModulesService:
    @pytest.fixture
    def client(self):
        return Mock()

    @pytest.fixture
    def svc(self, client):
        return ModulesService(client)

    def test_name(self, svc):
        assert svc.name == "modules"

    def test_inherits_service_base(self):
        assert issubclass(ModulesService, ServiceBase)

    def test_init(self, client):
        s = ModulesService(client)
        assert s.client is client

    @pytest.mark.asyncio
    async def test_get(self, svc, client):
        data = {"name": "ios_facts", "description": "Gather IOS facts"}
        client.get = AsyncMock(return_value=_make_response(data))
        result = await svc.get("ios_facts")
        client.get.assert_called_once_with("/modules/ios_facts")
        assert result == data

    @pytest.mark.asyncio
    async def test_get_all_single_page(self, svc, client):
        items = [{"name": "m1"}, {"name": "m2"}]
        client.get = AsyncMock(return_value=_make_response(_make_paginated(items)))
        result = await svc.get_all()
        assert result == items

    @pytest.mark.asyncio
    async def test_get_all_multiple_pages(self, svc, client):
        page1_items = [{"name": f"m{i}"} for i in range(100)]
        page2_items = [{"name": f"m{i}"} for i in range(100, 130)]
        client.get = AsyncMock(
            side_effect=[
                _make_response(_make_paginated(page1_items, total=130)),
                _make_response(_make_paginated(page2_items, total=130)),
            ]
        )
        result = await svc.get_all()
        assert len(result) == 130

    @pytest.mark.asyncio
    async def test_get_all_empty(self, svc, client):
        client.get = AsyncMock(return_value=_make_response(_make_paginated([])))
        result = await svc.get_all()
        assert result == []

    @pytest.mark.asyncio
    async def test_get_schema(self, svc, client):
        schema = {"type": "object", "properties": {"host": {"type": "string"}}}
        client.get = AsyncMock(return_value=_make_response(schema))
        result = await svc.get_schema("ios_facts")
        client.get.assert_called_once_with("/modules/ios_facts/schema")
        assert result == schema

    @pytest.mark.asyncio
    async def test_update_schema(self, svc, client):
        schema = {"type": "object"}
        updated = {"type": "object", "updated": True}
        client.put = AsyncMock(return_value=_make_response(updated))
        result = await svc.update_schema("ios_facts", schema)
        client.put.assert_called_once_with("/modules/ios_facts/schema", json=schema)
        assert result == updated

    @pytest.mark.asyncio
    async def test_delete_schema(self, svc, client):
        resp_data = {"deleted": True}
        client.delete = AsyncMock(return_value=_make_response(resp_data))
        result = await svc.delete_schema("ios_facts")
        client.delete.assert_called_once_with("/modules/ios_facts/schema")
        assert result == resp_data

    @pytest.mark.asyncio
    async def test_execute(self, svc, client):
        params = {"host": "router1"}
        exec_result = {"job_id": "j1", "status": "running"}
        client.post = AsyncMock(return_value=_make_response(exec_result))
        result = await svc.execute("ios_facts", params)
        client.post.assert_called_once_with("/modules/ios_facts/execute", json=params)
        assert result == exec_result

    @pytest.mark.asyncio
    async def test_execute_empty_params(self, svc, client):
        client.post = AsyncMock(return_value=_make_response({"status": "ok"}))
        await svc.execute("ios_facts", {})
        client.post.assert_called_once_with("/modules/ios_facts/execute", json={})

    @pytest.mark.asyncio
    async def test_get_history(self, svc, client):
        history = [{"job_id": "j1", "status": "completed"}]
        client.get = AsyncMock(return_value=_make_response(history))
        result = await svc.get_history("ios_facts")
        client.get.assert_called_once_with("/modules/ios_facts/history", params={})
        assert result == history

    @pytest.mark.asyncio
    async def test_get_history_with_params(self, svc, client):
        client.get = AsyncMock(return_value=_make_response([]))
        await svc.get_history("ios_facts", limit=5, status="completed")
        client.get.assert_called_once_with(
            "/modules/ios_facts/history", params={"limit": 5, "status": "completed"}
        )

    @pytest.mark.asyncio
    async def test_refresh(self, svc, client):
        resp = {"refreshed": True, "count": 5}
        client.post = AsyncMock(return_value=_make_response(resp))
        result = await svc.refresh()
        client.post.assert_called_once_with("/modules/refresh")
        assert result == resp


# ===========================================================================
# Roles
# ===========================================================================


class TestRolesService:
    @pytest.fixture
    def client(self):
        return Mock()

    @pytest.fixture
    def svc(self, client):
        return RolesService(client)

    def test_name(self, svc):
        assert svc.name == "roles"

    def test_inherits_service_base(self):
        assert issubclass(RolesService, ServiceBase)

    @pytest.mark.asyncio
    async def test_get(self, svc, client):
        data = {"name": "deploy_config"}
        client.get = AsyncMock(return_value=_make_response(data))
        result = await svc.get("deploy_config")
        client.get.assert_called_once_with("/roles/deploy_config")
        assert result == data

    @pytest.mark.asyncio
    async def test_get_all(self, svc, client):
        items = [{"name": "role1"}, {"name": "role2"}]
        client.get = AsyncMock(return_value=_make_response(_make_paginated(items)))
        result = await svc.get_all()
        assert result == items

    @pytest.mark.asyncio
    async def test_get_schema(self, svc, client):
        schema = {"type": "object"}
        client.get = AsyncMock(return_value=_make_response(schema))
        result = await svc.get_schema("deploy_config")
        client.get.assert_called_once_with("/roles/deploy_config/schema")
        assert result == schema

    @pytest.mark.asyncio
    async def test_update_schema(self, svc, client):
        schema = {"type": "object"}
        client.put = AsyncMock(return_value=_make_response({"updated": True}))
        result = await svc.update_schema("deploy_config", schema)
        client.put.assert_called_once_with("/roles/deploy_config/schema", json=schema)
        assert result == {"updated": True}

    @pytest.mark.asyncio
    async def test_delete_schema(self, svc, client):
        client.delete = AsyncMock(return_value=_make_response({"deleted": True}))
        result = await svc.delete_schema("deploy_config")
        client.delete.assert_called_once_with("/roles/deploy_config/schema")
        assert result == {"deleted": True}

    @pytest.mark.asyncio
    async def test_execute(self, svc, client):
        params = {"hosts": ["router1"]}
        client.post = AsyncMock(return_value=_make_response({"job_id": "j2"}))
        result = await svc.execute("deploy_config", params)
        client.post.assert_called_once_with("/roles/deploy_config/execute", json=params)
        assert result == {"job_id": "j2"}

    @pytest.mark.asyncio
    async def test_get_history(self, svc, client):
        client.get = AsyncMock(return_value=_make_response([{"job_id": "j1"}]))
        result = await svc.get_history("deploy_config")
        client.get.assert_called_once_with("/roles/deploy_config/history", params={})
        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_get_history_with_params(self, svc, client):
        client.get = AsyncMock(return_value=_make_response([]))
        await svc.get_history("deploy_config", limit=10)
        client.get.assert_called_once_with(
            "/roles/deploy_config/history", params={"limit": 10}
        )

    @pytest.mark.asyncio
    async def test_refresh(self, svc, client):
        client.post = AsyncMock(return_value=_make_response({"refreshed": True}))
        result = await svc.refresh()
        client.post.assert_called_once_with("/roles/refresh")
        assert result == {"refreshed": True}


# ===========================================================================
# Scripts
# ===========================================================================


class TestScriptsService:
    @pytest.fixture
    def client(self):
        return Mock()

    @pytest.fixture
    def svc(self, client):
        return ScriptsService(client)

    def test_name(self, svc):
        assert svc.name == "scripts"

    def test_inherits_service_base(self):
        assert issubclass(ScriptsService, ServiceBase)

    @pytest.mark.asyncio
    async def test_get(self, svc, client):
        data = {"name": "ping_test", "language": "python"}
        client.get = AsyncMock(return_value=_make_response(data))
        result = await svc.get("ping_test")
        client.get.assert_called_once_with("/scripts/ping_test")
        assert result == data

    @pytest.mark.asyncio
    async def test_get_all(self, svc, client):
        items = [{"name": "s1"}, {"name": "s2"}]
        client.get = AsyncMock(return_value=_make_response(_make_paginated(items)))
        result = await svc.get_all()
        assert result == items

    @pytest.mark.asyncio
    async def test_get_schema(self, svc, client):
        client.get = AsyncMock(return_value=_make_response({"type": "object"}))
        result = await svc.get_schema("ping_test")
        client.get.assert_called_once_with("/scripts/ping_test/schema")
        assert result == {"type": "object"}

    @pytest.mark.asyncio
    async def test_update_schema(self, svc, client):
        schema = {"type": "object", "properties": {"host": {"type": "string"}}}
        client.put = AsyncMock(return_value=_make_response(schema))
        result = await svc.update_schema("ping_test", schema)
        client.put.assert_called_once_with("/scripts/ping_test/schema", json=schema)
        assert result == schema

    @pytest.mark.asyncio
    async def test_delete_schema(self, svc, client):
        client.delete = AsyncMock(return_value=_make_response({"deleted": True}))
        result = await svc.delete_schema("ping_test")
        client.delete.assert_called_once_with("/scripts/ping_test/schema")
        assert result == {"deleted": True}

    @pytest.mark.asyncio
    async def test_execute(self, svc, client):
        params = {"target": "192.168.1.1"}
        exec_result = {"exit_code": 0, "stdout": "PING OK"}
        client.post = AsyncMock(return_value=_make_response(exec_result))
        result = await svc.execute("ping_test", params)
        client.post.assert_called_once_with("/scripts/ping_test/execute", json=params)
        assert result == exec_result

    @pytest.mark.asyncio
    async def test_get_history(self, svc, client):
        history = [{"job_id": "j1", "exit_code": 0}]
        client.get = AsyncMock(return_value=_make_response(history))
        result = await svc.get_history("ping_test")
        client.get.assert_called_once_with("/scripts/ping_test/history", params={})
        assert result == history

    @pytest.mark.asyncio
    async def test_get_history_with_params(self, svc, client):
        client.get = AsyncMock(return_value=_make_response([]))
        await svc.get_history("ping_test", limit=20, exit_code=0)
        client.get.assert_called_once_with(
            "/scripts/ping_test/history", params={"limit": 20, "exit_code": 0}
        )

    @pytest.mark.asyncio
    async def test_refresh(self, svc, client):
        client.post = AsyncMock(return_value=_make_response({"refreshed": True}))
        result = await svc.refresh()
        client.post.assert_called_once_with("/scripts/refresh")
        assert result == {"refreshed": True}


# ===========================================================================
# Nornir
# ===========================================================================


class TestNornirService:
    @pytest.fixture
    def client(self):
        return Mock()

    @pytest.fixture
    def svc(self, client):
        return NornirService(client)

    def test_name(self, svc):
        assert svc.name == "nornir"

    def test_inherits_service_base(self):
        assert issubclass(NornirService, ServiceBase)

    @pytest.mark.asyncio
    async def test_get(self, svc, client):
        data = {"name": "get_interfaces"}
        client.get = AsyncMock(return_value=_make_response(data))
        result = await svc.get("get_interfaces")
        client.get.assert_called_once_with("/nornir/get_interfaces")
        assert result == data

    @pytest.mark.asyncio
    async def test_get_all(self, svc, client):
        items = [{"name": "task1"}, {"name": "task2"}]
        client.get = AsyncMock(return_value=_make_response(_make_paginated(items)))
        result = await svc.get_all()
        assert result == items

    @pytest.mark.asyncio
    async def test_get_schema(self, svc, client):
        client.get = AsyncMock(return_value=_make_response({"type": "object"}))
        result = await svc.get_schema("get_interfaces")
        client.get.assert_called_once_with("/nornir/get_interfaces/schema")
        assert result == {"type": "object"}

    @pytest.mark.asyncio
    async def test_update_schema(self, svc, client):
        schema = {"type": "object"}
        client.put = AsyncMock(return_value=_make_response({"updated": True}))
        result = await svc.update_schema("get_interfaces", schema)
        client.put.assert_called_once_with("/nornir/get_interfaces/schema", json=schema)
        assert result == {"updated": True}

    @pytest.mark.asyncio
    async def test_delete_schema(self, svc, client):
        client.delete = AsyncMock(return_value=_make_response({"deleted": True}))
        result = await svc.delete_schema("get_interfaces")
        client.delete.assert_called_once_with("/nornir/get_interfaces/schema")
        assert result == {"deleted": True}

    @pytest.mark.asyncio
    async def test_execute(self, svc, client):
        params = {"hosts": ["router1", "router2"]}
        exec_result = {"results": {"router1": "ok", "router2": "ok"}}
        client.post = AsyncMock(return_value=_make_response(exec_result))
        result = await svc.execute("get_interfaces", params)
        client.post.assert_called_once_with(
            "/nornir/get_interfaces/execute", json=params
        )
        assert result == exec_result

    @pytest.mark.asyncio
    async def test_get_history(self, svc, client):
        history = [{"job_id": "j1"}]
        client.get = AsyncMock(return_value=_make_response(history))
        result = await svc.get_history("get_interfaces")
        client.get.assert_called_once_with("/nornir/get_interfaces/history", params={})
        assert result == history

    @pytest.mark.asyncio
    async def test_get_history_with_params(self, svc, client):
        client.get = AsyncMock(return_value=_make_response([]))
        await svc.get_history("get_interfaces", limit=5)
        client.get.assert_called_once_with(
            "/nornir/get_interfaces/history", params={"limit": 5}
        )

    @pytest.mark.asyncio
    async def test_refresh(self, svc, client):
        client.post = AsyncMock(return_value=_make_response({"refreshed": True}))
        result = await svc.refresh()
        client.post.assert_called_once_with("/nornir/refresh")
        assert result == {"refreshed": True}


# ===========================================================================
# Collections
# ===========================================================================


class TestCollectionsService:
    @pytest.fixture
    def client(self):
        return Mock()

    @pytest.fixture
    def svc(self, client):
        return CollectionsService(client)

    def test_name(self, svc):
        assert svc.name == "collections"

    def test_inherits_service_base(self):
        assert issubclass(CollectionsService, ServiceBase)

    @pytest.mark.asyncio
    async def test_get(self, svc, client):
        data = {"name": "cisco.ios", "version": "2.0.0"}
        client.get = AsyncMock(return_value=_make_response(data))
        result = await svc.get("cisco.ios")
        client.get.assert_called_once_with("/collections/cisco.ios")
        assert result == data

    @pytest.mark.asyncio
    async def test_get_all(self, svc, client):
        items = [{"name": "cisco.ios"}, {"name": "arista.eos"}]
        client.get = AsyncMock(return_value=_make_response(_make_paginated(items)))
        result = await svc.get_all()
        assert result == items

    @pytest.mark.asyncio
    async def test_install(self, svc, client):
        params = {"collection": "cisco.ios", "version": "3.0.0"}
        result_data = {"installed": True}
        client.post = AsyncMock(return_value=_make_response(result_data))
        result = await svc.install(params)
        client.post.assert_called_once_with("/collections/install", json=params)
        assert result == result_data

    @pytest.mark.asyncio
    async def test_refresh(self, svc, client):
        client.post = AsyncMock(return_value=_make_response({"refreshed": True}))
        result = await svc.refresh()
        client.post.assert_called_once_with("/collections/refresh")
        assert result == {"refreshed": True}

    # --- Module sub-resources ---

    @pytest.mark.asyncio
    async def test_get_module(self, svc, client):
        data = {"name": "facts", "collection": "cisco.ios"}
        client.get = AsyncMock(return_value=_make_response(data))
        result = await svc.get_module("cisco.ios", "facts")
        client.get.assert_called_once_with("/collections/cisco.ios/modules/facts")
        assert result == data

    @pytest.mark.asyncio
    async def test_get_modules(self, svc, client):
        modules = [{"name": "facts"}, {"name": "command"}]
        client.get = AsyncMock(return_value=_make_response(modules))
        result = await svc.get_modules("cisco.ios")
        client.get.assert_called_once_with("/collections/cisco.ios/modules", params={})
        assert result == modules

    @pytest.mark.asyncio
    async def test_get_modules_with_params(self, svc, client):
        client.get = AsyncMock(return_value=_make_response([]))
        await svc.get_modules("cisco.ios", limit=10)
        client.get.assert_called_once_with(
            "/collections/cisco.ios/modules", params={"limit": 10}
        )

    @pytest.mark.asyncio
    async def test_get_module_schema(self, svc, client):
        schema = {"type": "object"}
        client.get = AsyncMock(return_value=_make_response(schema))
        result = await svc.get_module_schema("cisco.ios", "facts")
        client.get.assert_called_once_with(
            "/collections/cisco.ios/modules/facts/schema"
        )
        assert result == schema

    @pytest.mark.asyncio
    async def test_update_module_schema(self, svc, client):
        schema = {"type": "object", "properties": {"host": {"type": "string"}}}
        client.put = AsyncMock(return_value=_make_response({"updated": True}))
        result = await svc.update_module_schema("cisco.ios", "facts", schema)
        client.put.assert_called_once_with(
            "/collections/cisco.ios/modules/facts/schema", json=schema
        )
        assert result == {"updated": True}

    @pytest.mark.asyncio
    async def test_delete_module_schema(self, svc, client):
        client.delete = AsyncMock(return_value=_make_response({"deleted": True}))
        result = await svc.delete_module_schema("cisco.ios", "facts")
        client.delete.assert_called_once_with(
            "/collections/cisco.ios/modules/facts/schema"
        )
        assert result == {"deleted": True}

    @pytest.mark.asyncio
    async def test_execute_module(self, svc, client):
        params = {"host": "router1"}
        exec_result = {"job_id": "j1", "status": "running"}
        client.post = AsyncMock(return_value=_make_response(exec_result))
        result = await svc.execute_module("cisco.ios", "facts", params)
        client.post.assert_called_once_with(
            "/collections/cisco.ios/modules/facts/execute", json=params
        )
        assert result == exec_result

    @pytest.mark.asyncio
    async def test_get_module_history(self, svc, client):
        history = [{"job_id": "j1"}]
        client.get = AsyncMock(return_value=_make_response(history))
        result = await svc.get_module_history("cisco.ios", "facts")
        client.get.assert_called_once_with(
            "/collections/cisco.ios/modules/facts/history", params={}
        )
        assert result == history

    @pytest.mark.asyncio
    async def test_get_module_history_with_params(self, svc, client):
        client.get = AsyncMock(return_value=_make_response([]))
        await svc.get_module_history("cisco.ios", "facts", limit=5)
        client.get.assert_called_once_with(
            "/collections/cisco.ios/modules/facts/history", params={"limit": 5}
        )

    # --- Role sub-resources ---

    @pytest.mark.asyncio
    async def test_get_role(self, svc, client):
        data = {"name": "deploy", "collection": "cisco.ios"}
        client.get = AsyncMock(return_value=_make_response(data))
        result = await svc.get_role("cisco.ios", "deploy")
        client.get.assert_called_once_with("/collections/cisco.ios/roles/deploy")
        assert result == data

    @pytest.mark.asyncio
    async def test_get_roles(self, svc, client):
        roles = [{"name": "deploy"}, {"name": "backup"}]
        client.get = AsyncMock(return_value=_make_response(roles))
        result = await svc.get_roles("cisco.ios")
        client.get.assert_called_once_with("/collections/cisco.ios/roles", params={})
        assert result == roles

    @pytest.mark.asyncio
    async def test_get_roles_with_params(self, svc, client):
        client.get = AsyncMock(return_value=_make_response([]))
        await svc.get_roles("cisco.ios", limit=5)
        client.get.assert_called_once_with(
            "/collections/cisco.ios/roles", params={"limit": 5}
        )

    @pytest.mark.asyncio
    async def test_get_role_schema(self, svc, client):
        schema = {"type": "object"}
        client.get = AsyncMock(return_value=_make_response(schema))
        result = await svc.get_role_schema("cisco.ios", "deploy")
        client.get.assert_called_once_with("/collections/cisco.ios/roles/deploy/schema")
        assert result == schema

    @pytest.mark.asyncio
    async def test_update_role_schema(self, svc, client):
        schema = {"type": "object"}
        client.put = AsyncMock(return_value=_make_response({"updated": True}))
        result = await svc.update_role_schema("cisco.ios", "deploy", schema)
        client.put.assert_called_once_with(
            "/collections/cisco.ios/roles/deploy/schema", json=schema
        )
        assert result == {"updated": True}

    @pytest.mark.asyncio
    async def test_delete_role_schema(self, svc, client):
        client.delete = AsyncMock(return_value=_make_response({"deleted": True}))
        result = await svc.delete_role_schema("cisco.ios", "deploy")
        client.delete.assert_called_once_with(
            "/collections/cisco.ios/roles/deploy/schema"
        )
        assert result == {"deleted": True}

    @pytest.mark.asyncio
    async def test_execute_role(self, svc, client):
        params = {"hosts": ["router1"]}
        exec_result = {"job_id": "j2", "status": "running"}
        client.post = AsyncMock(return_value=_make_response(exec_result))
        result = await svc.execute_role("cisco.ios", "deploy", params)
        client.post.assert_called_once_with(
            "/collections/cisco.ios/roles/deploy/execute", json=params
        )
        assert result == exec_result

    @pytest.mark.asyncio
    async def test_get_role_history(self, svc, client):
        history = [{"job_id": "j2"}]
        client.get = AsyncMock(return_value=_make_response(history))
        result = await svc.get_role_history("cisco.ios", "deploy")
        client.get.assert_called_once_with(
            "/collections/cisco.ios/roles/deploy/history", params={}
        )
        assert result == history

    @pytest.mark.asyncio
    async def test_get_role_history_with_params(self, svc, client):
        client.get = AsyncMock(return_value=_make_response([]))
        await svc.get_role_history("cisco.ios", "deploy", limit=3)
        client.get.assert_called_once_with(
            "/collections/cisco.ios/roles/deploy/history", params={"limit": 3}
        )


# ===========================================================================
# Terraforms
# ===========================================================================


class TestTerraformsService:
    @pytest.fixture
    def client(self):
        return Mock()

    @pytest.fixture
    def svc(self, client):
        return TerraformsService(client)

    def test_name(self, svc):
        assert svc.name == "terraforms"

    def test_inherits_service_base(self):
        assert issubclass(TerraformsService, ServiceBase)

    @pytest.mark.asyncio
    async def test_get(self, svc, client):
        data = {"name": "vpc_config", "provider": "aws"}
        client.get = AsyncMock(return_value=_make_response(data))
        result = await svc.get("vpc_config")
        client.get.assert_called_once_with("/terraforms/vpc_config")
        assert result == data

    @pytest.mark.asyncio
    async def test_get_all(self, svc, client):
        items = [{"name": "vpc_config"}, {"name": "subnet_config"}]
        client.get = AsyncMock(return_value=_make_response(_make_paginated(items)))
        result = await svc.get_all()
        assert result == items

    @pytest.mark.asyncio
    async def test_get_all_multiple_pages(self, svc, client):
        page1 = [{"name": f"tf{i}"} for i in range(100)]
        page2 = [{"name": f"tf{i}"} for i in range(100, 110)]
        client.get = AsyncMock(
            side_effect=[
                _make_response(_make_paginated(page1, total=110)),
                _make_response(_make_paginated(page2, total=110)),
            ]
        )
        result = await svc.get_all()
        assert len(result) == 110

    @pytest.mark.asyncio
    async def test_get_schema(self, svc, client):
        schema = {"type": "object", "properties": {"region": {"type": "string"}}}
        client.get = AsyncMock(return_value=_make_response(schema))
        result = await svc.get_schema("vpc_config")
        client.get.assert_called_once_with("/terraforms/vpc_config/schema")
        assert result == schema

    @pytest.mark.asyncio
    async def test_update_schema(self, svc, client):
        schema = {"type": "object"}
        client.put = AsyncMock(return_value=_make_response({"updated": True}))
        result = await svc.update_schema("vpc_config", schema)
        client.put.assert_called_once_with("/terraforms/vpc_config/schema", json=schema)
        assert result == {"updated": True}

    @pytest.mark.asyncio
    async def test_delete_schema(self, svc, client):
        client.delete = AsyncMock(return_value=_make_response({"deleted": True}))
        result = await svc.delete_schema("vpc_config")
        client.delete.assert_called_once_with("/terraforms/vpc_config/schema")
        assert result == {"deleted": True}

    @pytest.mark.asyncio
    async def test_init(self, svc, client):
        params = {"backend": "s3", "bucket": "my-tf-state"}
        result_data = {"initialized": True}
        client.post = AsyncMock(return_value=_make_response(result_data))
        result = await svc.init("vpc_config", params)
        client.post.assert_called_once_with("/terraforms/vpc_config/init", json=params)
        assert result == result_data

    @pytest.mark.asyncio
    async def test_apply(self, svc, client):
        params = {"var": {"region": "us-east-1"}}
        result_data = {"apply_result": "applied", "changes": 3}
        client.post = AsyncMock(return_value=_make_response(result_data))
        result = await svc.apply("vpc_config", params)
        client.post.assert_called_once_with("/terraforms/vpc_config/apply", json=params)
        assert result == result_data

    @pytest.mark.asyncio
    async def test_apply_empty_params(self, svc, client):
        client.post = AsyncMock(return_value=_make_response({"changes": 0}))
        await svc.apply("vpc_config", {})
        client.post.assert_called_once_with("/terraforms/vpc_config/apply", json={})

    @pytest.mark.asyncio
    async def test_plan(self, svc, client):
        params = {"var": {"env": "prod"}}
        result_data = {"plan": "will add 2 resources"}
        client.post = AsyncMock(return_value=_make_response(result_data))
        result = await svc.plan("vpc_config", params)
        client.post.assert_called_once_with("/terraforms/vpc_config/plan", json=params)
        assert result == result_data

    @pytest.mark.asyncio
    async def test_validate(self, svc, client):
        params = {}
        result_data = {"valid": True, "warnings": []}
        client.post = AsyncMock(return_value=_make_response(result_data))
        result = await svc.validate("vpc_config", params)
        client.post.assert_called_once_with(
            "/terraforms/vpc_config/validate", json=params
        )
        assert result == result_data

    @pytest.mark.asyncio
    async def test_destroy(self, svc, client):
        params = {"target": "aws_vpc.main"}
        result_data = {"destroyed": True}
        client.post = AsyncMock(return_value=_make_response(result_data))
        result = await svc.destroy("vpc_config", params)
        client.post.assert_called_once_with(
            "/terraforms/vpc_config/destroy", json=params
        )
        assert result == result_data

    @pytest.mark.asyncio
    async def test_get_history(self, svc, client):
        history = [{"job_id": "j1", "operation": "apply"}]
        client.get = AsyncMock(return_value=_make_response(history))
        result = await svc.get_history("vpc_config")
        client.get.assert_called_once_with("/terraforms/vpc_config/history", params={})
        assert result == history

    @pytest.mark.asyncio
    async def test_get_history_with_params(self, svc, client):
        client.get = AsyncMock(return_value=_make_response([]))
        await svc.get_history("vpc_config", operation="apply")
        client.get.assert_called_once_with(
            "/terraforms/vpc_config/history", params={"operation": "apply"}
        )

    @pytest.mark.asyncio
    async def test_refresh(self, svc, client):
        client.post = AsyncMock(return_value=_make_response({"refreshed": True}))
        result = await svc.refresh()
        client.post.assert_called_once_with("/terraforms/refresh")
        assert result == {"refreshed": True}
