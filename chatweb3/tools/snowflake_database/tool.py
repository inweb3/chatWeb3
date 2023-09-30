import json
import logging
import re
from typing import Any, Dict, List, Optional, Union

from langchain.base_language import BaseLanguageModel
from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
from langchain.chains.llm import LLMChain
from langchain.chat_models.base import BaseChatModel
from langchain.prompts.chat import (
    BaseChatPromptTemplate,
    BaseMessagePromptTemplate,
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
from langchain.schema import BaseMessage
from langchain.tools.sql_database.tool import (
    InfoSQLDatabaseTool,
    ListSQLDatabaseTool,
    QuerySQLCheckerTool,
    QuerySQLDataBaseTool,
)
from pydantic import Field, root_validator

from chatweb3.snowflake_database import SnowflakeContainer
from chatweb3.tools.base import BaseToolInput
from chatweb3.tools.snowflake_database.prompt import SNOWFLAKE_QUERY_CHECKER
from chatweb3.utils import parse_table_long_name_to_json_list  # parse_str_to_dict
from config.config import agent_config
from config.logging_config import get_logger
from langchain.tools.base import ToolException

from flipside.errors import (
    QueryRunCancelledError,
    QueryRunExecutionError,
    QueryRunTimeoutError,
    SDKError,
)

from chatweb3.tools.snowflake_database.constants import (
    LIST_SNOWFLAKE_DATABASE_TABLE_NAMES_TOOL_NAME,
    GET_SNOWFLAKE_DATABASE_TABLE_METADATA_TOOL_NAME,
    QUERY_SNOWFLAKE_DATABASE_TOOL_NAME,
    SNOWFLAKE_QUERY_CHECKER_TOOL_NAME,
    SELECT_SNOWFLAKE_DATABASE_SCHEMA_TOOL_NAME,
)

logger = get_logger(__name__)
# logger = get_logger(
#     __name__, log_level=logging.DEBUG, log_to_console=True, log_to_file=True
# )


# LIST_SNOWFLAKE_DATABASE_TABLE_NAMES_TOOL_NAME = "list_snowflake_db_table_names"
# GET_SNOWFLAKE_DATABASE_TABLE_METADATA_TOOL_NAME = "get_snowflake_db_table_metadata"
# QUERY_SNOWFLAKE_DATABASE_TOOL_NAME = "query_snowflake_db"
# SNOWFLAKE_QUERY_CHECKER_TOOL_NAME = "snowflake_query_checker"
# SELECT_SNOWFLAKE_DATABASE_SCHEMA_TOOL_NAME = "select_snowflake_db_schema"


DEFAULT_DATABASE = agent_config.get("database.default_database")
DEFAULT_SCHEMA = agent_config.get("database.default_schema")

FLIPSIDE_QUERY_TIMEOUT = agent_config.get("flipside.query_timeout")
FLIPSIDE_QUERY_MAX_RETRIES = agent_config.get("flipside.query_max_retries")
QUERY_DATABASE_TOOL_RETURN_DIRECT_IF_SUCCESSFUL = agent_config.get(
    "tool.query_database_tool_return_direct_if_successful"
)  # noqa E501


def handle_tool_error(error: ToolException) -> str:
    if isinstance(error, QueryRunTimeoutError):
        raise (
            Exception(
                "Query timed out. The Flipside database may be temporarily unavailable. Please try again later"
            )
        )  # noqa E501
        # return (
        #     "Query timed out. The database may be temporarily unavailable. Please try again later"
        # )
    else:
        return (
            "Error during tool execution:"
            + error.args[0]
            + "Please check what you should do next."
        )


class ListSnowflakeDatabaseTableNamesToolInput(BaseToolInput):
    database_name: str = Field(
        alias="database", description="The name of the database."
    )
    schema_name: str = Field(alias="schema", description="The name of the schema.")


class ListSnowflakeDatabaseTableNamesTool(ListSQLDatabaseTool):
    db: SnowflakeContainer = Field(exclude=True)  # type: ignore

    name = LIST_SNOWFLAKE_DATABASE_TABLE_NAMES_TOOL_NAME
    description = """
    Input is an empty string, output is a list of tables in long form, e.g., 'ethereum.core.ez_nft_sales' means the 'ez_nft_sales' table in 'core' schema of 'ethereum' database, and optionally with their brief summary information.
    """

    def _get_table_long_names_from_snowflake(self, tool_input: str) -> str:
        database = DEFAULT_DATABASE
        schema = DEFAULT_SCHEMA

        # Locate the SQLDatabase object with the given database and schema
        snowflake_database = self.db.get_database(database, schema)

        # Call its get_table_names() method
        table_names = snowflake_database.get_usable_table_names()

        # Add the database and schema to the table names
        table_long_names = [f"{database}.{schema}.{table}" for table in table_names]

        return ", ".join(table_long_names)

    def _run(
        self,
        tool_input: str = "",
        run_manager: Optional[CallbackManagerForToolRun] = None,
        mode: str = "default",
    ) -> str:
        """Get available tables in the databases

        mode:
        - "default": use local index to get the info, if not found, use snowflake as fallback
        - "snowflake": use snowflake to get the info
        - "local": use local index to get the info

        Note: since local index is currently enforced by the table_long_names_enabled variable, while snowflake is enforced by its own Magicdatabase and MagicSchema, the two modes often produce different results.

        """
        logger.debug(
            f"Entering list snowflake database table names tool _run with tool_input: {tool_input} and mode: {mode}"
        )

        if mode not in ["local", "snowflake", "default"]:
            raise ValueError(f"Invalid mode: {mode}")

        table_long_names_enabled_list = agent_config.get(
            "ethereum_core_table_long_name.enabled_list"
        )

        table_long_names_enabled = ", ".join(table_long_names_enabled_list)
        include_column_names = False
        # include_column_names = True
        include_column_info = False

        if mode == "local":
            # use local index to get the info
            return self.db.metadata_parser.get_metadata_by_table_long_names(
                table_long_names=table_long_names_enabled,
                include_column_names=include_column_names,
                include_column_info=include_column_info,
            )

        if mode == "snowflake":
            return self._get_table_long_names_from_snowflake(tool_input=tool_input)

        # default mode
        # use local index to get the info, if not found, use snowflake as fallback
        if mode == "default":
            try:
                # logger.debug(f"mode: {mode}")
                result = self.db.metadata_parser.get_metadata_by_table_long_names(
                    table_long_names=table_long_names_enabled,
                    include_column_names=include_column_names,
                    include_column_info=include_column_info,
                )
                if result:
                    return result
                else:
                    raise Exception("Table name list not found in local index")
            except Exception as e:
                logger.debug(f"Table name list not found in local index: {e}")
                return self._get_table_long_names_from_snowflake(tool_input=tool_input)

        return ""  # this is a dummy return, just to make mypy happy

    async def _arun(
        self,
        tool_input: str = "",
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> str:
        raise NotImplementedError("ListSQLDatabaseNameTool does not support async")


class GetSnowflakeDatabaseTableMetadataTool(InfoSQLDatabaseTool):
    """Tool for getting metadata about a SQL database schema."""

    db: SnowflakeContainer = Field(exclude=True)  # type: ignore

    name = GET_SNOWFLAKE_DATABASE_TABLE_METADATA_TOOL_NAME
    description = f"""
    Input to this tool is a list of tables specified by the long_name format (database_name.schema_name.table_name), make sure they are separated by a COMMA, not a colon or other characters!

    Output is the metadata including schema and sample rows for those tables.
    Be sure that the tables actually exist by calling {LIST_SNOWFLAKE_DATABASE_TABLE_NAMES_TOOL_NAME} first!

    Example Input: "database_name.schema_name.table_name1: database_name.schema_name.table_name2: database_name.schema_name.table_name3"
    """

    def _get_metadata_from_snowflake(self, tool_input: str) -> str:
        """First parse the input into a list of jsons with database and schema separated.
            Example:
            input: "ethereum.core.ez_dex_swaps, ethereum.core.ez_nft_mints, ethereum.uniswapv3.ez_swaps, ethereum.beacon_chain.fact_deposits, ethereum.uniswapv3.ez_pools"
            parsed_input: "[
                {"database": "ethereum", "schema": "beacon_chain", "tables": ["fact_deposits"]},
                {"database": "ethereum", "schema": "core", "tables": ["ez_dex_swaps", "ez_nft_mints"]},
                {"database": "ethereum", "schema": "uniswapv3", "tables": ["ez_swaps", "ez_pools"]}
            ]"

        Then iterate through the list and call self.db['database']['schema'].get_table_info_no_throw(tables)

        Sample final output:
        "database_name.schema_name.table_name1: metadata1;\n database_name.schema_name.table_name2: metadata2;\n database_name.schema_name.table_name3: metadata3"
        """
        input_table_json_list = parse_table_long_name_to_json_list(tool_input)
        logger.debug(
            f"Entering _get_metadata_from_snowflake with {input_table_json_list=}"
        )
        metadata_list = []
        for input_dict in input_table_json_list:
            logging.debug(f"\n{input_dict=}")
            database, schema, tables = (
                input_dict["database"],
                input_dict["schema"],
                input_dict["tables"],
            )
            snowflake_database = self.db.get_database(database, schema)
            # table_names = ", ".join(tables)
            metadata = snowflake_database.get_table_info_no_throw(
                table_names=tables, as_dict=True
            )
            assert isinstance(
                metadata, dict
            ), "Expected a dict from get_table_info_no_throw"  # make mypy happy

            logger.debug(f"\n Retrieved {metadata=}")

            # Add the formatted metadata string for each table to metadata_list
            for table, table_metadata in metadata.items():
                table_parts = table.split(".")
                table_name = table_parts[-1]
                table_schema = table_parts[-2] if len(table_parts) > 1 else schema
                table_database = table_parts[-3] if len(table_parts) > 2 else database
                # logger.debug( f"\n{table=}, {table_parts=}, {table_name=}, {table_schema=}, {table_database=}")

                formatted_metadata = (
                    f"{table_database}.{table_schema}.{table_name}: {table_metadata}"
                )
                metadata_list.append(formatted_metadata)

        return (
            ";\n\n\n".join(metadata_list)
            if len(metadata_list) > 1
            else metadata_list[0]
        )

    def _run(
        self,
        table_names: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
        mode: str = "local",
    ) -> str:
        # def _run(self, tool_input: str, mode: str = "default") -> str:
        """Get the metadata for tables in a comma-separated list.

        mode:
        - "default": use local index to get metadata, if not found, use snowflake to get metadata
        - "snowflake": use snowflake to get metadata
        - "local": use local index to get metadata

        """
        logger.debug(f"\n Entering get metadata tool _run with {table_names=}, {mode=}")

        if mode not in ["local", "snowflake", "default"]:
            raise ValueError(f"Invalid mode: {mode}")

        if mode == "local":
            # use local index to get metadata
            return self.db.metadata_parser.get_metadata_by_table_long_names(table_names)

        if mode == "snowflake":
            # use snowflake to get metadata
            return self._get_metadata_from_snowflake(table_names)

        if mode == "default":
            try:
                # use local index to get metadata
                logger.debug(f"{self.db.metadata_parser=}")
                result = self.db.metadata_parser.get_metadata_by_table_long_names(
                    table_names
                )
                if result:
                    return result
                else:
                    raise Exception("Not found in local index")
            except Exception:
                # if not found in local index, use snowflake to get metadata
                logger.warning(
                    "Metadata not found in local index, retrieving using snowflake"
                )
                return self._get_metadata_from_snowflake(table_names)

        return ""  # dummy return, just to make mypy happy


class QuerySnowflakeDatabaseTool(QuerySQLDataBaseTool):
    """Tool for querying a Snowflake database."""

    db: SnowflakeContainer = Field(exclude=True)  # type: ignore

    name = QUERY_SNOWFLAKE_DATABASE_TOOL_NAME
    description = f"""
    Never call this tool directly,
    - always use the {GET_SNOWFLAKE_DATABASE_TABLE_METADATA_TOOL_NAME} to get the metadata of the tables you want to query first, and make sure your query does NOT have any non-existent column names and other identifiers!
    - always use the {SNOWFLAKE_QUERY_CHECKER_TOOL_NAME} to check if your query is correct before executing it!

    Input to this tool is a database and a schema, along with a detailed and correct SQL query, output is a result from the database.
    If the query is not correct, an error message will be returned.
    If an error is returned, rewrite the query, check the query, and try again.

    Example Input: 'database: database_name, schema: schema_name, query: SELECT * FROM table_name'
    """

    def _process_tool_input(self, tool_input: Union[str, Dict]) -> Dict[str, str]:
        logger.debug(f"\nEntering with {tool_input=}")
        if isinstance(tool_input, str):
            pattern = r"database: (.*?), schema: (.*?), query: (.*)"
            match = re.search(pattern, tool_input)

            if match:
                input_dict = {
                    "database": match.group(1),
                    "schema": match.group(2),
                    "query": match.group(3),
                }
            else:
                # # try to see if the input is a query only
                # input_dict = {
                #     "database": DEFAULT_DATABASE,
                #     "schema": DEFAULT_SCHEMA,
                #     "query": tool_input,
                # }
                # try to see if the input is a string of a dict
                try:
                    input_dict = json.loads(tool_input)
                    if "query" in input_dict.keys():
                        if "database" not in input_dict.keys():
                            input_dict["database"] = DEFAULT_DATABASE
                        if "schema" not in input_dict.keys():
                            input_dict["schema"] = DEFAULT_SCHEMA
                except json.JSONDecodeError:
                    # try to see if the input is a query only
                    input_dict = {
                        "database": DEFAULT_DATABASE,
                        "schema": DEFAULT_SCHEMA,
                        "query": tool_input,
                    }
        elif isinstance(tool_input, dict):
            full_keys = {"database", "schema", "query"}
            if full_keys.issubset(tool_input.keys()):
                input_dict = tool_input
            elif "query" in tool_input.keys():
                # try to see if the input is a query only
                input_dict = {
                    "database": DEFAULT_DATABASE,
                    "schema": DEFAULT_SCHEMA,
                    "query": tool_input.get("query"),
                }
            # required_keys = {"database", "schema", "query"}
            # if required_keys.issubset(tool_input.keys()):
            #     input_dict = tool_input
            else:
                raise ValueError(
                    f"Invalid tool_input. Unable to parse 'query' from dictionary {tool_input=}"
                )
        else:
            raise ValueError("Invalid tool_input. Expected a string or a dictionary.")
        return input_dict

    #    def _run(self, *args, **kwargs) -> str:
    def _run(  # type: ignore
        self,
        *args,
        mode="default",
        run_manager: Optional[CallbackManagerForToolRun] = None,
        **kwargs,
    ) -> Union[str, List[Any]]:
        """Execute the query, return the results or an error message."""

        if mode not in ["flipside", "shroomdk", "snowflake", "default"]:
            raise ValueError(f"Invalid mode: {mode}")

        if args:
            tool_input = args[0]
        else:
            tool_input = kwargs

        input_dict = self._process_tool_input(tool_input)

        logger.debug(f"\nParsed input: {input_dict=}")

        # Retrieve values
        database = input_dict["database"]
        schema = input_dict["schema"]
        query = input_dict["query"]

        if mode == "flipside":
            logger.debug(f"{mode=}, flipside {query=}")
            result_flipside: List[Any] = []
            for i in range(FLIPSIDE_QUERY_MAX_RETRIES):
                try:
                    result_set = self.db.flipside.query(
                        query, timeout_minutes=FLIPSIDE_QUERY_TIMEOUT
                    )
                    result_flipside = result_set.rows
                    logger.debug(
                        f"Flipside query attempt {i+1} successful: \
                                  {result_set.rows=}"
                    )

                    logger.debug(f"{self.return_direct=}")
                    # enable return_direct if the query was successful

                    if (
                        QUERY_DATABASE_TOOL_RETURN_DIRECT_IF_SUCCESSFUL
                        and not self.return_direct
                    ):
                        self.return_direct = True
                        logger.debug(f"Updated {self.return_direct=}")

                    break  # Exit the loop if the query was successful

                except QueryRunTimeoutError as e:
                    logger.warning(
                        f"Flipside query attempt {i+1} timed out {e}. \
                                   Retrying..."
                    )
                    if i == FLIPSIDE_QUERY_MAX_RETRIES - 1:
                        logger.error(
                            f"All query attempts resulted in timeouts. \
                                     Raising exception. {str(e)}"
                        )
                        raise ToolException(
                            f"All query timeout retries exhausted, {str(e)}"
                        )  # Re-raise the exception after all retries are exhausted

                except Exception as e:
                    logger.error(f"Flipside query attempt failed due to: {e}")
                    raise ToolException(str(e))

            # for i in range(FLIPSIDE_QUERY_MAX_RETRIES):
            #     # try:
            #     result_set = self.db.flipside.query(
            #         query, timeout_minutes=FLIPSIDE_QUERY_TIMEOUT
            #     )
            #     result_flipside = result_set.rows
            #     # logger.debug(f"Flipside query: {result_set.rows=}")
            #     logger.debug(f"Flipside query attempt {i+1}: {result_set.rows=}")
            #     break
            # except AttributeError as e:
            #     if "FLIPSIDE_API_KEY" in str(e):
            #         raise Exception(
            #             "Flipside query error. Please double check whether \
            #                 your FLIPSIDE_API_KEY environmental variable \
            #                 is set correctly."
            #         )
            #     else:
            #     raise Exception(
            #         f"Flipside query error: {e}"
            #     )
            #         result_flipside = [
            #             f"AttributeError: Flipside query attempt {i+1} error: {e}"
            #         ]
            # except Exception as e:
            #     logger.debug(f"Flipside query attempt {i+1}: error: {e}")
            #     raise Exception(
            #         f"Flipside query error: {e}"
            #     )
            # result_flipside = [
            #     f"Exception: Flipside query attempt {i+1} error: {e}"
            # ]
            return result_flipside

        if mode == "snowflake":
            snowflake_database = self.db.get_database(database, schema)
            result_snowflake = snowflake_database.run_no_throw(query)
            assert isinstance(result_snowflake, str)
            logger.debug(f"snowflake {result_snowflake=}")
            return result_snowflake

        if mode == "shroomdk":
            logger.debug(f"{mode=}, shroomdk {query=}")
            result_set = self.db.shroomdk.query(query)
            logger.debug(f"shroomdk {result_set.rows=}")
            result_shroomdk: List[Any] = result_set.rows
            return result_shroomdk

        if mode == "default":
            # try to use flipside first
            try:
                logger.debug(f"{mode=}, flipside {query=}")
                result_set = self.db.flipside.query(query)
                logger.debug(f"flipside {result_set.rows=}")
                result_flipside_default: List[Any] = result_set.rows
                return result_flipside_default
                # logger.debug(f"{mode=}, shroomdk {query=}")
                # result_set = self.db.shroomdk.query(query)
                # logger.debug(
                #     f"shroomdk result: {result_set=}, to return {result_set.rows=}"
                # )
                # result_shroomdk = result_set.rows
                # return result_shroomdk
            except Exception:
                # if shroomdk fails, use snowflake
                try:
                    snowflake_database = self.db.get_database(database, schema)
                    result_snowflake = snowflake_database.run_no_throw(query)
                    assert isinstance(result_snowflake, str)
                    return result_snowflake
                except Exception:
                    raise Exception(
                        f"Unable to execute query {query=} on {database=}.{schema=} via either shroomdk or snowflake."
                    )

        return ""  # dummy return, just to make mypy happy


class SnowflakeQueryCheckerTool(QuerySQLCheckerTool):
    """Use an LLM to check if a query is correct.
    Adapted from https://www.patterns.app/blog/2023/01/18/crunchbot-sql-analyst-gpt/"""

    template: str = SNOWFLAKE_QUERY_CHECKER
    llm: BaseChatModel
    db: SnowflakeContainer = Field(exclude=True)  # type: ignore
    name = SNOWFLAKE_QUERY_CHECKER_TOOL_NAME

    description = f"""
    Use this tool to double check if your snowflake query is correct before executing it.
    Always use this tool before executing a query with {QUERY_SNOWFLAKE_DATABASE_TOOL_NAME}!
    """

    @root_validator(pre=True)
    def initialize_llm_chain(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        if "llm_chain" not in values:
            input_variables = ["query", "dialect"]
            messages = [
                SystemMessagePromptTemplate.from_template(
                    template=SNOWFLAKE_QUERY_CHECKER
                ),
                HumanMessagePromptTemplate.from_template(template="\n\n{query}"),
            ]
            assert isinstance(messages, list) and all(
                isinstance(
                    item,
                    (BaseMessagePromptTemplate, BaseMessage, BaseChatPromptTemplate),
                )
                for item in messages
            ), "Expected a list of BaseMessagePromptTemplate or BaseMessage or BaseChatPromptTemplate"

            llm = values.get("llm")
            assert isinstance(llm, BaseLanguageModel)
            values["llm_chain"] = LLMChain(
                llm=llm,
                prompt=ChatPromptTemplate(
                    input_variables=input_variables,
                    messages=messages,  # type: ignore[arg-type]
                ),
            )

        if values["llm_chain"].prompt.input_variables != ["query", "dialect"]:
            raise ValueError(
                "LLM chain for QuerySQLCheckerTool must have input variables ['query', 'dialect']"
            )

        return values
