# test_fastapi.py
from unittest.mock import patch

from fastapi.testclient import TestClient

from api.api_endpoints import BlockchainDataError, app
from api.services.blockchain_data import query_blockchain_data_from_flipside

client = TestClient(app)


@patch("api.api_endpoints.query_blockchain_data_from_flipside")
def test_query_chatweb3_success(mock_query):
    mock_query.return_value = ("Answer", "Thought Process")
    response = client.post("/query_blockchain_data", json={"query": "Some Input"})
    assert response.status_code == 200
    assert response.json() == {"answer": "Answer", "thought_process": "Thought Process"}


@patch("api.api_endpoints.query_blockchain_data_from_flipside")
def test_query_chatweb3_blockchain_data_error(mock_query):
    mock_query.side_effect = BlockchainDataError("Crypto Data Error", "Some Error")
    response = client.post("/query_blockchain_data", json={"query": "Some Input"})
    assert response.status_code == 400
    assert "error" in response.json()


@patch("api.api_endpoints.query_blockchain_data_from_flipside")
def test_query_chatweb3_internal_error(mock_query):
    mock_query.side_effect = Exception("Unexpected Error")
    response = client.post("/query_blockchain_data", json={"query": "Some Input"})
    assert response.status_code == 500
    assert "error" in response.json()
