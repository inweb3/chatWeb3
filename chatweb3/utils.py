"""
utils.py
This file contains the utility functions for the chatweb3 package.
"""
import datetime
import re
import warnings
from decimal import Decimal
from typing import Dict, List, Optional
from config.config import agent_config
from langchain.schema import AgentAction

CONVERSATION_MODE = agent_config.get("agent.conversational_chat")


def clean_text(text):
    text = re.sub(r"`|\\", "", str(text))  # remove problematic characters
    return text.strip().replace("\n", "\n  ")


def format_agent_action(agent_action_data, step_number, mode="string"):
    # print(f"{agent_action_data=}, {step_number=}")
    if mode == "string":
        tool = agent_action_data.tool
        tool_input = agent_action_data.tool_input
        log_text = clean_text(agent_action_data.log)

        if not log_text.startswith("Thought:"):
            log_text = "Thought: " + log_text

        # Now, since we ensured 'Thought:' is present,
        # we can extract the text between 'Thought:' and 'Action:'
        thought_text = log_text.split("Thought:")[1].split("Action:")[0].strip()

        agent_action_text = (
            f"**Thought {step_number}**: {thought_text}"
            f"\n\n*Action:*\n\nTool: {tool}"
            f"\n\nTool input: {tool_input}"
        )
    elif mode == "markdown":
        log_text = agent_action_data.log
        if log_text.startswith("Thought:"):
            log_text = log_text[len("Thought:") :].strip()
        agent_action_text = f"**Thought {step_number}**: {log_text}"
    else:
        raise ValueError(f"Unknown format_agent_action mode: {mode}")

    # print(f"{agent_action_text=}")
    return agent_action_text


def format_observation(observation, mode="string"):
    # print(f"{observation=}")
    if isinstance(observation, list):
        # print(f"observation is a list")
        # formatted_observation = "\n".join(
        #     [f"*Observation*: {clean_text(item)}" for item in observation]
        # )  # noqa: E501
        if mode == "string":
            formatted_observation = "\n".join(
                [f"{clean_text(item)}" for item in observation]
            )
            formatted_observation = f"*Observation*:\n{formatted_observation}"
        elif mode == "markdown":
            formatted_observation = f"*Observation*: {observation}"
        else:
            raise ValueError(f"Unknown format_observation mode: {mode}")
        # print(f"{formatted_observation=}")
    else:
        # print(f"observation is not a list")
        if mode == "string":
            formatted_observation = f"*Observation*: {clean_text(observation)}"
        elif mode == "markdown":
            formatted_observation = f"*Observation*: {observation}"
        else:
            raise ValueError(f"Unknown format_observation mode: {mode}")

        # print(f"{formatted_observation=}")

    observation_text = formatted_observation
    # observation_text = formatted_observation.replace("*Observation*: ", "")
    return observation_text

    # return formatted_observation.replace("*Observation*: ", "")


def format_response(response: dict, mode: str = "string") -> tuple:
    formatted_steps = []
    for i, step in enumerate(response["intermediate_steps"], start=1):
        # print(f"{i=}, {step=}")
        if isinstance(step[0], AgentAction):
            # print(f"step[0] is an AgentAction")
            formatted_steps.append(format_agent_action(step[0], i, mode=mode))
            # print(f"{formatted_steps=}")
            for item in step[1:]:
                formatted_steps.append(format_observation(item))
                # print(f"{formatted_steps=}")
        else:
            formatted_steps.append(format_observation(step[0]))
            # print(f"{formatted_steps=}")

    formatted_output = "\n\n".join(formatted_steps)
    # print(f"{formatted_output=}")

    if CONVERSATION_MODE:
        # print(f"CONVERSATION_MODE is True")
        chat_messages = "\n\n".join(
            [
                f"**{msg.__class__.__name__}**: {msg.content}"
                for msg in response.get("chat_history", [])
            ]
        )
        formatted_output = f"{chat_messages}\n\n{formatted_output}"
        # print(f"{formatted_output=}")
    else:
        # print(f"CONVERSATION_MODE is False")
        formatted_output += f"\n\n**Final answer**: {response['output']}"
        # print(f"{formatted_output=}")

    # return formatted_output
    query = ""
    # Extract the last AgentAction from the intermediate_steps
    last_step = response["intermediate_steps"][-1]
    last_agent_action = None
    for step_item in last_step:
        if isinstance(step_item, AgentAction):
            last_agent_action = step_item
            break

    # # Extract the query from the last AgentAction
    # if last_agent_action:
    #     query = last_agent_action.tool_input.get("query", "")

    # Extract the query from the last AgentAction
    if last_agent_action:
        if isinstance(last_agent_action.tool_input, dict):
            query = last_agent_action.tool_input.get("query", "")
        elif isinstance(last_agent_action.tool_input, str):
            query = last_agent_action.tool_input

    return formatted_output, query


def check_table_long_name(table_name_input):
    parts = table_name_input.split(".")
    if len(parts) != 3:
        raise ValueError(
            f"Invalid table name format. Expected table long name format: 'database_name.schema_name.table_name', got: {table_name_input}"
        )


def parse_table_long_name(table_long_name: str):
    pattern = r"(?P<database>[\w]+)\.(?P<schema>[\w]+)\.(?P<table>[\w]+)"
    match = re.match(pattern, table_long_name)

    if match:
        database = match.group("database")
        schema = match.group("schema")
        table = match.group("table")
        return database, schema, table
    else:
        raise ValueError("Invalid table long name format.")


def format_dict_to_string(d: dict) -> str:
    return ", ".join([f"{k}={v!r}" for k, v in d.items()])


def convert_rows_to_serializable(rows):
    converted_rows = []
    for row in rows:
        converted_row = []
        for item in row:
            if isinstance(item, datetime.datetime):
                item = item.isoformat()
            elif isinstance(item, datetime.date):
                item = item.isoformat()
            elif isinstance(item, Decimal):
                item = float(item)
            # Add more type conversions here as needed
            converted_row.append(item)
        converted_rows.append(converted_row)
    return converted_rows


def parse_table_long_name_to_json_list(table_long_names: str):
    """
    Parse the table long names into a list of jsons with their database_name, schema_name and table_names.
    The list should be sorted based on the database_name, then schema_name, then table_names.
    Combine the tables with the same database_name and schema_name into one json.

    Examples:

    input1: "ethereum.core.ez_dex_swaps, ethereum.core.ez_nft_mints, ethereum.core.ez_nft_transfers"
    output1: "[{"database": "ethereum", "schema": "core", "table_names": ["ez_dex_swaps", "ez_nft_mints", "ez_nft_transfers"]}]"

    input2: "ethereum.core.ez_dex_swaps, ethereum.core.ez_nft_mints, ethereum.uniswapv3.ez_swaps, ethereum.beacon_chain.fact_deposits, ethereum.uniswapv3.ez_pools"
    output2: "[
        {"database": "ethereum", "schema": "beacon_chain", "tables": ["fact_deposits"]},
        {"database": "ethereum", "schema": "core", "tables": ["ez_dex_swaps", "ez_nft_mints"]},
        {"database": "ethereum", "schema": "uniswapv3", "tables": ["ez_swaps", "ez_pools"]}]"
    """

    table_names = re.split(r",\s*", table_long_names)
    table_data: Dict[str, Dict[str, List[str]]] = {}

    for name in table_names:
        check_table_long_name(name)
        database, schema, table = name.split(".")
        if database not in table_data:
            table_data[database] = {}
        if schema not in table_data[database]:
            table_data[database][schema] = []
        table_data[database][schema].append(table)

    result = []
    for database, schemas in table_data.items():
        for schema, tables in schemas.items():
            result.append(
                {"database": database, "schema": schema, "tables": sorted(tables)}
            )

    result.sort(key=lambda x: (x["database"], x["schema"]))
    return result


def parse_str_to_dict(
    input_str: str, expected_keys: Optional[List[str]] = None
) -> Dict[str, str]:
    """Parse a string to a dictionary
    The string contains key-value pairs separated by a colon and comma.
    The keys are expected to be in the expected_keys list.
    The values are expected to be strings.
    If the value contains multiple sub-elements separated by a comma,
    the entire value is needs to be enclosed in a pair of square brackets, or quotes
    For example: tables: [table1, table2], or tables: "table1, table2", or tables: 'table1, table2'
    """

    if expected_keys is None:
        expected_keys = []

    # Split the string into key-value pairs
    # The regex is to split the string on commas
    # but not if the comma is inside square brackets or inside quotes
    key_value_pairs = [
        pair.strip()
        for pair in re.split(
            r",(?![^[]*\])(?=(?:[^']*'[^']*')*[^']*$)(?=(?:[^\"]*\"[^\"]*\")*[^\"]*$)",
            input_str,
        )
    ]

    input_dict = {}

    for pair in key_value_pairs:
        try:
            key, value = [s.strip() for s in pair.split(":")]
        except ValueError:
            raise ValueError(
                f"Error extracting key, value pair: {pair=}, {key_value_pairs=}, {input_str=}"
            )

        if (
            value.startswith("[")
            and value.endswith("]")
            or value.startswith("'")
            and value.endswith("'")
            or value.startswith('"')
            and value.endswith('"')
        ):
            # remove the square brackets or quotes if they exist
            value = value[1:-1].strip()
        input_dict[key] = value

    # Check for missing expected keys
    missing_keys = set(expected_keys) - set(input_dict.keys())
    if missing_keys:
        raise ValueError(f"Missing expected keys: {', '.join(missing_keys)}")

    # Warn for unexpected keys
    unexpected_keys = set(input_dict.keys()) - set(expected_keys)
    if unexpected_keys:
        warnings.warn(f"Unexpected keys: {', '.join(unexpected_keys)}")

    return input_dict
