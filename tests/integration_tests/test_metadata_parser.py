"""
test_metadata_parser.py
This file contains the tests for the metadata_parser module.
"""


def test_get_metadata_by_table_long_names(metadata_parser_with_sample_data):
    table_long_names = "ethereum.core.ez_nft_sales, ethereum.aave.ez_proposals, polygon.core.fact_blocks"
    expected_output = "'ethereum.aave.ez_proposals': the 'ez_proposals' table in 'aave' schema of 'ethereum' database. \nComment: Aave proposals.\nColumns in this table:\n\tName | Comment | Data type | List of sample values\n\t--- | --- | --- | ---\n\tblock_number | None | None | 10, 11, 12\n\n'ethereum.core.ez_nft_sales': the 'ez_nft_sales' table in 'core' schema of 'ethereum' database. \nComment: The sales of NFTs.\nColumns in this table:\n\tName | Comment | Data type | List of sample values\n\t--- | --- | --- | ---\n\tblock_number | None | None | 1, 2, 3\n\tevent_type | None | None | sale, bid_won, redeem\n\n'polygon.core.fact_blocks': the 'fact_blocks' table in 'core' schema of 'polygon' database. \nComment: The fact blocks on Polygon.\nColumns in this table:\n\tName | Comment | Data type | List of sample values\n\t--- | --- | --- | ---\n\tdifficulty | None | None | 6, 7, 8"
    result = metadata_parser_with_sample_data.get_metadata_by_table_long_names(
        table_long_names
    )
    assert result == expected_output
    assert "ethereum.aave.ez_proposals" in result
    assert "ethereum.core.ez_nft_sales" in result
    assert "polygon.core.fact_blocks" in result
    assert "Aave proposals" in result
    assert "The sales of NFTs" in result
    assert "The fact blocks on Polygon" in result
    assert "block_number" in result
    assert "event_type" in result
    assert "difficulty" in result


def test_get_metadata_by_table_long_names_table_summary(
    metadata_parser_with_sample_data,
):
    table_long_names = "ethereum.core.ez_nft_sales, ethereum.aave.ez_proposals, polygon.core.fact_blocks"
    result1 = metadata_parser_with_sample_data.get_metadata_by_table_long_names(
        table_long_names, include_column_info=False
    )

    result2 = metadata_parser_with_sample_data.get_metadata_by_table_long_names(
        table_long_names, include_column_names=True, include_column_info=False
    )

    expected_result_1 = "'ethereum.aave.ez_proposals': the 'ez_proposals' table in 'aave' schema of 'ethereum' database. Summary: This table contains Aave proposals.\n\n'ethereum.core.ez_nft_sales': the 'ez_nft_sales' table in 'core' schema of 'ethereum' database. Summary: This table contains the sales of NFTs.\n\n'polygon.core.fact_blocks': the 'fact_blocks' table in 'core' schema of 'polygon' database. Summary: This table contains the fact blocks on Polygon."
    expected_result_2 = "'ethereum.aave.ez_proposals': the 'ez_proposals' table in 'aave' schema of 'ethereum' database. Summary: This table contains Aave proposals.This table has the following columns: 'block_number'\n\n'ethereum.core.ez_nft_sales': the 'ez_nft_sales' table in 'core' schema of 'ethereum' database. Summary: This table contains the sales of NFTs.This table has the following columns: 'block_number, event_type'\n\n'polygon.core.fact_blocks': the 'fact_blocks' table in 'core' schema of 'polygon' database. Summary: This table contains the fact blocks on Polygon.This table has the following columns: 'difficulty'"
    assert result1 == expected_result_1
    assert result2 == expected_result_2
