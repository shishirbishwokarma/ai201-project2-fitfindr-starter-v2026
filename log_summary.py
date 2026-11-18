#!/usr/bin/env python3
"""
Read logs/requests.jsonl back and summarise it. ← CAPSTONE

    python log_summary.py                    everything in the log
    python log_summary.py --since 2026-11-18T06:00
    python log_summary.py --file results/capstone/trial1.jsonl
    python log_summary.py --tail 12          print the last 12 records as JSON

Answers, without adding code first: how many requests, how each one ended,
how long they took, what they cost in model calls and tokens, and where the
time went.
"""

import argparse
import json
import statistics
from pathlib import Path

import runlog


def pct(values, p):
    """Nearest-rank percentile. Fine for tens of values; that's what we have."""
    if not values:
        return None
    ordered = sorted(values)
    k = max(0, min(len(ordered) - 1, round(p / 100 * len(ordered) + 0.5) - 1))
    return ordered[k]


def fmt(x, unit=""):
    return "—" if x is None else f"{x:,.0f}{unit}"


def summarise(rows):
    print(f"{len(rows)} requests\n")

    outcomes = {}
    for r in rows:
        outcomes.setdefault((r["outcome"], r["status"]), []).append(r)
    print(f"{'outcome':<20}{'status':>7}{'count':>7}")
    for (outcome, status), rs in sorted(outcomes.items(), key=lambda kv: -len(kv[1])):
        print(f"{outcome:<20}{status:>7}{len(rs):>7}")

    print(f"\n{'duration (ms)':<20}{'n':>4}{'mean':>9}{'median':>9}{'p90':>9}{'max':>9}")
    for outcome in sorted({r['outcome'] for r in rows}):
        d = [r["duration_ms"] for r in rows if r["outcome"] == outcome]
        print(f"{outcome:<20}{len(d):>4}{fmt(statistics.mean(d)):>9}"
              f"{fmt(statistics.median(d)):>9}{fmt(pct(d, 90)):>9}{fmt(max(d)):>9}")

    full = [r for r in rows if r["outcome"] == "fit_card"]
    real = [r for r in full if r["cache_hits"] == 0]
    if full:
        print(f"\nfull runs (fit_card): {len(full)}, of which {len(real)} with no cache hits")
    if real:
        mean = lambda key: statistics.mean(r[key] for r in real)
        print(f"  per full run, cache off:  {mean('model_calls'):.2f} model calls, "
              f"{mean('prompt_tokens'):.0f} prompt + {mean('output_tokens'):.0f} output "
              f"= {mean('total_tokens'):.0f} tokens, {mean('duration_ms')/1000:.2f} s")
        stages = {}
        for r in real:
            for k, v in (r["stages_ms"] or {}).items():
                stages.setdefault(k, []).append(v)
        total = sum(statistics.mean(v) for v in stages.values())
        print("  where the time goes (mean ms, share of stage time):")
        for k, v in stages.items():
            m = statistics.mean(v)
            print(f"    {k:<20}{m:>8.0f}  {m/total:>5.0%}")
        waits = [r["wait_ms"] or 0 for r in real]
        print(f"    {'(queued for lock)':<20}{statistics.mean(waits):>8.0f}")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--file", type=Path, default=None)
    ap.add_argument("--since", default=None, help="only records with ts >= this (ISO prefix)")
    ap.add_argument("--tail", type=int, default=0, help="print the last N records instead")
    args = ap.parse_args()

    rows = runlog.read(args.file)
    if args.since:
        rows = [r for r in rows if r["ts"] >= args.since]
    if not rows:
        print("No records.")
        return
    if args.tail:
        for r in rows[-args.tail:]:
            print(json.dumps(r, ensure_ascii=False))
        return
    summarise(rows)


if __name__ == "__main__":
    main()
