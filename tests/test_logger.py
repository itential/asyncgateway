# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import logging
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

from asyncgateway import logger, metadata


class TestLogger:
    def setup_method(self):
        # Clear any existing handlers before each test
        test_logger = logging.getLogger(metadata.name)
        for handler in test_logger.handlers[:]:
            test_logger.removeHandler(handler)
        test_logger.setLevel(logging.NOTSET)

    def test_logging_constants(self):
        assert logger.NOTSET == logging.NOTSET
        assert logger.DEBUG == logging.DEBUG
        assert logger.INFO == logging.INFO
        assert logger.WARNING == logging.WARNING
        assert logger.ERROR == logging.ERROR
        assert logger.CRITICAL == logging.CRITICAL
        assert logger.FATAL == 90

    def test_fatal_level_added(self):
        assert logging.FATAL == 90
        assert logging.getLevelName(90) == "FATAL"

    @patch("asyncgateway.logger.logging.getLogger")
    def test_log_function(self, mock_get_logger):
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        logger.log(logging.INFO, "test message")

        mock_get_logger.assert_called_with(metadata.name)
        mock_logger.log.assert_called_with(logging.INFO, "test message")

    @patch("asyncgateway.logger.logging.getLogger")
    def test_debug_function(self, mock_get_logger):
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        logger.debug("debug message")
        mock_logger.log.assert_called_with(logging.DEBUG, "debug message")

    @patch("asyncgateway.logger.logging.getLogger")
    def test_info_function(self, mock_get_logger):
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        logger.info("info message")
        mock_logger.log.assert_called_with(logging.INFO, "info message")

    @patch("asyncgateway.logger.logging.getLogger")
    def test_warning_function(self, mock_get_logger):
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        logger.warning("warning message")
        mock_logger.log.assert_called_with(logging.WARNING, "warning message")

    @patch("asyncgateway.logger.logging.getLogger")
    def test_error_function(self, mock_get_logger):
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        logger.error("error message")
        mock_logger.log.assert_called_with(logging.ERROR, "error message")

    @patch("asyncgateway.logger.logging.getLogger")
    def test_critical_function(self, mock_get_logger):
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        logger.critical("critical message")
        mock_logger.log.assert_called_with(logging.CRITICAL, "critical message")

    @patch("asyncgateway.logger.log")
    def test_exception_function(self, mock_log):
        exc = ValueError("test exception")
        logger.exception(exc)
        mock_log.assert_called_with(logging.ERROR, str(exc))

    @patch("sys.exit")
    @patch("builtins.print")
    @patch("asyncgateway.logger.log")
    def test_fatal_function(self, mock_log, mock_print, mock_exit):
        logger.fatal("fatal message")

        mock_log.assert_called_with(logging.FATAL, "fatal message")
        mock_print.assert_called_with("ERROR: fatal message")
        mock_exit.assert_called_with(1)

    @patch("asyncgateway.logger.logging.getLogger")
    def test_set_level_without_propagate(self, mock_get_logger):
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        logger.set_level(logging.DEBUG, False)

        mock_logger.setLevel.assert_called_with(logging.DEBUG)
        mock_logger.log.assert_any_call(
            logging.INFO, f"asyncgateway version {metadata.version}"
        )
        mock_logger.log.assert_any_call(
            logging.INFO, f"Logging level set to {logging.DEBUG}"
        )
        mock_logger.log.assert_any_call(logging.INFO, "Logging propagation is False")

    @patch("asyncgateway.logger.logging.getLogger")
    def test_set_level_with_propagate(self, mock_get_logger):
        mock_logger = Mock()
        mock_ipsdk_logger = Mock()
        mock_get_logger.side_effect = (
            lambda name: mock_logger if name == metadata.name else mock_ipsdk_logger
        )

        logger.set_level(logging.INFO, True)

        mock_logger.setLevel.assert_called_with(logging.INFO)
        mock_ipsdk_logger.setLevel.assert_called_with(logging.INFO)
        mock_logger.log.assert_any_call(logging.INFO, "Logging propagation is True")

    def test_add_file_handler_creates_parent_dirs(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file_path = Path(temp_dir) / "subdir" / "test.log"

            logger.add_file_handler(str(log_file_path))

            assert log_file_path.parent.exists()
            assert log_file_path.exists()

    def test_add_file_handler_with_custom_level_and_format(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file_path = Path(temp_dir) / "test.log"
            custom_format = "%(levelname)s - %(message)s"

            logger.add_file_handler(str(log_file_path), logging.WARNING, custom_format)

            test_logger = logging.getLogger(metadata.name)
            file_handlers = [
                h for h in test_logger.handlers if isinstance(h, logging.FileHandler)
            ]

            assert len(file_handlers) == 1
            assert file_handlers[0].level == logging.WARNING
            assert file_handlers[0].formatter._fmt == custom_format

    def test_remove_file_handlers(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file_path1 = Path(temp_dir) / "test1.log"
            log_file_path2 = Path(temp_dir) / "test2.log"

            logger.add_file_handler(str(log_file_path1))
            logger.add_file_handler(str(log_file_path2))

            test_logger = logging.getLogger(metadata.name)
            initial_handlers = len(
                [h for h in test_logger.handlers if isinstance(h, logging.FileHandler)]
            )
            assert initial_handlers == 2

            logger.remove_file_handlers()

            remaining_handlers = len(
                [h for h in test_logger.handlers if isinstance(h, logging.FileHandler)]
            )
            assert remaining_handlers == 0

    @patch("asyncgateway.logger.set_level")
    @patch("asyncgateway.logger.add_file_handler")
    def test_configure_file_logging(self, mock_add_file_handler, mock_set_level):
        logger.configure_file_logging(
            "/tmp/test.log", logging.DEBUG, True, "custom format"
        )

        mock_set_level.assert_called_once_with(logging.DEBUG, True)
        mock_add_file_handler.assert_called_once_with(
            "/tmp/test.log", logging.DEBUG, "custom format"
        )

    def test_configure_file_logging_with_defaults(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file_path = Path(temp_dir) / "test.log"

            logger.configure_file_logging(str(log_file_path))

            test_logger = logging.getLogger(metadata.name)
            file_handlers = [
                h for h in test_logger.handlers if isinstance(h, logging.FileHandler)
            ]

            assert len(file_handlers) == 1
            assert test_logger.level == logging.INFO
