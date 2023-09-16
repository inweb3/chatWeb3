# noqa: E501
"""
test_gradio_app.py
This file contains the tests for the main chat module.
"""
import os
from unittest.mock import Mock
import pytest

from api.gradio.gradio_app import format_response  # split_thought_process_text,
from api.gradio.gradio_app import chat, set_openai_api_key
from langchain.schema import AgentAction

# from chatweb3.chat_ui import CONVERSATION_MODE
from config.config import agent_config

CONVERSATION_MODE = agent_config.get("agent.conversational_chat")


def test_set_openai_api_key():
    original_key = os.getenv("OPENAI_API_KEY")
    api_key = "test_key"
    agent = "test_agent"
    set_openai_api_key(api_key, agent)
    assert os.getenv("OPENAI_API_KEY") == ""

    if original_key is None:
        # if the original API key was None, delete the environment variable
        del os.environ["OPENAI_API_KEY"]
    else:
        # otherwise, restore the original API key
        os.environ["OPENAI_API_KEY"] = original_key


# Mock classes
class HumanMessage:
    def __init__(self, content, additional_kwargs=None, example=False):
        self.content = content
        self.additional_kwargs = additional_kwargs or {}
        self.example = example


class AIMessage:
    def __init__(self, content, additional_kwargs=None, example=False):
        self.content = content
        self.additional_kwargs = additional_kwargs or {}
        self.example = example


# class AgentAction:
#     def __init__(self, tool, tool_input, log):
#         self.tool = tool
#         self.tool_input = tool_input
#         self.log = log


def test_chat():
    inp = "test_input"
    history = [("question", "answer")]
    agent = None
    new_history, _, _ = chat(inp, history, agent)
    assert new_history == [
        ("question", "answer"),
        ("test_input", "Please paste your OpenAI API Key to use"),
    ]


def test_format_response_non_conversation_chat_mode():
    response = {
        "input": "What is yesterday's total trading volume on Uniswap in USD?",
        "output": 'Unfortunately, this question requires many thought steps that exceeded the context window length supported by the current AI model. Please try a different question, or a model that supports a larger context window needs to be used. \n\n Raw Error: "This model\'s maximum context length is 4097 tokens. However, you requested 4272 tokens (4016 in the messages, 256 in the completion). Please reduce the length of the messages or completion."',
        "intermediate_steps": [
            (
                AgentAction(
                    tool="check_available_tables_summary",
                    tool_input="",
                    log='Thought: I need to find the table that contains trading volume data on Uniswap. I should start by checking the available tables.\n\nAction:\n```\n{\n  "action": "check_available_tables_summary",\n  "action_input": ""\n}\n```',
                ),
                "'ethereum.core.dim_labels': the 'dim_labels' table in 'core' schema of 'ethereum' database. This table contains labels for addresses on the Ethereum Blockchain.\n\n'ethereum.core.ez_current_balances': the 'ez_current_balances' table in 'core' schema of 'ethereum' database.",
            ),
            (
                AgentAction(
                    tool="check_table_metadata_details",
                    tool_input="ethereum.core.ez_dex_swaps",
                    log='I need to check the metadata details of the \'ez_dex_swaps\' table to see if it contains the trading volume data on Uniswap.\n\nAction:\n```\n{\n  "action": "check_table_metadata_details",\n  "action_input": "ethereum.core.ez_dex_swaps"\n}\n```\n\n',
                ),
                "'ethereum.core.ez_dex_swaps': the 'ez_dex_swaps' table in 'core' schema of 'ethereum' database. \nComment: This table currently contains swap events from the ```fact_event_logs``` table for Uniswap V2, Uniswap V3, SushiSwap, Curve, Balancer, and Synthetix along with other helpful columns including an amount USD where possible. Other dexes coming soon!",
            ),
            (
                AgentAction(
                    tool="query_snowflake_database",
                    tool_input={
                        "query": "SELECT SUM(amount_in_usd) + SUM(amount_out_usd) AS total_volume FROM ethereum.core.ez_dex_swaps WHERE DATE_TRUNC('day', block_timestamp) = DATE_TRUNC('day', CURRENT_DATE() - INTERVAL '1' DAY) AND platform = 'uniswap-v2'"
                    },
                    log="I have found the 'ez_dex_swaps' table in the 'ethereum.core' schema of the 'ethereum' database. This table contains swap events for Uniswap V2, Uniswap V3, SushiSwap, Curve, Balancer, and Synthetix, along with other helpful columns including the amount of tokens put into the swap converted to USD using the price of the token (`amount_in_usd`) and the amount of tokens taken out of or received from the swap converted to USD using the price of the token (`amount_out_usd`).\n\nNote: I am assuming",
                ),
                [
                    "Exception: Flipside query attempt 1 error: QUERY_RUN_EXECUTION_ERROR: an error has occured while executing your query."
                ],
            ),
            (
                AgentAction(
                    tool="check_snowflake_query_syntax",
                    tool_input="SELECT SUM(amount_in_usd) + SUM(amount_out_usd) AS total_volume FROM ethereum.core.ez_dex_swaps WHERE DATE_TRUNC('day', block_timestamp) = DATE_TRUNC('day', CURRENT_DATE() - INTERVAL '1' DAY) AND platform = 'uniswap-v2'",
                    log="There seems to be a syntax error in the query. I should double-check the syntax using the `check_snowflake_query_syntax` tool.\n\nAction:\n```\n{\n  \"action\": \"check_snowflake_query_syntax\",\n  \"action_input\": \"SELECT SUM(amount_in_usd) + SUM(amount_out_usd) AS total_volume FROM ethereum.core.ez_dex_swaps WHERE DATE_TRUNC('day', block_timestamp) = DATE_TRUNC('day', CURRENT_DATE() - INTERVAL '1' DAY) AND platform = 'uniswap-v2'\"\n}\n```\n\n",
                ),
                "SELECT SUM(amount_in_usd) + SUM(amount_out_usd) AS total_volume \nFROM ethereum.core.ez_dex_swaps \nWHERE DATE_TRUNC('day', block_timestamp) = DATE_TRUNC('day', DATEADD(DAY, -1, CURRENT_DATE())) \nAND platform = 'uniswap-v2'",
            ),
            (
                AgentAction(
                    tool="_Exception",
                    tool_input="Invalid or incomplete response",
                    log="Could not parse LLM output: The corrected query to calculate yesterday's total trading volume on Uniswap in USD is:\n\n```\nSELECT SUM(amount_in_usd) + SUM(amount_out_usd) AS total_volume \nFROM ethereum.core.ez_dex_swaps \nWHERE DATE_TRUNC('day', block_timestamp) = DATE_TRUNC('day', DATEADD(DAY, -1, CURRENT_DATE())) \nAND platform = 'uniswap-v2'\n```\n\nAction:\n```\n{\n  \"action\": \"query_snowflake_database\",\n  \"action_input\": {\n    \"query\": \"SELECT SUM(amount_in_usd) + SUM(amount_out_usd) AS total_volume FROM ethereum.core.ez_dex_swaps WHERE DATE_TRUNC('day', block_timestamp) = DATE_TRUNC('day', DATEADD(DAY, -1, CURRENT_DATE())) AND platform = 'uniswap-v2'\"\n  }\n}\n```\n\n",
                ),
                "Invalid or incomplete response",
            ),
        ],
    }  # noqa: E501

    expected_response = '**Thought 1**: I need to find the table that contains trading volume data on Uniswap. I should start by checking the available tables.\n\n*Action:*\n\nTool: check_available_tables_summary\n\nTool input: \n\n*Observation*: \'ethereum.core.dim_labels\': the \'dim_labels\' table in \'core\' schema of \'ethereum\' database. This table contains labels for addresses on the Ethereum Blockchain.\n  \n  \'ethereum.core.ez_current_balances\': the \'ez_current_balances\' table in \'core\' schema of \'ethereum\' database.\n\n**Thought 2**: I need to check the metadata details of the \'ez_dex_swaps\' table to see if it contains the trading volume data on Uniswap.\n\n*Action:*\n\nTool: check_table_metadata_details\n\nTool input: ethereum.core.ez_dex_swaps\n\n*Observation*: \'ethereum.core.ez_dex_swaps\': the \'ez_dex_swaps\' table in \'core\' schema of \'ethereum\' database. \n  Comment: This table currently contains swap events from the fact_event_logs table for Uniswap V2, Uniswap V3, SushiSwap, Curve, Balancer, and Synthetix along with other helpful columns including an amount USD where possible. Other dexes coming soon!\n\n**Thought 3**: I have found the \'ez_dex_swaps\' table in the \'ethereum.core\' schema of the \'ethereum\' database. This table contains swap events for Uniswap V2, Uniswap V3, SushiSwap, Curve, Balancer, and Synthetix, along with other helpful columns including the amount of tokens put into the swap converted to USD using the price of the token (amount_in_usd) and the amount of tokens taken out of or received from the swap converted to USD using the price of the token (amount_out_usd).\n  \n  Note: I am assuming\n\n*Action:*\n\nTool: query_snowflake_database\n\nTool input: {\'query\': "SELECT SUM(amount_in_usd) + SUM(amount_out_usd) AS total_volume FROM ethereum.core.ez_dex_swaps WHERE DATE_TRUNC(\'day\', block_timestamp) = DATE_TRUNC(\'day\', CURRENT_DATE() - INTERVAL \'1\' DAY) AND platform = \'uniswap-v2\'"}\n\n*Observation*:\nException: Flipside query attempt 1 error: QUERY_RUN_EXECUTION_ERROR: an error has occured while executing your query.\n\n**Thought 4**: There seems to be a syntax error in the query. I should double-check the syntax using the check_snowflake_query_syntax tool.\n\n*Action:*\n\nTool: check_snowflake_query_syntax\n\nTool input: SELECT SUM(amount_in_usd) + SUM(amount_out_usd) AS total_volume FROM ethereum.core.ez_dex_swaps WHERE DATE_TRUNC(\'day\', block_timestamp) = DATE_TRUNC(\'day\', CURRENT_DATE() - INTERVAL \'1\' DAY) AND platform = \'uniswap-v2\'\n\n*Observation*: SELECT SUM(amount_in_usd) + SUM(amount_out_usd) AS total_volume \n  FROM ethereum.core.ez_dex_swaps \n  WHERE DATE_TRUNC(\'day\', block_timestamp) = DATE_TRUNC(\'day\', DATEADD(DAY, -1, CURRENT_DATE())) \n  AND platform = \'uniswap-v2\'\n\n**Thought 5**: Could not parse LLM output: The corrected query to calculate yesterday\'s total trading volume on Uniswap in USD is:\n  \n  \n  SELECT SUM(amount_in_usd) + SUM(amount_out_usd) AS total_volume \n  FROM ethereum.core.ez_dex_swaps \n  WHERE DATE_TRUNC(\'day\', block_timestamp) = DATE_TRUNC(\'day\', DATEADD(DAY, -1, CURRENT_DATE())) \n  AND platform = \'uniswap-v2\'\n\n*Action:*\n\nTool: _Exception\n\nTool input: Invalid or incomplete response\n\n*Observation*: Invalid or incomplete response\n\n**Final answer**: Unfortunately, this question requires many thought steps that exceeded the context window length supported by the current AI model. Please try a different question, or a model that supports a larger context window needs to be used. \n\n Raw Error: "This model\'s maximum context length is 4097 tokens. However, you requested 4272 tokens (4016 in the messages, 256 in the completion). Please reduce the length of the messages or completion."'  # noqa: E501
    
    formatted_response = format_response(response)
    print(f"{formatted_response=}")
    assert formatted_response == expected_response

    expected_response_markdown = '**Thought 1**: I need to find the table that contains trading volume data on Uniswap. I should start by checking the available tables.\n\nAction:\n```\n{\n  "action": "check_available_tables_summary",\n  "action_input": ""\n}\n```\n\n*Observation*: \'ethereum.core.dim_labels\': the \'dim_labels\' table in \'core\' schema of \'ethereum\' database. This table contains labels for addresses on the Ethereum Blockchain.\n  \n  \'ethereum.core.ez_current_balances\': the \'ez_current_balances\' table in \'core\' schema of \'ethereum\' database.\n\n**Thought 2**: I need to check the metadata details of the \'ez_dex_swaps\' table to see if it contains the trading volume data on Uniswap.\n\nAction:\n```\n{\n  "action": "check_table_metadata_details",\n  "action_input": "ethereum.core.ez_dex_swaps"\n}\n```\n\n\n\n*Observation*: \'ethereum.core.ez_dex_swaps\': the \'ez_dex_swaps\' table in \'core\' schema of \'ethereum\' database. \n  Comment: This table currently contains swap events from the fact_event_logs table for Uniswap V2, Uniswap V3, SushiSwap, Curve, Balancer, and Synthetix along with other helpful columns including an amount USD where possible. Other dexes coming soon!\n\n**Thought 3**: I have found the \'ez_dex_swaps\' table in the \'ethereum.core\' schema of the \'ethereum\' database. This table contains swap events for Uniswap V2, Uniswap V3, SushiSwap, Curve, Balancer, and Synthetix, along with other helpful columns including the amount of tokens put into the swap converted to USD using the price of the token (`amount_in_usd`) and the amount of tokens taken out of or received from the swap converted to USD using the price of the token (`amount_out_usd`).\n\nNote: I am assuming\n\n*Observation*:\nException: Flipside query attempt 1 error: QUERY_RUN_EXECUTION_ERROR: an error has occured while executing your query.\n\n**Thought 4**: There seems to be a syntax error in the query. I should double-check the syntax using the `check_snowflake_query_syntax` tool.\n\nAction:\n```\n{\n  "action": "check_snowflake_query_syntax",\n  "action_input": "SELECT SUM(amount_in_usd) + SUM(amount_out_usd) AS total_volume FROM ethereum.core.ez_dex_swaps WHERE DATE_TRUNC(\'day\', block_timestamp) = DATE_TRUNC(\'day\', CURRENT_DATE() - INTERVAL \'1\' DAY) AND platform = \'uniswap-v2\'"\n}\n```\n\n\n\n*Observation*: SELECT SUM(amount_in_usd) + SUM(amount_out_usd) AS total_volume \n  FROM ethereum.core.ez_dex_swaps \n  WHERE DATE_TRUNC(\'day\', block_timestamp) = DATE_TRUNC(\'day\', DATEADD(DAY, -1, CURRENT_DATE())) \n  AND platform = \'uniswap-v2\'\n\n**Thought 5**: Could not parse LLM output: The corrected query to calculate yesterday\'s total trading volume on Uniswap in USD is:\n\n```\nSELECT SUM(amount_in_usd) + SUM(amount_out_usd) AS total_volume \nFROM ethereum.core.ez_dex_swaps \nWHERE DATE_TRUNC(\'day\', block_timestamp) = DATE_TRUNC(\'day\', DATEADD(DAY, -1, CURRENT_DATE())) \nAND platform = \'uniswap-v2\'\n```\n\nAction:\n```\n{\n  "action": "query_snowflake_database",\n  "action_input": {\n    "query": "SELECT SUM(amount_in_usd) + SUM(amount_out_usd) AS total_volume FROM ethereum.core.ez_dex_swaps WHERE DATE_TRUNC(\'day\', block_timestamp) = DATE_TRUNC(\'day\', DATEADD(DAY, -1, CURRENT_DATE())) AND platform = \'uniswap-v2\'"\n  }\n}\n```\n\n\n\n*Observation*: Invalid or incomplete response\n\n**Final answer**: Unfortunately, this question requires many thought steps that exceeded the context window length supported by the current AI model. Please try a different question, or a model that supports a larger context window needs to be used. \n\n Raw Error: "This model\'s maximum context length is 4097 tokens. However, you requested 4272 tokens (4016 in the messages, 256 in the completion). Please reduce the length of the messages or completion."'  # noqa: E501
    
    formatted_response_markdown = format_response(response, mode="markdown")
    assert formatted_response_markdown == expected_response_markdown


# response = {'output': [['2023-09-16T00:00:00.000Z', 296787454.38, 0], ['2023-09-15T00:00:00.000Z', 609627053.49, 1], ['2023-09-14T00:00:00.000Z', 613539309.14, 2], ['2023-09-13T00:00:00.000Z', 691108021.87, 3], ['2023-09-12T00:00:00.000Z', 991597386.15, 4], ['2023-09-11T00:00:00.000Z', 1090563358.43, 5], ['2023-09-10T00:00:00.000Z', 555072218.97, 6], ['2023-09-09T00:00:00.000Z', 5272395.3, 7]], 'intermediate_steps': [(AgentAction(tool='_Exception', tool_input='Unable to parse output. Check your output format, especially when a valid $JSON_BLOB enclosed in triple backtick is required, make sure your output conforms!', log='Could not parse LLM output: Thought: I need to find the table that contains the trading volume data on Uniswap. Then I can construct a query to calculate the total daily trading volume in USD for the last 7 days.\n\nAction: Check available tables summary.\n'), 'Unable to parse output. Check your output format, especially when a valid $JSON_BLOB enclosed in triple backtick is required, make sure your output conforms!'), (AgentAction(tool='_Exception', tool_input='Unable to parse output. Check your output format, especially when a valid $JSON_BLOB enclosed in triple backtick is required, make sure your output conforms!', log='Could not parse LLM output: I need to check the available tables summary to find the table that contains the trading volume data on Uniswap.'), 'Unable to parse output. Check your output format, especially when a valid $JSON_BLOB enclosed in triple backtick is required, make sure your output conforms!'), (AgentAction(tool='check_available_tables_summary', tool_input='', log='I need to check the available tables summary to find the table that contains the trading volume data on Uniswap.\n\nAction:\n```json\n{\n  "action": "check_available_tables_summary",\n  "action_input": ""\n}\n```'), "'ethereum.core.dim_labels': the 'dim_labels' table in 'core' schema of 'ethereum' database. This table contains labels for addresses on the Ethereum Blockchain.\n\n'ethereum.core.ez_current_balances': the 'ez_current_balances' table in 'core' schema of 'ethereum' database. This table contains the current, non 0, balances for wallets on the Ethereum Blockchain. Symbol, name, and price are joined where possible. Prices are calculated as of the last activity date and as of the most recently recorded hourly price. ERC721s are included.\n\n'ethereum.core.ez_dex_swaps': the 'ez_dex_swaps' table in 'core' schema of 'ethereum' database. This table currently contains swap events for Uniswap V2, Uniswap V3, SushiSwap, Curve, Balancer, and Synthetix along with other helpful columns. Other dexes coming soon!\n\n'ethereum.core.ez_token_transfers': the 'ez_token_transfers' table in 'core' schema of 'ethereum' database. This table contains all events in the `ethereum.core.fact_token_transfers` table, along with joined columns such as token price, symbol, and decimals where possible that allow for easier analysis of token transfer events. Please note Native ETH transfers are not included here."), (AgentAction(tool='check_table_metadata_details', tool_input='ethereum.core.ez_dex_swaps', log='I have found the table that contains the trading volume data on Uniswap. It is called \'ez_dex_swaps\' in the \'core\' schema of the \'ethereum\' database. Now I can construct a query to calculate the total daily trading volume in USD for the last 7 days.\n\nAction:\n```json\n{\n  "action": "check_table_metadata_details",\n  "action_input": "ethereum.core.ez_dex_swaps"\n}\n```\n\n'), '\'ethereum.core.ez_dex_swaps\': the \'ez_dex_swaps\' table in \'core\' schema of \'ethereum\' database. \nComment: This table currently contains swap events from the ```fact_event_logs``` table for Uniswap V2, Uniswap V3, SushiSwap, Curve, Balancer, and Synthetix along with other helpful columns including an amount USD where possible. Other dexes coming soon! \nNote: A rule has been put in place to null out the amount_USD if that number is too divergent between amount_in_USD and amount_out_usd. This can happen for swaps of less liquid tokens during very high fluctuation of price.\nColumns in this table:\n\tName | Comment | Data type | List of sample values\n\t--- | --- | --- | ---\n\tamount_in | The amount of tokens put into the swap. | FLOAT | 11.569999999999999, 8.887181263806143, 105528376308547.83\n\tamount_in_usd | The amount of tokens put into the swap converted to USD using the price of the token. | FLOAT | 24544.7, 18853.35, None\n\tamount_out | The amount of tokens taken out of or received from the swap. | FLOAT | 22768727288.796886, 17006927838.52042, 0.8298762823393789\n\tamount_out_usd | The amount of tokens taken out of or received from the swap converted to USD using the price of the token. | FLOAT | None, None, 1850.12\n\tblock_number | Also known as block height. The block number, which indicates the length of the blockchain, increases after the addition of each new block. | NUMBER(38,0) | 12275337, 12275509, 12279239\n\tblock_timestamp | The date and time at which the block was produced. | TIMESTAMP_NTZ(9) | 2021-04-20T06:13:21, 2021-04-20T06:51:38, 2021-04-20T20:30:09\n\tcontract_address | The address interacted with for a given event. | VARCHAR(16777216) | 0x5d2c95651e0ee953b9abd8ec47ce2a165c852ae9, 0x5d2c95651e0ee953b9abd8ec47ce2a165c852ae9, 0x280ab9403372be0371313a9ddd9222b5590dbfef\n\tevent_index | Event number within a transaction. | FLOAT | 3.0, 158.0, 4.0\n\tevent_name | The decoded event name for a given event. | VARCHAR(16777216) | Swap, Swap, Swap\n\torigin_from_address | The from address at the transaction level. | VARCHAR(16777216) | 0xf6da21e95d74767009accb145b96897ac3630bad, 0xab104f53f80b665b206e3ed4eb24b9364c61e9fe, 0x136f4b5b6a306091b280e3f251fa0e21b1280cd5\n\torigin_function_signature | The function signature of this transaction. | VARCHAR(16777216) | 0x375734d9, 0x38ed1739, 0x791ac947\n\torigin_to_address | The to address at the transaction level. | VARCHAR(16777216) | 0xd78a3280085ee846196cb5fab7d510b279486d44, 0x7a250d5630b4cf539739df2c5dacb4c659f2488d, 0x7a250d5630b4cf539739df2c5dacb4c659f2488d\n\tplatform | This field denotes which application the liquidity pool belongs to. | VARCHAR(16777216) | uniswap-v2, uniswap-v2, uniswap-v2\n\tpool_name | None | VARCHAR(16777216) | None, None, None\n\tsender | The Router is the Sender in the swap function. | VARCHAR(16777216) | 0xd78a3280085ee846196cb5fab7d510b279486d44, 0x7a250d5630b4cf539739df2c5dacb4c659f2488d, 0x7a250d5630b4cf539739df2c5dacb4c659f2488d\n\tsymbol_in | The symbol of the token sent for swap. | VARCHAR(16777216) | WETH, WETH, JSHIBA\n\tsymbol_out | The symbol of the token being swapped to. | VARCHAR(16777216) | Pikachu, Pikachu, WETH\n\ttoken_in | The address of the token sent for swap. | VARCHAR(16777216) | 0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2, 0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2, 0x1426cc6d52d1b14e2b3b1cb04d57ea42b39c4c7c\n\ttoken_out | The address of the token being swapped to. | VARCHAR(16777216) | 0xe09fb60e8d6e7e1cebbe821bd5c3fc67a40f86bf, 0xe09fb60e8d6e7e1cebbe821bd5c3fc67a40f86bf, 0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2\n\ttx_hash | Transaction hash is a unique 66-character identifier that is generated when a transaction is executed. This field will not be unique in this table, as a given transaction can include multiple events. | VARCHAR(16777216) | 0x3aacd65f3b345bfe024b60e351b91685403da5620997a25a7c6dc1a81a86f995, 0xaa372a6a3b3b040af287d5e73d4331b2498c4c63472ab1fe238ae6d7379da781, 0xf28f18713b90ec72e23aba3fcb3206ca015626f2b7b646fc9bfc99a7926bea1c\n\ttx_to | The tx_to is the address who receives the swapped token. This corresponds to the \\"to\\" field in the swap function. | VARCHAR(16777216) | 0xf6da21e95d74767009accb145b96897ac3630bad, 0xab104f53f80b665b206e3ed4eb24b9364c61e9fe, 0x7a250d5630b4cf539739df2c5dacb4c659f2488d\n\t_log_id | This is the primary key for this table. This is a concatenation of the transaction hash and the event index at which the event occurred. This field can be used within other event based tables such as ```fact_transfers``` & ```ez_token_transfers```. | VARCHAR(16777216) | 0x3aacd65f3b345bfe024b60e351b91685403da5620997a25a7c6dc1a81a86f995-3, 0xaa372a6a3b3b040af287d5e73d4331b2498c4c63472ab1fe238ae6d7379da781-158, 0xf28f18713b90ec72e23aba3fcb3206ca015626f2b7b646fc9bfc99a7926bea1c-4'), (AgentAction(tool='query_snowflake_database', tool_input={'query': "SELECT DATE_TRUNC('day', block_timestamp) AS date, SUM(amount_in_usd) AS total_volume_usd FROM ethereum.core.ez_dex_swaps WHERE block_timestamp >= DATEADD('day', -7, CURRENT_TIMESTAMP()) GROUP BY date ORDER BY date DESC LIMIT 10"}, log='Now that I have the metadata details of the \'ez_dex_swaps\' table, I can construct a query to calculate the total daily trading volume in USD for the last 7 days.\n\nAction:\n```json\n{\n  "action": "query_snowflake_database",\n  "action_input": {\n    "query": "SELECT DATE_TRUNC(\'day\', block_timestamp) AS date, SUM(amount_in_usd) AS total_volume_usd FROM ethereum.core.ez_dex_swaps WHERE block_timestamp >= DATEADD(\'day\', -7, CURRENT_TIMESTAMP()) GROUP BY date ORDER BY date DESC LIMIT 10"\n  }\n}\n```\n\n'), [['2023-09-16T00:00:00.000Z', 296787454.38, 0], ['2023-09-15T00:00:00.000Z', 609627053.49, 1], ['2023-09-14T00:00:00.000Z', 613539309.14, 2], ['2023-09-13T00:00:00.000Z', 691108021.87, 3], ['2023-09-12T00:00:00.000Z', 991597386.15, 4], ['2023-09-11T00:00:00.000Z', 1090563358.43, 5], ['2023-09-10T00:00:00.000Z', 555072218.97, 6], ['2023-09-09T00:00:00.000Z', 5272395.3, 7]])]}