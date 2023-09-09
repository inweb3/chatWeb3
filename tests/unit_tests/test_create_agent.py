"""
test_create_agent.py
This file contains the tests for the create_agent module.
"""
from unittest.mock import Mock, patch

from chatweb3.create_agent import create_agent_executor


@patch("chatweb3.create_agent.create_snowflake_chat_agent")
@patch("chatweb3.create_agent.CustomSnowflakeDatabaseToolkit")
@patch("chatweb3.create_agent.SnowflakeContainer")
@patch("chatweb3.create_agent.ChatOpenAI")
def test_create_agent_executor(
    mock_chat_openai,
    mock_snowflake_container,
    mock_snowflake_toolkit,
    mock_create_snowflake_chat_agent,
):
    mock_agent_executor = Mock()
    mock_create_snowflake_chat_agent.return_value = mock_agent_executor

    agent_executor = create_agent_executor()

    assert agent_executor == mock_agent_executor
