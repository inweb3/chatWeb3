"""
test_chat.py
This file contains the tests for the main chat module.
"""
import os
from unittest.mock import Mock

from chat_ui import (
    chat,
    format_response,
    set_openai_api_key,
    split_thought_process_text,
)


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


def test_format_response():
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
