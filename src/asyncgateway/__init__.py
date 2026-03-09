# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Async Python client for the Itential Automation Gateway (IAG) 4.x REST API.

Exposes ``client`` (the ``Client`` class) and ``logging`` as top-level names.
Use ``async with asyncgateway.client(**kwargs) as c:`` to obtain a connected client.
"""

from . import logging, metadata
from .client import Client as client

__version__ = metadata.version

__all__ = ("client", "logging")
