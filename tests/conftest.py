"""
conftest.py
This file contains the fixtures for the tests.
"""

import logging

import pytest

from chatweb3.create_agent import INDEX_ANNOTATION_FILE_PATH, LOCAL_INDEX_FILE_PATH
from chatweb3.metadata_parser import Column, Database, MetadataParser, Schema, Table
from chatweb3.snowflake_database import SnowflakeContainer
from config.config import agent_config


@pytest.fixture
def clean_logging():
    # Setup: Backup existing handlers
    logger = logging.getLogger()
    backup_handlers = logger.handlers[:]

    yield

    # Teardown: Restore original handlers and configuration
    logger.handlers = backup_handlers


@pytest.fixture(scope="module")
def snowflake_params():
    return {
        **agent_config.get("snowflake_params"),
        **agent_config.get("flipside_params"),
        **agent_config.get("shroomdk_params"),
    }


@pytest.fixture(scope="module")
def snowflake_container(snowflake_params):
    return SnowflakeContainer(**snowflake_params)


@pytest.fixture(scope="module")
def snowflake_container_eth_core(snowflake_params):
    return SnowflakeContainer(
        **snowflake_params,
        local_index_file_path=LOCAL_INDEX_FILE_PATH,
        index_annotation_file_path=INDEX_ANNOTATION_FILE_PATH,
    )


@pytest.fixture(scope="module")
def eth_core_table_long_names_select_list():
    return agent_config.get("ethereum_core_table_long_name.enabled_list")


@pytest.fixture
def metadata_parser_with_sample_data():
    # Create the MetadataParser object
    metadata_parser = MetadataParser()

    # Add sample data to the parser's custom objects
    # Database 1: ethereum
    ethereum_db = Database("ethereum")
    ethereum_core_schema = Schema("core", "ethereum")
    ethereum_aave_schema = Schema("aave", "ethereum")

    # ethereum.core.ez_nft_sales
    ez_nft_sales = Table("ez_nft_sales", "core", "ethereum")
    ez_nft_sales.comment = "The sales of NFTs."
    ez_nft_sales.summary = "Summary: This table contains the sales of NFTs."
    columns1 = {
        "block_number": Column(
            "block_number",
            "NUMBER(38,0)",
            "The block number at which the NFT event occurred.",
        ),
        "event_type": Column(
            "event_type",
            "VARCHAR(16777216)",
            "The type of NFT event in this transaction, either sale`, `bid_won` or `redeem`.",
        ),
    }
    columns1["block_number"].sample_values_list = [1, 2, 3]
    columns1["event_type"].sample_values_list = ["sale", "bid_won", "redeem"]
    ez_nft_sales.columns = columns1
    ez_nft_sales.column_names = ["block_number", "event_type"]

    ethereum_core_schema.tables["ez_nft_sales"] = ez_nft_sales
    ethereum_db.schemas["core"] = ethereum_core_schema

    # ethereum.aave.ez_proposals
    ez_proposals = Table("ez_proposals", "aave", "ethereum")
    ez_proposals.comment = "Aave proposals."
    ez_proposals.summary = "Summary: This table contains Aave proposals."
    columns2 = {
        "block_number": Column(
            "block_number",
            "NUMBER(38,0)",
            "The block number at which the NFT event occurred.",
        ),
    }
    columns2["block_number"].sample_values_list = [10, 11, 12]
    ez_proposals.columns = columns2
    ez_proposals.column_names = ["block_number"]

    ethereum_aave_schema.tables["ez_proposals"] = ez_proposals
    ethereum_db.schemas["aave"] = ethereum_aave_schema

    metadata_parser.root_schema_obj.databases["ethereum"] = ethereum_db

    # Database 2: polygon
    polygon_db = Database("polygon")
    polygon_core_schema = Schema("core", "polygon")

    # polygon.core.fact_blocks
    fact_blocks = Table("fact_blocks", "core", "polygon")
    fact_blocks.comment = "The fact blocks on Polygon."
    fact_blocks.summary = "Summary: This table contains the fact blocks on Polygon."
    columns3 = {
        "difficulty": Column(
            "difficulty", "NUMBER(38,0)", "The effort required to mine the block"
        ),
    }
    columns3["difficulty"].sample_values_list = [6, 7, 8]
    fact_blocks.columns = columns3
    fact_blocks.column_names = ["difficulty"]

    polygon_core_schema.tables["fact_blocks"] = fact_blocks
    polygon_db.schemas["core"] = polygon_core_schema

    metadata_parser.root_schema_obj.databases["polygon"] = polygon_db

    return metadata_parser
