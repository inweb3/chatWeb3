"""Snowflake agent that uses a Chat model"""
import logging
from typing import Any, List, Optional, Sequence

from langchain.agents.agent import AgentExecutor, AgentOutputParser
from langchain.agents.agent_toolkits.sql.base import create_sql_agent
from langchain.agents.agent_toolkits.sql.prompt import SQL_PREFIX, SQL_SUFFIX
from langchain.agents.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain.agents.chat.base import ChatAgent

# from langchain.agents.chat.output_parser import ChatOutputParser
from langchain.agents.chat.prompt import FORMAT_INSTRUCTIONS
from langchain.callbacks.base import Callbacks
from langchain.chains.llm import LLMChain
from langchain.chat_models.base import BaseChatModel
from langchain.llms.base import BaseLLM
from langchain.schema import BaseMemory
from langchain.tools import BaseTool

# from chatweb3.agents.agent_toolkits.snowflake.prompt import (
#     SNOWFLAKE_PREFIX,
#     SNOWFLAKE_SUFFIX,
# )
from chatweb3.agents.agent import ChatWeb3AgentExecutor
from chatweb3.agents.agent_toolkits.snowflake.toolkit import SnowflakeDatabaseToolkit
from chatweb3.agents.chat.base import SnowflakeChatAgent
from chatweb3.agents.chat.output_parser import ChatWeb3ChatOutputParser
from chatweb3.agents.chat.prompt import (
    SNOWFLAKE_FORMAT_INSTRUCTIONS,
    SNOWFLAKE_HUMAN_MESSAGE,
    SNOWFLAKE_SYSTEM_MESSAGE_PREFIX,
    SNOWFLAKE_SYSTEM_MESSAGE_SUFFIX,
    SNOWFLAKE_SYSTEM_MESSAGE_SUFFIX_WITH_TOOLKIT_INSTRUCTIONS,
)
from chatweb3.agents.conversational_chat.base import SnowflakeConversationalChatAgent
from chatweb3.agents.conversational_chat.prompt import (
    CONV_SNOWFLAKE_PREFIX,
    CONV_SNOWFLAKE_SUFFIX,
)
from config.logging_config import get_logger

logger = get_logger(__name__)
# logger = get_logger(
#     __name__, log_level=logging.DEBUG, log_to_console=True, log_to_file=True
# )


def create_snowflake_conversational_chat_agent(
    # for llm chain of agent
    llm: BaseChatModel,
    # for prompt of llm chain
    prefix: str = CONV_SNOWFLAKE_PREFIX,
    suffix: str = CONV_SNOWFLAKE_SUFFIX,
    # format_instructions: Optional[str] = None,
    input_variables: Optional[List[str]] = None,
    top_k: int = 10,
    # system_template: Optional[str] = None,
    # human_template: Optional[str] = None,
    # shared by agent and agent executor chain
    tools: Optional[Sequence[BaseTool]] = None,
    toolkit: Optional[SnowflakeDatabaseToolkit] = None,
    # for agent
    output_parser: Optional[AgentOutputParser] = None,
    # for agent executor
    max_iterations: Optional[int] = 10,
    max_execution_time: Optional[float] = 20,
    early_stopping_method: Optional[str] = "force",
    return_intermediate_steps: Optional[bool] = False,
    # for chains
    # callbacks: Optional[List[BaseCallbackHandler]] = None,
    callbacks: Optional[Callbacks] = None,
    verbose: Optional[bool] = False,
    memory: Optional[BaseMemory] = None,
    # additional kwargs
    toolkit_kwargs: Optional[dict] = None,
    prompt_kwargs: Optional[dict] = None,
    agent_executor_kwargs: Optional[dict] = None,
    agent_kwargs: Optional[dict] = None,
    llm_chain_kwargs: Optional[dict] = None,
    # **kwargs: Any,
    # ) -> AgentExecutor:
) -> ChatWeb3AgentExecutor:
    """
    Construct a sql chat agent from an LLM and tools.
    """
    # get tools
    # if tools is None then get tools from toolkit
    if tools is None:
        if toolkit is None:
            raise ValueError("Must provide either tools or toolkit")
        else:
            toolkit_kwargs = toolkit_kwargs or {}
            tools = toolkit.get_tools(
                callbacks=callbacks, verbose=verbose, **toolkit_kwargs
            )
    else:
        if toolkit is not None:
            raise ValueError("Cannot provide both tools and toolkit, choose one")
    # output parser
    output_parser = (
        output_parser or SnowflakeConversationalChatAgent._get_default_output_parser()
    )
    # prompt for llm chain
    prompt_kwargs = prompt_kwargs or {}

    if toolkit is not None:
        prefix = prefix.format(dialect=toolkit.dialect, top_k=top_k)
    #     toolkit_instructions = toolkit.instructions
    # else:
    #     toolkit_instructions = None

    prompt = SnowflakeConversationalChatAgent.create_prompt(
        tools,
        # toolkit_instructions=toolkit_instructions,
        system_message=prefix,
        human_message=suffix,
        input_variables=input_variables,
        output_parser=output_parser,
        # prefix=prefix,
        # suffix=suffix,
        # format_instructions=format_instructions if format_instructions else None
        # system_template=system_template,
        # human_template=human_template,
        **prompt_kwargs,
    )
    # llm chain
    llm_chain_kwargs = llm_chain_kwargs or {}
    verbose = False if verbose is None else verbose
    llm_chain = LLMChain(
        llm=llm,
        prompt=prompt,
        # memory=memory,
        callbacks=callbacks,
        verbose=verbose,
        **llm_chain_kwargs,
    )
    # agent
    agent_kwargs = agent_kwargs or {}
    tool_names = [tool.name for tool in tools]
    agent = SnowflakeConversationalChatAgent(
        llm_chain=llm_chain,
        allowed_tools=tool_names,
        output_parser=output_parser,
        **agent_kwargs,
        # **kwargs,
    )
    # agent executor
    agent_executor_kwargs = agent_executor_kwargs or {}
    return ChatWeb3AgentExecutor.from_agent_and_tools(
        agent=agent,
        tools=tools,
        max_iterations=max_iterations,
        max_execution_time=max_execution_time,
        early_stopping_method=early_stopping_method,
        return_intermediate_steps=return_intermediate_steps,
        memory=memory,
        callbacks=callbacks,
        verbose=verbose,
        **agent_executor_kwargs,
    )


def create_snowflake_chat_agent(
    # shared by agent and agent executor chain
    toolkit: SnowflakeDatabaseToolkit,
    # for llm chain of agent
    llm: BaseChatModel,
    # for prompt of llm chain
    system_message_prefix: str = SNOWFLAKE_SYSTEM_MESSAGE_PREFIX,
    system_message_suffix: str = SNOWFLAKE_SYSTEM_MESSAGE_SUFFIX_WITH_TOOLKIT_INSTRUCTIONS,
    human_message: str = SNOWFLAKE_HUMAN_MESSAGE,
    format_instructions: str = SNOWFLAKE_FORMAT_INSTRUCTIONS,
    input_variables: Optional[List[str]] = None,
    top_k: int = 10,
    # system_template: Optional[str] = None,
    # human_template: Optional[str] = None,
    # for agent
    output_parser: AgentOutputParser = ChatWeb3ChatOutputParser(),
    # for agent executor
    max_iterations: Optional[int] = 10,
    max_execution_time: Optional[float] = 20,
    early_stopping_method: Optional[str] = "force",
    return_intermediate_steps: Optional[bool] = False,
    # for chains
    # callbacks: Optional[List[BaseCallbackHandler]] = None,
    callbacks: Optional[Callbacks] = None,
    verbose: Optional[bool] = False,
    memory: Optional[BaseMemory] = None,
    # additional kwargs
    toolkit_kwargs: Optional[dict] = None,
    prompt_kwargs: Optional[dict] = None,
    agent_executor_kwargs: Optional[dict] = None,
    agent_kwargs: Optional[dict] = None,
    llm_chain_kwargs: Optional[dict] = None,
    # **kwargs: Any,
    # ) -> AgentExecutor:
) -> ChatWeb3AgentExecutor:
    """
    Construct a sql chat agent from an LLM and tools.
    """
    # tools from toolkit
    toolkit_kwargs = toolkit_kwargs or {}
    tools = toolkit.get_tools(callbacks=callbacks, verbose=verbose, **toolkit_kwargs)
    # prompt for llm chain
    prompt_kwargs = prompt_kwargs or {}
    system_message_prefix = system_message_prefix.format(
        dialect=toolkit.dialect, top_k=top_k
    )
    # if isinstance(toolkit, CustomSnowflakeDatabaseToolkit):
    #     instructions = toolkit.instructions
    # else:
    #     instructions = ""
    prompt = SnowflakeChatAgent.create_prompt(
        tools,
        # toolkit_instructions=instructions,
        system_message_prefix=system_message_prefix,
        system_message_suffix=system_message_suffix,
        human_message=human_message,
        format_instructions=format_instructions,
        input_variables=input_variables,
        # system_template=system_template,
        # human_template=human_template,
        **prompt_kwargs,
    )
    # llm chain
    llm_chain_kwargs = llm_chain_kwargs or {}
    verbose = False if verbose is None else verbose
    llm_chain = LLMChain(
        llm=llm,
        prompt=prompt,
        memory=memory,
        callbacks=callbacks,
        verbose=verbose,
        **llm_chain_kwargs,
    )
    # agent
    agent_kwargs = agent_kwargs or {}
    tool_names = [tool.name for tool in tools]
    agent = SnowflakeChatAgent(
        llm_chain=llm_chain,
        allowed_tools=tool_names,
        output_parser=output_parser,
        **agent_kwargs,
        # **kwargs,
    )
    # agent executor
    agent_executor_kwargs = agent_executor_kwargs or {}
    return ChatWeb3AgentExecutor.from_agent_and_tools(
        agent=agent,
        tools=tools,
        max_iterations=max_iterations,
        max_execution_time=max_execution_time,
        early_stopping_method=early_stopping_method,
        return_intermediate_steps=return_intermediate_steps,
        memory=memory,
        callbacks=callbacks,
        verbose=verbose,
        **agent_executor_kwargs,
    )


def create_snowflake_agent(
    llm: BaseLLM,
    toolkit: SnowflakeDatabaseToolkit,
    # callbacks: Optional[List[BaseCallbackHandler]] = None,
    callbacks: Optional[Callbacks] = None,
    prefix: str = SNOWFLAKE_SYSTEM_MESSAGE_PREFIX,
    suffix: str = SNOWFLAKE_SYSTEM_MESSAGE_SUFFIX,
    format_instructions: str = FORMAT_INSTRUCTIONS,
    input_variables: Optional[List[str]] = None,
    top_k: int = 10,
    max_iterations: Optional[int] = 15,
    max_execution_time: Optional[float] = None,
    early_stopping_method: str = "force",
    verbose: bool = False,
    **kwargs: Any,
) -> AgentExecutor:
    # ) -> ChatWeb3AgentExecutor:
    return create_sql_agent(
        llm=llm,
        toolkit=toolkit,
        callbacks=callbacks,
        prefix=prefix,
        suffix=suffix,
        format_instructions=format_instructions,
        input_variables=input_variables,
        top_k=top_k,
        max_iterations=max_iterations,
        max_execution_time=max_execution_time,
        early_stopping_method=early_stopping_method,
        verbose=verbose,
        **kwargs,
    )


def create_sql_chat_agent(
    # shared by agent and agent executor chain
    toolkit: SQLDatabaseToolkit,
    # for llm chain of agent
    llm: BaseChatModel,
    # for prompt of llm chain
    prefix: str = SQL_PREFIX,
    suffix: str = SQL_SUFFIX,
    format_instructions: str = FORMAT_INSTRUCTIONS,
    input_variables: Optional[List[str]] = None,
    top_k: int = 10,
    # for agent
    output_parser: AgentOutputParser = ChatWeb3ChatOutputParser(),
    # for agent executor
    max_iterations: Optional[int] = 10,
    max_execution_time: Optional[float] = 20,
    early_stopping_method: Optional[str] = "force",
    return_intermeidate_steps: Optional[bool] = False,
    # for chains
    # callbacks: Optional[List[BaseCallbackHandler]] = None,
    callbacks: Optional[Callbacks] = None,
    verbose: Optional[bool] = False,
    # memory: Optional[BaseMemory] = None,
    # additional kwargs
    # toolkit_kwargs: Optional[dict] = None,
    # prompt_kwargs: Optional[dict] = None,
    # agent_executor_kwargs: Optional[dict] = None,
    # agent_kwargs: Optional[dict] = None,
    # llm_chain_kwargs: Optional[dict] = None,
    **kwargs: Any,
) -> AgentExecutor:
    # ) -> ChatWeb3AgentExecutor:
    """
    Construct a sql chat agent from an LLM and tools.
    """
    tools = toolkit.get_tools()
    prefix = prefix.format(dialect=toolkit.dialect, top_k=top_k)
    prompt = ChatAgent.create_prompt(
        tools,
        system_message_prefix=prefix,
        system_message_suffix=suffix,
        format_instructions=format_instructions,
        input_variables=input_variables,
        #    **prompt_kwargs,
    )
    verbose = False if verbose is None else verbose
    llm_chain = LLMChain(
        llm=llm,
        prompt=prompt,
        callbacks=callbacks,
        verbose=verbose,
    )
    tool_names = [tool.name for tool in tools]
    agent = ChatAgent(
        llm_chain=llm_chain,
        allowed_tools=tool_names,
        output_parser=output_parser,
    )
    return ChatWeb3AgentExecutor.from_agent_and_tools(
        agent=agent,
        tools=tools,
        max_iterations=max_iterations,
        max_execution_time=max_execution_time,
        early_stopping_method=early_stopping_method,
        return_intermeidate_steps=return_intermeidate_steps,
        callbacks=callbacks,
        verbose=verbose,
    )
