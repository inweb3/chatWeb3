# Description: This file contains the code to query crypto data from Flipside Crypto
# Path: api/services/crypto_data.py
import os

from chatweb3.create_agent import create_agent_executor
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


class CryptoDataError(Exception):
    def __init__(self, name, message):
        self.name = name
        self.message = message
        super().__init__(self.message)


def query_crypto_data_from_flipside(inp: str) -> str:
    try:
        response = agent(inp)
        answer = str(response["output"])
        thought_process = str(response.get("intermediate_steps"))
        return answer, thought_process
    except Exception as e:
        raise CryptoDataError(name="Crypto Data Error", message=str(e))


# def query_crypto_data_from_flipside(inp: str) -> str:
#     """
#     Answer a question using the agent.

#     Parameters:
#     question (str): The question to answer

#     Returns:
#     str: The answer to the question
#     """
#     answer = ""
#     thought_process = ""
#     try:
#         response = agent(inp)
#         try:
#             answer = str(response["output"])
#             logger.debug(f"answer: {answer}")
#             thought_process = str(response.get("intermediate_steps"))
#             # thought_process_text = format_response(response)
#             # history.append((inp, answer))
#         except Exception as e:
#             logger.error(
#                 f"{type(e).__name__=} exception from parsing {response=}: {e}"
#             ),
#             thought_process = f"Exception in parsing response: {e}"
#             # thought_process_text = f"Exception in parsing response: {e}"
#             # history.append((inp, thought_process_text))
#     except Exception as e:
#         logger.error(f"{type(e).__name__} exception from receiving response: {e}"),
#         thought_process = f"Exception in receiving response: {e}"
#         # thought_process_text = f"Exception in receiving response: {e}"

#     return answer, thought_process

# # XXX todo: consolidate with gradio_app.py on response formatting
