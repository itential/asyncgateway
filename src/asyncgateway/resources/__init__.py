# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from asyncgateway.services import Operation


class ResourceBase:
    name: str = ""

    def __init__(self, services):
        self.services = services


__all__ = ["ResourceBase", "Operation"]
