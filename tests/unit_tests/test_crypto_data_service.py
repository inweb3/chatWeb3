# test_crypto_data_service.py
from api.services.crypto_data import query_crypto_data_from_flipside, CryptoDataError
from unittest.mock import patch

@patch("api.services.crypto_data.agent")
def test_query_crypto_data_success(mock_agent):
    mock_agent.return_value = {"output": "Answer", "intermediate_steps": "Thought Process"}
    answer, thought_process = query_crypto_data_from_flipside("Some Input")
    assert answer == "Answer"
    assert thought_process == "Thought Process"

@patch("api.services.crypto_data.agent")
def test_query_crypto_data_failure(mock_agent):
    mock_agent.side_effect = Exception("Some Error")
    try:
        query_crypto_data_from_flipside("Some Input")
    except CryptoDataError as e:
        assert str(e) == "Some Error"
