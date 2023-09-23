# Description: This file contains the output parser for the chat agent.
# Path: chatweb3/agents/chat/output_parser.py
from langchain.agents.chat.output_parser import ChatOutputParser, FINAL_ANSWER_ACTION
import json
import re
from typing import Union
from json.decoder import JSONDecodeError

from langchain.schema import AgentAction, AgentFinish, OutputParserException

from chatweb3.agents.chat.prompt import SNOWFLAKE_FORMAT_INSTRUCTIONS


class ChatWeb3ChatOutputParser(ChatOutputParser):
    def get_format_instructions(self) -> str:
        return SNOWFLAKE_FORMAT_INSTRUCTIONS

    def parse(self, text: str) -> Union[AgentAction, AgentFinish]:
        includes_answer = FINAL_ANSWER_ACTION in text

        # List of patterns to try in order
        patterns = [
            r"Action:.*?`{3}(?:json)?\s*(.*?)\s*`{3}",  # with Action: and backticks
            r"`{3}(?:json)?\s*(.*?)\s*`{3}",  # just the backticks
            r"({\s*\"action\".*?})",  # any JSON-like block
        ]

        for pattern in patterns:
            found = re.search(pattern, text, re.DOTALL)
            if found:
                try:
                    action = found.group(1)
                    response = json.loads(action)
                    return AgentAction(
                        response["action"], response.get("action_input", {}), text
                    )
                except JSONDecodeError:
                    # If this pattern fails, we continue to the next pattern
                    continue

        # If none of the patterns matched and parsed correctly, we handle it as before
        if not includes_answer:
            raise OutputParserException(f"Could not parse LLM output: {text}")
        output = text.split(FINAL_ANSWER_ACTION)[-1].strip()
        return AgentFinish({"output": output}, text)
