# Description: This file contains the API endpoints for ChatWeb3
# Path: api/api_endpoints.py
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, Field
from config.logging_config import get_logger
from dotenv import load_dotenv

from api.routers.well_known import get_ai_plugin, get_host, well_known

# Importing the required tools from tool_custom.py
from chatweb3.tools.snowflake_database.tool_custom import (
    CheckTableSummaryTool,
    CheckTableMetadataTool,
    QueryDatabaseTool,
)
from chatweb3.create_agent import get_snowflake_container


logger = get_logger(__name__)


db = get_snowflake_container()

ai_plugin = get_ai_plugin()

app = FastAPI(
    title=ai_plugin["name_for_human"],
    description=ai_plugin["description_for_human"],
    version="0.1.0",
)

# origins = [
#     "https://chat.openai.com",
# ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://chat.openai.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(well_known)


# Exception Handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"An error occurred: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error"},
    )


# Endpoint: Get List of Available Tables
@app.get("/get_list_of_available_tables")
async def get_list_of_available_tables(table_list: str = ""):
    try:
        logger.debug(f"tool_input={table_list} Fetching list of available tables...")
        tool = CheckTableSummaryTool(db=db)
        result = tool.run(tool_input=table_list)
        logger.debug(
            f"tool_input={table_list} Fetched list of available tables {result=}"
        )
        return {"result": result}
    except Exception as e:
        logger.error(f"Error fetching list of available tables: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Endpoint: Get Detailed Metadata for Tables
@app.get("/get_detailed_metadata_for_tables")
async def get_detailed_metadata_for_tables(table_names: str):
    try:
        tool = CheckTableMetadataTool(db=db)
        result = tool.run(table_names)
        logger.debug(f"Fetched metadata for table(s): {table_names}.")
        return {"result": result}
    except Exception as e:
        logger.debug(f"Error fetching metadata for table(s) {table_names}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


class SnowflakeQuery(BaseModel):
    query: str = Field(
        ...,
        description="A Snowflake SQL query",
    )


# Endpoint: Query Snowflake SQL Database
@app.post("/query_snowflake_sql_database")
async def query_snowflake_sql_database(query: SnowflakeQuery):
    try:
        tool = QueryDatabaseTool(db=db)
        result = tool.run(tool_input=query.query)
        logger.debug(f"Executed query: {query.query}.")
        return {"result": result}
    except Exception as e:
        logger.error(f"Error executing query {query.query}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def start():
    import uvicorn

    uvicorn.run("api.api_endpoints:app", host="localhost", port=8000, reload=True)


# uvicorn api.api_endpoints:app --reload

# class ChatWeb3QueryRequest(BaseModel):
#     query: str = Field(
#         ...,
#         description="A natural English language query to query blockchain data",
#     )


# @app.post("/query_blockchain_data", include_in_schema=True)
# async def query_chatweb3(data: ChatWeb3QueryRequest, request: Request):
#     """Query blockchain data using a natural English language query
#     and get the answer as well as the thought process
#     """
#     try:
#         answer, thought_process = query_blockchain_data_from_flipside(data.query)
#         return {"answer": answer, "thought_process": thought_process}
#     except BlockchainDataError as e:
#         return JSONResponse(status_code=400, content={"error": str(e)})
#     except Exception as e:
#         return JSONResponse(
#             status_code=500, content={"error": "Internal server error" + str(e)}
#         )


# @app.exception_handler(BlockchainDataError)
# async def unicorn_exception_handler(request: Request, exc: BlockchainDataError):
#     return JSONResponse(
#         status_code=400,
#         content={"message": f"Oops! {exc.name} did something. There goes a rainbow..."},
#     )
