# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from unittest.mock import Mock

import httpx

from asyncgateway import exceptions


class TestAsyncGatewayError:
    def test_basic_creation(self):
        exc = exceptions.AsyncGatewayError("Test error")

        assert exc.message == "Test error"
        assert exc.details == {}
        assert str(exc) == "Test error"

    def test_creation_with_details(self):
        details = {"status_code": 404, "url": "https://api.example.com"}
        exc = exceptions.AsyncGatewayError("API error", details)

        assert exc.message == "API error"
        assert exc.details == details
        assert "Details:" in str(exc)
        assert "404" in str(exc)

    def test_str_without_details(self):
        exc = exceptions.AsyncGatewayError("Simple error")
        assert str(exc) == "Simple error"

    def test_str_with_details(self):
        details = {"key": "value"}
        exc = exceptions.AsyncGatewayError("Error with details", details)
        expected = "Error with details. Details: {'key': 'value'}"
        assert str(exc) == expected


class TestConnectionError:
    def test_basic_creation(self):
        exc = exceptions.ConnectionError("Connection failed")

        assert exc.message == "Connection failed"
        assert exc.details == {}
        assert isinstance(exc, exceptions.AsyncGatewayError)

    def test_creation_with_timeout(self):
        exc = exceptions.ConnectionError("Timeout occurred", timeout=30.0)

        assert exc.message == "Timeout occurred"
        assert exc.details["timeout"] == 30.0

    def test_creation_with_timeout_and_details(self):
        details = {"host": "example.com"}
        exc = exceptions.ConnectionError(
            "Connection failed", timeout=15.5, details=details
        )

        assert exc.details["timeout"] == 15.5
        assert exc.details["host"] == "example.com"


class TestAuthenticationError:
    def test_basic_creation(self):
        exc = exceptions.AuthenticationError("Auth failed")

        assert exc.message == "Auth failed"
        assert isinstance(exc, exceptions.AsyncGatewayError)


class TestValidationError:
    def test_basic_creation(self):
        exc = exceptions.ValidationError("Invalid data")

        assert exc.message == "Invalid data"
        assert exc.details == {}
        assert isinstance(exc, exceptions.AsyncGatewayError)

    def test_creation_with_field(self):
        exc = exceptions.ValidationError("Invalid email", field="email")

        assert exc.message == "Invalid email"
        assert exc.details["field"] == "email"

    def test_creation_with_field_and_details(self):
        details = {"value": "invalid-email"}
        exc = exceptions.ValidationError(
            "Invalid format", field="email", details=details
        )

        assert exc.details["field"] == "email"
        assert exc.details["value"] == "invalid-email"


class TestExceptionAliases:
    def test_json_error_alias(self):
        assert exceptions.JSONError is exceptions.ValidationError

    def test_http_error_alias(self):
        assert exceptions.HTTPError is exceptions.AsyncGatewayError

    def test_timeout_error_alias(self):
        assert exceptions.TimeoutError is exceptions.ConnectionError

    def test_configuration_error_alias(self):
        assert exceptions.ConfigurationError is exceptions.AsyncGatewayError

    def test_adapter_error_alias(self):
        assert exceptions.AdapterError is exceptions.AsyncGatewayError

    def test_cache_error_alias(self):
        assert exceptions.CacheError is exceptions.AsyncGatewayError


class TestClassifyHttpxError:
    def test_timeout_exception(self):
        httpx_exc = httpx.TimeoutException("Request timed out")
        result = exceptions.classify_httpx_error(httpx_exc, "https://api.example.com")

        assert isinstance(result, exceptions.ConnectionError)
        assert "Connection failed" in result.message
        assert result.details["original_error"] == str(httpx_exc)
        assert result.details["request_url"] == "https://api.example.com"

    def test_connect_error(self):
        httpx_exc = httpx.ConnectError("Failed to connect")
        result = exceptions.classify_httpx_error(httpx_exc)

        assert isinstance(result, exceptions.ConnectionError)
        assert "Connection failed" in result.message
        assert result.details["original_error"] == str(httpx_exc)

    def test_request_error(self):
        httpx_exc = httpx.RequestError("Request failed")
        result = exceptions.classify_httpx_error(httpx_exc)

        assert isinstance(result, exceptions.ConnectionError)
        assert "Connection failed" in result.message

    def test_http_status_error_401(self):
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"

        httpx_exc = httpx.HTTPStatusError(
            "401 Unauthorized", request=Mock(), response=mock_response
        )
        result = exceptions.classify_httpx_error(httpx_exc)

        assert isinstance(result, exceptions.AuthenticationError)
        assert "HTTP 401" in result.message
        assert result.details["status_code"] == 401
        assert result.details["response_body"] == "Unauthorized"

    def test_http_status_error_403(self):
        mock_response = Mock()
        mock_response.status_code = 403
        mock_response.text = "Forbidden"

        httpx_exc = httpx.HTTPStatusError(
            "403 Forbidden", request=Mock(), response=mock_response
        )
        result = exceptions.classify_httpx_error(httpx_exc)

        assert isinstance(result, exceptions.AuthenticationError)
        assert "HTTP 403" in result.message
        assert result.details["status_code"] == 403

    def test_http_status_error_500(self):
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"

        httpx_exc = httpx.HTTPStatusError(
            "500 Server Error", request=Mock(), response=mock_response
        )
        result = exceptions.classify_httpx_error(httpx_exc)

        assert isinstance(result, exceptions.AsyncGatewayError)
        assert "HTTP 500" in result.message
        assert result.details["status_code"] == 500

    def test_http_status_error_response_text_exception(self):
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.text.side_effect = Exception("Can't read response")

        httpx_exc = httpx.HTTPStatusError(
            "404 Not Found", request=Mock(), response=mock_response
        )
        result = exceptions.classify_httpx_error(httpx_exc)

        assert isinstance(result, exceptions.AsyncGatewayError)
        assert "response_body" not in result.details

    def test_unknown_exception(self):
        unknown_exc = ValueError("Some random error")
        result = exceptions.classify_httpx_error(unknown_exc)

        assert isinstance(result, exceptions.AsyncGatewayError)
        assert "Unexpected error" in result.message
        assert result.details["original_error"] == str(unknown_exc)


class TestClassifyHttpStatus:
    def test_status_401(self):
        result = exceptions.classify_http_status(
            401, request_url="https://api.example.com"
        )

        assert isinstance(result, exceptions.AuthenticationError)
        assert "HTTP 401" in result.message
        assert result.details["status_code"] == 401
        assert result.details["request_url"] == "https://api.example.com"

    def test_status_403(self):
        result = exceptions.classify_http_status(403)

        assert isinstance(result, exceptions.AuthenticationError)
        assert "HTTP 403" in result.message
        assert result.details["status_code"] == 403

    def test_status_404(self):
        result = exceptions.classify_http_status(404)

        assert isinstance(result, exceptions.AsyncGatewayError)
        assert "HTTP 404" in result.message
        assert result.details["status_code"] == 404

    def test_status_500(self):
        result = exceptions.classify_http_status(500)

        assert isinstance(result, exceptions.AsyncGatewayError)
        assert "HTTP 500" in result.message
        assert result.details["status_code"] == 500

    def test_with_response_object(self):
        mock_response = Mock()
        mock_response.text = "Not Found"

        result = exceptions.classify_http_status(404, response=mock_response)

        assert result.details["status_code"] == 404
        assert result.details["response_body"] == "Not Found"

    def test_with_response_object_text_exception(self):
        mock_response = Mock()
        mock_response.text.side_effect = Exception("Can't read response")

        result = exceptions.classify_http_status(500, response=mock_response)

        assert "response_body" not in result.details
        assert result.details["status_code"] == 500

    def test_response_body_truncation(self):
        mock_response = Mock()
        mock_response.text = "x" * 300  # Long response

        result = exceptions.classify_http_status(500, response=mock_response)

        assert len(result.details["response_body"]) == 200
