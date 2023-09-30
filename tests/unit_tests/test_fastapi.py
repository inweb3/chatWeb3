# test_fastapi.py
import pytest
from unittest.mock import patch

from fastapi.testclient import TestClient

# from api.api_endpoints import BlockchainDataError, app
# from api.services.blockchain_data import query_blockchain_data_from_flipside
from api.api_endpoints import (
    app,
    CheckTableSummaryTool,
    CheckTableMetadataTool,
    QueryDatabaseTool,
)

client = TestClient(app)


def test_get_list_of_available_tables():
    with patch.object(
        CheckTableSummaryTool, "run", return_value="mocked_return_value"
    ) as mock_method:
        response = client.get("/get_list_of_available_tables")
        assert response.status_code == 200
        assert response.json() == {"result": "mocked_return_value"}
        mock_method.assert_called_once()


def test_get_detailed_metadata_for_tables():
    with patch.object(
        CheckTableMetadataTool, "run", return_value="mocked_metadata_value"
    ) as mock_method:
        response = client.get(
            "/get_detailed_metadata_for_tables/", params={"table_names": "test_table"}
        )
        assert response.status_code == 200
        assert response.json() == {"result": "mocked_metadata_value"}
        mock_method.assert_called_once_with("test_table")


def test_query_snowflake_sql_database():
    with patch.object(
        QueryDatabaseTool, "run", return_value="mocked_query_result"
    ) as mock_method:
        response = client.post(
            "/query_snowflake_sql_database", json={"query": "SELECT * FROM test_table"}
        )
        assert response.status_code == 200
        assert response.json() == {"result": "mocked_query_result"}
        mock_method.assert_called_once_with(tool_input="SELECT * FROM test_table")


@pytest.mark.skip(reason="No longer in use")
@patch("api.api_endpoints.query_blockchain_data_from_flipside")
def test_query_chatweb3_success(mock_query):
    mock_query.return_value = ("Answer", "Thought Process")
    response = client.post("/query_blockchain_data", json={"query": "Some Input"})
    assert response.status_code == 200
    assert response.json() == {"answer": "Answer", "thought_process": "Thought Process"}


@pytest.mark.skip(reason="No longer in use")
@patch("api.api_endpoints.query_blockchain_data_from_flipside")
def test_query_chatweb3_blockchain_data_error(mock_query):
    mock_query.side_effect = BlockchainDataError("Crypto Data Error", "Some Error")
    response = client.post("/query_blockchain_data", json={"query": "Some Input"})
    assert response.status_code == 400
    assert "error" in response.json()


@pytest.mark.skip(reason="No longer in use")
@patch("api.api_endpoints.query_blockchain_data_from_flipside")
def test_query_chatweb3_internal_error(mock_query):
    mock_query.side_effect = Exception("Unexpected Error")
    response = client.post("/query_blockchain_data", json={"query": "Some Input"})
    assert response.status_code == 500
    assert "error" in response.json()
