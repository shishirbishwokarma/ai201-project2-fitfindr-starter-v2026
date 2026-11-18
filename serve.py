#!/usr/bin/env python3
"""
FitFindr over HTTP. ← UNIT 9

    python serve.py                       run it on your machine
    gunicorn serve:app                    run it the way a host runs it

Everything else in this repo exits after one command. A host has nothing to
keep running, so a command line cannot be deployed. This file is the smallest
thing that can: it starts a web server, waits, and hands each request to the
same `run_agent()` your CLI calls. **No new agent logic lives here.** If your
loop works from `python app.py ask`, it works from here; if it doesn't, fix it
there, not in this file.

Two routes:

    POST /ask       {"query": "vintage graphic tee under $30",
                     "wardrobe": {...}}     ← wardrobe is optional
    GET  /health    is it awake?

`/ask` returns the session dict from `run_agent()` as JSON, unchanged — the
same keys you print from the command line, including `error`. Read
`session["error"]` first, exactly as you do everywhere else.

It runs **one request at a time**, and one route is deliberately slower than a
web server has to be. The reason is worth reading before you deploy: see the
note above `_one_at_a_time` below — it also decides which gunicorn worker you
can use.

Capstone: every /ask request, including 400s and 500s, writes one JSON record
to logs/requests.jsonl through runlog.py: what came in, what came out, how
long it took (end to end, queued, and per stage), and the model calls and
tokens it used. Field list: runlog.py. Read it back: python log_summary.py.
"""

import os
import sys
import threading
import time
import uuid
from datetime import datetime, timezone

# config first, and before anything that talks to the model: it loads your .env
# and fixes the Windows console encoding for every module that imports it.
import config  # noqa: F401

from flask import Flask, jsonify, request

import generate
import runlog
from agent import run_agent
from utils.data_loader import get_example_wardrobe

app = Flask(__name__)


# ── one request at a time ─────────────────────────────────────────────────────
# Here's why this exists.
#
# A web server will happily run two requests at once. Two things in this repo
# assume otherwise:
#
#   • If you moved a tool onto MCP in unit 4, `mcp_client.call_tool` starts
#     `mcp_server.py` as a separate process over stdio, one per call. Two
#     overlapping requests means two extra Python interpreters, and the free
#     tier you're deploying to has 512 MB for all of it. That is the reason
#     that would still be here even if everything else were perfect.
#   • `generate.py`'s pacing window and its call counter are plain module
#     globals — deliberately, because that file is teaching pacing and quota,
#     not locking. Two threads sharing them means the per-minute limiter is
#     counting something that isn't true.
#
# What the lock covers is exactly the agent run: the part that spawns
# processes and calls the model. Reading the request, rejecting a bad one, and
# turning the answer into JSON all happen outside it — so a request with a
# malformed body comes straight back with a 400 instead of queueing behind
# somebody else's agent.
#
# Serialising the runs costs you nothing here — this is one user asking one
# question — and it keeps the deployed behaviour identical to the CLI's. When
# that stops being an acceptable trade, the fix is a real queue, not a bigger
# lock.
#
# The same constraint decides your start command, and this is the part that
# bites in deployment rather than on your machine. `mcp_client.call_tool`
# wraps `asyncio.run()`, and `asyncio.run()` refuses to start when an event
# loop is already running. An async worker always has one running. So under
# `gunicorn -k gevent` (or `-k eventlet`, or `serve:app` wrapped for an ASGI
# server like uvicorn) EVERY MCP call fails with "asyncio.run() cannot be
# called from a running event loop" — not some of them under load, all of
# them, every time, in a place your laptop never showed you.
#
#     gunicorn serve:app              ← right: the DEFAULT sync worker
#     gunicorn -k gevent serve:app    ← breaks every MCP call you make

_one_at_a_time = threading.Lock()


@app.get("/health")
def health():
    """Is the server awake? A host pings something like this to find out."""
    return jsonify({"status": "ok"})


@app.post("/ask")
def ask():
    """
    Run the agent on one query.

    In:   {"query": "...", "wardrobe": {...}}   wardrobe optional — leave it
                                                out and you get the same
                                                example wardrobe the CLI uses.
    Out:  the session dict from run_agent(), as JSON.
    """
    t_arrived = time.perf_counter()
    record = {
        "ts": datetime.now(timezone.utc).isoformat(timespec="milliseconds"),
        "request_id": uuid.uuid4().hex[:8],
        "route": "/ask",
        "model": config.MODEL,
    }

    def finish(body, status):
        """Every way out of this route goes through here, so every one is logged."""
        record["status"] = status
        record["duration_ms"] = round((time.perf_counter() - t_arrived) * 1000, 1)
        runlog.write(record)
        response = jsonify(body)
        response.status_code = status
        response.headers["X-Request-Id"] = record["request_id"]
        return response

    payload = request.get_json(silent=True)
    query = payload.get("query") if isinstance(payload, dict) else None
    record["query"] = query if isinstance(query, str) else (
        None if payload is None else repr(payload)[:200]
    )
    query = query.strip() if isinstance(query, str) else ""
    if not query:
        # 400 rather than a stack trace: the caller can act on this one.
        record["outcome"] = "bad_request"
        record["error"] = "missing or empty 'query'"
        return finish({"error": "Send JSON with a 'query' field, e.g. "
                                '{"query": "vintage graphic tee under $30"}'}, 400)

    wardrobe = payload.get("wardrobe")
    if not isinstance(wardrobe, dict):
        wardrobe = get_example_wardrobe()
    items = wardrobe.get("items")
    record["wardrobe_items"] = len(items) if isinstance(items, list) else None

    # A queued request should look like a queued request. Without this the
    # second caller just sits there, and "slow" and "waiting its turn" are
    # indistinguishable from the outside.
    if _one_at_a_time.locked():
        print(
            "  [serve] another request is still running. This one is waiting "
            "its turn — serve.py handles one at a time, on purpose.",
            file=sys.stderr,
            flush=True,
        )

    failure = None
    session = None
    t_queued = time.perf_counter()
    with _one_at_a_time:
        record["wait_ms"] = round((time.perf_counter() - t_queued) * 1000, 1)
        # generate.py's counters are module globals; inside the lock nobody
        # else moves them, so before/after is exactly this request's usage.
        calls0, hits0 = generate.call_count(), generate.cache_hit_count()
        tokens0 = generate.token_counts()
        waits0 = generate.wait_totals()
        try:
            session = run_agent(query, wardrobe)
        except Exception as exc:  # noqa: BLE001 — a 500 with a sentence beats a hang
            failure = f"{type(exc).__name__}: {exc}"
        tokens1 = generate.token_counts()
        waits1 = generate.wait_totals()
        record["rate_limit_wait_ms"] = round((waits1["limiter_s"] - waits0["limiter_s"]) * 1000, 1)
        record["model_wait_ms"] = round((waits1["model_s"] - waits0["model_s"]) * 1000, 1)
        record["model_calls"] = generate.call_count() - calls0
        record["cache_hits"] = generate.cache_hit_count() - hits0
        record["prompt_tokens"] = tokens1["prompt"] - tokens0["prompt"]
        record["output_tokens"] = tokens1["output"] - tokens0["output"]
        record["total_tokens"] = tokens1["total"] - tokens0["total"]

    # Outside the lock: building a response is not work the next caller should
    # be waiting on.
    if failure is not None:
        record["outcome"] = "crash"
        record["error"] = failure
        return finish({"error": failure}, 500)

    item = session.get("selected_item") or {}
    record.update({
        "outcome": session.get("error_kind") or "fit_card",
        "parsed": session.get("parsed"),
        "selected_id": item.get("id"),
        "selected_price": item.get("price"),
        "dropped": session.get("dropped"),
        "fit_card": session.get("fit_card"),
        "error": session.get("error"),
        "stages_ms": session.get("timings_ms"),
    })
    return finish(session, 200)


if __name__ == "__main__":
    # PORT and 0.0.0.0 are not decoration. A host tells you which port to
    # listen on through PORT, and it reaches your process from outside the
    # container — bind 127.0.0.1 and nothing but the container itself can
    # connect, which looks exactly like a broken app from the browser.
    port = int(os.getenv("PORT", "5000"))

    # Never on by default. Flask's debugger executes code typed into a browser,
    # and a deployed app with it on is a stranger's shell. Set AI201_DEBUG=1 in
    # your own terminal when you want the reloader.
    debug = os.getenv("AI201_DEBUG", "0") == "1"

    print(f"\nFitFindr is listening on http://localhost:{port}")
    print("It runs one request at a time — a second one waits for the first.")
    print("Ask it something (single quotes, as always):\n")
    print(
        f"  curl -X POST http://localhost:{port}/ask \\\n"
        f"    -H 'Content-Type: application/json' \\\n"
        f"    -d '{{\"query\": \"vintage graphic tee under $30\"}}'\n"
    )
    print("Ctrl-C to stop.\n")

    app.run(host="0.0.0.0", port=port, debug=debug)
