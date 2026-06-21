"""Tests for usepr.configs.dspy module."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import yaml

from usepr.configs.dspy import (
    APPLICATION_NAME,
    CONFIG_DIR,
    CONFIG_FILE,
    DEFAULT_EXTRA_BODY,
    DEFAULT_MODEL,
    configure_dspy,
    get_lm,
    load_config,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------


class TestConstants:
    def test_application_name(self) -> None:
        assert APPLICATION_NAME == "usepr"

    def test_default_model_is_set(self) -> None:
        assert DEFAULT_MODEL  # not empty
        assert isinstance(DEFAULT_MODEL, str)

    def test_default_extra_body_structure(self) -> None:
        assert "provider" in DEFAULT_EXTRA_BODY
        assert "order" in DEFAULT_EXTRA_BODY["provider"]
        assert "allow_fallbacks" in DEFAULT_EXTRA_BODY["provider"]

    def test_config_dir_is_under_home(self) -> None:
        assert str(CONFIG_DIR).endswith(".config/usepr")

    def test_config_file_is_under_config_dir(self) -> None:
        assert CONFIG_FILE.parent == CONFIG_DIR
        assert CONFIG_FILE.name == "config.yml"


# ---------------------------------------------------------------------------
# load_config()
# ---------------------------------------------------------------------------


class TestLoadConfig:
    def test_returns_empty_dict_when_no_file(self, tmp_path: Path) -> None:
        with patch("usepr.configs.dspy.CONFIG_FILE", tmp_path / "nonexistent.yml"):
            assert load_config() == {}

    def test_loads_valid_yaml(self, tmp_path: Path) -> None:
        config_file = tmp_path / "config.yml"
        config_file.write_text(yaml.dump({"model": "gpt-4", "cache": True}))

        with patch("usepr.configs.dspy.CONFIG_FILE", config_file):
            config = load_config()
            assert config["model"] == "gpt-4"
            assert config["cache"] is True

    def test_returns_empty_dict_on_invalid_yaml(self, tmp_path: Path) -> None:
        config_file = tmp_path / "config.yml"
        config_file.write_text("{{{{invalid yaml}}}}")

        with patch("usepr.configs.dspy.CONFIG_FILE", config_file):
            assert load_config() == {}

    def test_returns_empty_dict_on_non_dict_yaml(self, tmp_path: Path) -> None:
        config_file = tmp_path / "config.yml"
        config_file.write_text("- item1\n- item2")  # list, not dict

        with patch("usepr.configs.dspy.CONFIG_FILE", config_file):
            assert load_config() == {}

    def test_returns_empty_dict_on_empty_yaml(self, tmp_path: Path) -> None:
        config_file = tmp_path / "config.yml"
        config_file.write_text("")

        with patch("usepr.configs.dspy.CONFIG_FILE", config_file):
            assert load_config() == {}

    def test_returns_empty_dict_on_os_error(self, tmp_path: Path) -> None:
        config_file = tmp_path / "unreadable.yml"
        config_file.write_text("model: gpt-4")
        config_file.chmod(0o000)

        with patch("usepr.configs.dspy.CONFIG_FILE", config_file):
            try:
                result = load_config()
                assert result == {}
            finally:
                config_file.chmod(0o644)  # restore for cleanup


# ---------------------------------------------------------------------------
# get_lm()
# ---------------------------------------------------------------------------


class TestGetLM:
    @patch("usepr.configs.dspy.load_config")
    @patch("dspy.LM")
    def test_explicit_model_overrides_config(
        self, mock_lm: MagicMock, mock_load: MagicMock
    ) -> None:
        mock_load.return_value = {"model": "config-model"}
        get_lm(model="explicit-model")
        mock_lm.assert_called_once()
        call_args = mock_lm.call_args
        assert call_args[0][0] == "explicit-model"

    @patch("usepr.configs.dspy.load_config")
    @patch("dspy.LM")
    def test_config_model_overrides_default(
        self, mock_lm: MagicMock, mock_load: MagicMock
    ) -> None:
        mock_load.return_value = {"model": "config-model"}
        get_lm()
        call_args = mock_lm.call_args
        assert call_args[0][0] == "config-model"

    @patch("usepr.configs.dspy.load_config")
    @patch("dspy.LM")
    def test_default_model_used_when_no_override(
        self, mock_lm: MagicMock, mock_load: MagicMock
    ) -> None:
        mock_load.return_value = {}
        get_lm()
        call_args = mock_lm.call_args
        assert call_args[0][0] == DEFAULT_MODEL

    @patch("usepr.configs.dspy.load_config")
    @patch("dspy.LM")
    def test_cache_defaults_to_false(
        self, mock_lm: MagicMock, mock_load: MagicMock
    ) -> None:
        mock_load.return_value = {}
        get_lm()
        call_kwargs = mock_lm.call_args[1]
        assert call_kwargs["cache"] is False

    @patch("usepr.configs.dspy.load_config")
    @patch("dspy.LM")
    def test_cache_from_config(self, mock_lm: MagicMock, mock_load: MagicMock) -> None:
        mock_load.return_value = {"cache": True}
        get_lm()
        call_kwargs = mock_lm.call_args[1]
        assert call_kwargs["cache"] is True

    @patch("usepr.configs.dspy.load_config")
    @patch("dspy.LM")
    def test_extra_body_defaults(
        self, mock_lm: MagicMock, mock_load: MagicMock
    ) -> None:
        mock_load.return_value = {}
        get_lm()
        call_kwargs = mock_lm.call_args[1]
        assert call_kwargs["extra_body"] == DEFAULT_EXTRA_BODY

    @patch("usepr.configs.dspy.load_config")
    @patch("dspy.LM")
    def test_extra_body_from_config(
        self, mock_lm: MagicMock, mock_load: MagicMock
    ) -> None:
        custom_body = {"provider": {"order": ["openai"]}}
        mock_load.return_value = {"extra_body": custom_body}
        get_lm()
        call_kwargs = mock_lm.call_args[1]
        assert call_kwargs["extra_body"] == custom_body

    @patch("usepr.configs.dspy.load_config")
    @patch("dspy.LM")
    def test_extra_headers_contain_app_name(
        self, mock_lm: MagicMock, mock_load: MagicMock
    ) -> None:
        mock_load.return_value = {}
        get_lm()
        call_kwargs = mock_lm.call_args[1]
        headers = call_kwargs["extra_headers"]
        assert APPLICATION_NAME in headers["HTTP-Referer"]
        assert headers["X-Title"] == APPLICATION_NAME


# ---------------------------------------------------------------------------
# configure_dspy()
# ---------------------------------------------------------------------------


class TestConfigureDspy:
    @patch("dspy.configure")
    @patch("usepr.configs.dspy.get_lm")
    def test_calls_dspy_configure_with_lm(
        self, mock_get_lm: MagicMock, mock_configure: MagicMock
    ) -> None:
        mock_lm = MagicMock()
        mock_get_lm.return_value = mock_lm

        configure_dspy(model="test-model")

        mock_get_lm.assert_called_once_with("test-model")
        mock_configure.assert_called_once_with(lm=mock_lm)

    @patch("dspy.configure")
    @patch("usepr.configs.dspy.get_lm")
    def test_passes_none_model_by_default(
        self, mock_get_lm: MagicMock, mock_configure: MagicMock
    ) -> None:
        mock_get_lm.return_value = MagicMock()
        configure_dspy()
        mock_get_lm.assert_called_once_with(None)
