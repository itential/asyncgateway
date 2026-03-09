# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from . import logging, metadata
from .client import Client as client

__version__ = metadata.version

__all__ = ("client", "logging")
