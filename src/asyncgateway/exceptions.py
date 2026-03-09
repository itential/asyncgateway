# Copyright (c) 2025 Itential, Inc
# SPDX-License-Identifier: GPL-3.0-or-later
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Exception hierarchy for asyncgateway.

All exceptions inherit from ``AsyncGatewayError``.  ``ValidationError`` covers
data-validation, JSON/YAML-parsing, and input errors.
"""


class AsyncGatewayError(Exception):
    """Base exception for all asyncgateway errors."""


class ValidationError(AsyncGatewayError):
    """Data validation, JSON/YAML parsing, and input errors."""
