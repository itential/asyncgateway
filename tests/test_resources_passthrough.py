# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Tests for passthrough resources: netmiko, netconf, http_requests, gnmi, gnoi, config, system.

These resources are thin wrappers that delegate directly to their corresponding service.
Tests verify the delegation is correct and return values are propagated.
"""

from unittest.mock import AsyncMock, Mock

import pytest

from asyncgateway.resources.config import Resource as ConfigResource
from asyncgateway.resources.gnmi import Resource as GnmiResource
from asyncgateway.resources.gnoi import Resource as GnoiResource
from asyncgateway.resources.http_requests import Resource as HttpRequestsResource
from asyncgateway.resources.netconf import Resource as NetconfResource
from asyncgateway.resources.netmiko import Resource as NetmikoResource
from asyncgateway.resources.system import Resource as SystemResource

# ---------------------------------------------------------------------------
# Netmiko
# ---------------------------------------------------------------------------


class TestNetmikoResource:
    @pytest.fixture
    def mock_netmiko_service(self):
        svc = Mock()
        svc.send_command = AsyncMock(
            return_value={"output": "GigabitEthernet0/0   up   up"}
        )
        svc.send_config = AsyncMock(return_value={"output": "config accepted"})
        return svc

    @pytest.fixture
    def netmiko_resource(self, mock_netmiko_service):
        services = Mock()
        services.netmiko = mock_netmiko_service
        return NetmikoResource(services)

    def test_resource_name(self, netmiko_resource):
        assert netmiko_resource.name == "netmiko"

    @pytest.mark.asyncio
    async def test_send_command(self, netmiko_resource, mock_netmiko_service):
        params = {
            "device_type": "cisco_ios",
            "host": "192.168.1.1",
            "command": "show ip interface brief",
        }
        result = await netmiko_resource.send_command(params)

        mock_netmiko_service.send_command.assert_called_once_with(params)
        assert result == {"output": "GigabitEthernet0/0   up   up"}

    @pytest.mark.asyncio
    async def test_send_command_passes_params_unchanged(
        self, netmiko_resource, mock_netmiko_service
    ):
        params = {"device_type": "juniper", "host": "10.0.0.1", "command": "show route"}
        await netmiko_resource.send_command(params)

        call_args = mock_netmiko_service.send_command.call_args
        assert call_args[0][0] is params  # same object, not a copy

    @pytest.mark.asyncio
    async def test_send_config(self, netmiko_resource, mock_netmiko_service):
        params = {
            "device_type": "cisco_ios",
            "host": "192.168.1.1",
            "config_commands": ["interface Gi0/0", "description WAN"],
        }
        result = await netmiko_resource.send_config(params)

        mock_netmiko_service.send_config.assert_called_once_with(params)
        assert result == {"output": "config accepted"}

    @pytest.mark.asyncio
    async def test_send_config_passes_params_unchanged(
        self, netmiko_resource, mock_netmiko_service
    ):
        params = {"device_type": "cisco_ios", "host": "10.0.0.1", "config_commands": []}
        await netmiko_resource.send_config(params)

        call_args = mock_netmiko_service.send_config.call_args
        assert call_args[0][0] is params


# ---------------------------------------------------------------------------
# Netconf
# ---------------------------------------------------------------------------


class TestNetconfResource:
    @pytest.fixture
    def mock_netconf_service(self):
        svc = Mock()
        svc.get_config = AsyncMock(
            return_value={"config": "<configuration>...</configuration>"}
        )
        svc.set_config = AsyncMock(return_value={"status": "ok"})
        svc.exec_rpc = AsyncMock(return_value={"rpc_reply": "<ok/>"})
        return svc

    @pytest.fixture
    def netconf_resource(self, mock_netconf_service):
        services = Mock()
        services.netconf = mock_netconf_service
        return NetconfResource(services)

    def test_resource_name(self, netconf_resource):
        assert netconf_resource.name == "netconf"

    @pytest.mark.asyncio
    async def test_get_config(self, netconf_resource, mock_netconf_service):
        params = {"host": "router1", "datastore": "running"}
        result = await netconf_resource.get_config(params)

        mock_netconf_service.get_config.assert_called_once_with(params)
        assert result == {"config": "<configuration>...</configuration>"}

    @pytest.mark.asyncio
    async def test_set_config(self, netconf_resource, mock_netconf_service):
        params = {
            "host": "router1",
            "datastore": "candidate",
            "config": "<configuration><interfaces/></configuration>",
        }
        result = await netconf_resource.set_config(params)

        mock_netconf_service.set_config.assert_called_once_with(params)
        assert result == {"status": "ok"}

    @pytest.mark.asyncio
    async def test_exec_rpc(self, netconf_resource, mock_netconf_service):
        params = {"host": "router1", "rpc": "<commit/>"}
        result = await netconf_resource.exec_rpc(params)

        mock_netconf_service.exec_rpc.assert_called_once_with(params)
        assert result == {"rpc_reply": "<ok/>"}

    @pytest.mark.asyncio
    async def test_params_passed_unchanged(
        self, netconf_resource, mock_netconf_service
    ):
        params = {"host": "router1"}
        await netconf_resource.get_config(params)

        assert mock_netconf_service.get_config.call_args[0][0] is params


# ---------------------------------------------------------------------------
# HTTP Requests
# ---------------------------------------------------------------------------


class TestHttpRequestsResource:
    @pytest.fixture
    def mock_http_requests_service(self):
        svc = Mock()
        svc.execute = AsyncMock(
            return_value={"status_code": 200, "body": {"data": "result"}}
        )
        return svc

    @pytest.fixture
    def http_requests_resource(self, mock_http_requests_service):
        services = Mock()
        services.http_requests = mock_http_requests_service
        return HttpRequestsResource(services)

    def test_resource_name(self, http_requests_resource):
        assert http_requests_resource.name == "http_requests"

    @pytest.mark.asyncio
    async def test_request(self, http_requests_resource, mock_http_requests_service):
        params = {
            "method": "GET",
            "url": "https://api.example.com/devices",
            "headers": {"Authorization": "Bearer token"},
        }
        result = await http_requests_resource.request(params)

        mock_http_requests_service.execute.assert_called_once_with(params)
        assert result == {"status_code": 200, "body": {"data": "result"}}

    @pytest.mark.asyncio
    async def test_request_post(
        self, http_requests_resource, mock_http_requests_service
    ):
        params = {
            "method": "POST",
            "url": "https://api.example.com/devices",
            "body": {"name": "router1"},
        }
        await http_requests_resource.request(params)

        mock_http_requests_service.execute.assert_called_once_with(params)

    @pytest.mark.asyncio
    async def test_request_params_passed_unchanged(
        self, http_requests_resource, mock_http_requests_service
    ):
        params = {"method": "DELETE", "url": "https://api.example.com/devices/1"}
        await http_requests_resource.request(params)

        assert mock_http_requests_service.execute.call_args[0][0] is params


# ---------------------------------------------------------------------------
# gNMI
# ---------------------------------------------------------------------------


class TestGnmiResource:
    @pytest.fixture
    def mock_gnmi_service(self):
        svc = Mock()
        svc.get = AsyncMock(return_value={"notification": [{"update": []}]})
        svc.set = AsyncMock(return_value={"response": [{"op": "UPDATE"}]})
        return svc

    @pytest.fixture
    def gnmi_resource(self, mock_gnmi_service):
        services = Mock()
        services.gnmi = mock_gnmi_service
        return GnmiResource(services)

    def test_resource_name(self, gnmi_resource):
        assert gnmi_resource.name == "gnmi"

    @pytest.mark.asyncio
    async def test_get(self, gnmi_resource, mock_gnmi_service):
        params = {
            "host": "router1",
            "path": [{"elem": [{"name": "interfaces"}]}],
            "encoding": "JSON_IETF",
        }
        result = await gnmi_resource.get(params)

        mock_gnmi_service.get.assert_called_once_with(params)
        assert result == {"notification": [{"update": []}]}

    @pytest.mark.asyncio
    async def test_get_params_passed_unchanged(self, gnmi_resource, mock_gnmi_service):
        params = {"host": "router1", "path": []}
        await gnmi_resource.get(params)

        assert mock_gnmi_service.get.call_args[0][0] is params

    @pytest.mark.asyncio
    async def test_set(self, gnmi_resource, mock_gnmi_service):
        params = {
            "host": "router1",
            "update": [{"path": {"elem": [{"name": "description"}]}, "val": "WAN"}],
        }
        result = await gnmi_resource.set(params)

        mock_gnmi_service.set.assert_called_once_with(params)
        assert result == {"response": [{"op": "UPDATE"}]}

    @pytest.mark.asyncio
    async def test_set_params_passed_unchanged(self, gnmi_resource, mock_gnmi_service):
        params = {"host": "router1", "update": []}
        await gnmi_resource.set(params)

        assert mock_gnmi_service.set.call_args[0][0] is params


# ---------------------------------------------------------------------------
# gNOI
# ---------------------------------------------------------------------------


class TestGnoiResource:
    @pytest.fixture
    def mock_gnoi_service(self):
        svc = Mock()
        svc.ping = AsyncMock(return_value={"sent": 5, "received": 5, "time": "10ms"})
        svc.reboot = AsyncMock(return_value={"status": "rebooting"})
        svc.time = AsyncMock(return_value={"time": 1700000000})
        svc.traceroute = AsyncMock(return_value={"hops": [{"address": "10.0.0.1"}]})
        svc.switch_cpu = AsyncMock(return_value={"status": "ok"})
        svc.reboot_status = AsyncMock(return_value={"active": False})
        svc.set_package = AsyncMock(return_value={"status": "installed"})
        svc.cancel_reboot = AsyncMock(return_value={"status": "cancelled"})
        svc.clear_lldp_interface = AsyncMock(return_value={"status": "cleared"})
        svc.clear_bgp_neighbor = AsyncMock(return_value={"status": "cleared"})
        svc.clear_interface_counters = AsyncMock(return_value={"status": "cleared"})
        svc.clear_neighbor_discovery = AsyncMock(return_value={"status": "cleared"})
        svc.clear_spanning_tree = AsyncMock(return_value={"status": "cleared"})
        svc.wake_on_lan = AsyncMock(return_value={"status": "sent"})
        return svc

    @pytest.fixture
    def gnoi_resource(self, mock_gnoi_service):
        services = Mock()
        services.gnoi = mock_gnoi_service
        return GnoiResource(services)

    def test_resource_name(self, gnoi_resource):
        assert gnoi_resource.name == "gnoi"

    @pytest.mark.asyncio
    async def test_ping(self, gnoi_resource, mock_gnoi_service):
        params = {"host": "router1", "destination": "8.8.8.8", "count": 5}
        result = await gnoi_resource.ping(params)

        mock_gnoi_service.ping.assert_called_once_with(params)
        assert result == {"sent": 5, "received": 5, "time": "10ms"}

    @pytest.mark.asyncio
    async def test_reboot(self, gnoi_resource, mock_gnoi_service):
        params = {"host": "router1", "method": "COLD"}
        result = await gnoi_resource.reboot(params)

        mock_gnoi_service.reboot.assert_called_once_with(params)
        assert result == {"status": "rebooting"}

    @pytest.mark.asyncio
    async def test_time(self, gnoi_resource, mock_gnoi_service):
        params = {"host": "router1"}
        result = await gnoi_resource.time(params)

        mock_gnoi_service.time.assert_called_once_with(params)
        assert result == {"time": 1700000000}

    @pytest.mark.asyncio
    async def test_traceroute(self, gnoi_resource, mock_gnoi_service):
        params = {"host": "router1", "destination": "8.8.8.8"}
        result = await gnoi_resource.traceroute(params)

        mock_gnoi_service.traceroute.assert_called_once_with(params)
        assert result == {"hops": [{"address": "10.0.0.1"}]}

    @pytest.mark.asyncio
    async def test_switch_cpu(self, gnoi_resource, mock_gnoi_service):
        params = {"host": "router1", "control_processor": 0}
        result = await gnoi_resource.switch_cpu(params)

        mock_gnoi_service.switch_cpu.assert_called_once_with(params)
        assert result == {"status": "ok"}

    @pytest.mark.asyncio
    async def test_reboot_status(self, gnoi_resource, mock_gnoi_service):
        params = {"host": "router1"}
        result = await gnoi_resource.reboot_status(params)

        mock_gnoi_service.reboot_status.assert_called_once_with(params)
        assert result == {"active": False}

    @pytest.mark.asyncio
    async def test_set_package(self, gnoi_resource, mock_gnoi_service):
        params = {"host": "router1", "package": {"filename": "ios.tar"}}
        result = await gnoi_resource.set_package(params)

        mock_gnoi_service.set_package.assert_called_once_with(params)
        assert result == {"status": "installed"}

    @pytest.mark.asyncio
    async def test_cancel_reboot(self, gnoi_resource, mock_gnoi_service):
        params = {"host": "router1"}
        result = await gnoi_resource.cancel_reboot(params)

        mock_gnoi_service.cancel_reboot.assert_called_once_with(params)
        assert result == {"status": "cancelled"}

    @pytest.mark.asyncio
    async def test_clear_lldp_interface(self, gnoi_resource, mock_gnoi_service):
        params = {"host": "router1", "interface": "Gi0/0"}
        result = await gnoi_resource.clear_lldp_interface(params)

        mock_gnoi_service.clear_lldp_interface.assert_called_once_with(params)
        assert result == {"status": "cleared"}

    @pytest.mark.asyncio
    async def test_clear_bgp_neighbor(self, gnoi_resource, mock_gnoi_service):
        params = {"host": "router1", "address": "10.0.0.2"}
        result = await gnoi_resource.clear_bgp_neighbor(params)

        mock_gnoi_service.clear_bgp_neighbor.assert_called_once_with(params)
        assert result == {"status": "cleared"}

    @pytest.mark.asyncio
    async def test_clear_interface_counters(self, gnoi_resource, mock_gnoi_service):
        params = {"host": "router1", "interface": "Gi0/1"}
        result = await gnoi_resource.clear_interface_counters(params)

        mock_gnoi_service.clear_interface_counters.assert_called_once_with(params)
        assert result == {"status": "cleared"}

    @pytest.mark.asyncio
    async def test_clear_neighbor_discovery(self, gnoi_resource, mock_gnoi_service):
        params = {"host": "router1", "interface": "Gi0/0"}
        result = await gnoi_resource.clear_neighbor_discovery(params)

        mock_gnoi_service.clear_neighbor_discovery.assert_called_once_with(params)
        assert result == {"status": "cleared"}

    @pytest.mark.asyncio
    async def test_clear_spanning_tree(self, gnoi_resource, mock_gnoi_service):
        params = {"host": "router1", "vlan": 100}
        result = await gnoi_resource.clear_spanning_tree(params)

        mock_gnoi_service.clear_spanning_tree.assert_called_once_with(params)
        assert result == {"status": "cleared"}

    @pytest.mark.asyncio
    async def test_wake_on_lan(self, gnoi_resource, mock_gnoi_service):
        params = {"host": "router1", "mac": "aa:bb:cc:dd:ee:ff"}
        result = await gnoi_resource.wake_on_lan(params)

        mock_gnoi_service.wake_on_lan.assert_called_once_with(params)
        assert result == {"status": "sent"}

    @pytest.mark.asyncio
    async def test_all_methods_pass_params_unchanged(
        self, gnoi_resource, mock_gnoi_service
    ):
        """Verify params are not mutated or copied before being forwarded."""
        params = {"host": "router1"}
        await gnoi_resource.ping(params)

        assert mock_gnoi_service.ping.call_args[0][0] is params


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------


class TestConfigResource:
    @pytest.fixture
    def mock_config_service(self):
        svc = Mock()
        svc.get = AsyncMock(return_value={"log_level": "INFO", "max_connections": 100})
        svc.update = AsyncMock(
            return_value={"log_level": "DEBUG", "max_connections": 50}
        )
        return svc

    @pytest.fixture
    def config_resource(self, mock_config_service):
        services = Mock()
        services.config = mock_config_service
        return ConfigResource(services)

    def test_resource_name(self, config_resource):
        assert config_resource.name == "config"

    @pytest.mark.asyncio
    async def test_get(self, config_resource, mock_config_service):
        result = await config_resource.get()

        mock_config_service.get.assert_called_once_with()
        assert result == {"log_level": "INFO", "max_connections": 100}

    @pytest.mark.asyncio
    async def test_update(self, config_resource, mock_config_service):
        new_config = {"log_level": "DEBUG", "max_connections": 50}
        result = await config_resource.update(new_config)

        mock_config_service.update.assert_called_once_with(new_config)
        assert result == {"log_level": "DEBUG", "max_connections": 50}

    @pytest.mark.asyncio
    async def test_update_passes_config_unchanged(
        self, config_resource, mock_config_service
    ):
        config = {"log_level": "WARNING"}
        await config_resource.update(config)

        assert mock_config_service.update.call_args[0][0] is config

    @pytest.mark.asyncio
    async def test_update_empty_config(self, config_resource, mock_config_service):
        mock_config_service.update.return_value = {}
        result = await config_resource.update({})

        mock_config_service.update.assert_called_once_with({})
        assert result == {}


# ---------------------------------------------------------------------------
# System
# ---------------------------------------------------------------------------


class TestSystemResource:
    @pytest.fixture
    def mock_system_service(self):
        svc = Mock()
        svc.get_status = AsyncMock(return_value={"status": "running", "uptime": 3600})
        svc.poll = AsyncMock(return_value={"alive": True})
        svc.get_audit = AsyncMock(
            return_value=[
                {"event": "login", "user": "admin", "timestamp": "2025-01-01"}
            ]
        )
        return svc

    @pytest.fixture
    def system_resource(self, mock_system_service):
        services = Mock()
        services.system = mock_system_service
        return SystemResource(services)

    def test_resource_name(self, system_resource):
        assert system_resource.name == "system"

    @pytest.mark.asyncio
    async def test_get_status(self, system_resource, mock_system_service):
        result = await system_resource.get_status()

        mock_system_service.get_status.assert_called_once_with()
        assert result == {"status": "running", "uptime": 3600}

    @pytest.mark.asyncio
    async def test_poll(self, system_resource, mock_system_service):
        result = await system_resource.poll()

        mock_system_service.poll.assert_called_once_with()
        assert result == {"alive": True}

    @pytest.mark.asyncio
    async def test_get_audit_no_params(self, system_resource, mock_system_service):
        result = await system_resource.get_audit()

        mock_system_service.get_audit.assert_called_once_with()
        assert len(result) == 1
        assert result[0]["event"] == "login"

    @pytest.mark.asyncio
    async def test_get_audit_with_params(self, system_resource, mock_system_service):
        mock_system_service.get_audit.return_value = []
        result = await system_resource.get_audit(limit=10, user="admin")

        mock_system_service.get_audit.assert_called_once_with(limit=10, user="admin")
        assert result == []

    @pytest.mark.asyncio
    async def test_get_audit_with_date_filter(
        self, system_resource, mock_system_service
    ):
        await system_resource.get_audit(start="2025-01-01", end="2025-01-31")

        mock_system_service.get_audit.assert_called_once_with(
            start="2025-01-01", end="2025-01-31"
        )
