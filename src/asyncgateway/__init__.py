# Copyright (c) 2025 Itential, Inc
# SPDX-License-Identifier: GPL-3.0-or-later
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from . import logging, metadata
from .client import Client as client

__version__ = metadata.version

__all__ = ("client", "logging")
