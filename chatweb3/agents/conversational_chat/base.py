"""Base class for snowflake conversational chat agents."""
from typing import Sequence, Optional, List, Any
from chatweb3.agents.conversational_chat.output_parser import (
    ChatWeb3ChatConvoOutputParser,
)
from langchain.agents.agent import AgentOutputParser
from langchain.prompts.base import BasePromptTemplate
from langchain.prompts.chat import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
    SystemMessagePromptTemplate,
)
from langchain.tools import BaseTool


# from chatweb3.agents.agent_toolkits.snowflake.prompt import (
#     CONV_SNOWFLAKE_PREFIX,
#     CONV_SNOWFLAKE_SUFFIX,
# )
from chatweb3.agents.conversational_chat.prompt import (
    CONV_SNOWFLAKE_PREFIX,
    CONV_SNOWFLAKE_SUFFIX,
)
from langchain.agents.conversational_chat.base import ConversationalChatAgent
from langchain.schema import BaseOutputParser
import logging
from config.logging_config import get_logger

logger = get_logger(
    __name__, log_level=logging.DEBUG, log_to_console=True, log_to_file=True
)


class SnowflakeConversationalChatAgent(ConversationalChatAgent):
    @classmethod
    def _get_default_output_parser(cls, **kwargs: Any) -> AgentOutputParser:
        return ChatWeb3ChatConvoOutputParser()

    # @classmethod
    # def create_prompt(
    #     cls,
    #     tools: Sequence[BaseTool],
    #     system_message: str = CONV_SNOWFLAKE_PREFIX,
    #     human_message: str = CONV_SNOWFLAKE_SUFFIX,
    #     input_variables: Optional[List[str]] = None,
    #     output_parser: Optional[BaseOutputParser] = None,
    # ) -> BasePromptTemplate:
    #     tool_strings = "\n".join(
    #         [f"> {tool.name}: {tool.description}" for tool in tools]
    #     )
    #     tool_names = ", ".join([tool.name for tool in tools])
    #     _output_parser = output_parser or cls._get_default_output_parser()
    #     logger.debug(f"_output_parser: {_output_parser}")
    #     logger.debug(f"{_output_parser.get_format_instructions()=}")
    #     logger.debug(f"{human_message=}")
    #     format_instructions = human_message.format(
    #         format_instructions=_output_parser.get_format_instructions()
    #     )
    #     final_prompt = format_instructions.format(
    #         tool_names=tool_names, tools=tool_strings
    #     )
    #     if input_variables is None:
    #         input_variables = ["input", "chat_history", "agent_scratchpad"]
    #     messages = [
    #         SystemMessagePromptTemplate.from_template(system_message),
    #         MessagesPlaceholder(variable_name="chat_history"),
    #         HumanMessagePromptTemplate.from_template(final_prompt),
    #         MessagesPlaceholder(variable_name="agent_scratchpad"),
    #     ]
    #     return ChatPromptTemplate(input_variables=input_variables, messages=messages)

    # @classmethod
    # def create_prompt(
    #     cls,
    #     tools: Sequence[BaseTool],
    #     toolkit_instructions: Optional[str] = "",
    #     system_message: str = CONV_SNOWFLAKE_PREFIX,
    #     human_message: str = CONV_SNOWFLAKE_SUFFIX,
    #     input_variables: Optional[List[str]] = None,
    #     output_parser: Optional[BaseOutputParser] = None,
    #     format_instructions: Optional[str] = None,
    # ) -> BasePromptTemplate:
    #     """Create a prompt template for the Snowflake conversational chat agent."""
    #     # tool descriptions
    #     tool_strings = "\n".join(
    #         [f"> {tool.name}: {tool.description}" for tool in tools]
    #     )
    #     if toolkit_instructions:
    #         tool_strings += f"\n{toolkit_instructions}"
    #     # tool names
    #     tool_names = ", ".join([tool.name for tool in tools])
    #     # set up the output parser
    #     _output_parser = output_parser or cls._get_default_output_parser()
    #     human_message_final_prompt = human_message
    #     system_message_final_prompt = system_message
    #     # fill in the format instructions
    #     # if "{format_instructions}" in human_message:
    #     print(f"\nXXX {_output_parser=}")
    #     print(f"\nXXX{_output_parser.get_format_instructions()=}")
    #     # format_instructions = _output_parser.get_format_instructions()
    #     print(f"\nXXX{format_instructions=}")

    #     human_message_format_instructions = human_message.format(
    #         format_instructions=_output_parser.get_format_instructions()
    #         if not format_instructions
    #         else format_instructions
    #     )
    #     # fill in the tools
    #     if "{tools}" in human_message:
    #         human_message_final_prompt = human_message_format_instructions.format(
    #             tool_names=tool_names, tools=tool_strings
    #         )
    #     else:
    #         raise ValueError(
    #             "{format_instructions} in human message but {tools} are not, yet to be implemented"
    #         )
    #     # elif "{format_instructions}" in system_message:
    #     #     system_message_format_instructions = system_message.format(
    #     #         format_instructions=_output_parser.get_format_instructions()
    #     #         if not format_instructions
    #     #         else format_instructions
    #     #     )
    #     #     # fill in the tools
    #     #     if "{tools}" in system_message:
    #     #         system_message_final_prompt = system_message_format_instructions.format(
    #     #             tool_names=tool_names, tools=tool_strings
    #     #         )
    #     #     else:
    #     #         raise ValueError(
    #     #             "{format_instructions} in system message but {tools} are not, yet to be implemented"
    #     #         )
    #     # else:
    #     #     Warning("Format_instructions not found in system_message or human_message")

    #     if input_variables is None:
    #         input_variables = ["input", "chat_history", "agent_scratchpad"]
    #     messages = [
    #         SystemMessagePromptTemplate.from_template(system_message_final_prompt),
    #         MessagesPlaceholder(variable_name="chat_history"),
    #         HumanMessagePromptTemplate.from_template(human_message_final_prompt),
    #         MessagesPlaceholder(variable_name="agent_scratchpad"),
    #     ]
    #     return ChatPromptTemplate(input_variables=input_variables, messages=messages)

    # @classmethod
    # def create_prompt(
    #     cls,
    #     tools: Sequence[BaseTool],
    #     toolkit_instructions: Optional[str] = "",
    #     system_message: str = CONV_SNOWFLAKE_PREFIX,
    #     human_message: str = CONV_SNOWFLAKE_SUFFIX,
    #     input_variables: Optional[List[str]] = None,
    #     output_parser: Optional[BaseOutputParser] = None,
    #     format_instructions: Optional[str] = None,
    # ) -> BasePromptTemplate:
    #     """Create a prompt template for the Snowflake conversational chat agent."""
    #     # tool descriptions
    #     tool_strings = "\n".join(
    #         [f"> {tool.name}: {tool.description}" for tool in tools]
    #     )
    #     if toolkit_instructions:
    #         tool_strings += f"\n{toolkit_instructions}"
    #     # tool names
    #     tool_names = ", ".join([tool.name for tool in tools])
    #     # set up the output parser
    #     _output_parser = output_parser or cls._get_default_output_parser()
    #     human_message_final_prompt = human_message
    #     system_message_final_prompt = system_message
    #     # fill in the format instructions

    #     logger.debug(f"\nXXX {format_instructions=}")
    #     logger.debug(f"\nXXX {_output_parser=}")
    #     logger.debug(f"\nXXX {_output_parser.get_format_instructions()=}")

    #     if "{format_instructions}" in human_message:
    #         logger.debug(f"\nXXX {human_message=}")
    #         logger.debug(f"\nXXX format_instructions in human_message")
    #         human_message_format_instructions = human_message.format(
    #             format_instructions=_output_parser.get_format_instructions()
    #             if not format_instructions
    #             else format_instructions
    #         )
    #         logger.debug(f"\nXXX {human_message_format_instructions=}")
    #         # fill in the tools
    #         if "{tools}" in human_message:
    #             human_message_final_prompt = human_message_format_instructions.format(
    #                 tool_names=tool_names, tools=tool_strings
    #             )
    #         else:
    #             raise ValueError(
    #                 "{format_instructions} in human message but {tools} are not, yet to be implemented"
    #             )
    #     elif "{format_instructions}" in system_message:
    #         logger.debug(f"\nXXX {system_message=}")
    #         logger.debug(f"\nXXX format_instructions in system_message")
    #         system_message_format_instructions = system_message.format(
    #             format_instructions=_output_parser.get_format_instructions()
    #             if not format_instructions
    #             else format_instructions
    #         )
    #         logger.debug(f"\nXXX {system_message_format_instructions=}")
    #         # fill in the tools
    #         if "{tools}" in system_message:
    #             system_message_final_prompt = system_message_format_instructions.format(
    #                 tool_names=tool_names, tools=tool_strings
    #             )
    #         else:
    #             raise ValueError(
    #                 "{format_instructions} in system message but {tools} are not, yet to be implemented"
    #             )
    #     else:
    #         Warning("Format_instructions not found in system_message or human_message")

    #     if input_variables is None:
    #         input_variables = ["input", "chat_history", "agent_scratchpad"]
    #     messages = [
    #         SystemMessagePromptTemplate.from_template(system_message_final_prompt),
    #         MessagesPlaceholder(variable_name="chat_history"),
    #         HumanMessagePromptTemplate.from_template(human_message_final_prompt),
    #         MessagesPlaceholder(variable_name="agent_scratchpad"),
    #     ]
    #     return ChatPromptTemplate(input_variables=input_variables, messages=messages)
