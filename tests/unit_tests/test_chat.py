"""
test_chat.py
This file contains the tests for the main chat module.
"""
import os
import pytest
from unittest.mock import Mock

from chat_ui import (
    chat,
    format_response,
    set_openai_api_key,
    split_thought_process_text,
)

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


class AgentAction:
    def __init__(self, tool, tool_input, log):
        self.tool = tool
        self.tool_input = tool_input
        self.log = log


# Test data
response = {
    "input": "What is yesterday's total trading volume on Uniswap in USD?",
    "chat_history": [
        HumanMessage(
            content="What is yesterday's total trading volume on Uniswap in USD?"
        ),
        AIMessage(content="I don't know"),
    ],
    "output": "I don't know",
    "intermediate_steps": [
        (
            AgentAction(
                tool="check_available_tables_summary",
                tool_input="",
                log='{\n    "action": "check_available_tables_summary",\n    "action_input": ""\n}',
            ),
            "'ethereum.core.dim_labels': the 'dim_labels' table in 'core' schema of 'ethereum' database. This table contains labels for addresses on the Ethereum Blockchain.\n\n... etc.",
        )
    ],
}


# Test data
response = {
    "input": "What is yesterday's total trading volume on Uniswap in USD?",
    "chat_history": [
        HumanMessage(
            content="What is yesterday's total trading volume on Uniswap in USD?"
        ),
        AIMessage(content="I don't know"),
    ],
    "output": "I don't know",
    "intermediate_steps": [
        (
            AgentAction(
                tool="check_available_tables_summary",
                tool_input="",
                log='{\n    "action": "check_available_tables_summary",\n    "action_input": ""\n}',
            ),
            "'ethereum.core.dim_labels': the 'dim_labels' table in 'core' schema of 'ethereum' database. This table contains labels for addresses on the Ethereum Blockchain.\n\n... etc.",
        )
    ],
}
expected_output = "**HumanMessage**: What is yesterday's total trading volume on Uniswap in USD?\n\n**AIMessage**: I don't know\n\n*Action*: check_available_tables_summary\n\n*Observation*: 'ethereum.core.dim_labels': the 'dim_labels' table in 'core' schema of 'ethereum' database. This table contains labels for addresses on the Ethereum Blockchain.\n  \n  ... etc."


# Actual pytest
@pytest.mark.skipif(
    not CONVERSATION_MODE, reason="test only applicable in conversational_chat mode"
)
def test_format_response_chat_conversational():
    global CONVERSATION_MODE
    CONVERSATION_MODE = True  # Ensure the CONVERSATION_MODE is set to True
    output = format_response(response)
    print(f"{output=}")
    assert output == expected_output


@pytest.mark.skip(reason="Need to rewrite this test to reflect the new format")
def test_format_response_chat():
    step1 = Mock()
    step1.log = "Thought: step1\nAction: "
    step1.tool = None
    step1.tool_input = None

    step2 = Mock()
    step2.log = "Thought: step2\nAction: "
    step2.tool = None
    step2.tool_input = None

    response = {
        "output": "output",
        "intermediate_steps": [
            (step1, "step1_text"),
            (step2, "step2_text"),
        ],
    }
    expected_output = "**Thought 1**: step1\n\n*Action:*\n\n\tTool: None\n\n\tTool input: None\n\n*Observation:*\n\nstep1_text\n\n**Thought 2**: Thought: step2\n\n*Action:*\n\n\tTool: None\n\n\tTool input: None\n\n*Observation:*\n\nstep2_text\n\n**Final answer**: output"
    assert format_response(response) == expected_output


def test_split_thought_process_text():
    text = "_Thought 1: Thought1\n\nAction:\n\tTool: Tool1\n\nTool input: Input1\n\nObservation:\n\tObservation1\n\n_Thought 2: Thought2\n\nAction:\n\tTool: Tool2\n\nTool input: Input2\n\nObservation:\n\tObservation2\n\n_Final answer_: FinalAnswer"
    expected_sections = [
        (" 1: Thought1", "Tool: Tool1\n\nTool input: Input1", "Observation1\n\n"),
        (" 2: Thought2", "Tool: Tool2\n\nTool input: Input2", "Observation2\n\n"),
    ]
    expected_final_answer = "FinalAnswer"
    sections, final_answer = split_thought_process_text(text)
    assert sections == expected_sections
    assert final_answer == expected_final_answer


def test_chat():
    inp = "test_input"
    history = [("question", "answer")]
    agent = None
    new_history, _, _ = chat(inp, history, agent)
    assert new_history == [
        ("question", "answer"),
        ("test_input", "Please paste your OpenAI API Key to use"),
    ]
