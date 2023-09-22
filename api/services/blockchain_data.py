# Description: This file contains the code to query crypto data from Flipside Crypto
# Path: api/services/blockchain_data.py
import os

from chatweb3.create_agent import create_agent_executor
from chatweb3.utils import format_response
from config.config import agent_config
from config.logging_config import get_logger

logger = get_logger(__name__)

# check if FLIPSIDE_API_KEY is set
if not os.environ.get("FLIPSIDE_API_KEY"):
    raise Exception(
        "FLIPSIDE_API_KEY is not set, \
                    please set it in .env file or in the environment variable"
    )

# check if OpenAI_API_KEY is set
if not os.environ.get("OPENAI_API_KEY"):
    raise Exception(
        "OpenAI_API_KEY is not set. "
        "Please set it in the .env file or as an environment variable."
    )

CONVERSATION_MODE = agent_config.get("agent.conversational_chat")

agent = create_agent_executor(conversation_mode=CONVERSATION_MODE)


class BlockchainDataError(Exception):
    def __init__(self, name, message):
        self.name = name
        self.message = message
        super().__init__(self.message)


def query_blockchain_data_from_flipside(inp: str) -> str:
    try:
        response = agent(inp)
        answer = str(response["output"])
        # thought_process = str(response.get("intermediate_steps"))
        thought_process, extracted_query = format_response(response)

        if extracted_query:
            answer += (
                f"\n\nThe original SQL query used is:\n```\n{extracted_query}\n```"
            )
        return answer, thought_process
    except Exception as e:
        raise BlockchainDataError(name="Blockchain Data Retrival Error", message=str(e))
