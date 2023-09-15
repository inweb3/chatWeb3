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

    expected_response = "**Thought 1**: I need to find the table that contains trading volume data on Uniswap. I should start by checking the available tables.\n\n*Action:*\n\nTool: check_available_tables_summary\n\nTool input: \n\n*Observation*: 'ethereum.core.dim_labels': the 'dim_labels' table in 'core' schema of 'ethereum' database. This table contains labels for addresses on the Ethereum Blockchain.\n  \n  'ethereum.core.ez_current_balances': the 'ez_current_balances' table in 'core' schema of 'ethereum' database.\n\n**Thought 2**: I need to check the metadata details of the 'ez_dex_swaps' table to see if it contains the trading volume data on Uniswap.\n\n*Action:*\n\nTool: check_table_metadata_details\n\nTool input: ethereum.core.ez_dex_swaps\n\n*Observation*: 'ethereum.core.ez_dex_swaps': the 'ez_dex_swaps' table in 'core' schema of 'ethereum' database. \n  Comment: This table currently contains swap events from the fact_event_logs table for Uniswap V2, Uniswap V3, SushiSwap, Curve, Balancer, and Synthetix along with other helpful columns including an amount USD where possible. Other dexes coming soon!\n\n**Thought 3**: I have found the 'ez_dex_swaps' table in the 'ethereum.core' schema of the 'ethereum' database. This table contains swap events for Uniswap V2, Uniswap V3, SushiSwap, Curve, Balancer, and Synthetix, along with other helpful columns including the amount of tokens put into the swap converted to USD using the price of the token (amount_in_usd) and the amount of tokens taken out of or received from the swap converted to USD using the price of the token (amount_out_usd).\n  \n  Note: I am assuming\n\n*Action:*\n\nTool: query_snowflake_database\n\nTool input: {'query': \"SELECT SUM(amount_in_usd) + SUM(amount_out_usd) AS total_volume FROM ethereum.core.ez_dex_swaps WHERE DATE_TRUNC('day', block_timestamp) = DATE_TRUNC('day', CURRENT_DATE() - INTERVAL '1' DAY) AND platform = 'uniswap-v2'\"}\n\n*Observation*: Exception: Flipside query attempt 1 error: QUERY_RUN_EXECUTION_ERROR: an error has occured while executing your query.\n\n**Thought 4**: There seems to be a syntax error in the query. I should double-check the syntax using the check_snowflake_query_syntax tool.\n\n*Action:*\n\nTool: check_snowflake_query_syntax\n\nTool input: SELECT SUM(amount_in_usd) + SUM(amount_out_usd) AS total_volume FROM ethereum.core.ez_dex_swaps WHERE DATE_TRUNC('day', block_timestamp) = DATE_TRUNC('day', CURRENT_DATE() - INTERVAL '1' DAY) AND platform = 'uniswap-v2'\n\n*Observation*: SELECT SUM(amount_in_usd) + SUM(amount_out_usd) AS total_volume \n  FROM ethereum.core.ez_dex_swaps \n  WHERE DATE_TRUNC('day', block_timestamp) = DATE_TRUNC('day', DATEADD(DAY, -1, CURRENT_DATE())) \n  AND platform = 'uniswap-v2'\n\n**Thought 5**: Could not parse LLM output: The corrected query to calculate yesterday's total trading volume on Uniswap in USD is:\n  \n  \n  SELECT SUM(amount_in_usd) + SUM(amount_out_usd) AS total_volume \n  FROM ethereum.core.ez_dex_swaps \n  WHERE DATE_TRUNC('day', block_timestamp) = DATE_TRUNC('day', DATEADD(DAY, -1, CURRENT_DATE())) \n  AND platform = 'uniswap-v2'\n\n*Action:*\n\nTool: _Exception\n\nTool input: Invalid or incomplete response\n\n*Observation*: Invalid or incomplete response\n\n**Final answer**: Unfortunately, this question requires many thought steps that exceeded the context window length supported by the current AI model. Please try a different question, or a model that supports a larger context window needs to be used. \n\n Raw Error: \"This model's maximum context length is 4097 tokens. However, you requested 4272 tokens (4016 in the messages, 256 in the completion). Please reduce the length of the messages or completion.\""  # noqa: E501

    formatted_response = format_response(response)
    print(f"{formatted_response=}")
    assert formatted_response == expected_response

    expected_response_markdown = "**Thought 1**: I need to find the table that contains trading volume data on Uniswap. I should start by checking the available tables.\n\nAction:\n```\n{\n  \"action\": \"check_available_tables_summary\",\n  \"action_input\": \"\"\n}\n```\n\n*Observation*: 'ethereum.core.dim_labels': the 'dim_labels' table in 'core' schema of 'ethereum' database. This table contains labels for addresses on the Ethereum Blockchain.\n  \n  'ethereum.core.ez_current_balances': the 'ez_current_balances' table in 'core' schema of 'ethereum' database.\n\n**Thought 2**: I need to check the metadata details of the 'ez_dex_swaps' table to see if it contains the trading volume data on Uniswap.\n\nAction:\n```\n{\n  \"action\": \"check_table_metadata_details\",\n  \"action_input\": \"ethereum.core.ez_dex_swaps\"\n}\n```\n\n\n\n*Observation*: 'ethereum.core.ez_dex_swaps': the 'ez_dex_swaps' table in 'core' schema of 'ethereum' database. \n  Comment: This table currently contains swap events from the fact_event_logs table for Uniswap V2, Uniswap V3, SushiSwap, Curve, Balancer, and Synthetix along with other helpful columns including an amount USD where possible. Other dexes coming soon!\n\n**Thought 3**: I have found the 'ez_dex_swaps' table in the 'ethereum.core' schema of the 'ethereum' database. This table contains swap events for Uniswap V2, Uniswap V3, SushiSwap, Curve, Balancer, and Synthetix, along with other helpful columns including the amount of tokens put into the swap converted to USD using the price of the token (`amount_in_usd`) and the amount of tokens taken out of or received from the swap converted to USD using the price of the token (`amount_out_usd`).\n\nNote: I am assuming\n\n*Observation*: Exception: Flipside query attempt 1 error: QUERY_RUN_EXECUTION_ERROR: an error has occured while executing your query.\n\n**Thought 4**: There seems to be a syntax error in the query. I should double-check the syntax using the `check_snowflake_query_syntax` tool.\n\nAction:\n```\n{\n  \"action\": \"check_snowflake_query_syntax\",\n  \"action_input\": \"SELECT SUM(amount_in_usd) + SUM(amount_out_usd) AS total_volume FROM ethereum.core.ez_dex_swaps WHERE DATE_TRUNC('day', block_timestamp) = DATE_TRUNC('day', CURRENT_DATE() - INTERVAL '1' DAY) AND platform = 'uniswap-v2'\"\n}\n```\n\n\n\n*Observation*: SELECT SUM(amount_in_usd) + SUM(amount_out_usd) AS total_volume \n  FROM ethereum.core.ez_dex_swaps \n  WHERE DATE_TRUNC('day', block_timestamp) = DATE_TRUNC('day', DATEADD(DAY, -1, CURRENT_DATE())) \n  AND platform = 'uniswap-v2'\n\n**Thought 5**: Could not parse LLM output: The corrected query to calculate yesterday's total trading volume on Uniswap in USD is:\n\n```\nSELECT SUM(amount_in_usd) + SUM(amount_out_usd) AS total_volume \nFROM ethereum.core.ez_dex_swaps \nWHERE DATE_TRUNC('day', block_timestamp) = DATE_TRUNC('day', DATEADD(DAY, -1, CURRENT_DATE())) \nAND platform = 'uniswap-v2'\n```\n\nAction:\n```\n{\n  \"action\": \"query_snowflake_database\",\n  \"action_input\": {\n    \"query\": \"SELECT SUM(amount_in_usd) + SUM(amount_out_usd) AS total_volume FROM ethereum.core.ez_dex_swaps WHERE DATE_TRUNC('day', block_timestamp) = DATE_TRUNC('day', DATEADD(DAY, -1, CURRENT_DATE())) AND platform = 'uniswap-v2'\"\n  }\n}\n```\n\n\n\n*Observation*: Invalid or incomplete response\n\n**Final answer**: Unfortunately, this question requires many thought steps that exceeded the context window length supported by the current AI model. Please try a different question, or a model that supports a larger context window needs to be used. \n\n Raw Error: \"This model's maximum context length is 4097 tokens. However, you requested 4272 tokens (4016 in the messages, 256 in the completion). Please reduce the length of the messages or completion.\""
    formatted_response_markdown = format_response(response, mode="markdown")
    assert formatted_response_markdown == expected_response_markdown


# def test_format_response():
#     if CONVERSATION_MODE:
#         # Test data
#         response = {
# @pytest.mark.skip("this test has been obsoleted by the new format_response function")
# def test_format_response():
#     if CONVERSATION_MODE:
#         # Test data
#         response = {
#             "input": "What is yesterday's total trading volume on Uniswap in USD?",
#             "chat_history": [
#                 HumanMessage(
#                     content="What is yesterday's total trading volume on Uniswap in USD?"
#                 ),
#                 AIMessage(content="I don't know"),
#             ],
#             "output": "I don't know",
#             "intermediate_steps": [
#                 (
#                     AgentAction(
#                         tool="check_available_tables_summary",
#                         tool_input="",
#                         log='{\n    "action": "check_available_tables_summary",\n    "action_input": ""\n}',
#                     ),
#                     "'ethereum.core.dim_labels': the 'dim_labels' table in 'core' schema of 'ethereum' database. This table contains labels for addresses on the Ethereum Blockchain.\n\n... etc.",
#                 )
#             ],
#         }
#         expected_output = "**HumanMessage**: What is yesterday's total trading volume on Uniswap in USD?\n\n**AIMessage**: I don't know\n\n*Action*: check_available_tables_summary\n\n*Observation*: 'ethereum.core.dim_labels': the 'dim_labels' table in 'core' schema of 'ethereum' database. This table contains labels for addresses on the Ethereum Blockchain.\n  \n  ... etc."
#         output = format_response(response)
#         print(f"{output=}")
#         assert output == expected_output
#     else:
#         step1 = Mock()
#         step1.log = "Thought: step1\nAction: "
#         step1.tool = None
#         step1.tool_input = None

#         step2 = Mock()
#         step2.log = "Thought: step2\nAction: "
#         step2.tool = None
#         step2.tool_input = None

#         response = {
#             "output": "output",
#             "intermediate_steps": [
#                 (step1, "step1_text"),
#                 (step2, "step2_text"),
#             ],
#         }
#         # expected_output = "**Thought 1**: step1\n\n*Action:*\n\nTool: \n\nTool input: \n\n*Observation:*\n\nstep1_text\n\n**Thought 2**: Thought: step2\n\n*Action:*\n\nTool: \n\nTool input: \n\n*Observation:*\n\nstep2_text\n\n**Final answer**: output"
#         expected_output = "**Thought 1**: step1\n\n*Action:*\n\nTool: None\n\nTool input: None\n\n*Observation:*\n\nstep1_text\n\n**Thought 2**: Thought: step2\n\n*Action:*\n\nTool: None\n\nTool input: None\n\n*Observation:*\n\nstep2_text\n\n**Final answer**: output"
#         output = format_response(response)
#         print(f"{output=}")
#         assert output == expected_output
#         # # Test when agent_action.tool and agent_action.tool_input are long strings
#         # step = Mock()
#         # step.log = "Thought: step\nAction: "
#         # step.tool = "a" * 100  # Long string
#         # step.tool_input = "b" * 100  # Long string
#         # response = {
#         #     "output": "output",
#         #     "intermediate_steps": [(step, "step_text")],
#         # }
#         # output = format_response(response)
#         # assert "a" * 80 in output  # First line of the split string
#         # assert "a" * 20 in output  # Second line of the split string
#         # assert "b" * 80 in output  # First line of the split string
#         # assert "b" * 20 in output  # Second line of the split string

#         # # Test when agent_action.tool and agent_action.tool_input are None
#         # step.tool = None
#         # step.tool_input = None
#         # output = format_response(response)
#         # assert (
#         #     "Tool: \n\nTool input: " in output
#         # )  # Check that None is replaced with an empty string

#         # # Test when agent_action.tool and agent_action.tool_input are not strings
#         # step.tool = 123
#         # step.tool_input = 456
#         # output = format_response(response)
#         # assert (
#         #     "Tool: 123\n\nTool input: 456" in output
#         # )  # Check that non-string objects are converted to strings

# Actual pytest
# @pytest.mark.skipif(
#     not CONVERSATION_MODE, reason="test only applicable in conversational_chat mode"
# )
# @pytest.mark.skip
# def test_format_response_chat_conversational():
#     global CONVERSATION_MODE
#     CONVERSATION_MODE = True  # Ensure the CONVERSATION_MODE is set to True
#     output = format_response(response)
#     print(f"{output=}")
#     assert output == expected_output


# @pytest.mark.skipif(CONVERSATION_MODE, reason="test only applicable in chat mode")
# @pytest.mark.skip
# def test_format_response_chat():
#     step1 = Mock()
#     step1.log = "Thought: step1\nAction: "
#     step1.tool = None
#     step1.tool_input = None

#     step2 = Mock()
#     step2.log = "Thought: step2\nAction: "
#     step2.tool = None
#     step2.tool_input = None

#     response = {
#         "output": "output",
#         "intermediate_steps": [
#             (step1, "step1_text"),
#             (step2, "step2_text"),
#         ],
#     }
#     expected_output = "**Thought 1**: step1\n\n*Action:*\n\n\tTool: None\n\n\tTool input: None\n\n*Observation:*\n\nstep1_text\n\n**Thought 2**: Thought: step2\n\n*Action:*\n\n\tTool: None\n\n\tTool input: None\n\n*Observation:*\n\nstep2_text\n\n**Final answer**: output"
#     assert format_response(response) == expected_output


# def test_split_thought_process_text():
#     text = "_Thought 1: Thought1\n\nAction:\n\tTool: Tool1\n\nTool input: Input1\n\nObservation:\n\tObservation1\n\n_Thought 2: Thought2\n\nAction:\n\tTool: Tool2\n\nTool input: Input2\n\nObservation:\n\tObservation2\n\n_Final answer_: FinalAnswer"
#     expected_sections = [
#         (" 1: Thought1", "Tool: Tool1\n\nTool input: Input1", "Observation1\n\n"),
#         (" 2: Thought2", "Tool: Tool2\n\nTool input: Input2", "Observation2\n\n"),
#     ]
#     expected_final_answer = "FinalAnswer"
#     sections, final_answer = split_thought_process_text(text)
#     assert sections == expected_sections
#     assert final_answer == expected_final_answer


# # Test data
# response = {
#     "input": "What is yesterday's total trading volume on Uniswap in USD?",
#     "chat_history": [
#         HumanMessage(
#             content="What is yesterday's total trading volume on Uniswap in USD?"
#         ),
#         AIMessage(content="I don't know"),
#     ],
#     "output": "I don't know",
#     "intermediate_steps": [
#         (
#             AgentAction(
#                 tool="check_available_tables_summary",
#                 tool_input="",
#                 log='{\n    "action": "check_available_tables_summary",\n    "action_input": ""\n}',
#             ),
#             "'ethereum.core.dim_labels': the 'dim_labels' table in 'core' schema of 'ethereum' database. This table contains labels for addresses on the Ethereum Blockchain.\n\n... etc.",
#         )
#     ],
# }
