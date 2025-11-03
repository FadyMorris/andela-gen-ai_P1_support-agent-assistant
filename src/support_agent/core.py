from openai import OpenAI
from dotenv import load_dotenv
import os
import time
from pydantic import BaseModel, Field, conint, confloat
from typing import List, Optional
import json
import datetime

from pygments import highlight
from pygments.lexers import JsonLexer
from pygments.formatters import TerminalFormatter

COMPLETION_MODEL_NAME = "gpt-5-mini"

def print_highlighted_json(json_dict: dict):
    highlight(json.dumps(json_dict, indent=4), JsonLexer(), TerminalFormatter())
    """Prints a JSON string with syntax highlighting for terminal output."""
    highlighted_json = highlight(json.dumps(json_dict, indent=4), JsonLexer(), TerminalFormatter())
    print(highlighted_json)

# Pricing of the models in USD per 1,000,000 tokens.
# Source: https://platform.openai.com/docs/pricing
costs = {
    "gpt-5": {"input_tokens": 1.25, "cached_tokens": 0.125, "output_tokens": 10.00},
    "gpt-5-mini": {"input_tokens": 0.25, "cached_tokens": 0.025, "output_tokens": 2.00},
    "gpt-5-nano": {"input_tokens": 0.05, "cached_tokens": 0.005, "output_tokens": 0.40},
    "gpt-5-chat-latest": {"input_tokens": 1.25, "cached_tokens": 0.125, "output_tokens": 10.00},
    "gpt-5-codex": {"input_tokens": 1.25, "cached_tokens": 0.125, "output_tokens": 10.00},
    "gpt-5-pro": {"input_tokens": 15.00, "output_tokens": 120.00},
    "gpt-4.1": {"input_tokens": 2.00, "cached_tokens": 0.50, "output_tokens": 8.00},
    "gpt-4.1-mini": {"input_tokens": 0.40, "cached_tokens": 0.10, "output_tokens": 1.60},
    "gpt-4.1-nano": {"input_tokens": 0.10, "cached_tokens": 0.025, "output_tokens": 0.40},
    "gpt-4o": {"input_tokens": 2.50, "cached_tokens": 1.25, "output_tokens": 10.00},
    "gpt-4o-2024-05-13": {"input_tokens": 5.00, "output_tokens": 15.00},
    "gpt-4o-mini": {"input_tokens": 0.15, "cached_tokens": 0.075, "output_tokens": 0.60},
    "gpt-realtime": {"input_tokens": 4.00, "cached_tokens": 0.40, "output_tokens": 16.00},
    "gpt-realtime-mini": {"input_tokens": 0.60, "cached_tokens": 0.06, "output_tokens": 2.40},
    "gpt-4o-realtime-preview": {"input_tokens": 5.00, "cached_tokens": 2.50, "output_tokens": 20.00},
    "gpt-4o-mini-realtime-preview": {"input_tokens": 0.60, "cached_tokens": 0.30, "output_tokens": 2.40},
    "gpt-audio": {"input_tokens": 2.50, "output_tokens": 10.00},
    "gpt-audio-mini": {"input_tokens": 0.60, "output_tokens": 2.40},
    "gpt-4o-audio-preview": {"input_tokens": 2.50, "output_tokens": 10.00},
    "gpt-4o-mini-audio-preview": {"input_tokens": 0.15, "output_tokens": 0.60},
    "o1": {"input_tokens": 15.00, "cached_tokens": 7.50, "output_tokens": 60.00},
    "o1-pro": {"input_tokens": 150.00, "output_tokens": 600.00},
    "o3-pro": {"input_tokens": 20.00, "output_tokens": 80.00},
    "o3": {"input_tokens": 2.00, "cached_tokens": 0.50, "output_tokens": 8.00},
    "o3-deep-research": {"input_tokens": 10.00, "cached_tokens": 2.50, "output_tokens": 40.00},
    "o4-mini": {"input_tokens": 1.10, "cached_tokens": 0.275, "output_tokens": 4.40},
    "o4-mini-deep-research": {"input_tokens": 2.00, "cached_tokens": 0.50, "output_tokens": 8.00},
    "o3-mini": {"input_tokens": 1.10, "cached_tokens": 0.55, "output_tokens": 4.40},
    "o1-mini": {"input_tokens": 1.10, "cached_tokens": 0.55, "output_tokens": 4.40},
    "codex-mini-latest": {"input_tokens": 1.50, "cached_tokens": 0.375, "output_tokens": 6.00},
    "gpt-5-search-api": {"input_tokens": 1.25, "cached_tokens": 0.125, "output_tokens": 10.00},
    "gpt-4o-mini-search-preview": {"input_tokens": 0.15, "output_tokens": 0.60},
    "gpt-4o-search-preview": {"input_tokens": 2.50, "output_tokens": 10.00},
    "computer-use-preview": {"input_tokens": 3.00, "output_tokens": 12.00},
    "gpt-image-1": {"input_tokens": 5.00, "cached_tokens": 1.25},
    "gpt-image-1-mini": {"input_tokens": 2.00, "cached_tokens": 0.20}
}


load_dotenv()
if not os.getenv("OPENAI_API_KEY"):
    raise RuntimeError("OPENAI_API_KEY not found in environment or .env")


client = OpenAI()

# Read the system prompt from the markdown file
script_dir = os.path.dirname(os.path.abspath(__file__))
prompt_path = os.path.abspath(os.path.join(script_dir, "../..", "prompts", "main_prompt.md"))
with open(prompt_path, "r", encoding="utf-8") as f:
    system_prompt = f.read()

class SupportAgentResponse(BaseModel):
    """Structured response from the support agent assistant."""
    answer: str = Field(..., description="Concise answer to the user's question")
    actions: List[str] = Field(default_factory=list, description="Recommended actions for the support agent")
    confidence: confloat(ge=0.0, le=1.0) = Field(..., description="Confidence score between 0 and 1")


class Metrics(BaseModel):
    """
    Per-run metrics for support agent responses.
    """
    timestamp: int = Field(..., description="Unix epoch seconds timestamp")
    tokens_prompt: conint(ge=0) = Field(..., description="Number of prompt tokens used")
    tokens_completion: conint(ge=0) = Field(..., description="Number of completion tokens used")
    total_tokens: conint(ge=0) = Field(..., description="Total tokens used")
    latency_ms: confloat(ge=0) = Field(..., description="Latency in milliseconds")
    estimated_cost_usd: confloat(ge=0) = Field(..., description="Estimated cost in USD")

METRIC_KEYS = Metrics.model_json_schema()["properties"].keys()

def append_metrics_to_csv(metrics: dict, metrics_path: Optional[str] = None):
    """
    Append a metrics record to a CSV file, creating the file with a header if it does not exist.

    Parameters
    ----------
    metrics : dict
        Mapping containing metric data to write. Must include a 'timestamp' key whose
        value is a POSIX timestamp (int or float, seconds since the epoch). The rest
        of the metric values will be written after the timestamp in the CSV row.
    metrics_path : Optional[str], optional
        Path to the CSV file to append to. If None, a default path is constructed
        relative to the module's script_dir: ../../metrics/metrics.csv.

    Behavior
    --------
    - If the target CSV file does not exist, it is created and a header row is
      written using the module-level METRIC_KEYS iterable.
    - The function converts metrics["timestamp"] to an ISO 8601 formatted string
      (via datetime.fromtimestamp(...).isoformat()) and appends a single CSV row
      consisting of the ISO timestamp followed by the remaining metric values,
      separated by commas.
    - Metric values are converted to strings when written.
    - The ordering of appended metric values (after the timestamp) follows the
      order of values returned by list(metrics.values())[1:], therefore callers
      should ensure the input dict preserves the intended ordering or that METRIC_KEYS
      and the dict are consistent.

    Returns
    -------
    None

    Raises
    ------
    KeyError
        If 'timestamp' is not present in the metrics dict.
    OSError
        If the file cannot be created or written to.

    Notes
    -----
    - This function depends on the module-level names METRIC_KEYS and script_dir
      to build the default file path and header. Ensure these are defined and
      consistent with the keys/ordering used in metrics.
    - The function writes using the default system text encoding.
    """
    # Check if `metrics.csv` does not exist. If it doesnt, create it and write header
    if not metrics_path:
        metrics_path = os.path.abspath(os.path.join(script_dir, "../..", "metrics", "metrics.csv"))

    if not os.path.exists(metrics_path):
        with open(metrics_path, "w") as f:
            f.write(",".join(METRIC_KEYS) + "\n")

    # Append metrics to `metrics.csv`
    timestamp_iso = datetime.datetime.fromtimestamp(metrics["timestamp"]).isoformat()
    with open(metrics_path, "a") as f:
        f.write(
            timestamp_iso + "," + ",".join([str(x) for x in list(metrics.values())[1:]]) + "\n"
        )


def get_answer(user_query: str, metrics_path: Optional[str] = None) -> tuple[str, dict]:
    """
    Send a user query to the configured chat completion model, record runtime and usage metrics,
    append those metrics to a CSV, and return the model-generated answer along with the metrics.

    The function performs the following steps:
    1. Sends the provided user_query to the chat completion API using the configured model,
        system prompt and response format.
    2. Measures round-trip latency (in milliseconds) for the API call.
    3. Computes an estimated cost (USD) for the request using token usage and the global
        `costs` table for the selected model (including cached tokens).
    4. Constructs a metrics dictionary with the created timestamp, token counts, latency and
        estimated cost, and writes/appends these metrics to a CSV via `append_metrics_to_csv`.
    5. Returns the textual assistant response and the metrics dictionary.

    Parameters
    ----------
    user_query : str
         The user's query or prompt to send to the chat completion model.
    metrics_path : Optional[str], optional
         Path to the CSV file where metrics should be appended. If None, the behavior
         depends on the implementation of `append_metrics_to_csv` (it may use a default
         location or no-op).

    Returns
    -------
    tuple[str, dict]
         A tuple containing:
         - response_output (str): The text content of the model's response (response.choices[0].message.content).
         - metrics (dict): A dictionary containing the recorded metrics. Expected keys (as used by METRIC_KEYS)
            include:
              - timestamp: model-provided creation timestamp (typically an int).
              - tokens_prompt: number of prompt tokens consumed (int).
              - tokens_completion: number of completion tokens produced (int).
              - total_tokens: total tokens (int).
              - latency_ms: elapsed round-trip time in milliseconds (float).
              - estimated_cost_usd: estimated cost for this request in USD (float).

    Raises
    ------
    RuntimeError, ValueError, KeyError, OSError, ...
         The function may raise exceptions originating from the underlying model client (network errors,
         API errors), from missing or malformed response fields, from cost lookup failures in the global
         `costs` mapping, or from file I/O when appending metrics. Callers should handle/propagate exceptions
         appropriate to their context.

    Notes
    -----
    - This function relies on several module-global names: `client`, `COMPLETION_MODEL_NAME`, `system_prompt`,
      `SupportAgentResponse`, `costs`, `METRIC_KEYS`, and `append_metrics_to_csv`.
    - The exact format and types returned by the model client dictate the contents of `metrics`; callers
      should not assume more than the documented keys and general types above.
    - Estimated cost is computed using prompt_tokens, completion_tokens and prompt cached tokens as seen in the
      response usage fields; the precise pricing logic comes from the `costs` mapping for the chosen model.

    Example
    -------
    >>> answer, metrics = get_answer("How do I reset my password?", metrics_path="metrics.csv")
    >>> print(answer)
    "To reset your password, ..."
    >>> print(metrics["latency_ms"], metrics["estimated_cost_usd"])
    """
    start_time_sec = time.time()
    response = client.chat.completions.parse(
        model=COMPLETION_MODEL_NAME,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_query}
        ],
        reasoning_effort='minimal',
        response_format=SupportAgentResponse
    )
    end_time_sec = time.time()

    # Latency in milliseconds
    response_time_ms = (end_time_sec - start_time_sec) * 1000

    estimated_cost_usd = (
        (response.usage.prompt_tokens / 1_000_000) * costs[COMPLETION_MODEL_NAME]["input_tokens"] +
        (response.usage.completion_tokens / 1_000_000) * costs[COMPLETION_MODEL_NAME]["output_tokens"]  +
        (response.usage.prompt_tokens_details.cached_tokens / 1_000_000) * costs[COMPLETION_MODEL_NAME]["cached_tokens"]
    )

    # timestamp, tokens_prompt, tokens_completion, total_tokens, latency_ms, estimated_cost_usd
    metrics = dict(zip(
        METRIC_KEYS,
            [response.created,
             response.usage.prompt_tokens,
             response.usage.completion_tokens,
             response.usage.total_tokens,
             response_time_ms,
             estimated_cost_usd
            ]
        ))

    # Write metrics to CSV
    append_metrics_to_csv(metrics, metrics_path)

    response_output = response.choices[0].message.content
    return response_output, metrics