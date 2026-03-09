# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import re

import pytest

from asyncgateway import heuristics


class TestScanner:
    def setup_method(self):
        heuristics.Scanner.reset_singleton()

    def test_singleton_same_instance(self):
        s1 = heuristics.Scanner()
        s2 = heuristics.Scanner()
        assert s1 is s2

    def test_default_patterns_loaded(self):
        scanner = heuristics.Scanner()
        patterns = scanner.list_patterns()
        for name in ("api_key", "bearer_token", "jwt_token", "password", "secret"):
            assert name in patterns

    def test_custom_patterns_on_first_init(self):
        scanner = heuristics.Scanner({"ssn": r"\d{3}-\d{2}-\d{4}"})
        assert "ssn" in scanner.list_patterns()

    def test_custom_patterns_ignored_after_init(self):
        # Singleton: second call with different patterns is ignored
        heuristics.Scanner()
        scanner = heuristics.Scanner({"ignored": r"IGNORED_\d+"})
        assert "ignored" not in scanner.list_patterns()

    def test_add_pattern(self):
        scanner = heuristics.Scanner()
        scanner.add_pattern("test_key", r"TEST_[a-z]+")
        assert "test_key" in scanner.list_patterns()

    def test_add_pattern_with_custom_redaction(self):
        scanner = heuristics.Scanner()
        scanner.add_pattern(
            "custom", r"CUSTOM_\w+", redaction_func=lambda _: "[CUSTOM]"
        )
        result = scanner.scan_and_redact("CUSTOM_value here")
        assert "[CUSTOM]" in result

    def test_add_invalid_pattern_raises(self):
        scanner = heuristics.Scanner()
        with pytest.raises(re.error):
            scanner.add_pattern("bad", r"[invalid")

    def test_remove_existing_pattern(self):
        scanner = heuristics.Scanner()
        scanner.add_pattern("temp", r"TEMP_\d+")
        result = scanner.remove_pattern("temp")
        assert result is True
        assert "temp" not in scanner.list_patterns()

    def test_remove_nonexistent_pattern(self):
        scanner = heuristics.Scanner()
        assert scanner.remove_pattern("nonexistent") is False

    def test_list_patterns_returns_list(self):
        scanner = heuristics.Scanner()
        patterns = scanner.list_patterns()
        assert isinstance(patterns, list)
        assert len(patterns) > 0

    def test_scan_and_redact_api_key(self):
        scanner = heuristics.Scanner()
        text = "api_key=supersecretkey12345678"
        result = scanner.scan_and_redact(text)
        assert "supersecretkey12345678" not in result
        assert "[REDACTED_API_KEY]" in result

    def test_scan_and_redact_bearer_token(self):
        scanner = heuristics.Scanner()
        text = "Authorization: Bearer abcdefghijklmnopqrstuvwxyz1234567890"
        result = scanner.scan_and_redact(text)
        assert "abcdefghijklmnopqrstuvwxyz1234567890" not in result
        assert "[REDACTED_BEARER_TOKEN]" in result

    def test_scan_and_redact_password(self):
        scanner = heuristics.Scanner()
        text = "password=mysecretpassword"
        result = scanner.scan_and_redact(text)
        assert "mysecretpassword" not in result
        assert "[REDACTED_PASSWORD]" in result

    def test_scan_and_redact_secret(self):
        scanner = heuristics.Scanner()
        text = "secret=mysupersecretvalue1234"
        result = scanner.scan_and_redact(text)
        assert "mysupersecretvalue1234" not in result
        assert "[REDACTED_SECRET]" in result

    def test_scan_and_redact_jwt_token(self):
        scanner = heuristics.Scanner()
        # Minimal valid JWT-like structure
        jwt = "eyJhbGciOiJSUzI1NiJ9.eyJzdWIiOiJ1c2VyIn0.signature123"
        result = scanner.scan_and_redact(jwt)
        assert jwt not in result
        assert "[REDACTED_JWT_TOKEN]" in result

    def test_scan_and_redact_access_token(self):
        scanner = heuristics.Scanner()
        text = "access_token=abcdefghijklmnopqrstu"
        result = scanner.scan_and_redact(text)
        assert "abcdefghijklmnopqrstu" not in result

    def test_scan_and_redact_empty_string(self):
        scanner = heuristics.Scanner()
        assert scanner.scan_and_redact("") == ""

    def test_scan_and_redact_no_sensitive_data(self):
        scanner = heuristics.Scanner()
        text = "This is a normal log message with no secrets"
        assert scanner.scan_and_redact(text) == text

    def test_scan_and_redact_preserves_non_sensitive_parts(self):
        scanner = heuristics.Scanner()
        text = "Request to /api/devices with api_key=secret12345678901234"
        result = scanner.scan_and_redact(text)
        assert "Request to /api/devices with" in result

    def test_has_sensitive_data_true(self):
        scanner = heuristics.Scanner()
        assert scanner.has_sensitive_data("api_key=supersecretkey1234") is True

    def test_has_sensitive_data_false(self):
        scanner = heuristics.Scanner()
        assert scanner.has_sensitive_data("This is a normal message") is False

    def test_has_sensitive_data_empty_string(self):
        scanner = heuristics.Scanner()
        assert scanner.has_sensitive_data("") is False

    def test_get_sensitive_data_types_with_match(self):
        scanner = heuristics.Scanner()
        types = scanner.get_sensitive_data_types("api_key=secretkey12345678901234")
        assert "api_key" in types

    def test_get_sensitive_data_types_empty_string(self):
        scanner = heuristics.Scanner()
        assert scanner.get_sensitive_data_types("") == []

    def test_get_sensitive_data_types_no_match(self):
        scanner = heuristics.Scanner()
        assert scanner.get_sensitive_data_types("normal log message") == []

    def test_get_sensitive_data_types_multiple_matches(self):
        scanner = heuristics.Scanner()
        text = "api_key=secret1234567890 password=mypassword"
        types = scanner.get_sensitive_data_types(text)
        assert "api_key" in types
        assert "password" in types

    def test_reset_singleton_allows_new_instance(self):
        s1 = heuristics.Scanner()
        heuristics.Scanner.reset_singleton()
        s2 = heuristics.Scanner()
        assert s1 is not s2

    def test_default_redaction_format(self):
        scanner = heuristics.Scanner()
        scanner.add_pattern("mytoken", r"MYTOKEN_\w+")
        result = scanner.scan_and_redact("MYTOKEN_abc123")
        assert "[REDACTED_MYTOKEN]" in result


class TestModuleFunctions:
    def setup_method(self):
        heuristics.Scanner.reset_singleton()

    def test_get_scanner_returns_scanner_instance(self):
        scanner = heuristics.get_scanner()
        assert isinstance(scanner, heuristics.Scanner)

    def test_get_scanner_is_singleton(self):
        s1 = heuristics.get_scanner()
        s2 = heuristics.get_scanner()
        assert s1 is s2

    def test_configure_scanner_resets_and_reconfigures(self):
        s1 = heuristics.get_scanner()
        s2 = heuristics.configure_scanner({"custom_pat": r"CUSTOM_\d+"})
        assert s1 is not s2
        assert "custom_pat" in s2.list_patterns()

    def test_configure_scanner_none_patterns(self):
        scanner = heuristics.configure_scanner(None)
        assert isinstance(scanner, heuristics.Scanner)
        assert len(scanner.list_patterns()) > 0  # default patterns still loaded

    def test_scan_and_redact_convenience_redacts(self):
        result = heuristics.scan_and_redact("api_key=secretkey12345678")
        assert "secretkey12345678" not in result

    def test_scan_and_redact_convenience_passthrough(self):
        text = "nothing sensitive here"
        assert heuristics.scan_and_redact(text) == text

    def test_has_sensitive_data_convenience_true(self):
        assert heuristics.has_sensitive_data("password=hunter2") is True

    def test_has_sensitive_data_convenience_false(self):
        assert heuristics.has_sensitive_data("all clear") is False
