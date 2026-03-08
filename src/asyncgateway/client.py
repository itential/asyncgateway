# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import importlib
import importlib.util
import os
from pathlib import Path
from typing import Any, Dict, List

import ipsdk

from . import serdes
from .exceptions import AsyncGatewayError, ValidationError
from .services import Operation


class _Namespace:
    """Attribute container for dynamically discovered services or resources."""

    def __repr__(self) -> str:
        attrs = [a for a in dir(self) if not a.startswith("_")]
        return f"<Namespace [{', '.join(attrs)}]>"


class Client:
    def __init__(self, **kwargs):
        self.services = _Namespace()
        self.resources = _Namespace()
        self._init_services(**kwargs)
        self._init_resources()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        pass

    def _init_services(self, **kwargs):
        path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "services")
        ipsdk_client = ipsdk.gateway_factory(want_async=True, **kwargs)
        for name in self._discover_modules(path):
            module = self._load_module(name, os.path.join(path, f"{name}.py"))
            svc = getattr(module, "Service", None)
            if svc is not None:
                instance = svc(ipsdk_client)
                setattr(self.services, instance.name, instance)

    def _init_resources(self):
        path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "resources")
        for name in self._discover_modules(path):
            module = self._load_module(name, os.path.join(path, f"{name}.py"))
            res = getattr(module, "Resource", None)
            if res is not None:
                instance = res(self.services)
                setattr(self.resources, instance.name, instance)

    def _discover_modules(self, path: str) -> List[str]:
        return [
            f[:-3]
            for f in os.listdir(path)
            if f.endswith(".py") and not f.startswith("_")
        ]

    def _load_module(self, name: str, filepath: str):
        spec = importlib.util.spec_from_file_location(name, filepath)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def _get_available_services(self) -> List[str]:
        services = []
        for attr_name in dir(self.services):
            if attr_name.startswith("_"):
                continue
            attr = getattr(self.services, attr_name)
            if hasattr(attr, "name") and callable(getattr(attr, "get", None)):
                services.append(attr.name)
        return services

    async def load(self, path: str, op: str = Operation.MERGE) -> Dict[str, Any]:
        valid_operations = {Operation.MERGE, Operation.REPLACE, Operation.OVERWRITE}
        if op not in valid_operations:
            raise ValidationError(
                f"Invalid operation '{op}'. Must be one of: {valid_operations}"
            )

        load_path = Path(path)
        if not load_path.exists():
            raise FileNotFoundError(f"Load path does not exist: {path}")
        if not load_path.is_dir():
            raise ValidationError(f"Load path must be a directory: {path}")

        results: Dict[str, Any] = {
            "operation": op,
            "services_processed": 0,
            "total_resources_processed": 0,
            "total_resources_created": 0,
            "total_resources_updated": 0,
            "total_resources_deleted": 0,
            "service_results": {},
            "errors": [],
        }

        try:
            available_services = self._get_available_services()
            for service_name in available_services:
                service_dir = load_path / service_name
                if not service_dir.exists() or not service_dir.is_dir():
                    continue
                try:
                    service_data = await self._load_service_data(service_dir, service_name)
                    if not service_data:
                        continue
                    service = getattr(self.services, service_name)
                    if hasattr(service, "load"):
                        service_results = await service.load(service_data, op)
                        results["services_processed"] += 1
                        results["service_results"][service_name] = service_results
                        if isinstance(service_results, dict):
                            for key, value in service_results.items():
                                if key.endswith("_processed") and isinstance(value, int):
                                    results["total_resources_processed"] += value
                                elif key.endswith("_created") and isinstance(value, int):
                                    results["total_resources_created"] += value
                                elif key.endswith("_updated") and isinstance(value, int):
                                    results["total_resources_updated"] += value
                                elif key.endswith("_deleted") and isinstance(value, int):
                                    results["total_resources_deleted"] += value
                            if service_results.get("errors"):
                                results["errors"].extend(
                                    [f"{service_name}: {e}" for e in service_results["errors"]]
                                )
                    else:
                        results["errors"].append(
                            f"Service {service_name} does not support load operations"
                        )
                except Exception as e:
                    results["errors"].append(
                        f"Failed to process {service_name} service: {str(e)}"
                    )
            return results
        except Exception as e:
            raise AsyncGatewayError(f"Load from path failed: {str(e)}") from e

    async def _load_service_data(self, service_dir: Path, service_name: str) -> List[Dict[str, Any]]:
        all_data = []
        supported_extensions = {".json"}
        if serdes.YAML_AVAILABLE:
            supported_extensions.update({".yaml", ".yml"})
        try:
            for file_path in service_dir.rglob("*"):
                if file_path.is_file() and file_path.suffix.lower() in supported_extensions:
                    try:
                        content = file_path.read_text(encoding="utf-8").strip()
                        if not content:
                            continue
                        if file_path.suffix.lower() == ".json":
                            data = serdes.json_loads(content)
                        elif file_path.suffix.lower() in {".yaml", ".yml"}:
                            data = serdes.yaml_loads(content)
                        else:
                            continue
                        if isinstance(data, list):
                            all_data.extend(data)
                        elif isinstance(data, dict):
                            all_data.append(data)
                        else:
                            raise ValidationError(
                                f"Invalid data format in {file_path}: expected dict or list"
                            )
                    except Exception as e:
                        raise AsyncGatewayError(f"Failed to load {file_path}: {str(e)}") from e
        except Exception as e:
            raise AsyncGatewayError(f"Failed to scan {service_dir}: {str(e)}") from e
        return all_data
