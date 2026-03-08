# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from typing import Any, Dict, Optional, Union

import httpx


class AsyncGatewayError(Exception):
    """Base exception for all asyncgateway errors."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def __str__(self) -> str:
        if self.details:
            return f"{self.message}. Details: {self.details}"
        return self.message


class ConnectionError(AsyncGatewayError):
    """Network connection, communication, and timeout errors."""

    def __init__(
        self,
        message: str,
        timeout: Optional[float] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, details)
        if timeout:
            self.details["timeout"] = timeout


class AuthenticationError(AsyncGatewayError):
    """Authentication and authorization failures."""

    pass


class ValidationError(AsyncGatewayError):
    """Data validation, JSON parsing, and input errors."""

    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, details)
        if field:
            self.details["field"] = field


# Alias for backward compatibility
JSONError = ValidationError
HTTPError = AsyncGatewayError
TimeoutError = ConnectionError
ConfigurationError = AsyncGatewayError
AdapterError = AsyncGatewayError
CacheError = AsyncGatewayError


def classify_httpx_error(
    exc: Exception, request_url: Optional[str] = None
) -> AsyncGatewayError:
    """Convert httpx exceptions to appropriate asyncgateway exceptions."""
    details = {"original_error": str(exc)}
    if request_url:
        details["request_url"] = request_url

    if isinstance(
        exc, (httpx.TimeoutException, httpx.ConnectError, httpx.RequestError)
    ):
        return ConnectionError(f"Connection failed: {str(exc)}", details=details)

    elif isinstance(exc, httpx.HTTPStatusError):
        status_code = exc.response.status_code
        details["status_code"] = status_code  # type: ignore[assignment]

        try:
            details["response_body"] = exc.response.text[:500]
        except Exception:  # nosec B110
            # Response body may not be accessible or readable
            # Silently skip adding response_body to details
            pass

        if status_code in (401, 403):
            return AuthenticationError(
                f"HTTP {status_code}: Authentication failed", details=details
            )
        else:
            return AsyncGatewayError(f"HTTP {status_code} error", details=details)

    else:
        return AsyncGatewayError(f"Unexpected error: {str(exc)}", details=details)


def classify_http_status(
    status_code: int,
    response: Optional[httpx.Response] = None,
    request_url: Optional[str] = None,
) -> Union[AsyncGatewayError, AuthenticationError]:
    """Create appropriate exception for HTTP status codes."""
    details = {}
    if request_url:
        details["request_url"] = request_url
    if response:
        try:
            details["response_body"] = response.text[:200]
        except Exception:  # nosec B110
            # Response body may not be accessible or readable
            # Silently skip adding response_body to details
            pass

    message = f"HTTP {status_code} error"
    details["status_code"] = status_code  # type: ignore[assignment]

    if status_code in (401, 403):
        return AuthenticationError(message, details=details)

    return AsyncGatewayError(message, details=details)
