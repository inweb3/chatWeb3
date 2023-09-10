import logging
import os

import pytest
from config.logging_config import (
    _get_log_file_path,
    get_logger,
    initialize_root_logger,
    load_config,
)


def test_load_config():
    # Set environment variable to 'development'
    os.environ["ENV"] = "development"
    config = load_config()
    assert config["log_level"] == "DEBUG"
    assert config["log_to_console"] == True
    assert config["log_to_file"] == True

    # Set environment variable to 'production'
    os.environ["ENV"] = "production"
    config = load_config()
    assert config["log_level"] == "WARNING"
    assert config["log_to_console"] == False
    assert config["log_to_file"] == True

    # Unset environment variable to fall back to 'default'
    del os.environ["ENV"]
    config = load_config()
    assert config["log_level"] == "INFO"
    assert config["log_to_console"] == True
    assert config["log_to_file"] == True


def test_log_file_path_generation():
    path = _get_log_file_path()
    assert "logs" in path  # the path contains 'logs' directory
    assert path.endswith(".log")  # the path ends with '.log'


def test_logger_initialization(clean_logging):
    original_env = os.environ.get("ENV")
    logger = get_logger("test_logger")
    assert isinstance(logger, logging.LoggerAdapter)
    assert len(logger.logger.handlers) >= 1  # logger has at least one handler

    # Ensure correct log level
    os.environ["ENV"] = "development"
    logger = get_logger("test_logger_dev")
    assert logger.logger.level == logging.DEBUG

    os.environ["ENV"] = "production"
    logger = get_logger("test_logger_prod")
    assert logger.logger.level == logging.WARNING

    os.environ["ENV"] = original_env or "default"


def test_initialize_root_logger(clean_logging):
    initialize_root_logger()
    root_logger = logging.getLogger()
    assert len(root_logger.handlers) >= 1  # root logger has at least one handler
    assert isinstance(
        root_logger.handlers[0].formatter, logging.Formatter
    )  # handler has a formatter
