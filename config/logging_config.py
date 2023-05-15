"""
logging_config.py
This file contains the code for configuring the logger.
"""
import inspect
import logging
import os
import sys
from typing import Optional


# Define CustomLoggerAdapter class
class CustomLoggerAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        class_name = ""
        for frame_info in inspect.stack()[2:]:
            frame = frame_info.frame
            local_self = frame.f_locals.get("self")

            if local_self and not isinstance(local_self, CustomLoggerAdapter):
                class_name = local_self.__class__.__name__
                break

        if class_name:
            msg = f"{class_name}: {msg}"

        return msg, kwargs


# Helper function to configure logger handlers
def _configure_handlers(
    logger,
    log_level,
    log_to_console,
    log_to_file,
    log_format,
    date_format,
    log_file_path,
):
    handlers = []

    if log_to_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        console_handler.setFormatter(logging.Formatter(log_format, datefmt=date_format))
        handlers.append(console_handler)

    if log_to_file:
        file_handler = logging.FileHandler(log_file_path)
        file_handler.setLevel(log_level)
        file_handler.setFormatter(logging.Formatter(log_format, datefmt=date_format))
        handlers.append(file_handler)

    for handler in handlers:
        logger.addHandler(handler)


def _get_log_file_path():
    # Get the path of the current module
    current_module_path = os.path.abspath(__file__)

    # Get the path of the directory where the current module is located
    config_directory = os.path.dirname(current_module_path)

    # Get the path to the project root (assuming the config directory is located one level below the project root)
    project_root = os.path.dirname(config_directory)

    # Define the path for the log directory
    log_directory = os.path.join(project_root, "logs")
    os.makedirs(log_directory, exist_ok=True)

    # Determine the project name from the project_root path
    project_name = os.path.basename(project_root)

    # Define the log file name and path
    log_file_name = f"{project_name}.log"
    log_file_path = os.path.join(log_directory, log_file_name)

    return log_file_path


# default parameters
log_level = logging.INFO
log_to_console = True
log_to_file = False
log_format = "%(asctime)s [%(name)s] [%(levelname)s] [%(module)s:%(lineno)d] [%(funcName)s]: %(message)s"
date_format = "%Y-%m-%d %H:%M:%S"
log_file_path = _get_log_file_path()

# Configure the root logger
root_logger = logging.getLogger()
_configure_handlers(
    root_logger,
    log_level=log_level,
    log_to_console=log_to_console,
    log_to_file=log_to_file,
    log_format=log_format,
    date_format=date_format,
    log_file_path=log_file_path,
)

root_logger_adapter = CustomLoggerAdapter(root_logger, {})

# Log a statement during the root logger adapter initialization
root_logger_adapter.info(
    f"""LOGGER initialized with the following options:
Log level: {log_level}
Log to console: {log_to_console}
Log to file: {log_to_file}
Log file path: {log_file_path}
"""
)


# Child loggers will inherit the attributes from the root logger unless they are explicitly overridden
def get_logger(
    name: str,
    log_level: Optional[int] = None,
    log_to_console: Optional[bool] = None,
    log_to_file: Optional[bool] = None,
    log_format: Optional[str] = None,
    date_format: Optional[str] = None,
    log_file_path: Optional[str] = None,
):
    logger = logging.getLogger(name)

    if logger.handlers:
        return CustomLoggerAdapter(logger, {})

    if log_level is not None:
        logger.setLevel(log_level)
    else:
        logger.setLevel(logging.getLogger().level)  # Inherit log level from root logger

    if log_to_file and log_file_path is None:
        log_file_path = next(
            (
                handler.baseFilename
                for handler in root_logger.handlers
                if isinstance(handler, logging.FileHandler)
            ),
            None,
        )  # Use root logger's log_file_path

    if log_to_console is None:
        log_to_console = any(
            isinstance(handler, logging.StreamHandler)
            for handler in root_logger.handlers
        )

    if log_to_file is None:
        log_to_file = any(
            isinstance(handler, logging.FileHandler) for handler in root_logger.handlers
        )

    if log_format is None:
        if root_logger.handlers[0].formatter is not None:
            log_format = root_logger.handlers[0].formatter._fmt

    if date_format is None:
        if root_logger.handlers[0].formatter is not None:
            date_format = root_logger.handlers[0].formatter.datefmt

    if log_to_file and log_file_path is None:
        log_file_path = (
            _get_log_file_path()
        )  # Assign default log file path if not found in root_logger and log_to_file is True

    _configure_handlers(
        logger,
        log_level=logger.level,
        log_to_console=log_to_console,
        log_to_file=log_to_file,
        log_format=log_format,
        date_format=date_format,
        log_file_path=log_file_path,
    )

    # Add this line to prevent propagation of log messages to ancestor loggers
    logger.propagate = False

    logger_adapter = CustomLoggerAdapter(logger, {})
    if logger.level == logging.DEBUG:
        logger_adapter.info(
            f"\n\n\n *** Initialized '{name}' LOGGER with level '{logging.getLevelName(logger.level)}'"
        )

    return logger_adapter
