"""
Run run_eval.py and score every try against criteria.md.

    python score_runs.py --label before

run_eval.py runs each scenario five times with the cache off and writes the
report into results/, but it leaves PASS/FAIL blank. This runs it unchanged,
records each try's session as it goes, and checks each one against the
criterion its scenario is tagged with, exactly as criteria.md words it.

It also watches suggest_outfit so criterion 3 can compare the item the tool
actually received with session["selected_item"]. The wrapper only records the
argument and then calls the real function, so the agent behaves the same.
"""

import re
import sys

import agent
import run_eval
from utils.data_loader import load_listings

BRANDS = sorted({l["brand"] for l in load_listings() if l["brand"]})

received = []   # ids suggest_outfit was actually called with, per try
_real_suggest = agent.suggest_outfit


def _watching_suggest(new_item, wardrobe):
    received.append(new_item.get("id"))
    return _real_suggest(new_item, wardrobe)


agent.suggest_outfit = _watching_suggest

records = []    # (scenario, record, ids received during that try)
_real_run_once = run_eval.run_once


def _recording_run_once(scenario, use_trace=True):
    received.clear()
    record = _real_run_once(scenario, use_trace)
    records.append((scenario, record, list(received)))
    return record


run_eval.run_once = _recording_run_once


def score(criterion, scenario, record, got):
    """Return (passed, evidence) for one try."""
    if record["crashed"]:
        return False, f"crashed: {record['crashed']}"
    s = record["session"]
    item = s["selected_item"]
    card = s["fit_card"] or ""

    if criterion == 1:
        ok = s["error"] is None and bool(card.strip())
        return ok, "fit card returned" if ok else f"no fit card (error: {s['error']})"

    if criterion == 2:
        named = all(w in (s["error"] or "") for w in ("Try", "drop", "raise"))
        ok = s["error"] is not None and not got and s["fit_card"] is None and named
        return ok, f"suggest_outfit calls: {len(got)}, message names what to change: {named}"

    if criterion == 3:
        ok = item is not None and got == [item["id"]]
        return ok, f"selected_item {item and item['id']} / suggest_outfit got {got}"

    if criterion == 4:
        if item is None:
            return False, "no item, no card"
        price = item["price"]
        has_price = re.search(rf"\${price:.0f}(\.0+)?\b", card) is not None
        own = (item["brand"] or "").lower()
        stray = [b for b in BRANDS if b.lower() != own and b.lower().rstrip("'s") in card.lower()]
        ok = has_price and not stray
        return ok, f"price ${price:.0f} in card: {has_price}; other brands: {stray or 'none'}"

    if criterion == 5:
        limit = s["parsed"]["max_price"]
        prices = [r["price"] for r in s["search_results"]]
        over = [p for p in prices if limit is not None and p > limit]
        ok = limit is not None and not over
        return ok, f"limit ${limit:.0f}, {len(prices)} results, max ${max(prices, default=0):.0f}, over: {over or 'none'}"

    return None, "diagnostic"


if __name__ == "__main__":
    run_eval.main()

    print("\n=== Scored against criteria.md ===\n")
    by_scenario = {}
    for scenario, record, got in records:
        by_scenario.setdefault(scenario["name"], (scenario, []))[1].append((record, got))

    for name, (scenario, tries) in by_scenario.items():
        c = scenario.get("criterion")
        results = [score(c, scenario, r, g) for r, g in tries]
        if c is None:
            print(f"{name} (diagnostic)")
        else:
            marks = " | ".join("PASS" if ok else "FAIL" for ok, _ in results)
            print(f"{c}. {name}: {marks}  ({sum(ok for ok, _ in results)}/{len(results)})")
        for i, (_, evidence) in enumerate(results, 1):
            print(f"    try {i}: {evidence}")
        print()

        # Criterion 4 covers any matching query, not only the jacket scenario,
        # so check the fit cards from criterion 1's tries against it too.
        if c == 1:
            extra = [score(4, scenario, r, g) for r, g in tries]
            marks = " | ".join("PASS" if ok else "FAIL" for ok, _ in extra)
            print(f"4. (on criterion 1's tries): {marks}  ({sum(ok for ok, _ in extra)}/{len(extra)})")
            for i, (_, evidence) in enumerate(extra, 1):
                print(f"    try {i}: {evidence}")
            print()
    sys.stdout.flush()
