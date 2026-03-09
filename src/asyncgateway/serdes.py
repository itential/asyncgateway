# Copyright (c) 2025 Itential, Inc
# SPDX-License-Identifier: GPL-3.0-or-later
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import json
import traceback

from . import exceptions, logging

try:
    import yaml

    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False


def loads(s: str, format_hint: str | None = None) -> dict | list:
    """Automatically detect format and load from string.

    Args:
        s: The string to parse (JSON or YAML).
        format_hint: Optional format hint ('json' or 'yaml'). If omitted, JSON
            is tried first, then YAML.

    Returns:
        A dict or list object.

    Raises:
        ValidationError: If the format hint is unsupported, or if parsing fails.
    """
    if format_hint:
        if format_hint.lower() == "json":
            return json_loads(s)
        elif format_hint.lower() in ("yaml", "yml"):
            return yaml_loads(s)
        else:
            raise exceptions.ValidationError(
                f"Unsupported format hint: {format_hint!r}. Use 'json' or 'yaml'."
            )

    # Try JSON first (faster and more common)
    try:
        return json_loads(s)
    except exceptions.ValidationError:
        if YAML_AVAILABLE:
            try:
                return yaml_loads(s)
            except exceptions.ValidationError:
                pass

    available = "JSON or YAML" if YAML_AVAILABLE else "JSON"
    raise exceptions.ValidationError(f"Failed to parse string as {available}.")


def dumps(o: dict | list, format_type: str = "json", **kwargs) -> str:
    """Serialize object to string in the specified format.

    Args:
        o: The object to serialize.
        format_type: Output format ('json' or 'yaml'), defaults to 'json'.
        **kwargs: Additional options passed to the serializer.

    Returns:
        A string representation in the specified format.

    Raises:
        ValidationError: If format_type is unsupported or serialization fails.
    """
    if format_type.lower() == "json":
        return json_dumps(o)
    elif format_type.lower() in ("yaml", "yml"):
        return yaml_dumps(o, **kwargs)
    else:
        raise exceptions.ValidationError(
            f"Unsupported format type: {format_type!r}. Use 'json' or 'yaml'."
        )


def json_loads(s: str) -> dict | list:
    """Parse a JSON string into a dict or list.

    Raises:
        ValidationError: If JSON parsing fails.
    """
    try:
        return json.loads(s)
    except (json.JSONDecodeError, Exception) as exc:
        logging.error(traceback.format_exc())
        raise exceptions.ValidationError(f"Failed to parse JSON: {exc}") from exc


def json_dumps(o: dict | list) -> str:
    """Serialize a dict or list to a JSON string.

    Raises:
        ValidationError: If JSON serialization fails.
    """
    try:
        return json.dumps(o)
    except (TypeError, ValueError, Exception) as exc:
        logging.error(traceback.format_exc())
        raise exceptions.ValidationError(
            f"Failed to serialize object to JSON: {exc}"
        ) from exc


def yaml_loads(s: str) -> dict | list:
    """Parse a YAML string into a dict or list.

    Raises:
        ValidationError: If YAML support is not available or parsing fails.
    """
    if not YAML_AVAILABLE:
        raise exceptions.ValidationError(
            "YAML support not available. Install PyYAML to enable YAML parsing."
        )
    try:
        return yaml.safe_load(s)
    except (yaml.YAMLError, Exception) as exc:
        logging.error(traceback.format_exc())
        raise exceptions.ValidationError(f"Failed to parse YAML: {exc}") from exc


def yaml_dumps(o: dict | list, **kwargs) -> str:
    """Serialize a dict or list to a YAML string.

    Raises:
        ValidationError: If YAML support is not available or serialization fails.
    """
    if not YAML_AVAILABLE:
        raise exceptions.ValidationError(
            "YAML support not available. Install PyYAML to enable YAML serialization."
        )
    yaml_options = {
        "default_flow_style": False,
        "indent": 2,
        "width": 80,
        "allow_unicode": True,
        **kwargs,
    }
    try:
        return yaml.dump(o, **yaml_options)
    except (yaml.YAMLError, Exception) as exc:
        logging.error(traceback.format_exc())
        raise exceptions.ValidationError(
            f"Failed to serialize object to YAML: {exc}"
        ) from exc
