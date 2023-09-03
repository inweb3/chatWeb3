SNOWFLAKE_QUERY_CHECKER = """
Double check the {dialect} query for common mistakes, including:
- Using NOT IN with NULL values
- Using UNION when UNION ALL should have been used
- Using BETWEEN for exclusive ranges
- Data type mismatch in predicates
- Properly quoting identifiers
- Using the correct number of arguments for functions
- Casting to the correct data type
- Using the proper columns for joins

If there are any of the above mistakes, rewrite the query. If there are no mistakes, just reproduce the original query."""

# flake8: noqa
from chatweb3.tools.snowflake_database.tool_custom import (
    CHECK_TABLE_SUMMARY_TOOL_NAME,
    CHECK_TABLE_METADATA_TOOL_NAME,
    QUERY_DATABASE_TOOL_NAME,
    CHECK_QUERY_SYNTAX_TOOL_NAME,
)

TOOLKIT_INSTRUCTIONS = f"""
When using these tools, you MUST follow the instructions below:
1. You MUST always start with the {CHECK_TABLE_SUMMARY_TOOL_NAME} tool to check the available tables in the databases, and make selection of one or multiple tables you want to work with if applicable.
2. If you need to construct any SQL query for any table, you MUST always use the {CHECK_TABLE_METADATA_TOOL_NAME} tool to check the metadata detail of the table before you can create a query for that table. Note that you can check the metadata details of multiple tables at the same time.
3. When constructing a query containing a token or NFT, if you have both its address and and its symbol, you MUST always prefer using the token address over the token symbol since token symbols are often not unique.
4. If you receive and error from  {QUERY_DATABASE_TOOL_NAME} tool, you MUST always analyze the error message and determine how to resolve it. If it is a general syntax error, you MUST use the {CHECK_QUERY_SYNTAX_TOOL_NAME} tool to double check the query before you can run it again through the {QUERY_DATABASE_TOOL_NAME} tool. If it is due to invalid table or column names, you MUST double check the {CHECK_TABLE_METADATA_TOOL_NAME} tool and re-construct the query accordingly.
"""
