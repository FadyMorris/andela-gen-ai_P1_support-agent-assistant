import os
import sys
import time
import pytest
import json
import datetime

# Ensure repo root is on sys.path so we can import the module under test
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, repo_root)

# Set a dummy API key so importing core doesn't raise RuntimeError
os.environ.setdefault("OPENAI_API_KEY", "test-key")

import src.support_agent.core as core
from src.support_agent.core import get_answer, SupportAgentResponse, Metrics, append_metrics_to_csv

@pytest.fixture
def user_query():
    return "How do I reset my password?"

@pytest.fixture
def metrics():
    return {
        "timestamp": int(time.time()),
        "tokens_prompt": 50,
        "tokens_completion": 100,
        "total_tokens": 150,
        "latency_ms": 250.0,
        "estimated_cost_usd": 0.005
    }

@pytest.fixture
def metrics_path():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.abspath(os.path.join(script_dir, "..", "metrics", "test_metrics.csv"))

def test_append_metrics_to_csv(metrics: dict, metrics_path: str):
    """
    Test for append_metrics_to_csv(metrics: dict, metrics_path: str).

    Verifies that:
    - The CSV file at metrics_path is created or appended with the correct header row:
        "timestamp,tokens_prompt,tokens_completion,total_tokens,latency_ms,estimated_cost_usd\n"
    - The final line written corresponds to the provided metrics dict, with the timestamp
        converted to an ISO-8601 string using datetime.fromtimestamp(metrics['timestamp']).isoformat(),
        and the numeric fields formatted as expected (in this test: tokens_prompt=50,
        tokens_completion=100, total_tokens=150, latency_ms=250.0, estimated_cost_usd=0.005).

    Parameters:
    - metrics (dict): input metrics containing at least the keys 'timestamp',
        'tokens_prompt', 'tokens_completion', 'total_tokens', 'latency_ms',
        and 'estimated_cost_usd'.
    - metrics_path (str): filesystem path to the CSV file to read/verify.

    Behavior:
    - Calls append_metrics_to_csv(metrics, metrics_path), opens the file for reading,
        and asserts that the header and the last data row exactly match the expected
        CSV lines. Fails if header text, timestamp formatting, or numeric formatting
        differ from the expected values.
    """
    append_metrics_to_csv(metrics, metrics_path)
    with open(metrics_path, "r") as f:
        lines = f.readlines()

    assert lines[0] == "timestamp,tokens_prompt,tokens_completion,total_tokens,latency_ms,estimated_cost_usd\n", "Header row mismatch"
    assert lines[-1] == f"{datetime.datetime.fromtimestamp(metrics['timestamp']).isoformat()},50,100,150,250.0,0.005\n", "Data row mismatch"

def test_get_answer(user_query: str, metrics_path: str):
    """
    Test that get_answer produces a schema-valid response and metrics for a given query.

    This test invokes get_answer(user_query) and verifies two things:
    1. The returned metrics object conforms to the Metrics pydantic model.
    2. The returned response is a JSON-encoded string which, when parsed,
        conforms to the SupportAgentResponse pydantic model.

    Parameters
    ----------
    user_query : str
         The input query to pass to get_answer.

    Raises
    ------
    pydantic.ValidationError
         If either the metrics or the decoded response does not match its schema.
    """
    response, metrics = get_answer(user_query, metrics_path)
    # Validate metrics JSON schema against Metrics Pydantic model
    Metrics.model_validate(metrics)
    # Validate response JSON schema against SupportAgentResponse Pydantic model
    SupportAgentResponse.model_validate(json.loads(response))
    # Delete the test metrics file after the test
    os.remove(metrics_path)