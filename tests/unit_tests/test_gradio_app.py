# noqa: E501
"""
test_gradio_app.py
This file contains the tests for the main chat module.
"""
import os
from unittest.mock import Mock
import pytest

from chatweb3.utils import format_response  # split_thought_process_text,
from api.gradio.gradio_app import chat, set_openai_api_key
from langchain.schema import AgentAction

# from chatweb3.chat_ui import CONVERSATION_MODE
# from config.config import agent_config


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


def test_chat():
    inp = "test_input"
    history = [("question", "answer")]
    agent = None
    new_history, _, _ = chat(inp, history, agent)
    assert new_history == [
        ("question", "answer"),
        ("test_input", "Please paste your OpenAI API Key to use"),
    ]
