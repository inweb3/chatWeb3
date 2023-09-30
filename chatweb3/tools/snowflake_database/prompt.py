# SNOWFLAKE_QUERY_CHECKER_BACKUP = """
# Double check the {dialect} query for common mistakes and make sure it works specifically for Snowflake databases, including:
# - Using NOT IN with NULL values
# - Using UNION when UNION ALL should have been used
# - Using BETWEEN for exclusive ranges
# - Data type mismatch in predicates
# - Properly quoting identifiers
# - Using the correct number of arguments for functions
# - Casting to the correct data type
# - Using the proper columns for joins
# - Correct usage of `INTERVAL` in date functions e.g. in Snowflake, when using `DATEADD` to add or subtract days, months, years, etc., to a date or timestamp, it requires the unit of time you want to adjust (e.g., DAY, MONTH, YEAR), the number of units to adjust (positive or negative), and the date you're adjusting.

# So, while this is valid in some databases:
# ```sql
# CURRENT_DATE - INTERVAL '1' DAY
# ```
# In Snowflake, you'd use:
# ```sql
# DATEADD(DAY, -1, CURRENT_DATE)
# ```
# make sure these and similar errors are corrected and make sure the query works specifically for Snowflake database!

# If there are any of the above mistakes, rewrite the query. If there are no mistakes, just reproduce the original query."""

SNOWFLAKE_QUERY_CHECKER = """
Double check the {dialect} query for common mistakes and make sure it works specifically for Snowflake databases, including:
- Using NOT IN with NULL values
- Using UNION when UNION ALL should have been used
- Using BETWEEN for exclusive ranges
- Data type mismatch in predicates
- Properly quoting identifiers
- Using the correct number of arguments for functions
- Casting to the correct data type
- Using the proper columns for joins
- Correct usage of `INTERVAL` in date functions e.g. in Snowflake, when using `DATEADD` to add or subtract days, months, years, etc., to a date or timestamp, it requires the unit of time you want to adjust (e.g., DAY, MONTH, YEAR), the number of units to adjust (positive or negative), and the date you're adjusting.

So, while this is valid in some databases:
```sql
CURRENT_DATE - INTERVAL '1' DAY
```
In Snowflake, you'd use:
```sql
DATEADD(DAY, -1, CURRENT_DATE)
```
make sure these and similar errors are corrected and make sure the query works specifically for Snowflake database! 

If there are any of the above mistakes, rewrite the query. If there are no mistakes, just reproduce the original query. Make sure your response is concise, only include the query and nothing else."""
# flake8: noqa
# from chatweb3.tools.snowflake_database.tool_custom import (
#     CHECK_QUERY_SYNTAX_TOOL_NAME,
#     CHECK_TABLE_METADATA_TOOL_NAME,
#     CHECK_TABLE_SUMMARY_TOOL_NAME,
#     QUERY_DATABASE_TOOL_NAME,
# )
from chatweb3.tools.snowflake_database.constants import (
    CHECK_QUERY_SYNTAX_TOOL_NAME,
    CHECK_TABLE_METADATA_TOOL_NAME,
    CHECK_TABLE_SUMMARY_TOOL_NAME,
    QUERY_DATABASE_TOOL_NAME,
)

# TOOLKIT_INSTRUCTIONS = f"""
# When using these tools, you MUST follow the instructions below:
# 1. You MUST always start with the {CHECK_TABLE_SUMMARY_TOOL_NAME} tool to check the available tables in the databases, and make selection of one or multiple tables you want to work with if applicable.
# 2. If you need to construct any SQL query for any table, you MUST always use the {CHECK_TABLE_METADATA_TOOL_NAME} tool to check the metadata detail of the table before you can create a query for that table. Note that you can check the metadata details of multiple tables at the same time.
# 3. When constructing a query containing a token or NFT, if you have both its address and and its symbol, you MUST always prefer using the token address over the token symbol since token symbols are often not unique.
# 4. If you receive and error from  {QUERY_DATABASE_TOOL_NAME} tool, you MUST always analyze the error message and determine how to resolve it. If it is a general syntax error, you MUST use the {CHECK_QUERY_SYNTAX_TOOL_NAME} tool to double check the query before you can run it again through the {QUERY_DATABASE_TOOL_NAME} tool. If it is due to invalid table or column names, you MUST double check the {CHECK_TABLE_METADATA_TOOL_NAME} tool and re-construct the query accordingly.
# """

TOOLKIT_INSTRUCTIONS = f"""
When using these tools, you MUST follow the instructions below:
1. You MUST always start with the {CHECK_TABLE_SUMMARY_TOOL_NAME} tool to check the available tables in the databases, and make selection of one or multiple tables you want to work with if applicable. Once you received the tables summary information, you should proceed to the next step. 
2. Once you have the table summraries, you MUST always use the {CHECK_TABLE_METADATA_TOOL_NAME} tool to check the metadata detail of the table before you can create a query for that table. Note that you can check the metadata details of multiple tables at the same time.
3. When constructing a query containing a token or NFT, if you have both its address and and its symbol, you MUST always prefer using the token address over the token symbol since token symbols are often not unique.
4. If you receive and error from  {QUERY_DATABASE_TOOL_NAME} tool, you MUST always analyze the error message and determine how to resolve it. If it is a general syntax error, you MUST use the {CHECK_QUERY_SYNTAX_TOOL_NAME} tool to double check the query before you can run it again through the {QUERY_DATABASE_TOOL_NAME} tool. If it is due to invalid table or column names, you MUST double check the {CHECK_TABLE_METADATA_TOOL_NAME} tool and re-construct the query accordingly.
"""

# We may consider amend the instruction: if it is query execution error, then rewrite the query and run again, if it is timeout error, then do not retry, instead, return and ask the user to try again later.
