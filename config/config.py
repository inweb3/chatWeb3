"""
path: config/config.py
This file contains the configuration for the chatbot application.
"""
import os

import yaml
from dotenv import load_dotenv

load_dotenv()


class Config:
    PLUGIN_MODE = True  # whether we are running as chatgpt plugin mode or not

    def __init__(self, config_file):
        with open(config_file, "r") as f:
            self.config = yaml.safe_load(f)
        self.config["proj_root_dir"] = os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))
        )
        # self.config["tool"]["query_database_tool_return_direct"] = (
        #     True if self.config["tool"]["query_database_tool_top_k"] > 10 else False
        # )

        # Load from environment variables
        self.config["snowflake_params"] = {
            "user": os.getenv("SNOWFLAKE_USER"),
            "password": os.getenv("SNOWFLAKE_PASSWORD"),
            "account_identifier": os.getenv("SNOWFLAKE_ACCOUNT_IDENTIFIER"),
        }
        self.config["flipside_params"] = {
            "flipside_api_key": os.getenv("FLIPSIDE_API_KEY"),
        }
        self.config["shroomdk_params"] = {
            "shroomdk_api_key": os.getenv("SHROOMDK_API_KEY"),
        }

    def get(self, path, default=None):
        keys = path.split(".")
        value = self.config
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
            else:
                return default
        return value

    def set(self, path, value):
        keys = path.split(".")
        current_level = self.config
        for key in keys[:-1]:
            current_level = current_level.setdefault(key, {})
        current_level[keys[-1]] = value


agent_config = Config(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.yaml")
)
