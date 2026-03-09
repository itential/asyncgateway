# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Package metadata for asyncgateway.

Reads ``name``, ``author``, and ``version`` from the installed package metadata
via ``importlib.metadata``.  Version is derived from git tags at build time.
"""

from importlib.metadata import version as _version

name: str = "asyncgateway"
author: str = "Itential"
version: str = _version(name)
