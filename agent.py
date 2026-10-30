"""
The FitFindr planning loop.

This is the file that makes FitFindr an agent rather than a script. It decides
which tool to run next based on what the last one returned.

If your loop calls all three tools no matter what comes back, you have a list
of function calls. A loop looks at the last result before it picks the next
step. **That branch is the graded part of this unit.**

Build and test your three tools in `tools.py` first. Then come here.

    python agent.py          runs both example paths below
"""

import re

import config
import trace
from mcp_client import MCPError, call_tool
from tools import suggest_outfit, create_fit_card
from generate import ModelUnavailable


# ── session state ─────────────────────────────────────────────────────────────

def new_session(query: str, wardrobe: dict) -> dict:
    """
    A fresh session for one user interaction.

    The session is the single source of truth for a run. Every tool result goes
    in here, and the next tool reads it back out.

    You could pass values straight from one call to the next. It would work,
    and you would not be able to test it — you can't print a variable you have
    already overwritten. Going through the session is what makes the state
    visible, and unit 4 has you write a criterion about exactly that.

    Add fields if you need them.
    """
    return {
        "query": query,              # what the user typed
        "parsed": {},                # description / size / max_price you pulled out of it
        "search_results": [],        # everything search_listings returned
        "selected_item": None,       # the one you chose — goes into suggest_outfit
        "wardrobe": wardrobe,        # the user's wardrobe
        "outfit_suggestion": None,   # what suggest_outfit returned
        "fit_card": None,            # what create_fit_card returned
        "error": None,               # set when the run ended early
    }


# ── planning loop ─────────────────────────────────────────────────────────────

def run_agent(query: str, wardrobe: dict) -> dict:
    """
    Run the loop once and return the finished session.

    Args:
        query:    what the user asked for, in plain language
                  (e.g. "vintage graphic tee under $30, size M").
        wardrobe: a wardrobe dict — get_example_wardrobe() or
                  get_empty_wardrobe() from utils/data_loader.py.

    Returns:
        The session dict. **Check session["error"] first** — if it isn't None,
        the run ended early and the later fields will still be None.

    ─────────────────────────────────────────────────────────────────────────
    TODO — build this, following the branch rule you wrote in Milestone 2.

      1. Start a session with new_session().

      2. Count the times round the loop, and call trace.check_iterations(count)
         on each one before you go again. It raises when the count passes
         MAX_ITERATIONS in config.py — see trace.py.

      3. Parse the query into a description, a size, and a max_price. Regex,
         string splitting, or asking the model are all fine — say which you
         chose in your README. Put the result in session["parsed"].

      4. Call search_listings() with what you parsed.
         Put the results in session["search_results"].

         ⚠️ THIS IS THE BRANCH. If nothing came back:
              - put a message in session["error"] saying what the user could
                change — "No results" is not that message
              - return the session
              - do NOT call suggest_outfit with nothing

      5. Choose an item — the first result is fine. Put it in
         session["selected_item"].

      6. Call suggest_outfit() with the selected item and the wardrobe.
         Put the result in session["outfit_suggestion"].

      7. Call create_fit_card() with the outfit and the item.
         Put the result in session["fit_card"].

      8. Return the session.

    ─────────────────────────────────────────────────────────────────────────
    IN UNIT 4 you come back and add two things:

      • Trace calls. One per step. `trace.step("search_listings", inputs=...,
        returned=...)` — see trace.py. Your README needs the output.

      • A handler for ModelUnavailable, so a bad key produces a message rather
        than a stack trace. The import is already at the top of this file.
    """
    session = new_session(query, wardrobe)
    session["parsed"] = parse_query(query)
    trace.step("parse_query", inputs=repr(query), returned=str(session["parsed"]))

    next_step = "search"
    count = 0
    while next_step != "done":
        count += 1
        trace.check_iterations(count)

        try:
            if next_step == "search":
                p = session["parsed"]
                # Unit 4: search_listings now runs on the MCP server (mcp_server.py).
                args = {
                    "description": p["description"],
                    "size": p["size"],
                    "max_price": p["max_price"],
                }
                session["search_results"] = call_tool("search_listings", args)
                # The branch: nothing found means stop here, before any model call.
                if not session["search_results"]:
                    session["error"] = _no_results_message(p)
                    next_step = "done"
                    note = "branch: empty search, stopping before suggest_outfit"
                else:
                    session["selected_item"] = session["search_results"][0]
                    next_step = "outfit"
                    note = f"branch: {len(session['search_results'])} found, selected_item = first ({session['selected_item']['id']})"
                trace.step("search_listings (via MCP)", inputs=f"call_tool('search_listings', {args})",
                           returned=session["search_results"], note=note)

            elif next_step == "outfit":
                items = session["wardrobe"].get("items") or []
                session["outfit_suggestion"] = suggest_outfit(
                    session["selected_item"], session["wardrobe"]
                )
                trace.step(
                    "suggest_outfit",
                    inputs=f"new_item={session['selected_item']['id']} (session['selected_item']), wardrobe={len(items)} items",
                    returned=session["outfit_suggestion"],
                    note="empty wardrobe, general advice" if not items else "",
                )
                next_step = "fit_card"

            elif next_step == "fit_card":
                session["fit_card"] = create_fit_card(
                    session["outfit_suggestion"], session["selected_item"]
                )
                trace.step(
                    "create_fit_card",
                    inputs=f"outfit=session['outfit_suggestion'], new_item={session['selected_item']['id']}",
                    returned=session["fit_card"],
                )
                next_step = "done"

        except ModelUnavailable as exc:
            tool = "suggest_outfit" if next_step == "outfit" else "create_fit_card"
            found = session["selected_item"]
            session["error"] = (
                f"The search worked and found {found['title']} (${found['price']:.0f} on "
                f"{found['platform']}), but the AI model couldn't be reached for {tool}, "
                f"so there's no outfit or fit card. The model said: {exc} "
                "Fix the key in .env (or check your internet), then ask again."
            )
            trace.step(tool, note=f"ModelUnavailable, stopping: {exc}")
            next_step = "done"

        except MCPError as exc:
            session["error"] = (
                "The listing search couldn't run, because the MCP server didn't answer. "
                "Check that `python mcp_server.py` starts without an error, then ask again. "
                f"Details: {str(exc).splitlines()[0]}"
            )
            trace.step("search_listings (via MCP)", note="MCPError, stopping")
            next_step = "done"

    return session


# ── query parsing ─────────────────────────────────────────────────────────────

_FILLER = {
    "looking", "for", "a", "an", "the", "i", "im", "i'm", "want", "need",
    "some", "something", "please", "find", "me", "under", "in", "below",
}


def parse_query(query: str) -> dict:
    """
    Pull a price ceiling and a size out of the query with regex. Whatever is
    left, minus filler words, is the description.

        "vintage graphic tee under $30, size M"
        -> {"description": "vintage graphic tee", "size": "M", "max_price": 30.0}
    """
    text = query.strip()

    max_price = None
    price = re.search(r"(?:under|below|max|less than)?\s*\$\s*(\d+(?:\.\d+)?)", text, re.I) \
        or re.search(r"(?:under|below)\s+(\d+(?:\.\d+)?)", text, re.I)
    if price:
        max_price = float(price.group(1))
        text = text[: price.start()] + " " + text[price.end():]

    size = None
    size_match = re.search(r"\bsize\s+([a-z0-9./]+)", text, re.I)
    if size_match:
        size = size_match.group(1).upper()
        text = text[: size_match.start()] + " " + text[size_match.end():]

    words = [w for w in re.findall(r"[a-z0-9'\-]+", text.lower()) if w not in _FILLER]
    return {"description": " ".join(words), "size": size, "max_price": max_price}


def _no_results_message(parsed: dict) -> str:
    """Say what was searched for and which filter to loosen first."""
    used = [f'"{parsed["description"]}"']
    tips = []
    if parsed["size"]:
        used.append(f"size {parsed['size']}")
        tips.append(f"drop the size {parsed['size']} filter")
    if parsed["max_price"] is not None:
        used.append(f"under ${parsed['max_price']:.0f}")
        tips.append(f"raise the ${parsed['max_price']:.0f} limit (listings start at $12)")
    tips.append("use fewer or more common words, like a category (tee, jeans, jacket, dress, sneakers) or a style (vintage, y2k, 90s)")
    return (
        f"No listings matched {', '.join(used)}. Try one change at a time: "
        + "; or ".join(tips) + "."
    )


# ── running it directly ───────────────────────────────────────────────────────

def _show(session: dict) -> None:
    if session["error"]:
        print(f"  stopped: {session['error']}")
        print(f"  fit_card is {session['fit_card']!r} — it should still be None here")
        return

    item = session["selected_item"] or {}
    print(f"  found:    {item.get('title')} — ${item.get('price')} on {item.get('platform')}")
    print(f"  outfit:   {session['outfit_suggestion']}")
    print(f"  fit card: {session['fit_card']}")


if __name__ == "__main__":
    from utils.data_loader import get_example_wardrobe

    print("=== A query the data can match ===")
    _show(run_agent(
        query="looking for a vintage graphic tee under $30",
        wardrobe=get_example_wardrobe(),
    ))

    print("\n=== A query it can't ===")
    _show(run_agent(
        query="designer ballgown size XXS under $5",
        wardrobe=get_example_wardrobe(),
    ))

    print(
        "\nThe second one should stop before the fit card. If both paths look "
        "the same,\nthe branch isn't doing anything yet."
    )
