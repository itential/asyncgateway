# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import json
from unittest.mock import patch

import pytest

from asyncgateway import serdes
from asyncgateway.exceptions import ValidationError

JSONError = ValidationError


class TestSerdesModule:
    """Test the enhanced serdes module with both JSON and YAML support."""

    # Fixtures for test data
    @pytest.fixture
    def simple_dict_data(self):
        """Simple dictionary for testing."""
        return {"name": "test", "value": 42, "enabled": True}

    @pytest.fixture
    def complex_dict_data(self):
        """Complex dictionary with nested structures."""
        return {
            "name": "complex_test",
            "metadata": {
                "version": "1.0.0",
                "tags": ["test", "automation", "python"],
                "settings": {
                    "debug": True,
                    "timeout": 30.5,
                    "retries": None,
                },
            },
            "items": [
                {"id": 1, "name": "item1"},
                {"id": 2, "name": "item2", "optional": False},
            ],
        }

    @pytest.fixture
    def list_data(self):
        """List data for testing."""
        return [
            {"name": "item1", "value": 1},
            {"name": "item2", "value": 2},
            {"name": "item3", "value": 3},
        ]

    def test_yaml_available_flag(self):
        """Test that YAML_AVAILABLE flag is correctly set."""
        # The flag should be boolean
        assert isinstance(serdes.YAML_AVAILABLE, bool)

    # JSON functionality tests
    def test_json_loads_valid_dict(self, simple_dict_data):
        """Test JSON loads with valid dictionary."""
        json_str = json.dumps(simple_dict_data)
        result = serdes.json_loads(json_str)
        assert result == simple_dict_data
        assert isinstance(result, dict)

    def test_json_loads_complex_dict(self, complex_dict_data):
        """Test JSON loads with complex nested dictionary."""
        json_str = json.dumps(complex_dict_data)
        result = serdes.json_loads(json_str)
        assert result == complex_dict_data
        assert isinstance(result, dict)
        # Verify nested structures are preserved
        assert result["metadata"]["version"] == "1.0.0"
        assert len(result["metadata"]["tags"]) == 3
        assert result["metadata"]["settings"]["retries"] is None

    def test_json_loads_valid_list(self, list_data):
        """Test JSON loads with valid list."""
        json_str = json.dumps(list_data)
        result = serdes.json_loads(json_str)
        assert result == list_data
        assert isinstance(result, list)
        assert len(result) == 3
        assert all("name" in item and "value" in item for item in result)

    def test_json_loads_invalid_json(self):
        """Test JSON loads with various invalid JSON formats."""
        invalid_cases = [
            ('{"name": "test", "value": }', "trailing comma"),
            ('{"name": "test" "value": 42}', "missing comma"),
            ('{"name": "test", value: 42}', "unquoted key"),
            ('["item1", "item2",]', "trailing comma in array"),
            ('"unclosed string', "unclosed string"),
            ("{broken json}", "malformed structure"),
        ]

        for invalid_json, description in invalid_cases:
            with pytest.raises(JSONError, match="Failed to parse JSON"):
                serdes.json_loads(invalid_json)

            assert description  # Just to use the description variable

    def test_json_dumps_valid_dict(self, simple_dict_data, complex_dict_data):
        """Test JSON dumps with valid dictionaries."""
        # Test simple dictionary
        result = serdes.json_dumps(simple_dict_data)
        assert isinstance(result, str)
        reparsed = serdes.json_loads(result)
        assert reparsed == simple_dict_data

        # Test complex nested dictionary
        result_complex = serdes.json_dumps(complex_dict_data)
        assert isinstance(result_complex, str)
        reparsed_complex = serdes.json_loads(result_complex)
        assert reparsed_complex == complex_dict_data

    def test_json_dumps_valid_list(self, list_data):
        """Test JSON dumps with valid list."""
        result = serdes.json_dumps(list_data)
        assert isinstance(result, str)
        reparsed = serdes.json_loads(result)
        assert reparsed == list_data

    def test_json_dumps_non_serializable(self):
        """Test JSON dumps with non-serializable objects."""

        class NonSerializable:
            def __init__(self, value):
                self.value = value

        # Test various non-serializable types
        non_serializable_cases = [
            ({"obj": NonSerializable("test")}, "custom class"),
            ({"func": lambda x: x}, "function"),
            ({"set": {1, 2, 3}}, "set"),
        ]

        for data, description in non_serializable_cases:
            with pytest.raises(JSONError, match="Failed to serialize object to JSON"):
                serdes.json_dumps(data)

            assert description  # Just to use the description variable

    def test_json_type_preservation(self):
        """Test that JSON preserves various Python data types correctly."""
        data = {
            "string": "hello",
            "integer": 42,
            "float": 3.14,
            "boolean_true": True,
            "boolean_false": False,
            "null_value": None,
            "empty_list": [],
            "empty_dict": {},
        }

        json_str = serdes.json_dumps(data)
        result = serdes.json_loads(json_str)

        assert result == data
        assert isinstance(result["string"], str)
        assert isinstance(result["integer"], int)
        assert isinstance(result["float"], float)
        assert isinstance(result["boolean_true"], bool)
        assert isinstance(result["boolean_false"], bool)
        assert result["null_value"] is None
        assert isinstance(result["empty_list"], list)
        assert isinstance(result["empty_dict"], dict)

    # YAML functionality tests
    @pytest.mark.skipif(not serdes.YAML_AVAILABLE, reason="PyYAML not available")
    def test_yaml_loads_valid_dict(self, simple_dict_data):
        """Test YAML loads with valid dictionary."""
        # Test simple dictionary
        yaml_str = "name: test\nvalue: 42\nenabled: true"
        result = serdes.yaml_loads(yaml_str)
        expected = {"name": "test", "value": 42, "enabled": True}
        assert result == expected
        assert isinstance(result, dict)

        # Test with YAML-generated string
        yaml_from_dumps = serdes.yaml_dumps(simple_dict_data)
        result_from_dumps = serdes.yaml_loads(yaml_from_dumps)
        assert result_from_dumps == simple_dict_data

    @pytest.mark.skipif(not serdes.YAML_AVAILABLE, reason="PyYAML not available")
    def test_yaml_loads_complex_dict(self, complex_dict_data):
        """Test YAML loads with complex nested dictionary."""
        yaml_str = serdes.yaml_dumps(complex_dict_data)
        result = serdes.yaml_loads(yaml_str)
        assert result == complex_dict_data
        assert isinstance(result, dict)
        # Verify nested structures are preserved
        assert result["metadata"]["version"] == "1.0.0"
        assert len(result["metadata"]["tags"]) == 3
        assert result["metadata"]["settings"]["retries"] is None

    @pytest.mark.skipif(not serdes.YAML_AVAILABLE, reason="PyYAML not available")
    def test_yaml_loads_valid_list(self, list_data):
        """Test YAML loads with valid list."""
        yaml_str = serdes.yaml_dumps(list_data)
        result = serdes.yaml_loads(yaml_str)
        assert result == list_data
        assert isinstance(result, list)
        assert len(result) == 3
        assert all("name" in item and "value" in item for item in result)

    @pytest.mark.skipif(not serdes.YAML_AVAILABLE, reason="PyYAML not available")
    def test_yaml_loads_invalid_yaml(self):
        """Test YAML loads with various invalid YAML formats."""
        invalid_cases = [
            (
                "---\n- item1\n- item2\n  - nested but invalid\n- item3\n  invalid: [ unclosed bracket",
                "unclosed bracket",
            ),
            ("key: !!python/object/apply:os.system ['echo hello']", "unsafe yaml"),
        ]

        for invalid_yaml, description in invalid_cases:
            with pytest.raises(JSONError, match="Failed to parse YAML"):
                serdes.yaml_loads(invalid_yaml)

            assert description  # Just to use the description variable

    def test_yaml_loads_without_yaml_support(self):
        """Test YAML loads when PyYAML is not available."""
        with patch.object(serdes, "YAML_AVAILABLE", False):
            with pytest.raises(ValidationError) as exc_info:
                serdes.yaml_loads("name: test")

            assert "YAML support not available" in str(exc_info.value)
            assert "PyYAML" in str(exc_info.value)

    @pytest.mark.skipif(not serdes.YAML_AVAILABLE, reason="PyYAML not available")
    def test_yaml_dumps_valid_dict(self, simple_dict_data, complex_dict_data):
        """Test YAML dumps with valid dictionaries."""
        # Test simple dictionary
        result = serdes.yaml_dumps(simple_dict_data)
        assert isinstance(result, str)
        reparsed = serdes.yaml_loads(result)
        assert reparsed == simple_dict_data

        # Check basic YAML formatting
        assert "name: test" in result
        assert "value: 42" in result
        assert "enabled: true" in result

        # Test complex nested dictionary
        result_complex = serdes.yaml_dumps(complex_dict_data)
        assert isinstance(result_complex, str)
        reparsed_complex = serdes.yaml_loads(result_complex)
        assert reparsed_complex == complex_dict_data

    @pytest.mark.skipif(not serdes.YAML_AVAILABLE, reason="PyYAML not available")
    def test_yaml_dumps_valid_list(self, list_data):
        """Test YAML dumps with valid list."""
        result = serdes.yaml_dumps(list_data)
        assert isinstance(result, str)
        reparsed = serdes.yaml_loads(result)
        assert reparsed == list_data

        # Check YAML list formatting
        assert "- name: item1" in result
        assert "  value: 1" in result

    @pytest.mark.skipif(not serdes.YAML_AVAILABLE, reason="PyYAML not available")
    def test_yaml_dumps_custom_options(self):
        """Test YAML dumps with custom formatting options."""
        data = {
            "name": "test",
            "items": ["item1", "item2", "item3"],
            "description": "A very long description that should wrap at a certain width to test the width parameter",
        }

        # Test with custom indentation and width
        result = serdes.yaml_dumps(data, indent=4, width=40)
        assert isinstance(result, str)
        reparsed = serdes.yaml_loads(result)
        assert reparsed == data

        # Test with flow style for lists
        result_flow = serdes.yaml_dumps(data, default_flow_style=True)
        assert isinstance(result_flow, str)
        reparsed_flow = serdes.yaml_loads(result_flow)
        assert reparsed_flow == data

        # Test with no unicode (ASCII only)
        unicode_data = {"message": "Hello 世界"}
        result_ascii = serdes.yaml_dumps(unicode_data, allow_unicode=False)
        assert isinstance(result_ascii, str)
        reparsed_ascii = serdes.yaml_loads(result_ascii)
        assert reparsed_ascii == unicode_data

    def test_yaml_dumps_without_yaml_support(self):
        """Test YAML dumps when PyYAML is not available."""
        with patch.object(serdes, "YAML_AVAILABLE", False):
            with pytest.raises(ValidationError) as exc_info:
                serdes.yaml_dumps({"name": "test"})

            assert "YAML support not available" in str(exc_info.value)
            assert "PyYAML" in str(exc_info.value)

    # Enhanced loads/dumps functionality tests
    def test_loads_empty_string(self):
        """Test loads with empty string."""
        if serdes.YAML_AVAILABLE:
            # With YAML available, empty string returns None from YAML parser
            result = serdes.loads("")
            assert result is None
        else:
            # Without YAML, it should fail on JSON parsing
            with pytest.raises(ValidationError, match="Failed to parse string as"):
                serdes.loads("")

    def test_loads_whitespace_only(self):
        """Test loads with whitespace-only string."""
        # Whitespace-only strings fail both JSON and YAML parsing
        with pytest.raises(ValidationError, match="Failed to parse string as"):
            serdes.loads("   \n\t  ")

    def test_loads_none_input(self):
        """Test loads with None input."""
        # None input fails with ValidationError when both formats fail
        with pytest.raises(ValidationError, match="Failed to parse string as"):
            serdes.loads(None)

    def test_loads_with_json_hint(self, simple_dict_data, list_data):
        """Test loads with explicit JSON hint."""
        # Test with dictionary
        json_str = json.dumps(simple_dict_data)
        result = serdes.loads(json_str, format_hint="json")
        assert result == simple_dict_data

        # Test with list
        json_list_str = json.dumps(list_data)
        result_list = serdes.loads(json_list_str, format_hint="json")
        assert result_list == list_data

        # Test case insensitive hint
        result_case = serdes.loads(json_str, format_hint="JSON")
        assert result_case == simple_dict_data

    @pytest.mark.skipif(not serdes.YAML_AVAILABLE, reason="PyYAML not available")
    def test_loads_with_yaml_hint(self, simple_dict_data, list_data):
        """Test loads with explicit YAML hint."""
        # Test with dictionary
        yaml_str = serdes.yaml_dumps(simple_dict_data)
        result = serdes.loads(yaml_str, format_hint="yaml")
        assert result == simple_dict_data

        # Test with list
        yaml_list_str = serdes.yaml_dumps(list_data)
        result_list = serdes.loads(yaml_list_str, format_hint="yaml")
        assert result_list == list_data

        # Test case insensitive hint and yml variant
        result_case = serdes.loads(yaml_str, format_hint="YAML")
        assert result_case == simple_dict_data

        result_yml = serdes.loads(yaml_str, format_hint="yml")
        assert result_yml == simple_dict_data

    def test_loads_invalid_hint(self):
        """Test loads with invalid format hint."""
        invalid_hints = ["xml", "csv", "ini", ""]

        for hint in invalid_hints:
            if hint == "":  # Empty string hint is falsy, so no hint is processed
                # Empty string format_hint is treated as no hint, so it will try auto-detection
                # "data" is actually valid YAML (it's just a string), so it succeeds
                result = serdes.loads("data", format_hint=hint)
                assert result == "data"  # Valid YAML string
            else:
                with pytest.raises(
                    ValidationError, match="Unsupported format hint"
                ) as exc_info:
                    serdes.loads("data", format_hint=hint)
                assert hint in str(exc_info.value)

    def test_loads_auto_detect_json(self, simple_dict_data, list_data):
        """Test loads auto-detecting JSON format."""
        # Test with dictionary
        json_str = json.dumps(simple_dict_data)
        result = serdes.loads(json_str)
        assert result == simple_dict_data

        # Test with list
        json_list_str = json.dumps(list_data)
        result_list = serdes.loads(json_list_str)
        assert result_list == list_data

        # Test with primitive values
        assert serdes.loads('"hello"') == "hello"
        assert serdes.loads("42") == 42
        assert serdes.loads("true") is True
        assert serdes.loads("false") is False
        assert serdes.loads("null") is None

    @pytest.mark.skipif(not serdes.YAML_AVAILABLE, reason="PyYAML not available")
    def test_loads_auto_detect_yaml(self, simple_dict_data, list_data):
        """Test loads auto-detecting YAML when JSON fails."""
        # Test YAML-only syntax that would fail JSON parsing
        yaml_only_cases = [
            ("name: test\nvalue: 42", {"name": "test", "value": 42}),
            ("- item1\n- item2\n- item3", ["item1", "item2", "item3"]),
            ("enabled: yes\ndisabled: no", {"enabled": True, "disabled": False}),
            ("key: 'quoted value'", {"key": "quoted value"}),
        ]

        for yaml_str, expected in yaml_only_cases:
            result = serdes.loads(yaml_str)
            assert result == expected

        # Test with fixture data converted to YAML format
        yaml_dict_str = serdes.yaml_dumps(simple_dict_data)
        result_dict = serdes.loads(yaml_dict_str)
        assert result_dict == simple_dict_data

        yaml_list_str = serdes.yaml_dumps(list_data)
        result_list = serdes.loads(yaml_list_str)
        assert result_list == list_data

    def test_loads_invalid_both_formats(self):
        """Test loads when string is invalid in both formats."""
        # Use strings that are truly invalid in both JSON and YAML formats
        truly_invalid_cases = [
            '{ "unclosed": "json" and invalid: [ yaml',
            "{[malformed structure}]",
            '[{"broken": json and: yaml}]',
        ]

        for invalid_str in truly_invalid_cases:
            # These should fail both JSON and YAML parsing
            with pytest.raises(ValidationError, match="Failed to parse string as"):
                serdes.loads(invalid_str)

        # Test a case that's valid YAML but invalid JSON to ensure we're testing the right thing
        yaml_only_valid = "key: value"
        result = serdes.loads(yaml_only_valid)
        assert result == {"key": "value"}  # Should succeed as YAML

    def test_dumps_json_format(self, simple_dict_data, complex_dict_data, list_data):
        """Test dumps with JSON format."""
        # Test simple data
        result = serdes.dumps(simple_dict_data, format_type="json")
        assert isinstance(result, str)
        reparsed = serdes.json_loads(result)
        assert reparsed == simple_dict_data

        # Test complex nested data
        result_complex = serdes.dumps(complex_dict_data, format_type="json")
        assert isinstance(result_complex, str)
        reparsed_complex = serdes.json_loads(result_complex)
        assert reparsed_complex == complex_dict_data

        # Test list data
        result_list = serdes.dumps(list_data, format_type="json")
        assert isinstance(result_list, str)
        reparsed_list = serdes.json_loads(result_list)
        assert reparsed_list == list_data

        # Test case insensitive format
        result_case = serdes.dumps(simple_dict_data, format_type="JSON")
        assert isinstance(result_case, str)
        reparsed_case = serdes.json_loads(result_case)
        assert reparsed_case == simple_dict_data

    @pytest.mark.skipif(not serdes.YAML_AVAILABLE, reason="PyYAML not available")
    def test_dumps_yaml_format(self, simple_dict_data, complex_dict_data, list_data):
        """Test dumps with YAML format."""
        # Test simple data
        result = serdes.dumps(simple_dict_data, format_type="yaml")
        assert isinstance(result, str)
        reparsed = serdes.yaml_loads(result)
        assert reparsed == simple_dict_data

        # Test complex nested data
        result_complex = serdes.dumps(complex_dict_data, format_type="yaml")
        assert isinstance(result_complex, str)
        reparsed_complex = serdes.yaml_loads(result_complex)
        assert reparsed_complex == complex_dict_data

        # Test list data
        result_list = serdes.dumps(list_data, format_type="yaml")
        assert isinstance(result_list, str)
        reparsed_list = serdes.yaml_loads(result_list)
        assert reparsed_list == list_data

        # Test case insensitive format and yml variant
        result_case = serdes.dumps(simple_dict_data, format_type="YAML")
        assert isinstance(result_case, str)
        reparsed_case = serdes.yaml_loads(result_case)
        assert reparsed_case == simple_dict_data

        result_yml = serdes.dumps(simple_dict_data, format_type="yml")
        assert isinstance(result_yml, str)
        reparsed_yml = serdes.yaml_loads(result_yml)
        assert reparsed_yml == simple_dict_data

    def test_dumps_invalid_format(self):
        """Test dumps with invalid format type."""
        invalid_formats = ["xml", "csv", "ini", ""]
        data = {"name": "test"}

        for fmt in invalid_formats:
            with pytest.raises(
                ValidationError, match="Unsupported format type"
            ) as exc_info:
                serdes.dumps(data, format_type=fmt)

            assert fmt in str(exc_info.value) or fmt == ""

    # Backward compatibility tests
    def test_loads_backward_compatibility_json_only(self, simple_dict_data, list_data):
        """Test that loads() maintains backward compatibility for JSON-only usage."""
        # Test with dictionary
        json_str = json.dumps(simple_dict_data)
        result = serdes.loads(json_str)  # No format hint - should auto-detect JSON
        assert result == simple_dict_data

        # Test with list
        json_list_str = json.dumps(list_data)
        result_list = serdes.loads(json_list_str)
        assert result_list == list_data

    def test_dumps_backward_compatibility_json_only(
        self, simple_dict_data, complex_dict_data, list_data
    ):
        """Test that dumps() maintains backward compatibility for JSON-only usage."""
        # Test simple data - defaults to JSON
        result = serdes.dumps(
            simple_dict_data
        )  # No format_type - should default to JSON
        assert isinstance(result, str)
        reparsed = serdes.loads(result)
        assert reparsed == simple_dict_data

        # Test complex data
        result_complex = serdes.dumps(complex_dict_data)
        assert isinstance(result_complex, str)
        reparsed_complex = serdes.loads(result_complex)
        assert reparsed_complex == complex_dict_data

        # Test list data
        result_list = serdes.dumps(list_data)
        assert isinstance(result_list, str)
        reparsed_list = serdes.loads(result_list)
        assert reparsed_list == list_data

    # Edge cases and error handling
    def test_empty_string_handling(self):
        """Test handling of empty strings."""
        with pytest.raises(JSONError, match="Failed to parse JSON"):
            serdes.json_loads("")

        if serdes.YAML_AVAILABLE:
            # Empty YAML should return None
            result = serdes.yaml_loads("")
            assert result is None

            # Empty string with loads should fail on JSON first, then succeed with YAML returning None
            result = serdes.loads("")
            assert result is None

    def test_none_input_handling(self):
        """Test handling of None input."""
        with pytest.raises(JSONError, match="Failed to parse JSON"):
            serdes.json_loads(None)

        if serdes.YAML_AVAILABLE:
            with pytest.raises(JSONError, match="Failed to parse YAML"):
                serdes.yaml_loads(None)

    def test_large_data_handling(self):
        """Test handling of large data structures."""
        # Create a large nested structure
        large_data = {
            "items": [
                {"id": i, "name": f"item_{i}", "data": list(range(10))}
                for i in range(100)
            ],
            "metadata": {
                "total": 100,
                "nested": {"level1": {"level2": {"level3": "deep_value"}}},
            },
        }

        # Test JSON handling
        json_result = serdes.json_dumps(large_data)
        assert isinstance(json_result, str)
        json_reparsed = serdes.json_loads(json_result)
        assert json_reparsed == large_data

        # Test YAML handling if available
        if serdes.YAML_AVAILABLE:
            yaml_result = serdes.yaml_dumps(large_data)
            assert isinstance(yaml_result, str)
            yaml_reparsed = serdes.yaml_loads(yaml_result)
            assert yaml_reparsed == large_data

    def test_special_characters_handling(self):
        """Test handling of special characters in data."""
        special_data = {
            "newlines": "line1\nline2\nline3",
            "tabs": "col1\tcol2\tcol3",
            "quotes": 'He said "Hello!"',
            "backslashes": "path\\to\\file",
            "unicode": "Special chars: àáâãäå æç èéêë",
            "emojis": "😀 🎉 🚀 ⭐ 🌟",
        }

        # Test JSON handling
        json_result = serdes.json_dumps(special_data)
        json_reparsed = serdes.json_loads(json_result)
        assert json_reparsed == special_data

        # Test YAML handling if available
        if serdes.YAML_AVAILABLE:
            yaml_result = serdes.yaml_dumps(special_data)
            yaml_reparsed = serdes.yaml_loads(yaml_result)
            assert yaml_reparsed == special_data

    @pytest.mark.skipif(not serdes.YAML_AVAILABLE, reason="PyYAML not available")
    def test_yaml_complex_types(self):
        """Test YAML handling of complex data types."""
        data = {
            "string": "test",
            "integer": 42,
            "float": 3.14,
            "boolean_true": True,
            "boolean_false": False,
            "null_value": None,
            "list": [1, 2, 3],
            "nested": {"key": "value"},
            "mixed_list": ["string", 42, True, None, {"nested": "dict"}],
        }

        yaml_str = serdes.yaml_dumps(data)
        reparsed = serdes.yaml_loads(yaml_str)
        assert reparsed == data

        # Verify types are preserved
        assert isinstance(reparsed["string"], str)
        assert isinstance(reparsed["integer"], int)
        assert isinstance(reparsed["float"], float)
        assert isinstance(reparsed["boolean_true"], bool)
        assert isinstance(reparsed["boolean_false"], bool)
        assert reparsed["null_value"] is None
        assert isinstance(reparsed["list"], list)
        assert isinstance(reparsed["nested"], dict)
        assert isinstance(reparsed["mixed_list"], list)

    @pytest.mark.skipif(not serdes.YAML_AVAILABLE, reason="PyYAML not available")
    def test_yaml_multiline_strings(self):
        """Test YAML handling of multiline strings and special YAML features."""
        multiline_cases = {
            "description": "This is a very long description that should\nspan multiple lines and contain\nspecial characters like: colons, quotes, etc.",
            "script": "#!/bin/bash\necho 'Hello World'\nls -la",
            "yaml_special": "Key: value\nAnother: 'quoted value'\nList:\n  - item1\n  - item2",
        }

        for key, value in multiline_cases.items():
            data = {key: value}
            yaml_str = serdes.yaml_dumps(data)
            reparsed = serdes.yaml_loads(yaml_str)
            assert reparsed == data, f"Failed for {key}"

        # Test all together
        yaml_str = serdes.yaml_dumps(multiline_cases)
        reparsed = serdes.yaml_loads(yaml_str)
        assert reparsed == multiline_cases

    def test_unicode_handling_json(self):
        """Test JSON handling of Unicode characters."""
        unicode_cases = {
            "chinese": "你好世界",
            "japanese": "こんにちは世界",
            "korean": "안녕하세요 세계",
            "arabic": "مرحبا بالعالم",
            "emoji": "🌍 🚀 ⭐ 😀 🎉",
            "mixed": "Hello 世界! 🌍 مرحبا",
            "special": "àáâãäå æç èéêë ñ ü",
        }

        for key, value in unicode_cases.items():
            data = {"message": value}
            json_str = serdes.json_dumps(data)
            reparsed = serdes.json_loads(json_str)
            assert reparsed == data, f"Failed for {key}: {value}"

        # Test all together
        json_str = serdes.json_dumps(unicode_cases)
        reparsed = serdes.json_loads(json_str)
        assert reparsed == unicode_cases

    @pytest.mark.skipif(not serdes.YAML_AVAILABLE, reason="PyYAML not available")
    def test_unicode_handling_yaml(self):
        """Test YAML handling of Unicode characters."""
        unicode_cases = {
            "chinese": "你好世界",
            "japanese": "こんにちは世界",
            "korean": "안녕하세요 세계",
            "arabic": "مرحبا بالعالم",
            "emoji": "🌍 🚀 ⭐ 😀 🎉",
            "mixed": "Hello 世界! 🌍 مرحبا",
            "special": "àáâãäå æç èéêë ñ ü",
        }

        for key, value in unicode_cases.items():
            data = {"message": value}
            yaml_str = serdes.yaml_dumps(data)
            reparsed = serdes.yaml_loads(yaml_str)
            assert reparsed == data, f"Failed for {key}: {value}"

        # Test all together
        yaml_str = serdes.yaml_dumps(unicode_cases)
        reparsed = serdes.yaml_loads(yaml_str)
        assert reparsed == unicode_cases

    # Error message tests
    def test_json_error_message(self):
        """Test that JSON errors include a descriptive message."""
        with pytest.raises(JSONError, match="Failed to parse JSON"):
            serdes.json_loads('{"invalid": json}')

    @pytest.mark.skipif(not serdes.YAML_AVAILABLE, reason="PyYAML not available")
    def test_yaml_error_message(self):
        """Test that YAML errors include a descriptive message."""
        with pytest.raises(JSONError, match="Failed to parse YAML"):
            serdes.yaml_loads("invalid: [ yaml")

    def test_validation_error_messages(self):
        """Test that ValidationErrors include descriptive messages."""
        with pytest.raises(ValidationError, match="Unsupported format hint"):
            serdes.loads("data", format_hint="invalid")

        with pytest.raises(ValidationError, match="Unsupported format type"):
            serdes.dumps({"test": "data"}, format_type="invalid")

    @pytest.mark.skipif(not serdes.YAML_AVAILABLE, reason="PyYAML not available")
    def test_format_detection_priority(self):
        """Test that JSON is tried before YAML in auto-detection."""
        # This string is valid in both JSON and YAML, but should be parsed as JSON first
        ambiguous_str = '["item1", "item2", "item3"]'

        # Should parse as JSON (list)
        result = serdes.loads(ambiguous_str)
        assert result == ["item1", "item2", "item3"]
        assert isinstance(result, list)

        # Verify it would also work as YAML but gives same result
        yaml_result = serdes.yaml_loads(ambiguous_str)
        assert yaml_result == result

    def test_round_trip_consistency(
        self, simple_dict_data, complex_dict_data, list_data
    ):
        """Test that data survives multiple serialization/deserialization cycles."""
        test_cases = [simple_dict_data, complex_dict_data, list_data]

        for original_data in test_cases:
            # Test JSON round trip
            json_str = serdes.json_dumps(original_data)
            json_parsed = serdes.json_loads(json_str)
            json_str2 = serdes.json_dumps(json_parsed)
            json_parsed2 = serdes.json_loads(json_str2)
            assert json_parsed2 == original_data

            # Test enhanced loads/dumps round trip
            enhanced_str = serdes.dumps(original_data)
            enhanced_parsed = serdes.loads(enhanced_str)
            enhanced_str2 = serdes.dumps(enhanced_parsed)
            enhanced_parsed2 = serdes.loads(enhanced_str2)
            assert enhanced_parsed2 == original_data

            # Test YAML round trip if available
            if serdes.YAML_AVAILABLE:
                yaml_str = serdes.yaml_dumps(original_data)
                yaml_parsed = serdes.yaml_loads(yaml_str)
                yaml_str2 = serdes.yaml_dumps(yaml_parsed)
                yaml_parsed2 = serdes.yaml_loads(yaml_str2)
                assert yaml_parsed2 == original_data
