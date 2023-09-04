from langchain.agents.conversational_chat.output_parser import ConvoOutputParser

from chatweb3.agents.conversational_chat.prompt import (
    CONV_SNOWFLAKE_FORMAT_INSTRUCTIONS,
)


class ChatWeb3ChatConvoOutputParser(ConvoOutputParser):
    # overwrite format instructions
    def get_format_instructions(self) -> str:
        return CONV_SNOWFLAKE_FORMAT_INSTRUCTIONS
