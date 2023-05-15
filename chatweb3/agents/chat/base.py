"""Base class for snowflake chat agents."""
from typing import List, Optional, Sequence, Union, cast

from langchain.agents.chat.base import ChatAgent
from langchain.agents.chat.prompt import FORMAT_INSTRUCTIONS
from langchain.prompts.base import BasePromptTemplate
from langchain.prompts.chat import (
    BaseMessagePromptTemplate,
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
from langchain.schema import BaseMessage
from langchain.tools import BaseTool

from chatweb3.agents.agent_toolkits.snowflake.prompt import (
    SNOWFLAKE_PREFIX,
    SNOWFLAKE_SUFFIX,
)


class SnowflakeChatAgent(ChatAgent):
    @classmethod
    def create_prompt(  # type: ignore[override]
        cls,
        tools: Sequence[BaseTool],
        prefix: str = SNOWFLAKE_PREFIX,
        suffix: str = SNOWFLAKE_SUFFIX,
        format_instructions: str = FORMAT_INSTRUCTIONS,
        toolkit_instructions: Optional[str] = "",
        input_variables: Optional[List[str]] = None,
        system_template: Optional[str] = None,
        human_template: Optional[str] = None,
        # **kwargs: Any,
    ) -> BasePromptTemplate:
        """Create a prompt template for the Snowflake chat agent."""
        tool_strings = "\n".join([f"{tool.name}: {tool.description}" for tool in tools])
        if toolkit_instructions:
            tool_strings += f"\n{toolkit_instructions}"
        tool_names = ", ".join([tool.name for tool in tools])
        format_instructions = format_instructions.format(tool_names=tool_names)
        if system_template is None:
            system_template = "\n\n".join(
                [prefix, tool_strings, format_instructions, suffix]
            )
        if human_template is None:
            human_template = "Question: {input}\n\n{agent_scratchpad}"
        messages = [
            SystemMessagePromptTemplate.from_template(system_template),
            HumanMessagePromptTemplate.from_template(human_template),
        ]
        if input_variables is None:
            input_variables = ["input", "agent_scratchpad"]
        return ChatPromptTemplate(
            input_variables=input_variables,
            messages=cast(
                List[Union[BaseMessagePromptTemplate, BaseMessage]], messages
            ),
        )
