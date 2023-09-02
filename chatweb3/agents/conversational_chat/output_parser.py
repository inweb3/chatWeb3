from langchain.agents.conversational_chat.output_parser import ConvoOutputParser
from chatweb3.agents.conversational_chat.prompt import CUSTOM_CONV_FORMAT_INSTRUCTIONS


class ChatWeb3ConvOutputParser(ConvoOutputParser):
    # overwrite format instructions
    def get_format_instructions(self) -> str:
        return CUSTOM_CONV_FORMAT_INSTRUCTIONS
