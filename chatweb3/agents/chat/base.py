"""Base class for snowflake chat agents."""

from langchain.agents.chat.base import ChatAgent

# from chatweb3.agents.agent_toolkits.snowflake.prompt import (
#     SNOWFLAKE_PREFIX,
#     SNOWFLAKE_SUFFIX,
# )


class SnowflakeChatAgent(ChatAgent):
    ...
    # @classmethod
    # def create_prompt(
    #     cls,
    #     tools: Sequence[BaseTool],
    #     system_message_prefix: str = SYSTEM_MESSAGE_PREFIX,
    #     system_message_suffix: str = SYSTEM_MESSAGE_SUFFIX,
    #     human_message: str = HUMAN_MESSAGE,
    #     format_instructions: str = FORMAT_INSTRUCTIONS,
    #     input_variables: Optional[List[str]] = None,
    # ) -> BasePromptTemplate:
    #     tool_strings = "\n".join([f"{tool.name}: {tool.description}" for tool in tools])
    #     tool_names = ", ".join([tool.name for tool in tools])
    #     format_instructions = format_instructions.format(tool_names=tool_names)
    #     template = "\n\n".join(
    #         [
    #             system_message_prefix,
    #             tool_strings,
    #             format_instructions,
    #             system_message_suffix,
    #         ]
    #     )
    #     messages = [
    #         SystemMessagePromptTemplate.from_template(template),
    #         HumanMessagePromptTemplate.from_template(human_message),
    #     ]
    #     if input_variables is None:
    #         input_variables = ["input", "agent_scratchpad"]
    #     return ChatPromptTemplate(input_variables=input_variables, messages=messages)

    # @classmethod
    # def create_prompt(  # type: ignore[override]
    #     cls,
    #     tools: Sequence[BaseTool],
    #     prefix: str = SNOWFLAKE_PREFIX,
    #     suffix: str = SNOWFLAKE_SUFFIX,
    #     format_instructions: str = FORMAT_INSTRUCTIONS,
    #     toolkit_instructions: Optional[str] = "",
    #     input_variables: Optional[List[str]] = None,
    #     system_template: Optional[str] = None,
    #     human_template: Optional[str] = None,
    #     # **kwargs: Any,
    # ) -> BasePromptTemplate:
    #     """Create a prompt template for the Snowflake chat agent."""
    #     tool_strings = "\n".join([f"{tool.name}: {tool.description}" for tool in tools])
    #     if toolkit_instructions:
    #         tool_strings += f"\n{toolkit_instructions}"
    #     tool_names = ", ".join([tool.name for tool in tools])
    #     format_instructions = format_instructions.format(tool_names=tool_names)
    #     if system_template is None:
    #         system_template = "\n\n".join(
    #             [prefix, tool_strings, format_instructions, suffix]
    #         )
    #     if human_template is None:
    #         human_template = "Question: {input}\n\n{agent_scratchpad}"
    #     messages = [
    #         SystemMessagePromptTemplate.from_template(system_template),
    #         HumanMessagePromptTemplate.from_template(human_template),
    #     ]
    #     if input_variables is None:
    #         input_variables = ["input", "agent_scratchpad"]
    #     return ChatPromptTemplate(
    #         input_variables=input_variables,
    #         messages=cast(
    #             List[Union[BaseMessagePromptTemplate, BaseMessage]], messages
    #         ),
    #     )

    # @classmethod
    # def create_prompt(  # type: ignore[override]
    #     cls,
    #     tools: Sequence[BaseTool],
    #     system_message_prefix: str = SNOWFLAKE_SYSTEM_MESSAGE_PREFIX,
    #     # prefix: str = SNOWFLAKE_PREFIX,
    #     system_message_suffix: str = SNOWFLAKE_SYSTEM_MESSAGE_SUFFIX_WITH_TOOLKIT_INSTRUCTIONS,
    #     # suffix: str = SNOWFLAKE_SUFFIX,
    #     human_message: str = SNOWFLAKE_HUMAN_MESSAGE,
    #     format_instructions: str = SNOWFLAKE_FORMAT_INSTRUCTIONS,
    #     input_variables: Optional[List[str]] = None,
    #     # toolkit_instructions: Optional[str] = "",
    #     # system_template: Optional[str] = None,
    #     # human_template: Optional[str] = None,
    #     # **kwargs: Any,
    # ) -> BasePromptTemplate:
    #     """Create a prompt template for the Snowflake chat agent."""
    #     tool_strings = "\n".join([f"{tool.name}: {tool.description}" for tool in tools])
    #     # if toolkit_instructions:
    #     #     tool_strings += f"\n{toolkit_instructions}"
    #     tool_names = ", ".join([tool.name for tool in tools])
    #     format_instructions = format_instructions.format(tool_names=tool_names)
    #     template = "\n\n".join(
    #         [
    #             system_message_prefix,
    #             tool_strings,
    #             format_instructions,
    #             system_message_suffix,
    #         ]
    #     )
    #     # if system_template is None:
    #     #     system_template = "\n\n".join(
    #     #         [prefix, tool_strings, format_instructions, suffix]
    #     #     )
    #     # if human_template is None:
    #     #     human_template = "Question: {input}\n\n{agent_scratchpad}"
    #     messages = [
    #         SystemMessagePromptTemplate.from_template(template),
    #         HumanMessagePromptTemplate.from_template(human_message),
    #     ]
    #     if input_variables is None:
    #         input_variables = ["input", "agent_scratchpad"]
    #     return ChatPromptTemplate(input_variables=input_variables, messages=messages)
