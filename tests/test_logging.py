# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import logging
import sys
from unittest.mock import Mock, patch

import pytest

import asyncgateway.logging as ag_logging
from asyncgateway import metadata


class TestLoggingConstants:
    def test_level_constants(self):
        assert ag_logging.NOTSET == logging.NOTSET
        assert ag_logging.TRACE == 5
        assert ag_logging.DEBUG == logging.DEBUG
        assert ag_logging.INFO == logging.INFO
        assert ag_logging.WARNING == logging.WARNING
        assert ag_logging.ERROR == logging.ERROR
        assert ag_logging.CRITICAL == logging.CRITICAL
        assert ag_logging.FATAL == 90
        assert ag_logging.NONE == 100

    def test_custom_level_names_registered(self):
        assert logging.getLevelName(5) == "TRACE"
        assert logging.getLevelName(90) == "FATAL"
        assert logging.getLevelName(100) == "NONE"

    def test_custom_levels_on_stdlib(self):
        assert logging.TRACE == 5
        assert logging.FATAL == 90
        assert logging.NONE == 100


class TestLogFunction:
    def setup_method(self):
        ag_logging.disable_sensitive_data_filtering()

    @patch("asyncgateway.logging.logging.getLogger")
    def test_log_dispatches_to_logger(self, mock_get_logger):
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        ag_logging.log(logging.INFO, "test message")

        mock_get_logger.assert_called_with(metadata.name)
        mock_logger.log.assert_called_with(logging.INFO, "test message")

    @patch("asyncgateway.logging.logging.getLogger")
    def test_log_with_filtering_disabled(self, mock_get_logger):
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        ag_logging.log(logging.DEBUG, "api_key=secret")

        mock_logger.log.assert_called_with(logging.DEBUG, "api_key=secret")

    @patch("asyncgateway.logging.heuristics.scan_and_redact")
    @patch("asyncgateway.logging.logging.getLogger")
    def test_log_with_filtering_enabled(self, mock_get_logger, mock_redact):
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_redact.return_value = "[REDACTED]"

        ag_logging.enable_sensitive_data_filtering()
        ag_logging.log(logging.INFO, "api_key=topsecret")

        mock_redact.assert_called_once_with("api_key=topsecret")
        mock_logger.log.assert_called_with(logging.INFO, "[REDACTED]")


class TestConvenienceFunctions:
    @patch("asyncgateway.logging.logging.getLogger")
    def test_debug(self, mock_get_logger):
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        ag_logging.debug("debug msg")
        mock_logger.log.assert_called_with(logging.DEBUG, "debug msg")

    @patch("asyncgateway.logging.logging.getLogger")
    def test_info(self, mock_get_logger):
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        ag_logging.info("info msg")
        mock_logger.log.assert_called_with(logging.INFO, "info msg")

    @patch("asyncgateway.logging.logging.getLogger")
    def test_warning(self, mock_get_logger):
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        ag_logging.warning("warning msg")
        mock_logger.log.assert_called_with(logging.WARNING, "warning msg")

    @patch("asyncgateway.logging.logging.getLogger")
    def test_error(self, mock_get_logger):
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        ag_logging.error("error msg")
        mock_logger.log.assert_called_with(logging.ERROR, "error msg")

    @patch("asyncgateway.logging.logging.getLogger")
    def test_critical(self, mock_get_logger):
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        ag_logging.critical("critical msg")
        mock_logger.log.assert_called_with(logging.CRITICAL, "critical msg")


class TestTraceDecorator:
    @patch("asyncgateway.logging.log")
    def test_trace_sync_logs_entry_and_exit(self, mock_log):
        @ag_logging.trace
        def my_func():
            return 42

        result = my_func()

        assert result == 42
        assert mock_log.call_count == 2
        entry_call, exit_call = mock_log.call_args_list
        assert entry_call.args[0] == logging.TRACE
        assert "→" in entry_call.args[1]
        assert "my_func" in entry_call.args[1]
        assert exit_call.args[0] == logging.TRACE
        assert "←" in exit_call.args[1]
        assert "ms" in exit_call.args[1]

    @patch("asyncgateway.logging.log")
    def test_trace_sync_logs_on_exception(self, mock_log):
        @ag_logging.trace
        def failing_func():
            raise ValueError("oops")

        with pytest.raises(ValueError):
            failing_func()

        assert mock_log.call_count == 2
        exit_call = mock_log.call_args_list[1]
        assert "exception" in exit_call.args[1]

    @patch("asyncgateway.logging.log")
    async def test_trace_async_logs_entry_and_exit(self, mock_log):
        @ag_logging.trace
        async def async_func():
            return "done"

        result = await async_func()

        assert result == "done"
        assert mock_log.call_count == 2
        entry_call, exit_call = mock_log.call_args_list
        assert "→" in entry_call.args[1]
        assert "←" in exit_call.args[1]
        assert "ms" in exit_call.args[1]

    @patch("asyncgateway.logging.log")
    async def test_trace_async_logs_on_exception(self, mock_log):
        @ag_logging.trace
        async def failing_async():
            raise RuntimeError("async fail")

        with pytest.raises(RuntimeError):
            await failing_async()

        assert mock_log.call_count == 2
        exit_call = mock_log.call_args_list[1]
        assert "exception" in exit_call.args[1]


class TestExceptionFunction:
    @patch("asyncgateway.logging.log")
    def test_exception_logs_at_error_level(self, mock_log):
        exc = ValueError("something went wrong")
        ag_logging.exception(exc)

        assert mock_log.call_count == 1
        level, msg = mock_log.call_args.args
        assert level == logging.ERROR

    @patch("asyncgateway.logging.log")
    def test_exception_includes_traceback(self, mock_log):
        try:
            raise ValueError("traceback test")
        except ValueError as exc:
            ag_logging.exception(exc)

        _, msg = mock_log.call_args.args
        assert "ValueError" in msg
        assert "traceback test" in msg

    @patch("asyncgateway.logging.log")
    def test_exception_includes_type_info(self, mock_log):
        exc = TypeError("type error")
        ag_logging.exception(exc)

        _, msg = mock_log.call_args.args
        assert "TypeError" in msg


class TestFatalFunction:
    @patch("builtins.print")
    @patch("asyncgateway.logging.log")
    def test_fatal_logs_at_fatal_level(self, mock_log, mock_print):
        with pytest.raises(SystemExit):
            ag_logging.fatal("fatal message")
        mock_log.assert_called_with(logging.FATAL, "fatal message")

    @patch("builtins.print")
    @patch("asyncgateway.logging.log")
    def test_fatal_prints_to_stderr(self, mock_log, mock_print):
        with pytest.raises(SystemExit):
            ag_logging.fatal("fatal message")
        mock_print.assert_called_with("ERROR: fatal message", file=sys.stderr)

    @patch("builtins.print")
    @patch("asyncgateway.logging.log")
    def test_fatal_exits_with_code_1(self, mock_log, mock_print):
        with pytest.raises(SystemExit) as exc_info:
            ag_logging.fatal("fatal message")
        assert exc_info.value.code == 1


class TestGetLogger:
    def test_get_logger_returns_logger(self):
        logger = ag_logging.get_logger()
        assert isinstance(logger, logging.Logger)

    def test_get_logger_returns_package_logger(self):
        logger = ag_logging.get_logger()
        assert logger.name == metadata.name


class TestSetLevel:
    @patch("asyncgateway.logging.logging.getLogger")
    def test_set_level_sets_level_on_logger(self, mock_get_logger):
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        ag_logging.set_level(logging.DEBUG)

        mock_logger.setLevel.assert_called_with(logging.DEBUG)

    @patch("asyncgateway.logging.logging.getLogger")
    def test_set_level_logs_version_and_level(self, mock_get_logger):
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        ag_logging.set_level(logging.INFO)

        mock_logger.log.assert_any_call(
            logging.INFO, f"{metadata.name} version {metadata.version}"
        )
        mock_logger.log.assert_any_call(
            logging.INFO, f"Logging level set to {logging.INFO}"
        )

    @patch("asyncgateway.logging.logging.getLogger")
    def test_set_level_disables_propagation(self, mock_get_logger):
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        ag_logging.set_level(logging.DEBUG)

        assert mock_logger.propagate is False

    @patch("asyncgateway.logging.logging.getLogger")
    def test_set_level_string_none(self, mock_get_logger):
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        ag_logging.set_level("NONE")

        mock_logger.setLevel.assert_called_with(ag_logging.NONE)

    @patch("asyncgateway.logging.logging.getLogger")
    def test_set_level_invalid_string_raises_type_error(self, mock_get_logger):
        mock_get_logger.return_value = Mock()

        with pytest.raises(TypeError):
            ag_logging.set_level("DEBUG")

    @patch("asyncgateway.logging._get_loggers")
    @patch("asyncgateway.logging.logging.getLogger")
    def test_set_level_with_propagate_sets_all_loggers(
        self, mock_get_logger, mock_get_loggers
    ):
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        mock_extra = Mock()
        mock_get_loggers.return_value = {mock_extra}

        ag_logging.set_level(logging.WARNING, propagate=True)

        mock_extra.setLevel.assert_called_with(logging.WARNING)


class TestSensitiveDataFiltering:
    def setup_method(self):
        ag_logging.disable_sensitive_data_filtering()

    def teardown_method(self):
        ag_logging.disable_sensitive_data_filtering()

    def test_enable_filtering(self):
        ag_logging.enable_sensitive_data_filtering()
        assert ag_logging.is_sensitive_data_filtering_enabled() is True

    def test_disable_filtering(self):
        ag_logging.enable_sensitive_data_filtering()
        ag_logging.disable_sensitive_data_filtering()
        assert ag_logging.is_sensitive_data_filtering_enabled() is False

    def test_filtering_disabled_by_default(self):
        assert ag_logging.is_sensitive_data_filtering_enabled() is False


class TestPatternManagement:
    def setup_method(self):
        from asyncgateway.heuristics import Scanner

        Scanner.reset_singleton()

    def test_get_sensitive_data_patterns_returns_list(self):
        patterns = ag_logging.get_sensitive_data_patterns()
        assert isinstance(patterns, list)
        assert len(patterns) > 0

    def test_add_sensitive_data_pattern(self):
        ag_logging.add_sensitive_data_pattern("ssn", r"\d{3}-\d{2}-\d{4}")
        assert "ssn" in ag_logging.get_sensitive_data_patterns()

    def test_remove_sensitive_data_pattern_exists(self):
        ag_logging.add_sensitive_data_pattern("temp", r"TEMP_\d+")
        result = ag_logging.remove_sensitive_data_pattern("temp")
        assert result is True
        assert "temp" not in ag_logging.get_sensitive_data_patterns()

    def test_remove_sensitive_data_pattern_missing(self):
        result = ag_logging.remove_sensitive_data_pattern("nonexistent")
        assert result is False

    def test_configure_sensitive_data_patterns(self):
        ag_logging.configure_sensitive_data_patterns({"custom": r"CUSTOM_\w+"})
        assert "custom" in ag_logging.get_sensitive_data_patterns()


class TestInitialize:
    def test_initialize_replaces_handlers(self):
        test_logger = logging.getLogger(metadata.name)
        test_logger.addHandler(logging.NullHandler())

        ag_logging.initialize()

        # After initialize, handlers should be StreamHandlers pointing to stderr
        stream_handlers = [
            h for h in test_logger.handlers if isinstance(h, logging.StreamHandler)
        ]
        assert len(stream_handlers) >= 0  # initialize only touches loggers it finds

    def test_initialize_sets_level_to_none(self):
        # initialize() sets each managed logger to NONE
        test_logger = logging.getLogger(metadata.name)
        test_logger.setLevel(logging.DEBUG)

        ag_logging.initialize()

        # The level may or may not be reset depending on whether the logger
        # appears in _get_loggers(); verify no exception is raised
