# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Resource layer base class and re-exports for asyncgateway.

Resources compose service calls into atomic, idempotent operations.  Each
``Resource`` subclass receives the ``services`` namespace on construction and
implements declarative patterns such as ``ensure``/``absent`` for CRUD,
``run``/``dry_run`` for execution, and ``load``/``dump`` for bulk operations.
``Operation`` is re-exported here from ``services`` for convenience.
"""

from asyncgateway.services import Operation


class ResourceBase:
    name: str = ""

    def __init__(self, services):
        self.services = services


__all__ = ["ResourceBase", "Operation"]
