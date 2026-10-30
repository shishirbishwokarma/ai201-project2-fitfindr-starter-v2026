# FitFindr

**Shishir Bishwokarma**

> ### 👋 Start here
>
> **New to this repo? Read [RUNNING.md](RUNNING.md) first** — setup, every
> command, and what to do when something breaks.
>
> Once `python test.py` passes:
>
> ```bash
> python app.py listings --full -n 6      # read the data (Milestone 1)
> python app.py fields                    # what you can filter on
> python app.py ask 'vintage graphic tee under $30'
> ```
>
> All three tools are stubs, so that last command will do nothing useful yet.
> That's the starting position.
>
> **The rest of this file is your submission.** Fill it in as you go.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     HOW TO USE THIS FILE

     This is your submission. Fill each section in as you finish the milestone
     it belongs to — don't leave it all to the end.

     Unit 3 asks for the first five sections. Unit 4 adds the five below them.
     Leave the unit 4 sections alone until then; they're here so you know
     what's coming.

     Everything is pasted as TEXT. No screenshots, no images, no video links.
     A typed block of output gets full credit; a picture of the same output
     gets none.
     ───────────────────────────────────────────────────────────────────────── -->

<!-- ═══════════════════════ UNIT 3 — THE BUILD ═══════════════════════ -->

## What This Does

<!-- Three or four sentences: what a user asks for, and what they get back. -->

You type what you're hunting for in plain words, like `vintage graphic tee under $30, size M`, and FitFindr searches 40 secondhand listings from Depop, thredUp and Poshmark for something that fits the description, the size and the budget. If it finds one, it takes the best match, works out one or two outfits with clothes you already own (or general styling ideas if your wardrobe is empty), and writes a short caption you could post with the fit. If nothing matches, it stops right there and tells you which filter to loosen, without making anything up.



---

## Tool Inventory

<!-- Four lines per tool. This is worth 2 points and it's the single most
     common place students lose them.

     "Returns a list" earns NOTHING. The description has to say what is IN
     the list.

     The empty case isn't optional either — it's the thing your loop branches
     on, and if you don't decide it here you'll discover it as a crash in
     Milestone 5. -->

### `search_listings`

- **What it does:** Looks through the 40 listings in `data/listings.json`, drops anything over the price or in the wrong size, and ranks the rest by how many words from the description show up in the listing's title, description, style tags, category, colors and brand. Doesn't call the model.
- **Inputs:** <!-- name and type each: `max_price` (float), not "a price" -->
  - `description` (str): the words the user is looking for, e.g. `"vintage graphic tee"`.
  - `size` (str or None): the size to filter by, or `None` for any size. A listing matches if the requested size is one of the separate parts of its size field, ignoring case. The size field is split on anything that isn't a letter, digit or dot. So `"M"` matches `M`, `S/M` and `M/L`, but not `XL (oversized)`, because `m` isn't a whole part of it. `"8"` matches `US 8` but not `US 8.5`. Listings marked `One Size` match any size.
  - `max_price` (float or None): the highest price allowed, inclusive, or `None` for no limit.
- **Returns:** A `list[dict]` of at most 10 listings (`config.SEARCH_RESULT_LIMIT`), best match first. Each dict is the full listing exactly as it is in the data: `id` (str), `title` (str), `description` (str), `category` (str), `style_tags` (list[str]), `size` (str), `condition` (str), `price` (float), `colors` (list[str]), `brand` (str or None), `platform` (str). Listings that share zero words with the description are left out.
- **When it has nothing:** an empty list, `[]`. Never `None`, and never an exception. This is the value the loop branches on.

### `suggest_outfit`

- **What it does:** Asks the model for one or two outfits built around the new item. If the wardrobe has things in it, the outfits use pieces the user already owns, by name.
- **Inputs:**
  - `new_item` (dict): one listing dict, in the same shape `search_listings` returns.
  - `wardrobe` (dict): `{"items": [...]}`, where each item has `name`, `category`, `colors`, `style_tags` and `notes`. The list can be empty.
- **Returns:** A non-empty `str` of plain text: one or two outfit ideas, each naming the new item plus the wardrobe pieces it goes with.
- **When it has nothing:** If `wardrobe["items"]` is empty, it still returns a non-empty `str`, but with general styling advice for the item (what kinds of pieces and colors it goes with), since there's nothing to name. It never returns `""` and never raises for an empty wardrobe. If the model can't be reached at all, `generate()` raises `ModelUnavailable`, and the loop catches that.

### `create_fit_card`

- **What it does:** Asks the model for a short caption someone would actually post about the find, built from the item and the outfit idea.
- **Inputs:**
  - `outfit` (str): the text `suggest_outfit` returned.
  - `new_item` (dict): the same listing dict that went into `suggest_outfit`.
- **Returns:** A `str` of two to four sentences in a casual, social-post voice. It mentions the item, its price and its platform once each. It only mentions the brand if `brand` isn't `None`. It comes out with different words on different runs, because `TEMPERATURE` is 0.9.
- **When it has nothing:** If `outfit` is empty or only whitespace, it doesn't call the model and returns the fixed string `"Can't write a fit card without an outfit suggestion."` It never raises for an empty outfit.

---

## Planning Loop

<!-- Your branch rule, stated as a rule — the condition AND both paths — plus
     the file and function that holds it.

     Like this:
       "If search_listings returns an empty list, put a message in the session
        and stop. Otherwise take the first result and go to suggest_outfit."
        — agent.py::run_agent

     The grader checks your code against what you claim here, so the file and
     function have to be real. -->

**Branch rule:** If `search_listings` returns an empty list, put a message in `session["error"]` that says which filters were used and what to loosen (raise the price, drop the size, or use fewer or different words), then stop and return the session without calling `suggest_outfit` or `create_fit_card`. Otherwise take the first result as `session["selected_item"]` and go on to `suggest_outfit`.

**Where it lives:** `agent.py::run_agent`

**How the query is parsed:** <!-- regex, string splitting, or asking the model — say which --> Regex, without the model. A price comes from `under $30` / `under 30` / `$30`. A size comes from `size M` / `size 8` / `in size M`. Whatever is left over, minus filler words like "looking for", "a" and "under", becomes the description.

**What moves through the session:** <!-- which fields, in what order --> `query` → `parsed` (`description`, `size`, `max_price`) → `search_results` → `selected_item` → `outfit_suggestion` → `fit_card`. Each tool reads its inputs out of the session, not from the previous call's return value directly. On the empty path it's `query` → `parsed` → `search_results` (`[]`) → `error`, and `selected_item`, `outfit_suggestion` and `fit_card` stay `None`.

---

## Sample Run

<!-- Two things go here.

     1. One FULL query and its output, pasted as text.
     2. Your three per-tool terminal tests — the command and what it printed. -->

**One full query**

```
$ python app.py ask 'vintage graphic tee under $30, size M'

  Found:    Y2K Baby Tee — Butterfly Print — $18.0 on depop

  Outfit:   Outfit 1: Pair the Y2K Baby Tee with the baggy straight-leg jeans for a classic, balanced Y2K silhouette. Add the chunky white sneakers for a casual, everyday footwear choice, and accessorize with the black crossbody bag to complete the look. 

Outfit 2: Tuck the Y2K Baby Tee into the wide-leg khaki trousers for a subtle mix of Y2K and cottagecore aesthetics. Layer the vintage black denim jacket over top for added warmth and edge, and finish the outfit with the black combat boots and the brown leather belt.

  Fit card: Score this butterfly baby tee for just $18 on depop and I'm honestly obsessed with how cute it is. I've been living in these baggy jeans and chunky sneakers for that ultimate effortless Y2K vibe. It's giving major early 2000s nostalgia without trying too hard.
```

And the same loop with a query nothing can match (`python agent.py`, which runs `agent.py::run_agent`):

```
=== A query it can't ===
  stopped: No listings matched "designer ballgown", size XXS, under $5. Try one change at a time: drop the size XXS filter; or raise the $5 limit (listings start at $12); or use fewer or more common words, like a category (tee, jeans, jacket, dress, sneakers) or a style (vintage, y2k, 90s).
  fit_card is None — it should still be None here
```

To check the state handoff, I wrapped `suggest_outfit` so it recorded the `id` of the item it was actually given, then compared that to the session:

```
selected_item: lst_002 | reached suggest_outfit: lst_002 | same: True
```

On the empty path, the session ends with `search_results: []`, and `selected_item`, `outfit_suggestion` and `fit_card` all stay `None`.

**The three tools, tested one at a time**

```
$ python -c "from tools import search_listings; print([(x['id'], x['title'], x['price'], x['size']) for x in search_listings('graphic tee', max_price=30)])"
[('lst_002', 'Y2K Baby Tee — Butterfly Print', 18.0, 'S/M'), ('lst_006', 'Graphic Tee — 2003 Tour Bootleg Style', 24.0, 'L'), ('lst_017', 'Mesh Long-Sleeve Top — Black', 15.0, 'S/M'), ('lst_033', 'Vintage Band Tee — Faded Grey', 19.0, 'L'), ('lst_011', 'Low-Rise Cargo Pants — Khaki', 27.0, 'W29'), ('lst_015', 'Vintage Graphic Hoodie — Faded Black', 26.0, 'L')]

$ python -c "from tools import search_listings; print(search_listings('designer ballgown', size='XXS', max_price=5))"
[]
```

Everything's under $30, and the empty case is `[]`. One thing I noticed: cargo pants show up for "graphic tee". That's because the search counts shared words, and the listing's text shares a word with the query. It's a plain keyword match, so it doesn't know the user wanted a top.

```
$ python -c "from tools import suggest_outfit; from utils.data_loader import get_example_wardrobe, load_listings; print(suggest_outfit(load_listings()[0], get_example_wardrobe()))"
Outfit 1: Pair the Vintage Levi's 501 Jeans with the White ribbed tank top, the Black cropped zip hoodie worn unzipped on top, and finish the look with the Chunky white sneakers and the Black crossbody bag for an easy, casual streetwear vibe. 

Outfit 2: Combine the Vintage Levi's 501 Jeans with the Oversized grey crewneck sweatshirt, add the Brown leather belt at the waist, and step into the Black combat boots. Layer the Vintage black denim jacket over the top for a cool, double-denim monochrome look.

$ python -c "from tools import suggest_outfit; from utils.data_loader import get_empty_wardrobe, load_listings; print(suggest_outfit(load_listings()[0], get_empty_wardrobe()))"
These vintage Levi's 501s are a versatile wardrobe staple that easily bridges casual and smart-casual looks. For an effortless weekend outfit, pair them with a boxy white crewneck t-shirt, a classic black leather belt, and retro canvas sneakers in white or black. Layer a distressed oversized cardigan in oatmeal or forest green over top for texture and warmth. [...]
```

With a wardrobe, it names real pieces from it (white ribbed tank top, chunky white sneakers). With an empty wardrobe, it falls back to general advice, not an error.

```
$ AI201_CACHE=0 python -c "from tools import create_fit_card; from utils.data_loader import load_listings; print(create_fit_card('jeans and white sneakers', load_listings()[0]))"   # run 3 times
Scored these vintage Levi's on Depop for just $38 and I'm literally never taking them off. Paired them with my go-to white sneakers for that effortless 90s off-duty look. Such a classic staple find that goes with literally everything.
---
Found these vintage Levi's on depop for just $38 and they instantly became my daily go-to. Paired them with crisp white sneakers for that effortlessly chill, classic 90s streetwear look. Honestly, nothing beats a broken-in pair of denim that actually fits right.
---
Scored these vintage Levi's on depop for just $38 and they honestly fit like a dream. Paired them with crisp white sneakers for that effortless, casual 90s look that never misses. Can't beat finding the perfect wash without spending a fortune.

$ python -c "from tools import create_fit_card; from utils.data_loader import load_listings; print(repr(create_fit_card('   ', load_listings()[0])))"
"Can't write a fit card without an outfit suggestion."
```

I ran the fit card three times with the cache off. The three captions are worded differently, and each one has the price and platform. Two of them open with "Scored these", which is something to watch in Unit 4.

---

## How I Used AI

<!-- Two specific moments. What you asked, what came back, what you changed.

     "I used Claude to help me code" is not enough.

     "I gave Claude my search_listings spec. It returned None on no match
     instead of an empty list, so I changed it" is the level we want. -->

**Moment 1**

- *What I asked for:* How `search_listings` should match sizes, after reading that the size field mixes `M`, `S/M`, `M/L`, `XL (oversized)`, `W30 L30`, `US 8.5` and `One Size`.
- *What came back:* Claude suggested splitting the listing's size on anything that isn't a letter, digit or dot, and matching only whole parts, so `"s" in "us 9"` and `"l" in "xl"` (the two traps the starter warns about) can't happen. It asked me whether `S/M` and `M/L` should count as a match for M.
- *What I changed:* I decided they should, since someone asking for M would want to see an S/M tee, and I made `One Size` match any size. Before it went into the spec, we ran the rule against all 22 sizes in the data: M → `M, M/L, S/M`, L → `L, L/XL, M/L`, 8 → `US 8` only.

**Moment 2**

- *What I asked for:* I had Claude write the three tools and the loop in `tools.py` and `agent.py` from the Tool Inventory and branch rule in this README.
- *What came back:* Working code. Running the tools one at a time showed two things I wouldn't have guessed. Cargo pants come back for "graphic tee", because a plain keyword search only counts shared words. And two of the three fit cards for the same jeans opened with "Scored these".
- *What I changed:* I didn't just trust that the loop passed the right item along, so I wrapped `suggest_outfit` to record the `id` it actually received and checked it against `session["selected_item"]` (both `lst_002`). I left the cargo-pants and "Scored these" results as they are and wrote them down, because those are the kinds of things my criteria should catch in Unit 4.

**Unit 4 — Moment 3**

- *What I asked for:* For Claude to run my five criteria five times each and score every try.
- *What came back:* `run_eval.py` leaves PASS/FAIL blank, so Claude wrote `score_runs.py` to check each try against `criteria.md` as worded. It said every criterion was 5/5. Then it read all 25 fit cards and pointed out that two cards for the $18 tee said "eighteen bucks". The script had passed criterion 4 only because I'd tagged the $45 Champion jacket scenario for it.
- *What I changed:* I had to decide whether that counted. I chose MISSED (3/5), because my criterion says *any* query that matches, not only the scenario I happened to tag, and the brief warns against the generous reading. I had the script check criterion 4 on the tee's tries too, so the after run would be scored the same way. That miss became my diagnosis and my one improvement.

**Unit 4 — Moment 4**

- *What I asked for:* The MCP move, the three failure modes, and a trace, built by Claude.
- *What came back:* `search_listings` on MCP, returning exactly what the direct call did (`same as direct: True`), plus a `ModelUnavailable` handler and `trace.step()` calls in `run_agent`. The first two bad-key tests didn't actually test anything. One query matched nothing, so it never reached the model. The other picked an item whose prompts were already cached.
- *What I changed:* We re-ran the bad-key test with `AI201_CACHE=0` and a query that matches, so the model really was called and the handler really fired. I also had the trace show the actual call and values, not `dict with keys: …`, because the first version hid exactly the thing a trace is for.

<!-- ═══════════════════════ UNIT 4 — THE TEST ═══════════════════════

     Don't fill these in during unit 3.
     ═══════════════════════════════════════════════════════════════════ -->

---

## Run Log — Before

<!-- Five criteria, five tries each, in this exact format.

     Five, because your criteria are written out of five. Mark each try PASS
     or FAIL, count the passes, and read that count against your target — a
     row targeting 4 of 5 with three PASS cells is MISSED (3/5).

     `python run_eval.py --label before` runs everything and writes the table
     into results/. Paste it here and fill in the verdicts. -->

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1. Matching query completes all three tools | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 2. Impossible query stops before `suggest_outfit` | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 3. `selected_item` id = id `suggest_outfit` received | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 4. Fit card states the price, no stray brand (tee query) | 4 of 5 | FAIL | PASS | PASS | FAIL | PASS | MISSED (3/5) |
| 5. Every result at or under the price limit | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |

Full log: `results/run_2026-10-30_0007_before.md`, written by `run_eval.py::main` (five tries per scenario, cache off, temperature 0.9). The queries are in `scenarios.py`. `run_eval.py` leaves PASS/FAIL blank, so I wrote `score_runs.py`, which runs `run_eval.py` unchanged and checks each try against `criteria.md` as worded. It also wraps `suggest_outfit` to record the `id` it actually received, which criterion 3 needs. The wrapper only records the argument and then calls the real function, so it doesn't change how the agent behaves.

**About criterion 4's row.** The scenario I tagged for criterion 4 was `90s track jacket in size M` ($45, Champion), and that came out 5/5. But the criterion says *any* query that matches, and when I read every fit card from the run, the tee query from criterion 1 (`vintage graphic tee under $30`, the $18 Y2K Baby Tee) wrote the price as words twice. So the row above is the tee's five tries. Across all the matching-query scenarios, it held 5/5 on the jacket, the flannel and the denim jacket, and 3/5 on the tee.

**Real output from one try per criterion:**

Criterion 1, `run_eval.py::main`, scenario "matching query completes", try 2:
```
- stopped early: no
- selected_item: Y2K Baby Tee — Butterfly Print ($18.0, depop)
- search_results: 6

Fit card:
Score this little butterfly baby tee for just $18 on Depop and I'm obsessed with how versatile it is. I've been living in it paired with baggy jeans and chunky sneakers for that ultimate early 2000s look, but it's also so cute dressed down with khaki trousers and combat boots. It's giving major nostalgic vibes and I already know I'm going to wear it with everything.
```

Criterion 2, `run_eval.py::main`, scenario "impossible query stops early", try 1 (`score_runs.py`: `suggest_outfit calls: 0`):
```
- stopped early: yes — No listings matched "designer ballgown", size XXS, under $5. Try one change at a time: drop the size XXS filter; or raise the $5 limit (listings start at $12); or use fewer or more common words, like a category (tee, jeans, jacket, dress, sneakers) or a style (vintage, y2k, 90s).
- selected_item: (none)
- search_results: 0
```

Criterion 3, `score_runs.py` over `agent.py::run_agent`, scenario "selected item reaches suggest_outfit", all five tries:
```
try 1: selected_item lst_003 / suggest_outfit got ['lst_003']
try 2: selected_item lst_003 / suggest_outfit got ['lst_003']
try 3: selected_item lst_003 / suggest_outfit got ['lst_003']
try 4: selected_item lst_003 / suggest_outfit got ['lst_003']
try 5: selected_item lst_003 / suggest_outfit got ['lst_003']
```

Criterion 4, `tools.py::create_fit_card`, tee query, try 1 (FAIL: the price is written as "eighteen bucks", not "$18") and try 4 (FAIL, same):
```
scored this butterfly baby tee on depop for just eighteen bucks and honestly it's giving the ultimate y2k streetwear energy. been living in it layered under my baggy denim and zip hoodie for that effortless everyday look.
```
```
Score this butterfly baby tee on depop for just eighteen bucks and I'm honestly obsessed with how cute it is. I'm leaning into total 2000s mall-goth energy today by pairing it with baggy dark-wash jeans, a cropped zip hoodie, and chunky white sneakers. [...]
```

Criterion 5, `score_runs.py` over `agent.py::run_agent`, scenario "results stay under the price limit", all five tries:
```
try 1: limit $50, 7 results, max $45, over: none
try 2: limit $50, 7 results, max $45, over: none
try 3: limit $50, 7 results, max $45, over: none
try 4: limit $50, 7 results, max $45, over: none
try 5: limit $50, 7 results, max $45, over: none
```

The five tries really are five different answers, not the cache: every fit card in the log is worded differently.

---

## Verdicts and Diagnoses

<!-- MET or MISSED per criterion against LAST UNIT's target, plus a sentence on
     how you decided.

     Then, for every miss: which of the four places it happened — a tool, the
     loop's branch, the session, or the model's output — AND the mechanism.

     Not a diagnosis:  "The fit card was bad."
     A diagnosis:      "The fit card criterion missed on 2 of 5 items. Both had
                        an empty brand field. My prompt puts the brand in the
                        first sentence, so the card opened with a blank and read
                        like a fragment. The tool worked; the prompt assumed a
                        field that isn't always there."

     Look for a pattern. Three misses on the same tool is one problem, not
     three. -->

| # | Criterion | Target | Verdict | How I decided |
|---|---|---|---|---|
| 1 | Matching query completes all three tools | 4 of 5 | MET (5/5) | All five tries ended with a fit card and no error. Not close. |
| 2 | Impossible query stops before `suggest_outfit` | 5 of 5 | MET (5/5) | All five stopped after the search, `suggest_outfit` was called 0 times, `fit_card` stayed `None`, and every message said what to drop or raise. |
| 3 | Same `id` reaches `suggest_outfit` | 5 of 5 | MET (5/5) | The recorded argument was `lst_003` all five times, the same as `session["selected_item"]`. |
| 4 | Fit card states the price, no stray brand | 4 of 5 | **MISSED (3/5)** | On the tee query, two cards said "eighteen bucks" and not "$18". My criterion gives "$18" as the example of stating the price, so I counted words as a fail. No card named a wrong brand. This was the closest call: the jacket scenario I'd tagged for criterion 4 passed 5/5, and I could have scored only that. But the criterion covers any matching query, and on this one it held 3 of 5, which is under 4. |
| 5 | Every result at or under the price limit | 5 of 5 | MET (5/5) | All five tries returned 7 results, the most expensive $45 against a $50 limit. |

**Diagnoses**

**Criterion 4 — the model's output, in `tools.py::create_fit_card`.** The tool worked: it was called with the right item, and the card came back. What went wrong is in the prompt. It says *"casual, first person, like a real person posting their outfit"* and *"Mention the price ($18)"*, but nothing says the price has to be written as a dollar figure. Both misses were on the cheapest item in the run, the $18 tee. The jacket ($45), the flannel ($22) and the denim jacket ($42) came out as digits in all 20 of their cards. So it's one problem, not two: a casual voice plus a small, round number makes the model say it the way a person would out loud ("eighteen bucks"). Try 1 also lost its capital letters ("scored this butterfly baby tee…"), which is the same casual voice going a step further. The fix belongs in the prompt, not the loop or the session.

**The four I met, honestly.** Criteria 2, 3 and 5 don't involve the model at all. The branch is an `if not results` check, the state is a dictionary read back out, and the price limit is a `>` comparison inside `search_listings`. So 5 of 5 was close to guaranteed, and they mostly prove the plumbing works. Criterion 1 is the one I set too easy, because of the query I picked to test it, not because of the target. `vintage graphic tee under $30` uses the same words as the listings. In `notes_for_unit4.md`, I found real listings that my agent can't find when you word the query like a person: `Levis jeans size 30` gets nothing, even though Levi's 501s in `W30 L30` are in the data, and `size medium hoodie` gets nothing because "medium" isn't read as `M`. If I ran criterion 1 on queries like those, I'd expect it to miss. That's the criterion I'd tighten: same 4 of 5, but tested on five different phrasings of items that are in the data, not one phrasing that copies the listing's words.



---

## Loop Trace

<!-- One full run, printed step by step, with the MCP call visible in it.

     `python app.py ask '...' --trace` once you've added the trace.step()
     calls in Milestone 2.

     Worth pasting BOTH the happy path and the empty-search path. The empty
     one should be visibly shorter, because it stops. If your two traces are
     the same length, your branch isn't working — and this is the fastest way
     anyone will ever find that out. -->

**Happy path**

```
$ python app.py ask 'flannel shirt under $25' --trace
[1] parse_query
      in:  'flannel shirt under $25'
      out: {'description': 'flannel shirt', 'size': None, 'max_price': 25.0}
[2] search_listings (via MCP)
      in:  call_tool('search_listings', {'description': 'flannel shirt', 'size': None, 'max_price': 25.0})
      out: 2 items: Oversized Flannel Shirt — Plaid Red/Black, Vintage Polo Shirt — Forest Green
      →    branch: 2 found, selected_item = first (lst_003)
[3] suggest_outfit
      in:  new_item=lst_003 (session['selected_item']), wardrobe=10 items
      out: Outfit one: Layer the Oversized Flannel Shirt — Plaid Red/Black over the White ribbed tank top, paired with th…
[4] create_fit_card
      in:  outfit=session['outfit_suggestion'], new_item=lst_003
      out: Score this vintage Woolrich flannel on thredUp for just $22 and I am never taking it off. I've been living in …
```

**Empty search**

```
$ python app.py ask 'designer ballgown size XXS under $5' --trace
[1] parse_query
      in:  'designer ballgown size XXS under $5'
      out: {'description': 'designer ballgown', 'size': 'XXS', 'max_price': 5.0}
[2] search_listings (via MCP)
      in:  call_tool('search_listings', {'description': 'designer ballgown', 'size': 'XXS', 'max_price': 5.0})
      out: [] (empty)
      →    branch: empty search, stopping before suggest_outfit

  No listings matched "designer ballgown", size XXS, under $5. Try one change at a time: drop the size XXS filter; or raise the $5 limit (listings start at $12); or use fewer or more common words, like a category (tee, jeans, jacket, dress, sneakers) or a style (vintage, y2k, 90s).
```

The empty one stops after step 2, two steps shorter than the happy path, which is the branch doing its job. The trace calls are in `agent.py::run_agent`, one per step, and the MCP call is labelled `search_listings (via MCP)`.

**The three failure modes, triggered on purpose**

| Failure | How I triggered it | What the agent said | Handler |
|---|---|---|---|
| Empty search | `designer ballgown size XXS under $5` | The "No listings matched…" message above: it names the filters it used and what to loosen. | Already there from Unit 3: the branch in `run_agent` |
| Empty wardrobe | `python app.py ask 'denim jacket under $50' --empty-wardrobe` | Found the Denim Jacket ($42, poshmark), then general advice: *"Pair this light wash cropped Wrangler jacket with a fitted black ribbed turtleneck, high-waisted wide-leg trousers in beige or olive green, and chunky white sneakers…"*, and a fit card. No crash, no empty string. | Already there: `tools.py::suggest_outfit` switches prompts when `wardrobe["items"]` is empty |
| Model unavailable | Changed one character of `GEMINI_API_KEY` in `.env`, ran with `AI201_CACHE=0` so it couldn't answer from the cache, then put the key back | See below | **New this unit** |

Before I added a handler, a bad key only got caught by `app.py`'s catch-all, which printed `ModelUnavailable: The model rejected your API key…`. No stack trace, but the agent lost its session and the message didn't say which step broke or that the search had worked. So I added `except ModelUnavailable` (and `except MCPError` for the search) inside `run_agent`, which puts a message in `session["error"]` and stops:

```
[2] search_listings (via MCP)
      ...
      →    branch: 10 found, selected_item = first (lst_003)
[3] suggest_outfit
      →    ModelUnavailable, stopping: The model rejected your API key. Check GEMINI_API_KEY in your .env file, or create a fresh key at aistudio.google.com.

  The search worked and found Oversized Flannel Shirt — Plaid Red/Black ($22 on thredUp), but the AI model couldn't be reached for suggest_outfit, so there's no outfit or fit card. The model said: The model rejected your API key. Check GEMINI_API_KEY in your .env file, or create a fresh key at aistudio.google.com. Fix the key in .env (or check your internet), then ask again.
```

One thing I tripped over: my first bad-key run used a query that matched nothing, so it never reached the model, and the second one picked an item whose prompts were already cached. The model is only actually called with the cache off.

**On the MCP move:** <!-- what changed in your code, and whether anything
behaved differently afterwards. If the rewire didn't work, say exactly where it
broke — the error text and the last thing that worked. That earns the point in
full. -->

I moved `search_listings` onto MCP, because it's the one tool that doesn't call the model. In `mcp_server.py` it's registered under the same name with typed inputs (`description: str`, `size: str | None`, `max_price: float | None`), matching my Tool Inventory, plus a description written for someone who can't see my code, including the empty case. In `agent.py::run_agent`, the direct `search_listings(...)` call became `call_tool("search_listings", {...})` from `mcp_client.py`. `suggest_outfit` and `create_fit_card` are still called directly.

Nothing behaved differently afterwards. I compared the two directly: `call_tool('search_listings', {'description': 'graphic tee', 'size': None, 'max_price': 30})` returns the same 6 listing dicts as calling the function (`same as direct: True`), and the impossible query still comes back as `[]`, so the branch still works. The one difference you can feel is speed: every call now starts the server, asks, and shuts it down again.



---

## The Improvement

<!-- What you changed, why your diagnosis pointed at it, and the after-run in
     the same table format. One change, measured properly.

     `python run_eval.py --label after` -->

**What I changed:** One sentence of the prompt in `tools.py::create_fit_card`. Before, it said:

```
Mention the price ($18) and the platform (depop) once each.
```

Now it says:

```
Mention the price once, written exactly as $18 with the dollar sign and digits, never spelled out in words. Mention the platform (depop) once.
```

Nothing else changed: same scenarios, same scoring script, same temperature (0.9), cache off.

**Which failure it was meant to fix:** Criterion 4's miss. The casual-voice prompt let the model write the $18 tee's price as "eighteen bucks" in 2 of 5 cards, because it was told to mention the price but not how to write it.

### Run Log — After

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1. Matching query completes all three tools | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 2. Impossible query stops before `suggest_outfit` | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 3. `selected_item` id = id `suggest_outfit` received | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 4. Fit card states the price, no stray brand (tee query) | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 5. Every result at or under the price limit | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |

Full log: `results/run_2026-10-30_0016_after.md` (`run_eval.py::main`), scored with `score_runs.py`. Criterion 4's row is the tee again, same as before. The jacket scenario was 5/5 again too.

Criterion 4, tee query, try 1 and try 4 after the change (the two tries that failed before):
```
scored this butterfly baby tee on depop for $18 and I am so obsessed with the nostalgic Y2K vibe. Outfit one leans into that casual everyday look with baggy denim and chunky sneakers, while outfit two mixes in my black denim jacket and wide-leg trousers for a slightly tougher edge. [...]
```
```
Still obsessed with this butterfly baby tee I found on depop for only $18. I've been styling it with everything from baggy jeans for that ultimate early 2000s look to wide-leg trousers for a softer, vintage vibe. [...]
```

**Did it help, and how do I know:**

<!-- If it made things worse, say that. Honestly reported, that earns full
     credit and is more interesting than one that worked. -->

Yes, for the thing it was aimed at. Criterion 4 on the tee went from **3/5 (MISSED) to 5/5 (MET)**, and across all 25 fit cards in the after run, none writes the price in words. Before, 2 of the 5 tee cards did. The other four criteria stayed at 5/5, which is what I'd expect, since the change only touches the fit card prompt.

Two things I'd be careful about. It's five tries, and the miss was 2 in 5 before, so a clean 5/5 is good evidence but not proof it can never happen again. And the casual voice is mostly still there, but tee try 1 now says *"Outfit one leans into… while outfit two mixes in…"*, which copies the outfit suggestion's wording into the caption. It passes my criterion, but it reads less like something a person would post. The stricter prompt may have pushed the model toward following the input more literally. That one didn't happen before the change.



---

## Stretch — Retry With Looser Constraints

**Declared before building.** When `search_listings` comes back empty and the query had a size, `agent.py::run_agent` will retry the search once without the size filter. If the retry finds something, the run carries on with that item, and the session and final output say plainly that the size was dropped (e.g. "Nothing in size MEDIUM, so I searched without the size filter"). If the retry is empty too, or there was no size to drop, the loop stops with the same "No listings matched…" message as before. It never retries more than once and never loosens the price. Why: in `notes_for_unit4.md`, `size medium hoodie` came back with nothing, even though hoodies are in the data. I'll show it in the trace and in a run log with a scenario that triggers the retry.

## What's Still Broken

<!-- For each criterion still missed: what you'd do, and why you stopped where
     you did. "I ran out of time" is fine if it's true. Pretending nothing is
     left is not. -->

After the fix, none of my five criteria are missed. But that's partly because four of them test plumbing that was always going to work, and the problems I know about are ones my criteria don't reach:

**The search can't find things that are really there.** From `notes_for_unit4.md`: `Levis jeans size 30` returns nothing, even though Levi's 501s in `W30 L30` are in the data. `size medium hoodie` returns nothing, because "medium" never becomes `M`. `black boots` returns a flannel shirt, because a color word counts as much as the item. These sit in two places: `agent.py::parse_query` only takes sizes in the data's exact format, and `tools.py::search_listings` scores every shared word the same and compares whole words exactly. I'd fix the size first, mapping "small/medium/large" to S/M/L and a bare number to `W30` for jeans, because that one turns a real match into "no results". I stopped because the unit allows one improvement, and the measured miss was criterion 4. My criterion 1 test query copied the listing's own words, so it never caught these. Testing criterion 1 on five real phrasings would.

**The fit card prompt fix has a side effect.** One of the five tee cards after the change says "Outfit one… outfit two…", copying the outfit text into the caption. It passes criterion 4, but it reads like a summary, not a post. I'd add a line telling the model not to refer to the outfits by number, then run five tries again. I didn't, because that would be a second change in a unit that asks for one, and I'd lose the clean before/after.

**Criterion 4 only checks the brand against six names.** The check passes as long as none of Champion, Demonia, Levi's, Ralph Lauren, Woolrich or Wrangler appears where it shouldn't. A model that made up a brand that isn't in the data, like "Nike", would still pass. No card did that in 50, but my test couldn't have caught it.

**Model unavailable still costs a full search first.** With a bad key, the agent runs the search and only finds out at `suggest_outfit`. The message is clear about that, but checking the key before searching would save the user a step. I left it, because the handler does what this unit asks.



<!-- ═════════════════════════════════════════════════════════════════════

     SUBMISSION CHECKLIST — unit 3

       [ ] criteria.md has five numbered criteria, each with a target
       [ ] Each criterion has a reason underneath it
       [ ] All five unit 3 sections above have real content
       [ ] Tool Inventory: all three tools, inputs WITH TYPES, a specific
           return value, and the empty case
       [ ] Planning Loop names the branch rule and agent.py::run_agent
       [ ] Sample Run: one full query plus the three per-tool tests, as text
       [ ] At least four new commits
       [ ] Repository URL submitted — WRITE IT DOWN, you submit the same one
           next unit

     SUBMISSION CHECKLIST — unit 4

       [ ] mcp_server.py exists with one tool registered
           (or a written record of exactly where the rewire broke)
       [ ] Run Log — Before, five criteria, five tries each
       [ ] Real output pasted underneath, naming file and function
       [ ] A verdict on every criterion
       [ ] A diagnosis for every miss, naming a place AND a mechanism
       [ ] Loop Trace, with the MCP call visible in it
       [ ] All three failure modes triggered and handled
       [ ] One improvement, with Run Log — After in the same format
       [ ] What's Still Broken
       [ ] At least four new commits
       [ ] The SAME repository URL as last unit

     Do not delete and recreate this repository. Your commit history is what
     shows your criteria existed before your results did.
     ═════════════════════════════════════════════════════════════════════ -->

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**
