# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import pytest

from asyncgateway import exceptions


class TestAsyncGatewayError:
    def test_basic_creation(self):
        exc = exceptions.AsyncGatewayError("Test error")
        assert str(exc) == "Test error"

    def test_is_exception(self):
        exc = exceptions.AsyncGatewayError("Test error")
        assert isinstance(exc, Exception)

    def test_can_be_raised(self):
        with pytest.raises(exceptions.AsyncGatewayError, match="Test error"):
            raise exceptions.AsyncGatewayError("Test error")


class TestValidationError:
    def test_basic_creation(self):
        exc = exceptions.ValidationError("Invalid data")
        assert str(exc) == "Invalid data"

    def test_is_async_gateway_error(self):
        exc = exceptions.ValidationError("Invalid data")
        assert isinstance(exc, exceptions.AsyncGatewayError)

    def test_can_be_raised(self):
        with pytest.raises(exceptions.ValidationError, match="Invalid data"):
            raise exceptions.ValidationError("Invalid data")

    def test_caught_as_base(self):
        with pytest.raises(exceptions.AsyncGatewayError):
            raise exceptions.ValidationError("Invalid data")
