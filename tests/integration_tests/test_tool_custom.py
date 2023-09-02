"""
test_tool_custom.py
This file contains the tests for the tool_custom module.
"""

import pytest

from chatweb3.tools.snowflake_database.tool_custom import (
    CheckTableMetadataTool,
    CheckTableSummaryTool,
    QueryDatabaseTool,
)


def test_check_table_summary_tool_local(
    snowflake_container_eth_core, eth_core_table_long_names_select_list
):
    tool = CheckTableSummaryTool(db=snowflake_container_eth_core)
    tool_input = ""
    result = tool._run(tool_input=tool_input, mode="local")
    for i in range(len(eth_core_table_long_names_select_list)):
        assert eth_core_table_long_names_select_list[i] in result


def test_check_table_metadata_tool_local(snowflake_container_eth_core):
    tool = CheckTableMetadataTool(db=snowflake_container_eth_core)
    table_names = "ethereum.core.ez_dex_swaps, ethereum.core.ez_nft_mints, ethereum.core.ez_nft_transfers"

    result = tool._run(table_names=table_names, mode="local")
    assert "ethereum.core.ez_dex_swaps" in result
    assert "ethereum.core.ez_nft_mints" in result
    assert "ethereum.core.ez_nft_transfers" in result
    with pytest.raises(ValueError):
        tool._run("invalid_input")


def test_query_database_tool_str_flipside(snowflake_container_eth_core):
    tool = QueryDatabaseTool(db=snowflake_container_eth_core)

    tool_input = "select * from ethereum.beacon_chain.fact_attestations limit 3"

    result = tool._run(tool_input, mode="flipside")
    print(f"{result=}")
    num_items = len(result)
    assert num_items == 3


def test_query_database_tool_dict_flipside(snowflake_container_eth_core):
    tool = QueryDatabaseTool(db=snowflake_container_eth_core)

    tool_input = {
        "query": "select * from ethereum.beacon_chain.fact_attestations limit 3",
    }
    print(f"\n{tool_input=}")

    result = tool._run(tool_input, mode="flipside")
    print(f"{result=}")
    num_items = len(result)
    assert num_items == 3


def test_query_database_tool_dict_str_flipside(snowflake_container_eth_core):
    tool = QueryDatabaseTool(db=snowflake_container_eth_core)

    tool_input = (
        '{"query": "select * from ethereum.beacon_chain.fact_attestations limit 3"}'
    )
    print(f"\n{tool_input=}")

    result = tool._run(tool_input, mode="flipside")
    print(f"{result=}")
    num_items = len(result)
    assert num_items == 3


@pytest.mark.skip(reason="shroomdk is deprecated")
def test_query_database_tool_str_shroomdk(snowflake_container_eth_core):
    tool = QueryDatabaseTool(db=snowflake_container_eth_core)

    tool_input = "select * from ethereum.beacon_chain.fact_attestations limit 3"

    result = tool._run(tool_input, mode="shroomdk")
    print(f"{result=}")
    num_items = len(result)
    assert num_items == 3


@pytest.mark.skip(reason="shroomdk is deprecated")
def test_query_database_tool_dict_shroomdk(snowflake_container_eth_core):
    tool = QueryDatabaseTool(db=snowflake_container_eth_core)

    tool_input = {
        "query": "select * from ethereum.beacon_chain.fact_attestations limit 3",
    }
    print(f"\n{tool_input=}")

    result = tool._run(tool_input, mode="shroomdk")
    print(f"{result=}")
    num_items = len(result)
    assert num_items == 3


@pytest.mark.skip(reason="shroomdk is deprecated")
def test_query_database_tool_dict_str_shroomdk(snowflake_container_eth_core):
    tool = QueryDatabaseTool(db=snowflake_container_eth_core)

    tool_input = (
        '{"query": "select * from ethereum.beacon_chain.fact_attestations limit 3"}'
    )
    print(f"\n{tool_input=}")

    result = tool._run(tool_input, mode="shroomdk")
    print(f"{result=}")
    num_items = len(result)
    assert num_items == 3


@pytest.mark.skip(reason="requires snowflake credentials")
def test_query_database_tool_dict_snowflake(snowflake_container_eth_core):
    tool = QueryDatabaseTool(db=snowflake_container_eth_core)

    tool_input = {
        "query": "select * from ethereum.beacon_chain.fact_attestations limit 3",
    }
    print(f"\n{tool_input=}")

    result = tool._run(tool_input, mode="snowflake")
    print(f"{result=}")
    num_items = result.count("'), (") + 1
    assert num_items == 3
