# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)


class AsyncGatewayError(Exception):
    """Base exception for all asyncgateway errors."""


class ValidationError(AsyncGatewayError):
    """Data validation, JSON/YAML parsing, and input errors."""
