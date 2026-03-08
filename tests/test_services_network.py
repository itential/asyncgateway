# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Tests for network protocol services: gnmi, gnoi, netmiko, netconf, http_requests."""

from unittest.mock import AsyncMock, Mock

import pytest

from asyncgateway.services import ServiceBase
from asyncgateway.services.gnmi import Service as GnmiService
from asyncgateway.services.gnoi import Service as GnoiService
from asyncgateway.services.http_requests import Service as HttpRequestsService
from asyncgateway.services.netconf import Service as NetconfService
from asyncgateway.services.netmiko import Service as NetmikoService


def _resp(data):
    r = Mock()
    r.json.return_value = data
    return r


# ===========================================================================
# gNMI
# ===========================================================================


class TestGnmiService:
    @pytest.fixture
    def client(self):
        return Mock()

    @pytest.fixture
    def svc(self, client):
        return GnmiService(client)

    def test_name(self, svc):
        assert svc.name == "gnmi"

    def test_inherits_service_base(self):
        assert issubclass(GnmiService, ServiceBase)

    def test_init(self, client):
        s = GnmiService(client)
        assert s.client is client

    @pytest.mark.asyncio
    async def test_get(self, svc, client):
        params = {"host": "router1", "path": [{"elem": [{"name": "interfaces"}]}]}
        result_data = {"notification": [{"update": [{"val": "10GE0/0"}]}]}
        client.post = AsyncMock(return_value=_resp(result_data))
        result = await svc.get(params)
        client.post.assert_called_once_with("/gnmi/get/execute", json=params)
        assert result == result_data

    @pytest.mark.asyncio
    async def test_get_returns_json(self, svc, client):
        client.post = AsyncMock(return_value=_resp({"data": "value"}))
        result = await svc.get({"host": "r1"})
        assert result == {"data": "value"}

    @pytest.mark.asyncio
    async def test_set(self, svc, client):
        params = {"host": "router1", "update": [{"path": {}, "val": "description"}]}
        result_data = {"response": [{"op": "UPDATE", "path": {}}]}
        client.post = AsyncMock(return_value=_resp(result_data))
        result = await svc.set(params)
        client.post.assert_called_once_with("/gnmi/set/execute", json=params)
        assert result == result_data

    @pytest.mark.asyncio
    async def test_get_history(self, svc, client):
        history = [{"job_id": "j1", "command": "get"}]
        client.get = AsyncMock(return_value=_resp(history))
        result = await svc.get_history("get")
        client.get.assert_called_once_with("/gnmi/get/history", params={})
        assert result == history

    @pytest.mark.asyncio
    async def test_get_history_set_command(self, svc, client):
        client.get = AsyncMock(return_value=_resp([]))
        await svc.get_history("set")
        client.get.assert_called_once_with("/gnmi/set/history", params={})

    @pytest.mark.asyncio
    async def test_get_history_with_params(self, svc, client):
        client.get = AsyncMock(return_value=_resp([]))
        await svc.get_history("get", limit=10, status="completed")
        client.get.assert_called_once_with(
            "/gnmi/get/history", params={"limit": 10, "status": "completed"}
        )


# ===========================================================================
# gNOI
# ===========================================================================


class TestGnoiService:
    @pytest.fixture
    def client(self):
        return Mock()

    @pytest.fixture
    def svc(self, client):
        return GnoiService(client)

    def test_name(self, svc):
        assert svc.name == "gnoi"

    def test_inherits_service_base(self):
        assert issubclass(GnoiService, ServiceBase)

    def test_init(self, client):
        s = GnoiService(client)
        assert s.client is client

    @pytest.mark.asyncio
    async def test_ping(self, svc, client):
        params = {"host": "router1", "destination": "8.8.8.8", "count": 5}
        result_data = {"sent": 5, "received": 5, "avg_rtt_ms": 2}
        client.post = AsyncMock(return_value=_resp(result_data))
        result = await svc.ping(params)
        client.post.assert_called_once_with("/gnoi/ping/execute", json=params)
        assert result == result_data

    @pytest.mark.asyncio
    async def test_reboot(self, svc, client):
        params = {"host": "router1", "method": "COLD", "delay": 0}
        client.post = AsyncMock(return_value=_resp({"status": "rebooting"}))
        result = await svc.reboot(params)
        client.post.assert_called_once_with("/gnoi/reboot/execute", json=params)
        assert result == {"status": "rebooting"}

    @pytest.mark.asyncio
    async def test_time(self, svc, client):
        params = {"host": "router1"}
        client.post = AsyncMock(return_value=_resp({"time": 1700000000000000000}))
        result = await svc.time(params)
        client.post.assert_called_once_with("/gnoi/time/execute", json=params)
        assert result == {"time": 1700000000000000000}

    @pytest.mark.asyncio
    async def test_traceroute(self, svc, client):
        params = {"host": "router1", "destination": "10.0.0.1"}
        client.post = AsyncMock(return_value=_resp({"hops": [{"address": "10.0.0.1"}]}))
        result = await svc.traceroute(params)
        client.post.assert_called_once_with("/gnoi/traceroute/execute", json=params)
        assert result["hops"][0]["address"] == "10.0.0.1"

    @pytest.mark.asyncio
    async def test_switch_cpu(self, svc, client):
        params = {"host": "router1", "control_processor": 0}
        client.post = AsyncMock(return_value=_resp({"status": "ok"}))
        result = await svc.switch_cpu(params)
        client.post.assert_called_once_with("/gnoi/switch_cpu/execute", json=params)
        assert result == {"status": "ok"}

    @pytest.mark.asyncio
    async def test_reboot_status(self, svc, client):
        params = {"host": "router1"}
        client.post = AsyncMock(return_value=_resp({"active": False, "reason": ""}))
        result = await svc.reboot_status(params)
        client.post.assert_called_once_with("/gnoi/reboot_status/execute", json=params)
        assert result["active"] is False

    @pytest.mark.asyncio
    async def test_set_package(self, svc, client):
        params = {"host": "router1", "package": {"filename": "ios.tar", "hash": "abc"}}
        client.post = AsyncMock(return_value=_resp({"status": "installed"}))
        result = await svc.set_package(params)
        client.post.assert_called_once_with("/gnoi/set_package/execute", json=params)
        assert result == {"status": "installed"}

    @pytest.mark.asyncio
    async def test_cancel_reboot(self, svc, client):
        params = {"host": "router1"}
        client.post = AsyncMock(return_value=_resp({"status": "cancelled"}))
        result = await svc.cancel_reboot(params)
        client.post.assert_called_once_with("/gnoi/cancel_reboot/execute", json=params)
        assert result == {"status": "cancelled"}

    @pytest.mark.asyncio
    async def test_clear_lldp_interface(self, svc, client):
        params = {"host": "router1", "interface": "Gi0/0"}
        client.post = AsyncMock(return_value=_resp({"cleared": True}))
        result = await svc.clear_lldp_interface(params)
        client.post.assert_called_once_with(
            "/gnoi/clear_lldp_interface/execute", json=params
        )
        assert result == {"cleared": True}

    @pytest.mark.asyncio
    async def test_clear_bgp_neighbor(self, svc, client):
        params = {"host": "router1", "address": "10.0.0.2", "soft_reset": True}
        client.post = AsyncMock(return_value=_resp({"cleared": True}))
        result = await svc.clear_bgp_neighbor(params)
        client.post.assert_called_once_with(
            "/gnoi/clear_bgp_neighbor/execute", json=params
        )
        assert result == {"cleared": True}

    @pytest.mark.asyncio
    async def test_clear_interface_counters(self, svc, client):
        params = {"host": "router1", "interface": "Gi0/1"}
        client.post = AsyncMock(return_value=_resp({"cleared": True}))
        result = await svc.clear_interface_counters(params)
        client.post.assert_called_once_with(
            "/gnoi/clear_interface_counters/execute", json=params
        )
        assert result == {"cleared": True}

    @pytest.mark.asyncio
    async def test_clear_neighbor_discovery(self, svc, client):
        params = {"host": "router1", "interface": "Gi0/0"}
        client.post = AsyncMock(return_value=_resp({"cleared": True}))
        result = await svc.clear_neighbor_discovery(params)
        client.post.assert_called_once_with(
            "/gnoi/clear_neighbor_discovery/execute", json=params
        )
        assert result == {"cleared": True}

    @pytest.mark.asyncio
    async def test_clear_spanning_tree(self, svc, client):
        params = {"host": "router1", "vlan": 100}
        client.post = AsyncMock(return_value=_resp({"cleared": True}))
        result = await svc.clear_spanning_tree(params)
        client.post.assert_called_once_with(
            "/gnoi/clear_spanning_tree/execute", json=params
        )
        assert result == {"cleared": True}

    @pytest.mark.asyncio
    async def test_wake_on_lan(self, svc, client):
        params = {"host": "router1", "mac": "aa:bb:cc:dd:ee:ff"}
        client.post = AsyncMock(return_value=_resp({"sent": True}))
        result = await svc.wake_on_lan(params)
        client.post.assert_called_once_with("/gnoi/wake_on_lan/execute", json=params)
        assert result == {"sent": True}

    @pytest.mark.asyncio
    async def test_get_history(self, svc, client):
        history = [{"job_id": "j1", "command": "ping"}]
        client.get = AsyncMock(return_value=_resp(history))
        result = await svc.get_history("ping")
        client.get.assert_called_once_with("/gnoi/ping/history", params={})
        assert result == history

    @pytest.mark.asyncio
    async def test_get_history_with_params(self, svc, client):
        client.get = AsyncMock(return_value=_resp([]))
        await svc.get_history("reboot", limit=5)
        client.get.assert_called_once_with("/gnoi/reboot/history", params={"limit": 5})


# ===========================================================================
# Netmiko
# ===========================================================================


class TestNetmikoService:
    @pytest.fixture
    def client(self):
        return Mock()

    @pytest.fixture
    def svc(self, client):
        return NetmikoService(client)

    def test_name(self, svc):
        assert svc.name == "netmiko"

    def test_inherits_service_base(self):
        assert issubclass(NetmikoService, ServiceBase)

    def test_init(self, client):
        s = NetmikoService(client)
        assert s.client is client

    @pytest.mark.asyncio
    async def test_send_command(self, svc, client):
        params = {
            "device_type": "cisco_ios",
            "host": "192.168.1.1",
            "username": "admin",
            "command_string": "show ip interface brief",
        }
        result_data = {"output": "Interface   IP-Address  OK? Method Status Protocol"}
        client.post = AsyncMock(return_value=_resp(result_data))
        result = await svc.send_command(params)
        client.post.assert_called_once_with(
            "/netmiko/send_command/execute", json=params
        )
        assert result == result_data

    @pytest.mark.asyncio
    async def test_send_command_returns_json(self, svc, client):
        client.post = AsyncMock(return_value=_resp({"output": ""}))
        result = await svc.send_command({"host": "r1", "command_string": "show ver"})
        assert isinstance(result, dict)
        assert "output" in result

    @pytest.mark.asyncio
    async def test_get_send_command_history(self, svc, client):
        history = [{"job_id": "j1", "command": "show ip interface brief"}]
        client.get = AsyncMock(return_value=_resp(history))
        result = await svc.get_send_command_history()
        client.get.assert_called_once_with("/netmiko/send_command/history", params={})
        assert result == history

    @pytest.mark.asyncio
    async def test_get_send_command_history_with_params(self, svc, client):
        client.get = AsyncMock(return_value=_resp([]))
        await svc.get_send_command_history(limit=10, status="completed")
        client.get.assert_called_once_with(
            "/netmiko/send_command/history",
            params={"limit": 10, "status": "completed"},
        )

    @pytest.mark.asyncio
    async def test_send_config(self, svc, client):
        params = {
            "device_type": "cisco_ios",
            "host": "192.168.1.1",
            "config_commands": ["interface Gi0/0", "description WAN"],
        }
        result_data = {"output": "interface Gi0/0\n description WAN"}
        client.post = AsyncMock(return_value=_resp(result_data))
        result = await svc.send_config(params)
        client.post.assert_called_once_with(
            "/netmiko/send_config_set/execute", json=params
        )
        assert result == result_data

    @pytest.mark.asyncio
    async def test_get_send_config_history(self, svc, client):
        history = [{"job_id": "j2", "status": "completed"}]
        client.get = AsyncMock(return_value=_resp(history))
        result = await svc.get_send_config_history()
        client.get.assert_called_once_with(
            "/netmiko/send_config_set/history", params={}
        )
        assert result == history

    @pytest.mark.asyncio
    async def test_get_send_config_history_with_params(self, svc, client):
        client.get = AsyncMock(return_value=_resp([]))
        await svc.get_send_config_history(limit=5)
        client.get.assert_called_once_with(
            "/netmiko/send_config_set/history", params={"limit": 5}
        )

    @pytest.mark.asyncio
    async def test_get_schema(self, svc, client):
        schema = {"type": "object", "properties": {"host": {"type": "string"}}}
        client.get = AsyncMock(return_value=_resp(schema))
        result = await svc.get_schema("send_command")
        client.get.assert_called_once_with("/netmiko/send_command/schema")
        assert result == schema

    @pytest.mark.asyncio
    async def test_get_schema_send_config(self, svc, client):
        client.get = AsyncMock(return_value=_resp({"type": "object"}))
        result = await svc.get_schema("send_config_set")
        client.get.assert_called_once_with("/netmiko/send_config_set/schema")
        assert result == {"type": "object"}


# ===========================================================================
# Netconf
# ===========================================================================


class TestNetconfService:
    @pytest.fixture
    def client(self):
        return Mock()

    @pytest.fixture
    def svc(self, client):
        return NetconfService(client)

    def test_name(self, svc):
        assert svc.name == "netconf"

    def test_inherits_service_base(self):
        assert issubclass(NetconfService, ServiceBase)

    def test_init(self, client):
        s = NetconfService(client)
        assert s.client is client

    @pytest.mark.asyncio
    async def test_get_config(self, svc, client):
        params = {
            "host": "router1",
            "datastore": "running",
            "filter": "<interfaces/>",
        }
        result_data = {
            "config": "<interfaces><interface>Gi0/0</interface></interfaces>"
        }
        client.post = AsyncMock(return_value=_resp(result_data))
        result = await svc.get_config(params)
        client.post.assert_called_once_with("/netconf/get_config/execute", json=params)
        assert result == result_data

    @pytest.mark.asyncio
    async def test_get_config_returns_json(self, svc, client):
        client.post = AsyncMock(return_value=_resp({"config": ""}))
        result = await svc.get_config({"host": "r1"})
        assert "config" in result

    @pytest.mark.asyncio
    async def test_set_config(self, svc, client):
        params = {
            "host": "router1",
            "datastore": "candidate",
            "config": "<interfaces/>",
        }
        result_data = {"status": "ok", "message": "config committed"}
        client.post = AsyncMock(return_value=_resp(result_data))
        result = await svc.set_config(params)
        client.post.assert_called_once_with("/netconf/set_config/execute", json=params)
        assert result == result_data

    @pytest.mark.asyncio
    async def test_exec_rpc(self, svc, client):
        params = {"host": "router1", "rpc": "<commit/>"}
        result_data = {"rpc_reply": "<ok/>"}
        client.post = AsyncMock(return_value=_resp(result_data))
        result = await svc.exec_rpc(params)
        client.post.assert_called_once_with("/netconf/exec_rpc/execute", json=params)
        assert result == result_data

    @pytest.mark.asyncio
    async def test_exec_rpc_with_complex_rpc(self, svc, client):
        params = {"host": "router1", "rpc": "<lock><target><running/></target></lock>"}
        client.post = AsyncMock(return_value=_resp({"rpc_reply": "<ok/>"}))
        await svc.exec_rpc(params)
        client.post.assert_called_once_with("/netconf/exec_rpc/execute", json=params)

    @pytest.mark.asyncio
    async def test_get_history(self, svc, client):
        history = [{"job_id": "j1", "command": "get_config"}]
        client.get = AsyncMock(return_value=_resp(history))
        result = await svc.get_history("get_config")
        client.get.assert_called_once_with("/netconf/get_config/history", params={})
        assert result == history

    @pytest.mark.asyncio
    async def test_get_history_for_set_config(self, svc, client):
        client.get = AsyncMock(return_value=_resp([]))
        await svc.get_history("set_config")
        client.get.assert_called_once_with("/netconf/set_config/history", params={})

    @pytest.mark.asyncio
    async def test_get_history_with_params(self, svc, client):
        client.get = AsyncMock(return_value=_resp([]))
        await svc.get_history("exec_rpc", limit=10, status="completed")
        client.get.assert_called_once_with(
            "/netconf/exec_rpc/history",
            params={"limit": 10, "status": "completed"},
        )


# ===========================================================================
# HTTP Requests
# ===========================================================================


class TestHttpRequestsService:
    @pytest.fixture
    def client(self):
        return Mock()

    @pytest.fixture
    def svc(self, client):
        return HttpRequestsService(client)

    def test_name(self, svc):
        assert svc.name == "http_requests"

    def test_inherits_service_base(self):
        assert issubclass(HttpRequestsService, ServiceBase)

    def test_init(self, client):
        s = HttpRequestsService(client)
        assert s.client is client

    @pytest.mark.asyncio
    async def test_get_schema(self, svc, client):
        schema = {
            "type": "object",
            "properties": {
                "method": {"type": "string", "enum": ["GET", "POST", "PUT", "DELETE"]},
                "url": {"type": "string"},
            },
        }
        client.get = AsyncMock(return_value=_resp(schema))
        result = await svc.get_schema()
        client.get.assert_called_once_with("/http_requests/request/schema")
        assert result == schema

    @pytest.mark.asyncio
    async def test_get_schema_empty(self, svc, client):
        client.get = AsyncMock(return_value=_resp({}))
        result = await svc.get_schema()
        assert result == {}

    @pytest.mark.asyncio
    async def test_execute_get(self, svc, client):
        params = {
            "method": "GET",
            "url": "https://api.example.com/devices",
            "headers": {"Authorization": "Bearer token123"},
        }
        result_data = {"status_code": 200, "body": [{"id": "d1"}]}
        client.post = AsyncMock(return_value=_resp(result_data))
        result = await svc.execute(params)
        client.post.assert_called_once_with(
            "/http_requests/request/execute", json=params
        )
        assert result == result_data

    @pytest.mark.asyncio
    async def test_execute_post(self, svc, client):
        params = {
            "method": "POST",
            "url": "https://api.example.com/devices",
            "body": {"name": "router1", "type": "cisco"},
        }
        client.post = AsyncMock(return_value=_resp({"status_code": 201, "body": {}}))
        result = await svc.execute(params)
        client.post.assert_called_once_with(
            "/http_requests/request/execute", json=params
        )
        assert result["status_code"] == 201

    @pytest.mark.asyncio
    async def test_execute_returns_json(self, svc, client):
        client.post = AsyncMock(return_value=_resp({"status_code": 204, "body": None}))
        result = await svc.execute({"method": "DELETE", "url": "https://example.com"})
        assert result["status_code"] == 204

    @pytest.mark.asyncio
    async def test_get_history(self, svc, client):
        history = [
            {"job_id": "j1", "method": "GET", "url": "https://api.example.com"},
            {"job_id": "j2", "method": "POST", "url": "https://api.example.com"},
        ]
        client.get = AsyncMock(return_value=_resp(history))
        result = await svc.get_history()
        client.get.assert_called_once_with("/http_requests/request/history", params={})
        assert len(result) == 2

    @pytest.mark.asyncio
    async def test_get_history_with_params(self, svc, client):
        client.get = AsyncMock(return_value=_resp([]))
        await svc.get_history(limit=5, status="completed")
        client.get.assert_called_once_with(
            "/http_requests/request/history",
            params={"limit": 5, "status": "completed"},
        )

    @pytest.mark.asyncio
    async def test_get_history_empty(self, svc, client):
        client.get = AsyncMock(return_value=_resp([]))
        result = await svc.get_history()
        assert result == []
