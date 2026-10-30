"""
The runs your test needs. ← UNIT 4, MILESTONE 3

Each of your five criteria needs something run against it. A criterion about
the empty-search branch needs an impossible query. One about the fit card needs
the same item run more than once. Working that out is Milestone 3's first step,
and this file is where you write it down.

`run_eval.py` runs everything here five times and writes the run log — five
because your criteria are written out of five.

Three scenarios are filled in to show the shape. Add or change whatever your
own criteria need — these are a starting point, not a fixed set.
"""

SCENARIOS = [
    {
        # A query the data can match. Criterion 1.
        "name": "matching query completes",
        "query": "vintage graphic tee under $30",
        "wardrobe": "example",
        "criterion": 1,
    },
    {
        # A query nothing can match. Criterion 2 — the branch.
        "name": "impossible query stops early",
        "query": "designer ballgown size XXS under $5",
        "wardrobe": "example",
        "criterion": 2,
    },
    {
        # Criterion 3: the id in session["selected_item"] is the id that
        # actually reached suggest_outfit. Any normal query works.
        "name": "selected item reaches suggest_outfit",
        "query": "flannel shirt under $25",
        "wardrobe": "example",
        "criterion": 3,
    },
    {
        # Criterion 4: fit card states the price and names no other brand from
        # the data. This item HAS a brand (Champion), so the card is allowed
        # that one and no other.
        "name": "fit card has price, no stray brand",
        "query": "90s track jacket in size M",
        "wardrobe": "example",
        "criterion": 4,
    },
    {
        # Criterion 5: every result is at or under the price limit.
        "name": "results stay under the price limit",
        "query": "denim jacket under $50",
        "wardrobe": "example",
        "criterion": 5,
    },
    {
        # Stretch: an empty search with a size retries once without it.
        # "medium" isn't read as M, so the first search finds nothing.
        "name": "retry without the size filter",
        "query": "size medium hoodie",
        "wardrobe": "example",
        "criterion": None,
    },
    {
        # A user with nothing saved. One of unit 4's three failure modes.
        "name": "empty wardrobe",
        "query": "denim jacket under $50",
        "wardrobe": "empty",
        "criterion": None,
    },
]

WARDROBES = ("example", "empty")


def validate() -> list[str]:
    """Complain about anything malformed, before a long run rather than during."""
    problems = []
    for i, scenario in enumerate(SCENARIOS, 1):
        if not scenario.get("query", "").strip():
            problems.append(f"scenario {i} has no query")
        if scenario.get("wardrobe") not in WARDROBES:
            problems.append(
                f"scenario {i} has wardrobe {scenario.get('wardrobe')!r} — "
                f"it should be one of {WARDROBES}"
            )
    return problems
