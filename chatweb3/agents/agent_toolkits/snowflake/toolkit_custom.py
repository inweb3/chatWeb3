# path: chatweb3/agents/agent_toolkits/snowflake/toolkit_custom.py

from typing import List, Optional

from langchain.callbacks.base import Callbacks
from langchain.chains.llm import LLMChain
from langchain.prompts.chat import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
from langchain.tools import BaseTool
from pydantic import Field

from chatweb3.agents.agent_toolkits.snowflake.toolkit import SnowflakeDatabaseToolkit
from chatweb3.callbacks.logger_callback import LoggerCallbackHandler
from chatweb3.tools.snowflake_database.prompt import (
    SNOWFLAKE_QUERY_CHECKER,
    TOOLKIT_INSTRUCTIONS,
)
from chatweb3.tools.snowflake_database.tool_custom import (
    CheckQuerySyntaxTool,
    CheckTableMetadataTool,
    CheckTableSummaryTool,
    QueryDatabaseTool,
)
from config.config import agent_config
from config.logging_config import get_logger

logger = get_logger(__name__)

# logfile = os.path.join(os.path.dirname(__file__), "logs", "agent.log")
# logger.add(logfile, colorize=True, enqueue=True)
log_callback_handler = LoggerCallbackHandler()
callbacks = [log_callback_handler]


class CustomSnowflakeDatabaseToolkit(SnowflakeDatabaseToolkit):
    """Toolkit for interacting with FPS databases."""

    instructions = Field(default=TOOLKIT_INSTRUCTIONS)

    def get_tools(
        self,
        # callback_manager: Optional[BaseCallbackManager] = None,
        # callbacks: Optional[List[BaseCallbackHandler]] = callbacks,  # type: ignore[arg-type, assignment]
        callbacks: Optional[Callbacks] = callbacks,  # type: ignore[assignment]
        verbose: Optional[bool] = False,
        # input_variables: Optional[List[str]] = None,
        **kwargs,
    ) -> List[BaseTool]:
        """Get the tools available in the toolkit.
        Returns:
            The tools available in the toolkit.
        """

        # if input_variables is None:
        input_variables = ["query", "dialect"]
        messages = [
            SystemMessagePromptTemplate.from_template(template=SNOWFLAKE_QUERY_CHECKER),
            HumanMessagePromptTemplate.from_template(template="\n\n{query}"),
        ]

        verbose = False if verbose is None else verbose

        checker_llm_chain = LLMChain(
            llm=self.llm,
            prompt=ChatPromptTemplate(
                input_variables=input_variables,
                messages=messages,  # type: ignore[arg-type]
            ),
            # callback_manager=callback_manager,
            callbacks=callbacks,
            verbose=verbose,
        )

        query_database_tool_return_direct = agent_config.get(
            "tool.query_database_tool_return_direct"
        )
        # logger.debug(f"{query_database_tool_return_direct=}")

        return [
            CheckTableSummaryTool(
                # db=self.db, callback_manager=callback_manager, verbose=verbose  # type: ignore[call-arg, arg-type]
                db=self.db,
                callbacks=callbacks,
                verbose=verbose,  # type: ignore[call-arg, arg-type]
            ),
            CheckTableMetadataTool(
                db=self.db,
                callbacks=callbacks,
                verbose=verbose  # type: ignore[call-arg, arg-type]
                # callback_manager=callback_manager,
            ),
            CheckQuerySyntaxTool(  # type: ignore[call-arg]
                db=self.db,  # type: ignore[arg-type]
                template=SNOWFLAKE_QUERY_CHECKER,
                llm=self.llm,
                llm_chain=checker_llm_chain,
                # callback_manager=callback_manager,
                callbacks=callbacks,
                verbose=verbose,
            ),
            QueryDatabaseTool(  # type: ignore[call-arg]
                db=self.db,  # type: ignore[arg-type]
                return_direct=query_database_tool_return_direct,
                # return_direct=agent_config.get(
                #     "tool.query_database_tool_return_direct"
                # ),
                # callback_manager=callback_manager,
                callbacks=callbacks,
                verbose=verbose,
            ),
        ]
