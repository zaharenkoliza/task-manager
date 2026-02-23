"""Tests for app.config module."""
import tempfile
from pathlib import Path

import pytest

from app.config import (
    DatabaseSettings,
    Settings,
    _deep_merge,
    _load_yaml,
)


class TestDeepMerge:
    """Tests for _deep_merge function."""

    def test_merge_empty_dicts(self):
        """Merging empty dicts returns empty dict."""
        assert _deep_merge({}, {}) == {}

    def test_merge_override_into_empty(self):
        """Override values added to empty base."""
        base = {}
        override = {"key": "value"}
        assert _deep_merge(base, override) == {"key": "value"}

    def test_merge_empty_override(self):
        """Empty override keeps base values."""
        base = {"key": "value"}
        override = {}
        assert _deep_merge(base, override) == {"key": "value"}

    def test_merge_simple_values(self):
        """Override replaces simple values."""
        base = {"a": 1, "b": 2}
        override = {"b": 3, "c": 4}
        assert _deep_merge(base, override) == {"a": 1, "b": 3, "c": 4}

    def test_merge_nested_dicts(self):
        """Nested dicts are merged recursively."""
        base = {"db": {"host": "localhost", "port": 5432}}
        override = {"db": {"port": 5433, "name": "test"}}
        result = _deep_merge(base, override)
        assert result == {"db": {"host": "localhost", "port": 5433, "name": "test"}}

    def test_merge_deeply_nested(self):
        """Deep nesting is handled correctly."""
        base = {"a": {"b": {"c": 1, "d": 2}}}
        override = {"a": {"b": {"d": 3, "e": 4}}}
        result = _deep_merge(base, override)
        assert result == {"a": {"b": {"c": 1, "d": 3, "e": 4}}}

    def test_override_dict_with_value(self):
        """Non-dict override replaces dict."""
        base = {"a": {"b": 1}}
        override = {"a": "replaced"}
        assert _deep_merge(base, override) == {"a": "replaced"}

    def test_override_value_with_dict(self):
        """Dict override replaces non-dict."""
        base = {"a": "value"}
        override = {"a": {"b": 1}}
        assert _deep_merge(base, override) == {"a": {"b": 1}}


class TestLoadYaml:
    """Tests for _load_yaml function."""

    def test_load_nonexistent_file(self):
        """Nonexistent file returns empty dict."""
        path = Path("/nonexistent/path/file.yaml")
        assert _load_yaml(path) == {}

    def test_load_valid_yaml(self):
        """Valid YAML file is loaded correctly."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("debug: true\ndatabase:\n  host: testhost\n")
            f.flush()
            path = Path(f.name)

        try:
            result = _load_yaml(path)
            assert result == {"debug": True, "database": {"host": "testhost"}}
        finally:
            path.unlink()

    def test_load_empty_yaml(self):
        """Empty YAML file returns empty dict."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("")
            f.flush()
            path = Path(f.name)

        try:
            result = _load_yaml(path)
            assert result == {}
        finally:
            path.unlink()

    def test_load_yaml_with_list_returns_empty(self):
        """YAML file with list at root returns empty dict."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("- item1\n- item2\n")
            f.flush()
            path = Path(f.name)

        try:
            result = _load_yaml(path)
            assert result == {}
        finally:
            path.unlink()


class TestDatabaseSettings:
    """Tests for DatabaseSettings model."""

    def test_default_values(self):
        """Default values are set correctly."""
        settings = DatabaseSettings()
        assert settings.host == "localhost"
        assert settings.port == 5432
        assert settings.user == "postgres"
        assert settings.password == "postgres"
        assert settings.name == "tasks_db"

    def test_custom_values(self):
        """Custom values are accepted."""
        settings = DatabaseSettings(
            host="myhost",
            port=5433,
            user="myuser",
            password="mypass",
            name="mydb",
        )
        assert settings.host == "myhost"
        assert settings.port == 5433
        assert settings.user == "myuser"
        assert settings.password == "mypass"
        assert settings.name == "mydb"

    def test_url_property(self):
        """URL property constructs correct connection string."""
        settings = DatabaseSettings(
            host="dbhost",
            port=5433,
            user="admin",
            password="secret",
            name="testdb",
        )
        expected = "postgresql+asyncpg://admin:secret@dbhost:5433/testdb"
        assert settings.url == expected

    def test_url_with_defaults(self):
        """URL with default values is correct."""
        settings = DatabaseSettings()
        expected = "postgresql+asyncpg://postgres:postgres@localhost:5432/tasks_db"
        assert settings.url == expected


class TestSettings:
    """Tests for Settings model."""

    def test_default_values(self):
        """Default values are set correctly."""
        settings = Settings()
        assert settings.debug is False
        assert isinstance(settings.database, DatabaseSettings)

    def test_custom_debug(self):
        """Debug flag can be set."""
        settings = Settings(debug=True)
        assert settings.debug is True

    def test_nested_database_settings(self):
        """Nested database settings work correctly."""
        settings = Settings(
            debug=True,
            database={"host": "custom", "port": 1234},
        )
        assert settings.debug is True
        assert settings.database.host == "custom"
        assert settings.database.port == 1234
        # Defaults for unspecified fields
        assert settings.database.user == "postgres"

    def test_full_database_override(self):
        """Full database settings can be provided."""
        db_settings = DatabaseSettings(
            host="h", port=1, user="u", password="p", name="n"
        )
        settings = Settings(database=db_settings)
        assert settings.database.host == "h"
        assert settings.database.url == "postgresql+asyncpg://u:p@h:1/n"

