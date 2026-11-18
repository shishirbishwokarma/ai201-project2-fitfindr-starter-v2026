"""
Structured request log for serve.py. ← CAPSTONE

Every request to /ask writes ONE line of JSON to logs/requests.jsonl — the good
runs, the empty searches, the model failures, the 400s and the 500s. A failure
that only shows up as a missing line is one nobody ever finds, so the write
happens on every path out of the route.

Fields (every record has all of them; ones that don't apply are null):

    ts              UTC time the request arrived, ISO 8601
    request_id      8 hex chars, also sent back as the X-Request-Id header
    route           "/ask"
    status          HTTP status sent back (200 / 400 / 500)
    outcome         fit_card | no_results | model_unavailable | mcp_error
                    | bad_request | crash
    query           what came in, as sent
    parsed          {description, size, max_price} from parse_query
    wardrobe_items  how many wardrobe items the run used
    selected_id     id of the listing chosen, or null
    selected_price  its price
    dropped         the filter the retry removed, e.g. "size MEDIUM"
    fit_card        what came out (the caption), or null
    error           the message the user got, or null
    duration_ms     arrival → response built, end to end, including any wait
    wait_ms         time spent queued behind another request (the lock)
    rate_limit_wait_ms  time generate.py slept for the rate limiter (own
                    pacing + 429 backoff) during this request   [improvement]
    model_wait_ms   time spent inside the model API call itself [improvement]
    stages_ms       {parse, search, retry_without_size, outfit, fit_card}
    model_calls     real calls made to the model during this request
    cache_hits      answers served from .cache instead of the model
    prompt_tokens   tokens sent, as the service reported them
    output_tokens   tokens received
    total_tokens    prompt + output
    model           config.MODEL

Read it back with `python log_summary.py`.
"""

import json
import os
import sys
from pathlib import Path

import config

LOG_PATH = Path(os.getenv("AI201_LOG", config.ROOT / "logs" / "requests.jsonl"))

FIELDS = (
    "ts", "request_id", "route", "status", "outcome", "query", "parsed",
    "wardrobe_items", "selected_id", "selected_price", "dropped", "fit_card",
    "error", "duration_ms", "wait_ms", "rate_limit_wait_ms", "model_wait_ms",
    "stages_ms", "model_calls", "cache_hits",
    "prompt_tokens", "output_tokens", "total_tokens", "model",
)


def write(record: dict) -> None:
    """Append one record. Never raises: a broken log must not break a request."""
    row = {key: record.get(key) for key in FIELDS}
    try:
        LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with LOG_PATH.open("a", encoding="utf-8") as f:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    except Exception as exc:  # noqa: BLE001
        print(f"  [log] couldn't write {LOG_PATH}: {exc}", file=sys.stderr, flush=True)


def read(path: Path | None = None) -> list[dict]:
    """Every record in the log, oldest first. Skips a line that isn't JSON."""
    path = path or LOG_PATH
    if not path.exists():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return rows
