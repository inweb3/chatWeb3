# test_blockchain_data_service.py
from unittest.mock import patch
import pytest

from api.services.blockchain_data import (
    BlockchainDataError,
    query_blockchain_data_from_flipside,
)


@pytest.mark.skip(reason="This test needs to be updated")
@patch("api.services.blockchain_data.agent")
def test_query_blockchain_data_success(mock_agent):
    mock_agent.return_value = {
        "output": "Answer",
        "intermediate_steps": "Thought Process",
    }
    answer, thought_process = query_blockchain_data_from_flipside("Some Input")
    print({"answer": answer, "thought_process": thought_process})
    assert answer == "Answer"
    assert (
        thought_process
        == "*Observation*: T\n\n*Observation*: h\n\n*Observation*: o\n\n*Observation*: u\n\n*Observation*: g\n\n*Observation*: h\n\n*Observation*: t\n\n*Observation*: \n\n*Observation*: P\n\n*Observation*: r\n\n*Observation*: o\n\n*Observation*: c\n\n*Observation*: e\n\n*Observation*: s\n\n*Observation*: s\n\n**Final answer**: Answer"
    )


@patch("api.services.blockchain_data.agent")
def test_query_blockchain_data_failure(mock_agent):
    mock_agent.side_effect = Exception("Some Error")
    try:
        query_blockchain_data_from_flipside("Some Input")
    except BlockchainDataError as e:
        assert str(e) == "Some Error"
