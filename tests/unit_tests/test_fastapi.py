# test_fastapi.py
from fastapi.testclient import TestClient
from api.fastapi import app, CryptoDataError
from api.services.crypto_data import query_crypto_data_from_flipside
from unittest.mock import patch

from fastapi.testclient import TestClient
from api.fastapi import app, CryptoDataError
from unittest.mock import patch

client = TestClient(app)

@patch('api.fastapi.query_crypto_data_from_flipside')
def test_query_chatweb3_success(mock_query):
    mock_query.return_value = ("Answer", "Thought Process")
    response = client.post("/query_crypto_data", json={"string": "Some Input"})
    assert response.status_code == 200
    assert response.json() == {"answer": "Answer", "thought_process": "Thought Process"}

@patch('api.fastapi.query_crypto_data_from_flipside')
def test_query_chatweb3_crypto_data_error(mock_query):
    mock_query.side_effect = CryptoDataError("Crypto Data Error", "Some Error")
    response = client.post("/query_crypto_data", json={"string": "Some Input"})
    assert response.status_code == 400
    assert "error" in response.json()

@patch('api.fastapi.query_crypto_data_from_flipside')
def test_query_chatweb3_internal_error(mock_query):
    mock_query.side_effect = Exception("Unexpected Error")
    response = client.post("/query_crypto_data", json={"string": "Some Input"})
    assert response.status_code == 500
    assert "error" in response.json()


