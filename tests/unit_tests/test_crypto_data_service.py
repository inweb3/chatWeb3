# test_crypto_data_service.py
from unittest.mock import patch

from api.services.crypto_data import CryptoDataError, query_crypto_data_from_flipside


@patch("api.services.crypto_data.agent")
def test_query_crypto_data_success(mock_agent):
    mock_agent.return_value = {
        "output": "Answer",
        "intermediate_steps": "Thought Process",
    }
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
