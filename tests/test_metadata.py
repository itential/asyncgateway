# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)


from asyncgateway import metadata


class TestMetadata:
    def test_name_attribute(self):
        assert metadata.name == "asyncgateway"

    def test_author_attribute(self):
        assert metadata.author == "Itential"

    def test_version_attribute_exists(self):
        assert hasattr(metadata, "version")
        assert isinstance(metadata.version, str)

    def test_version_retrieval_mechanism(self):
        # Test that version is retrieved from importlib.metadata
        # The actual call is tested implicitly by the fact that version exists and is a string
        assert hasattr(metadata, "version")
        assert isinstance(metadata.version, str)
        # Version should not be empty or just whitespace
        assert metadata.version.strip()

    def test_module_constants_are_strings(self):
        assert isinstance(metadata.name, str)
        assert isinstance(metadata.author, str)
        assert isinstance(metadata.version, str)

    def test_name_not_empty(self):
        assert len(metadata.name) > 0

    def test_author_not_empty(self):
        assert len(metadata.author) > 0

    def test_version_not_empty(self):
        assert len(metadata.version) > 0
