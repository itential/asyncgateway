# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import json
import traceback

from . import exceptions, logger

try:
    import yaml

    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False


def loads(s: str, format_hint: str | None = None) -> dict | list:
    """Automatically detect format and load from string

    This function replaces the previous JSON-only loads() function and now supports
    both JSON and YAML formats with automatic detection.

    Args:
        s (str): The string to parse (JSON or YAML)
        format_hint (str, optional): Format hint ('json' or 'yaml')
            If provided, uses that format directly

    Returns:
        A dict or list object

    Raises:
        ValidationError: If format cannot be determined or parsing fails
        JSONError: If parsing fails

    Note:
        For backward compatibility with existing JSON-only usage:
        - When called with just a string parameter, tries JSON first, then YAML
        - Maintains the same error types as the original JSON-only function
    """
    if format_hint:
        if format_hint.lower() == "json":
            return json_loads(s)
        elif format_hint.lower() in ("yaml", "yml"):
            return yaml_loads(s)
        else:
            raise exceptions.ValidationError(
                f"Unsupported format hint: {format_hint}. Use 'json', 'yaml', or 'yml'",
                details={"format_hint": format_hint},
            )

    # Try JSON first (faster and more common, maintains backward compatibility)
    try:
        return json_loads(s)
    except exceptions.JSONError:
        # If JSON fails, try YAML
        if YAML_AVAILABLE:
            try:
                return yaml_loads(s)
            except exceptions.JSONError:
                pass

        # If both fail, provide helpful error
        available_formats = ["JSON"]
        if YAML_AVAILABLE:
            available_formats.append("YAML")

        raise exceptions.ValidationError(
            f"Failed to parse string as {' or '.join(available_formats)}. "
            f"Check format and syntax.",
            details={
                "available_formats": available_formats,
                "input_preview": str(s)[:200] if s else "None",
            },
        ) from None


def dumps(o: dict | list, format_type: str = "json", **kwargs) -> str:
    """Serialize object to string in specified format

    This function replaces the previous JSON-only dumps() function and now supports
    both JSON and YAML formats.

    Args:
        o (list, dict): The object to serialize
        format_type (str): Output format ('json' or 'yaml'), defaults to 'json'
        **kwargs: Additional options passed to the serializer

    Returns:
        A string representation in the specified format

    Raises:
        ValidationError: If format_type is unsupported
        JSONError: If serialization fails

    Note:
        For backward compatibility with existing JSON-only usage:
        - Defaults to JSON format when no format_type is specified
        - Maintains the same behavior as the original JSON-only function
    """
    if format_type.lower() == "json":
        return json_dumps(o)
    elif format_type.lower() in ("yaml", "yml"):
        return yaml_dumps(o, **kwargs)
    else:
        raise exceptions.ValidationError(
            f"Unsupported format type: {format_type}. Use 'json' or 'yaml'",
            details={"format_type": format_type},
        )


def json_loads(s: str) -> dict | list:
    """Convert a JSON formatted string to a dict or list object

    Args:
        s (str): The JSON object represented as a string

    Returns:
        A dict or list object

    Raises:
        JSONError: If JSON parsing fails
    """
    try:
        return json.loads(s)
    except json.JSONDecodeError as exc:
        logger.error(traceback.format_exc())
        input_data = str(s)[:200] if s is not None else "None"
        raise exceptions.JSONError(
            f"Failed to parse JSON: {str(exc)}",
            details={"input_data": input_data, "json_error": str(exc)},
        ) from exc
    except Exception as exc:
        logger.error(traceback.format_exc())
        input_data = str(s)[:200] if s is not None else "None"
        raise exceptions.JSONError(
            f"Unexpected error parsing JSON: {str(exc)}",
            details={"input_data": input_data, "original_error": str(exc)},
        ) from exc


def json_dumps(o: dict | list) -> str:
    """Convert a dict or list to a JSON string

    Args:
        o (list, dict): The list or dict object to dump to a string

    Returns:
        A JSON string representation

    Raises:
        JSONError: If JSON serialization fails
    """
    try:
        return json.dumps(o)
    except (TypeError, ValueError) as exc:
        logger.error(traceback.format_exc())
        raise exceptions.JSONError(
            f"Failed to serialize object to JSON: {str(exc)}",
            details={"object_type": str(type(o)), "json_error": str(exc)},
        ) from exc
    except Exception as exc:
        logger.error(traceback.format_exc())
        raise exceptions.JSONError(
            f"Unexpected error serializing JSON: {str(exc)}",
            details={"object_type": str(type(o)), "original_error": str(exc)},
        ) from exc


def yaml_loads(s: str) -> dict | list:
    """Convert a YAML formatted string to a dict or list object

    Args:
        s (str): The YAML object represented as a string

    Returns:
        A dict or list object

    Raises:
        ValidationError: If YAML support is not available
        JSONError: If YAML parsing fails (for consistency with JSON errors)
    """
    if not YAML_AVAILABLE:
        raise exceptions.ValidationError(
            "YAML support not available. Install PyYAML to use YAML functionality.",
            details={"feature": "yaml_loads", "required_package": "PyYAML"},
        )

    try:
        return yaml.safe_load(s)
    except yaml.YAMLError as exc:
        logger.error(traceback.format_exc())
        input_data = str(s)[:200] if s is not None else "None"
        raise exceptions.JSONError(
            f"Failed to parse YAML: {str(exc)}",
            details={"input_data": input_data, "yaml_error": str(exc)},
        ) from exc
    except Exception as exc:
        logger.error(traceback.format_exc())
        input_data = str(s)[:200] if s is not None else "None"
        raise exceptions.JSONError(
            f"Unexpected error parsing YAML: {str(exc)}",
            details={"input_data": input_data, "original_error": str(exc)},
        ) from exc


def yaml_dumps(o: dict | list, **kwargs) -> str:
    """Convert a dict or list to a YAML string

    Args:
        o (list, dict): The list or dict object to dump to a string
        **kwargs: Additional keyword arguments passed to yaml.dump()

    Returns:
        A YAML string representation

    Raises:
        ValidationError: If YAML support is not available
        JSONError: If YAML serialization fails (for consistency with JSON errors)
    """
    if not YAML_AVAILABLE:
        raise exceptions.ValidationError(
            "YAML support not available. Install PyYAML to use YAML functionality.",
            details={"feature": "yaml_dumps", "required_package": "PyYAML"},
        )

    # Default YAML dump options for better formatting
    yaml_options = {
        "default_flow_style": False,
        "indent": 2,
        "width": 80,
        "allow_unicode": True,
        **kwargs,
    }

    try:
        return yaml.dump(o, **yaml_options)
    except yaml.YAMLError as exc:
        logger.error(traceback.format_exc())
        raise exceptions.JSONError(
            f"Failed to serialize object to YAML: {str(exc)}",
            details={"object_type": str(type(o)), "yaml_error": str(exc)},
        ) from exc
    except Exception as exc:
        logger.error(traceback.format_exc())
        raise exceptions.JSONError(
            f"Unexpected error serializing YAML: {str(exc)}",
            details={"object_type": str(type(o)), "original_error": str(exc)},
        ) from exc
