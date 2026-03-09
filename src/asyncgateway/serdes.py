# Copyright (c) 2025 Itential, Inc
# SPDX-License-Identifier: GPL-3.0-or-later
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

"""JSON, YAML, and TOML serialization utilities for asyncgateway.

Public API
----------
``loads(s, format_hint=None)``
    Parse a string to a Python object.  Format is auto-detected (JSON first,
    then YAML) unless a *format_hint* is provided.  TOML requires an explicit
    hint because it is syntactically ambiguous with other formats.

``dumps(o, format_type='json', **kwargs)``
    Serialize a Python object to a string.  *format_type* accepts ``'json'``,
    ``'yaml'`` / ``'yml'``, or ``'toml'``.

Low-level helpers follow the ``{format}_loads`` / ``{format}_dumps`` naming
convention and are exported for callers that know the format up front:
``json_loads``, ``json_dumps``, ``yaml_loads``, ``yaml_dumps``,
``toml_loads``, ``toml_dumps``.

Optional format support
-----------------------
All three formats are always importable, but YAML and TOML depend on optional
packages.  Calling a function whose dependency is absent raises
``ValidationError`` (not ``ImportError``), so callers do not need to guard
imports.

+----------------------------+--------------------------------------------------+
| Flag                       | Condition                                        |
+============================+==================================================+
| ``YAML_AVAILABLE``         | PyYAML is installed.                             |
+----------------------------+--------------------------------------------------+
| ``TOML_AVAILABLE``         | Python ≥ 3.11 (stdlib ``tomllib``) **or**        |
|                            | the ``tomli`` backport is installed.             |
+----------------------------+--------------------------------------------------+
| ``TOML_WRITE_AVAILABLE``   | ``tomli_w`` is installed.  Required for          |
|                            | ``toml_dumps`` / ``dumps(..., format_type='toml')``|
+----------------------------+--------------------------------------------------+

TOML constraints
----------------
TOML documents always have a dict at the top level; lists are not valid TOML
root values.  ``toml_loads`` therefore returns ``dict``, not ``dict | list``,
and ``toml_dumps`` raises ``ValidationError`` when passed a list.
"""

import json
import sys
import traceback

from . import exceptions, logging

try:
    import yaml

    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False

if sys.version_info >= (3, 11):
    try:
        import tomllib

        TOML_AVAILABLE = True
    except ImportError:  # pragma: no cover
        TOML_AVAILABLE = False
else:
    try:
        import tomli as tomllib  # type: ignore[no-redef]

        TOML_AVAILABLE = True
    except ImportError:
        TOML_AVAILABLE = False

try:
    import tomli_w

    TOML_WRITE_AVAILABLE = True
except ImportError:
    TOML_WRITE_AVAILABLE = False


def loads(s: str, format_hint: str | None = None) -> dict | list:
    """Parse a string into a Python object.

    When *format_hint* is omitted, JSON is tried first (fast path), then YAML
    if ``YAML_AVAILABLE`` is ``True``.  TOML is never tried automatically
    because syntactically valid TOML overlaps with both JSON and YAML; always
    pass ``format_hint='toml'`` for TOML input.

    Args:
        s: The string to parse.
        format_hint: Optional format specifier.  Accepted values:

            - ``'json'`` — parse as JSON.
            - ``'yaml'`` or ``'yml'`` — parse as YAML (requires PyYAML).
            - ``'toml'`` — parse as TOML (requires ``tomllib`` / ``tomli``).

            Case-insensitive.  If ``None`` or an empty string, auto-detection
            is used (JSON → YAML).

    Returns:
        A ``dict`` or ``list`` depending on the document structure.  TOML
        always returns a ``dict``.

    Raises:
        ValidationError: If the format hint is not recognised, if the required
            optional library is absent, or if parsing fails.
    """
    if format_hint:
        if format_hint.lower() == "json":
            return json_loads(s)
        elif format_hint.lower() in ("yaml", "yml"):
            return yaml_loads(s)
        elif format_hint.lower() == "toml":
            return toml_loads(s)
        else:
            raise exceptions.ValidationError(
                f"Unsupported format hint: {format_hint!r}. Use 'json', 'yaml', or 'toml'."
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
    """Serialize a Python object to a string.

    Args:
        o: The object to serialize.  Must be a ``dict`` when *format_type* is
            ``'toml'`` (TOML does not support top-level lists).
        format_type: Output format.  Accepted values:

            - ``'json'`` *(default)* — standard JSON.
            - ``'yaml'`` or ``'yml'`` — YAML (requires PyYAML).
            - ``'toml'`` — TOML (requires ``tomli_w``).

            Case-insensitive.
        **kwargs: Extra keyword arguments forwarded to the underlying
            serializer.  Supported options vary by format:

            - YAML: any keyword accepted by ``yaml.dump`` (e.g.
              ``default_flow_style``, ``indent``, ``width``).
            - TOML: any keyword accepted by ``tomli_w.dumps``.
            - JSON: no extra options are forwarded.

    Returns:
        A string representation in the requested format.

    Raises:
        ValidationError: If *format_type* is not recognised, if the required
            optional library is absent, if *o* is a list and *format_type* is
            ``'toml'``, or if serialization fails.
    """
    if format_type.lower() == "json":
        return json_dumps(o)
    elif format_type.lower() in ("yaml", "yml"):
        return yaml_dumps(o, **kwargs)
    elif format_type.lower() == "toml":
        return toml_dumps(o, **kwargs)
    else:
        raise exceptions.ValidationError(
            f"Unsupported format type: {format_type!r}. Use 'json', 'yaml', or 'toml'."
        )


def json_loads(s: str) -> dict | list:
    """Parse a JSON string into a ``dict`` or ``list``.

    Args:
        s: A valid JSON string.

    Returns:
        A ``dict`` or ``list`` depending on the JSON document root.

    Raises:
        ValidationError: If *s* is not valid JSON.
    """
    try:
        return json.loads(s)
    except (json.JSONDecodeError, Exception) as exc:
        logging.error(traceback.format_exc())
        raise exceptions.ValidationError(f"Failed to parse JSON: {exc}") from exc


def json_dumps(o: dict | list) -> str:
    """Serialize a ``dict`` or ``list`` to a JSON string.

    Args:
        o: The object to serialize.

    Returns:
        A compact JSON string (no extra whitespace).

    Raises:
        ValidationError: If *o* contains types that are not JSON-serializable.
    """
    try:
        return json.dumps(o)
    except (TypeError, ValueError, Exception) as exc:
        logging.error(traceback.format_exc())
        raise exceptions.ValidationError(
            f"Failed to serialize object to JSON: {exc}"
        ) from exc


def yaml_loads(s: str) -> dict | list:
    """Parse a YAML string into a ``dict`` or ``list``.

    Uses ``yaml.safe_load``; arbitrary Python objects are not deserialised.

    Args:
        s: A valid YAML string.

    Returns:
        A ``dict`` or ``list`` depending on the YAML document root.

    Raises:
        ValidationError: If PyYAML is not installed (``YAML_AVAILABLE`` is
            ``False``) or if *s* is not valid YAML.
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
    """Serialize a ``dict`` or ``list`` to a YAML string.

    Default formatting options (``default_flow_style=False``, ``indent=2``,
    ``width=80``, ``allow_unicode=True``) can be overridden via *kwargs*.

    Args:
        o: The object to serialize.
        **kwargs: Options forwarded to ``yaml.dump``.  Any key accepted by
            ``yaml.dump`` is valid (e.g. ``sort_keys=False``).

    Returns:
        A YAML string.

    Raises:
        ValidationError: If PyYAML is not installed (``YAML_AVAILABLE`` is
            ``False``) or if *o* contains types that cannot be represented in
            YAML.
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


def toml_loads(s: str) -> dict:
    """Parse a TOML string into a ``dict``.

    TOML documents always have a mapping at the root; this function therefore
    returns ``dict``, not ``dict | list``.

    Args:
        s: A valid TOML string.

    Returns:
        A ``dict`` representing the TOML document.

    Raises:
        ValidationError: If TOML support is not available (``TOML_AVAILABLE``
            is ``False``; on Python 3.10 install ``tomli``) or if *s* is not
            valid TOML.
    """
    if not TOML_AVAILABLE:
        raise exceptions.ValidationError(
            "TOML support not available. "
            "On Python 3.10, install 'tomli' to enable TOML parsing."
        )
    try:
        return tomllib.loads(s)
    except Exception as exc:
        logging.error(traceback.format_exc())
        raise exceptions.ValidationError(f"Failed to parse TOML: {exc}") from exc


def toml_dumps(o: dict | list, **kwargs) -> str:
    """Serialize a ``dict`` to a TOML string.

    TOML does not support lists at the document root; passing a ``list`` raises
    ``ValidationError`` immediately.  Requires ``tomli_w`` to be installed
    (``TOML_WRITE_AVAILABLE`` must be ``True``).

    Args:
        o: The object to serialize.  Must be a ``dict``.
        **kwargs: Options forwarded to ``tomli_w.dumps``.

    Returns:
        A TOML-formatted string.

    Raises:
        ValidationError: If ``tomli_w`` is not installed
            (``TOML_WRITE_AVAILABLE`` is ``False``), if *o* is not a ``dict``,
            or if *o* contains types that are not representable in TOML (e.g.
            mixed-type arrays, ``None`` values).
    """
    if not TOML_WRITE_AVAILABLE:
        raise exceptions.ValidationError(
            "TOML write support not available. Install 'tomli-w' to enable TOML serialization."
        )
    if not isinstance(o, dict):
        raise exceptions.ValidationError(
            "TOML serialization requires a dict at the top level, not a list."
        )
    try:
        return tomli_w.dumps(o, **kwargs)
    except Exception as exc:
        logging.error(traceback.format_exc())
        raise exceptions.ValidationError(
            f"Failed to serialize object to TOML: {exc}"
        ) from exc
