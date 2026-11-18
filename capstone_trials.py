#!/usr/bin/env python3
"""
Run the capstone trials and score them against criteria.md (Capstone 1–5).

    python capstone_trials.py --label before            three trials
    python capstone_trials.py --label after --trials 3

One trial:
  1. Start serve.py fresh (cache off), its log going to
     results/capstone/<label>/trialN.jsonl, its terminal output to trialN_server.txt.
  2. Send 10 matching queries back to back            (criterion 2, and 1)
     then 2 more matching, 2 impossible, 5 malformed  (criterion 5, and 1)
  3. Stop it, start it again with a broken GEMINI_API_KEY, same log file.
     Send 5 matching queries                         (criterion 4; the first is in 1)
  4. Score every criterion from the log records and the HTTP responses.

Nothing is changed between trials. Trials are 60 s apart so the service's
per-minute quota starts each trial clean.
"""

import argparse
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).parent
PORT = 5057
URL = f"http://localhost:{PORT}"

MATCHING = [
    "vintage graphic tee under $30",
    "90s track jacket in size M",
    "silk slip dress in midi length under $40",
    "platform sneakers size 8",
    "denim jacket under $50",
    "flannel shirt under $25",
    "jacket $50",
    "something cute for a date under $40",
    "black boots",
    "size medium hoodie",
    "cheap sneakers",
    "denim jaket",
]
IMPOSSIBLE = ["designer ballgown size XXS under $5", "sequin tuxedo size XXXL under $3"]
MALFORMED = [  # (name, raw body) — criterion 5's five, in its order
    ("blank query", json.dumps({"query": "   "})),
    ("not JSON", "query=vintage tee"),
    ("query is a number", json.dumps({"query": 42})),
    ("wardrobe items not a list", json.dumps({"query": "denim jacket", "wardrobe": {"items": "x"}})),
    ("5,000-character query", json.dumps({"query": ("vintage tee " * 500)[:5000]})),
]
BROKEN_KEY = "AIzaBROKENKEY0000000000000000000000000"
SLOW_MS = 5000


def post(body: str) -> dict:
    """Send one /ask. Returns status, request id header, parsed body, client time."""
    req = urllib.request.Request(f"{URL}/ask", data=body.encode(), method="POST",
                                 headers={"Content-Type": "application/json"})
    t = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            status, headers, raw = r.status, r.headers, r.read()
    except urllib.error.HTTPError as e:
        status, headers, raw = e.code, e.headers, e.read()
    except Exception as e:  # noqa: BLE001 — a dropped connection is a result too
        return {"status": None, "rid": None, "body": {"error": repr(e)},
                "client_ms": round((time.perf_counter() - t) * 1000, 1)}
    try:
        parsed = json.loads(raw)
    except Exception:  # noqa: BLE001
        parsed = {"raw": raw[:300].decode(errors="replace")}
    return {"status": status, "rid": headers.get("X-Request-Id"), "body": parsed,
            "client_ms": round((time.perf_counter() - t) * 1000, 1)}


def start_server(log: Path, out: Path, broken_key: bool) -> subprocess.Popen:
    env = dict(os.environ, AI201_CACHE="0", PORT=str(PORT), AI201_LOG=str(log))
    if broken_key:
        env["GEMINI_API_KEY"] = BROKEN_KEY   # beats .env: load_dotenv doesn't override
    proc = subprocess.Popen([sys.executable, "serve.py"], cwd=ROOT, env=env,
                            stdout=out.open("a"), stderr=subprocess.STDOUT)
    for _ in range(60):
        try:
            urllib.request.urlopen(f"{URL}/health", timeout=1)
            return proc
        except Exception:  # noqa: BLE001
            time.sleep(0.25)
    proc.kill()
    raise RuntimeError("server didn't come up; see " + str(out))


def stop_server(proc):
    proc.terminate()
    try:
        proc.wait(timeout=10)
    except subprocess.TimeoutExpired:
        proc.kill()


def run_trial(n: int, outdir: Path) -> dict:
    log, out = outdir / f"trial{n}.jsonl", outdir / f"trial{n}_server.txt"
    for f in (log, out):
        f.unlink(missing_ok=True)

    sent = []  # (group, label, response)
    proc = start_server(log, out, broken_key=False)
    try:
        for q in MATCHING:
            sent.append(("matching", q, post(json.dumps({"query": q}))))
            print(f"  trial {n}: {sent[-1][2]['status']} {sent[-1][2]['client_ms']:>8.0f} ms  {q}", flush=True)
        for q in IMPOSSIBLE:
            sent.append(("impossible", q, post(json.dumps({"query": q}))))
        for name, body in MALFORMED:
            sent.append(("malformed", name, post(body)))
    finally:
        stop_server(proc)

    proc = start_server(log, out, broken_key=True)
    try:
        for q in MATCHING[:5]:
            sent.append(("broken_key", q, post(json.dumps({"query": q}))))
    finally:
        stop_server(proc)

    records = [json.loads(l) for l in log.read_text().splitlines() if l.strip()]
    return {"sent": sent, "records": records}


def cause_fields(rec: dict) -> dict:
    """Top-level numeric fields that name a reason for waiting."""
    return {k: v for k, v in rec.items()
            if (k == "wait_ms" or k.endswith("_wait_ms")) and isinstance(v, (int, float))}


def score(trial: dict) -> dict:
    sent, records = trial["sent"], trial["records"]
    by_id = {}
    for r in records:
        by_id.setdefault(r["request_id"], []).append(r)
    rec = lambda resp: (by_id.get(resp["rid"]) or [None])[0]

    # 1 — the defined 20: 12 matching, 2 impossible, 5 malformed, first broken-key
    c1_set = [s for s in sent if s[0] != "broken_key"] + [s for s in sent if s[0] == "broken_key"][:1]
    c1_ok = [s for s in c1_set if s[2]["rid"] and len(by_id.get(s[2]["rid"], [])) == 1]
    extra = len(records) - len(sent)
    c1 = {"n": len(c1_ok), "of": len(c1_set), "pass": len(c1_ok) == len(c1_set),
          "note": f"{len(records)} records for {len(sent)} requests sent"
                  + (f", {extra:+d} unaccounted" if extra else "")}

    # 2 — first ten matching, back to back
    first10 = [s for s in sent if s[0] == "matching"][:10]
    durs = [(s[1], (rec(s[2]) or {}).get("duration_ms")) for s in first10]
    fast = [d for _, d in durs if d is not None and d < SLOW_MS]
    c2 = {"n": len(fast), "of": 10, "pass": len(fast) >= 9,
          "slow": [(q, d) for q, d in durs if d is None or d >= SLOW_MS]}

    # 3 — every slow request in the trial names its cause
    slow = [r for r in records if (r.get("duration_ms") or 0) > SLOW_MS]
    explained = []
    for r in slow:
        causes = cause_fields(r)
        best = max(causes.items(), key=lambda kv: kv[1], default=(None, 0))
        explained.append((r["request_id"], r["query"], r["duration_ms"], best,
                          best[1] >= r["duration_ms"] / 2))
    c3 = {"n": sum(e[-1] for e in explained), "of": len(slow),
          "pass": all(e[-1] for e in explained), "detail": explained}

    # 4 — broken key: 503 and the body names the key
    bk = [s for s in sent if s[0] == "broken_key"]
    c4_rows = []
    for _, q, resp in bk:
        err = json.dumps(resp["body"]).lower()
        c4_rows.append((q, resp["status"], "api key" in err, resp["status"] == 503 and "api key" in err))
    c4 = {"n": sum(r[-1] for r in c4_rows), "of": len(bk),
          "pass": all(r[-1] for r in c4_rows), "detail": c4_rows}

    # 5 — malformed: 4xx, under 200 ms, never 500
    c5_rows = []
    for _, name, resp in [s for s in sent if s[0] == "malformed"]:
        r = rec(resp)
        d = r.get("duration_ms") if r else None
        ok = resp["status"] is not None and 400 <= resp["status"] < 500 and d is not None and d < 200
        c5_rows.append((name, resp["status"], d, (r or {}).get("outcome"), ok))
    c5 = {"n": sum(r[-1] for r in c5_rows), "of": len(c5_rows),
          "pass": all(r[-1] for r in c5_rows), "detail": c5_rows}

    return {1: c1, 2: c2, 3: c3, 4: c4, 5: c5}


TARGETS = {1: "20 of 20", 2: "9 of 10 < 5 s", 3: "all slow ones", 4: "5 of 5", 5: "5 of 5"}
NAMES = {1: "Every request leaves exactly one record", 2: "Ten in a row stay under 5 s",
         3: "A slow request explains itself in the log", 4: "Broken key returns 503",
         5: "Bad input: 4xx under 200 ms, no 500"}


def report(label: str, scores: list[dict], outdir: Path) -> str:
    lines = [f"# Capstone run log — {label}", "",
             "Produced by `capstone_trials.py` (`run_trial`, `score`). Raw records: "
             f"`results/capstone/{label}/trialN.jsonl`; server output: `trialN_server.txt`.", "",
             "| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |", "|---|---|---|---|---|---|"]
    for c in range(1, 6):
        cells = []
        for s in scores:
            x = s[c]
            cells.append(f"{x['n']}/{x['of']}" + ("" if x["pass"] else " ✗"))
        verdict = "MET" if all(s[c]["pass"] for s in scores) else "MISSED"
        lines.append(f"| {c}. {NAMES[c]} | {TARGETS[c]} | " + " | ".join(cells) + f" | {verdict} |")
    lines.append("")
    for i, s in enumerate(scores, 1):
        lines.append(f"## Run {i} detail")
        lines.append(f"- 1: {s[1]['note']}")
        lines.append(f"- 2: slow: {s[2]['slow'] or 'none'}")
        lines.append(f"- 3: {len(s[3]['detail'])} slow requests")
        for rid, q, d, best, ok in s[3]["detail"]:
            lines.append(f"    - {rid} {q!r} {d:.0f} ms, best cause field {best[0]}={best[1]} → {'PASS' if ok else 'FAIL'}")
        lines.append("- 4: " + "; ".join(f"{st} key-named={k}" for _, st, k, _ in s[4]["detail"]))
        lines.append("- 5: " + "; ".join(f"{n}: {st}, {d} ms, {o}" for n, st, d, o, _ in s[5]["detail"]))
        lines.append("")
    text = "\n".join(lines)
    (outdir.parent / f"{label}.md").write_text(text)
    return text


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--label", required=True)
    ap.add_argument("--trials", type=int, default=3)
    args = ap.parse_args()
    outdir = ROOT / "results" / "capstone" / args.label
    outdir.mkdir(parents=True, exist_ok=True)

    scores = []
    for n in range(1, args.trials + 1):
        if n > 1:
            print("  waiting 60 s so the service's per-minute quota starts clean", flush=True)
            time.sleep(60)
        trial = run_trial(n, outdir)
        (outdir / f"trial{n}_responses.json").write_text(
            json.dumps([{"group": g, "label": l, **r} for g, l, r in trial["sent"]], indent=1, ensure_ascii=False))
        scores.append(score(trial))
    print(report(args.label, scores, outdir))


if __name__ == "__main__":
    main()
