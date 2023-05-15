"""Toolkit for interacting with Snowflake databases."""

from typing import List, Optional, Union, cast

from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from langchain.callbacks.base import BaseCallbackManager
from langchain.chains.llm import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.chat_models.base import BaseChatModel
from langchain.memory.readonly import ReadOnlySharedMemory
from langchain.prompts.chat import (
    BaseMessagePromptTemplate,
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
from langchain.schema import BaseMessage
from langchain.tools import BaseTool
from pydantic import Field

from chatweb3.snowflake_database import SnowflakeContainer
from chatweb3.tools.snowflake_database.prompt import SNOWFLAKE_QUERY_CHECKER
from chatweb3.tools.snowflake_database.tool import (
    GetSnowflakeDatabaseTableMetadataTool,
    ListSnowflakeDatabaseTableNamesTool,
    QuerySnowflakeDatabaseTool,
    SnowflakeQueryCheckerTool,
)


class SnowflakeDatabaseToolkit(SQLDatabaseToolkit):
    """Snowflake database toolkit."""

    # override the db attribute to be a SnowflakeContainer
    # it contains a dictionary of SnowflakeDatabase objects
    db: SnowflakeContainer = Field(exclude=True)  # type: ignore[assignment]
    # override the llm attribute to be a ChatOpenAI object
    llm: BaseChatModel = Field(default_factory=lambda: ChatOpenAI(temperature=0))  # type: ignore[call-arg]
    readonly_shared_memory: ReadOnlySharedMemory = Field(default=None)

    def get_tools(
        self,
        callback_manager: Optional[BaseCallbackManager] = None,
        verbose: bool = False,
        **kwargs,
    ) -> List[BaseTool]:
        """Get the tools available in the toolkit.

        Returns:
            The tools available in the toolkit.
        """

        # if input_variables is None:
        messages = [
            SystemMessagePromptTemplate.from_template(template=SNOWFLAKE_QUERY_CHECKER),
            HumanMessagePromptTemplate.from_template(template="\n\n{query}"),
        ]
        input_variables = ["query", "dialect"]
        checker_llm_chain = LLMChain(
            llm=self.llm,
            prompt=ChatPromptTemplate(
                input_variables=input_variables,
                messages=cast(
                    List[Union[BaseMessagePromptTemplate, BaseMessage]], messages
                ),  # casting it for now XXX
            ),
            callback_manager=callback_manager,
            memory=self.readonly_shared_memory,
            verbose=verbose,
        )

        return [
            QuerySnowflakeDatabaseTool(db=self.db),  # type: ignore[arg-type]
            ListSnowflakeDatabaseTableNamesTool(db=self.db),  # type: ignore[arg-type]
            GetSnowflakeDatabaseTableMetadataTool(db=self.db),  # type: ignore[arg-type]
            SnowflakeQueryCheckerTool(
                db=self.db,  # type: ignore[arg-type]
                template=SNOWFLAKE_QUERY_CHECKER,
                llm=self.llm,
                llm_chain=checker_llm_chain,
                callback_manager=callback_manager,
                verbose=verbose,
            ),  # type: ignore[call-arg]
        ]
