#!/usr/bin/env python3
"""
Capstone stretch: a load observation.

    python load_test.py

Normal rate for FitFindr is one request at a time, each sent when the last one
answers. Ten times that is ten requests at once. This runs both against a fresh
serve.py (cache off), 60 s apart so each starts with a clean per-minute quota:

  normal  — 10 matching queries, one after another
  10x     — the same 10 queries, all sent at the same moment (10 threads)

and compares them from the log: end-to-end latency, time queued for serve.py's
lock (wait_ms), rate-limiter wait, model time, errors, tokens per run.
Records: results/capstone/load/{normal,10x}.jsonl. Report: results/capstone/load.md.
"""

import json
import statistics
import threading
import time
from pathlib import Path

import capstone_trials as ct

ROOT = Path(__file__).parent
OUT = ROOT / "results" / "capstone" / "load"
QUERIES = ct.MATCHING[:10]


def batch(label: str, concurrent: bool) -> list[dict]:
    log, out = OUT / f"{label}.jsonl", OUT / f"{label}_server.txt"
    for f in (log, out):
        f.unlink(missing_ok=True)
    proc = ct.start_server(log, out, broken_key=False)
    results = [None] * len(QUERIES)
    t0 = time.perf_counter()
    try:
        if concurrent:
            def go(i, q):
                results[i] = ct.post(json.dumps({"query": q}))
            threads = [threading.Thread(target=go, args=(i, q)) for i, q in enumerate(QUERIES)]
            for t in threads:
                t.start()
            for t in threads:
                t.join()
        else:
            for i, q in enumerate(QUERIES):
                results[i] = ct.post(json.dumps({"query": q}))
    finally:
        wall = time.perf_counter() - t0
        ct.stop_server(proc)
    records = [json.loads(l) for l in log.read_text().splitlines() if l.strip()]
    statuses = [r["status"] for r in results]
    return {"label": label, "wall_s": wall, "statuses": statuses, "records": records}


def stats(b: dict) -> dict:
    rs = b["records"]
    d = [r["duration_ms"] for r in rs]
    ok = [r for r in rs if r["status"] == 200 and r["outcome"] == "fit_card"]
    m = lambda k: statistics.mean((r.get(k) or 0) for r in rs) if rs else 0
    return {
        "sent": len(QUERIES), "records": len(rs),
        "fit_cards": len(ok),
        "errors": sum(1 for s in b["statuses"] if s != 200),
        "wall_s": b["wall_s"],
        "median_ms": statistics.median(d), "max_ms": max(d),
        "mean_wait_ms": m("wait_ms"), "max_wait_ms": max((r.get("wait_ms") or 0) for r in rs),
        "mean_rate_limit_ms": m("rate_limit_wait_ms"), "mean_model_ms": m("model_wait_ms"),
        "tokens_per_run": statistics.mean(r["total_tokens"] for r in ok) if ok else 0,
    }


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    normal = batch("normal", concurrent=False)
    print("normal done; waiting 60 s for a clean quota minute", flush=True)
    time.sleep(60)
    tenx = batch("10x", concurrent=True)

    a, b = stats(normal), stats(tenx)
    rows = [
        ("requests sent / records logged", f"{a['sent']} / {a['records']}", f"{b['sent']} / {b['records']}"),
        ("fit cards returned", a["fit_cards"], b["fit_cards"]),
        ("non-200 responses", a["errors"], b["errors"]),
        ("wall clock for all 10", f"{a['wall_s']:.1f} s", f"{b['wall_s']:.1f} s"),
        ("median duration_ms", f"{a['median_ms']:,.0f}", f"{b['median_ms']:,.0f}"),
        ("max duration_ms", f"{a['max_ms']:,.0f}", f"{b['max_ms']:,.0f}"),
        ("mean wait_ms (queued for the lock)", f"{a['mean_wait_ms']:,.0f}", f"{b['mean_wait_ms']:,.0f}"),
        ("max wait_ms", f"{a['max_wait_ms']:,.0f}", f"{b['max_wait_ms']:,.0f}"),
        ("mean rate_limit_wait_ms", f"{a['mean_rate_limit_ms']:,.0f}", f"{b['mean_rate_limit_ms']:,.0f}"),
        ("mean model_wait_ms", f"{a['mean_model_ms']:,.0f}", f"{b['mean_model_ms']:,.0f}"),
        ("tokens per full run", f"{a['tokens_per_run']:.0f}", f"{b['tokens_per_run']:.0f}"),
    ]
    lines = ["# Load observation", "",
             "Produced by `load_test.py`. Records: `results/capstone/load/normal.jsonl`, `10x.jsonl`.", "",
             "| Measure | Normal (1 at a time) | 10x (10 at once) |", "|---|---|---|"]
    lines += [f"| {k} | {x} | {y} |" for k, x, y in rows]
    lines += ["", "10x, per request in the order the lock let them through:", "",
              "```", f"{'request_id':<10} {'duration':>9} {'wait_ms':>9} {'rate_lim':>9} {'model':>8}  query"]
    for r in sorted(tenx["records"], key=lambda r: r["wait_ms"] or 0):
        lines.append(f"{r['request_id']:<10} {r['duration_ms']:>9.0f} {r['wait_ms'] or 0:>9.0f} "
                     f"{r.get('rate_limit_wait_ms') or 0:>9.0f} {r.get('model_wait_ms') or 0:>8.0f}  {r['query']}")
    lines.append("```")
    text = "\n".join(lines)
    (OUT.parent / "load.md").write_text(text)
    print(text)


if __name__ == "__main__":
    main()
