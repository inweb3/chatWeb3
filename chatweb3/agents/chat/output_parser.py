from langchain.agents.chat.output_parser import ChatOutputParser

from chatweb3.agents.chat.prompt import SNOWFLAKE_FORMAT_INSTRUCTIONS


class ChatWeb3ChatOutputParser(ChatOutputParser):
    def get_format_instructions(self) -> str:
        return SNOWFLAKE_FORMAT_INSTRUCTIONS
