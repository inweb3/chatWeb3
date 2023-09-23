"""
logging_config.py
This file contains the code for configuring the logger.
"""
import inspect
import logging
import os
import sys
from typing import Optional

import yaml


def load_config():
    # Get the directory of the current script
    dir_path = os.path.dirname(os.path.realpath(__file__))
    config_file_path = os.path.join(dir_path, "config.yaml")  # Updated to config.yaml

    try:
        with open(config_file_path, "r") as file:
            full_config = yaml.safe_load(file)
    except Exception as e:
        raise RuntimeError(f"Failed to load the logger configuration: {e}")

    # Extract logging configurations
    logging_config = full_config.get("logging", {})
    # print(f"Logging config: {logging_config}")

    # if ENV is set, print its value
    env = os.environ.get("ENV")

    acceptable_envs = set(logging_config.keys())
    if env:
        if env not in acceptable_envs:
            raise ValueError(f"ENV value '{env}' is not set to one of the acceptable values: {', '.join(acceptable_envs)}")
        else:
            print(f"ENV is set to: {env}")
    else:
        env = "default"
        print(f"ENV is not set, using default: {env}")

    # env = os.environ.get("ENV", "default")

    # This updates the env_config dictionary with values from default_config,
    # but only for keys that are missing in env_config.
    env_config = logging_config.get(env, {})
    # print(f"Logging config for ENV={env}: {env_config}")
    default_config = logging_config.get("default", {})
    # print(f"Default logging config: {default_config}")
    final_config = {**default_config, **env_config}
    print(f"Final config for ENV={env}: {final_config}")  # Add this print statement
    return final_config


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
    # print(
    #     f"_configure_handlers called with log_file_path: {log_file_path}"
    # )  # Debug print statement

    # Remove all existing handlers to avoid duplicates
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Set the logger's level
    logger.setLevel(log_level)
    # print(
    #     f"Set log level for logger '{logger.name}' to {log_level}"
    # )  # Add this print statement

    handlers = []

    if log_to_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        console_handler.setFormatter(logging.Formatter(log_format, datefmt=date_format))
        handlers.append(console_handler)

    if log_to_file:
        # print(f"Trying to create or open log file at: {log_file_path}")
        print(f"{log_file_path=}, set up its file handler")  # Debug print statement
        file_handler = logging.FileHandler(log_file_path)
        file_handler.setLevel(log_level)
        file_handler.setFormatter(logging.Formatter(log_format, datefmt=date_format))
        handlers.append(file_handler)

    for handler in handlers:
        logger.addHandler(handler)


def _find_project_root(start_path):
    path = os.path.dirname(start_path) if os.path.isfile(start_path) else start_path
    while (
        os.path.dirname(path) != path
    ):  # Checks if we've reached the top-most directory
        if ".projectroot" in os.listdir(path):
            # print(f"Found project root at: {path}")  # Debug print statement
            return path
        path = os.path.dirname(path)
    raise ValueError("Project root not found!")


def _get_log_file_path(config_path=None):
    # print(f"_get_log_file_path called with config_path: {config_path}")

    project_root = _find_project_root(os.path.abspath(__file__))

    if config_path:
        # If a config_path is provided, check if it's relative or absolute
        if os.path.isabs(config_path):
            log_file_path = config_path
        else:
            log_file_path = os.path.join(project_root, config_path)
        # print(f"Received Log file path from config as: {log_file_path}")

    else:
        # Define the path for the log directory
        log_directory = os.path.join(project_root, "logs")

        # Determine the project name from the project_root path
        project_name = os.path.basename(project_root)

        # Define the log file name and path
        log_file_name = f"{project_name}.log"
        log_file_path = os.path.join(log_directory, log_file_name)

        # print(f"Set Log file path to default as: {log_file_path}")

    # Make sure the directory of the log_file_path exists
    log_directory = os.path.dirname(log_file_path)  # Extract directory from the log_file_path
    try:
        os.makedirs(log_directory, exist_ok=True)
        # print(f"Successfully created or found logs directory at: {log_directory}")
    except Exception as e:
        raise RuntimeError(f"Failed to create logs directory at {log_directory}. \
                           Error: {e}")

    # Ensure the log file itself exists
    open(log_file_path, 'a').close()

    # print(f"Log file path determined as: {log_file_path}")  # Debug print statement

    return log_file_path



def get_logger(
    name: str,
    log_level: Optional[int] = None,
    log_to_console: Optional[bool] = None,
    log_to_file: Optional[bool] = None,
    log_format: Optional[str] = None,
    date_format: Optional[str] = None,
    log_file_path: Optional[str] = None,
):
    config = load_config()
    logger = logging.getLogger(name)
    # avoid relaoding the logger if it already has handlers
    # if logger.handlers:
    #     return CustomLoggerAdapter(logger, {})

    # Use provided arguments, if they exist. Otherwise, fall back to the config values.
    log_level = log_level or config["log_level"]
    # print(
    #     f"Received logger '{name}' with log_level={log_level}"
    # )  # Add this print statement
    log_to_console = (
        log_to_console if log_to_console is not None else config["log_to_console"]
    )  # noqa E501
    log_to_file = log_to_file if log_to_file is not None else config["log_to_file"]
    log_format = log_format or config["log_format"]
    date_format = date_format or config["date_format"]
    log_file_path = log_file_path or _get_log_file_path(config.get("log_file_path"))
    # log_file_path = log_file_path or config.get("log_file_path", _get_log_file_path())

    _configure_handlers(
        logger,
        log_level=log_level,
        log_to_console=log_to_console,
        log_to_file=log_to_file,
        log_format=log_format,
        date_format=date_format,
        log_file_path=log_file_path,
    )

    logger.propagate = False
    logger_adapter = CustomLoggerAdapter(logger, {})
    if logger.level == logging.DEBUG:
        logger_adapter.info(
            f"*** Initialized '{name}' LOGGER with level"
            f" {logging.getLevelName(logger.level)}\n"
        )
    return logger_adapter


def initialize_root_logger():
    config = load_config()
    log_level = config["log_level"]
    log_to_console = config["log_to_console"]
    log_to_file = config["log_to_file"]
    log_format = config["log_format"]
    date_format = config["date_format"]
    # log_file_path = config.get("log_file_path", _get_log_file_path())
    # Always pass the log_file_path from config to _get_log_file_path
    log_file_path = _get_log_file_path(config.get("log_file_path"))

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
    root_logger_adapter.info(
        f"""LOGGER initialized with the following options:
    Log level: {log_level}
    Log to console: {log_to_console}
    Log to file: {log_to_file}
    Log file path: {log_file_path}
    """
    )

    # check if log_levl is DEBUG, if so, print the config
    if log_level == logging.DEBUG:
        print(f"Initializing root logger with config: {config}")
