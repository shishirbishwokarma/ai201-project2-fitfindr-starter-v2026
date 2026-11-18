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

**Built.** In `agent.py::run_agent` the loop has a new step, `retry_without_size`. The search step goes there when the search is empty *and* the parsed query had a size. That step calls `search_listings` over MCP again with `size: None`, keeps the price limit, and records `session["dropped"] = "size …"`. It can only happen once, because nothing goes back to `search` after it. `app.py` prints a line saying what was dropped and what size the item actually is.

**Run log with the retry** — `results/run_2026-10-30_0028_retry.md` (`run_eval.py::main`, five tries, cache off, scored with `score_runs.py`). Same five scenarios as before, plus a retry scenario (`size medium hoodie`):

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1. Matching query completes all three tools | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 2. Impossible query stops before `suggest_outfit` | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 3. `selected_item` id = id `suggest_outfit` received | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 4. Fit card states the price, no stray brand (tee query) | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 5. Every result at or under the price limit | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| retry without the size filter *(diagnostic, not one of my five)* | — | retried | retried | retried | retried | retried | — |

The retry ran in all 5 hoodie tries (`retry dropped size MEDIUM` appears 5 times in the log), and it also ran in all 5 impossible-query tries (`retry dropped size XXS: still empty` appears 5 times). Criterion 2 still passes: the retry is a second search, not a call to `suggest_outfit`.

The retry in the run log, `size medium hoodie`, try 1:

```
[1] parse_query
      in:  'size medium hoodie'
      out: {'description': 'hoodie', 'size': 'MEDIUM', 'max_price': None}
[2] search_listings (via MCP)
      in:  call_tool('search_listings', {'description': 'hoodie', 'size': 'MEDIUM', 'max_price': None})
      out: [] (empty)
      →    branch: empty, but size MEDIUM was set, retrying once without it
[3] search_listings (via MCP, retry)
      in:  call_tool('search_listings', {'description': 'hoodie', 'size': None, 'max_price': None})
      out: 1 items: Vintage Graphic Hoodie — Faded Black
      →    retry dropped size MEDIUM: 1 found, selected_item = first (lst_015, size L)
[4] suggest_outfit
      in:  new_item=lst_015 (session['selected_item']), wardrobe=10 items
      out: Outfit 1: Pair the Vintage Graphic Hoodie with your baggy straight-leg jeans, black combat boots, and the blac…
[5] create_fit_card
      in:  outfit=session['outfit_suggestion'], new_item=lst_015
      out: Finally caved and grabbed this faded black graphic hoodie off depop for only $26 and I am so obsessed with how…
```

What the user sees (`python app.py ask 'size medium hoodie'`):

```
  Nothing matched in size MEDIUM, so I searched again without the size filter. This one is size L.
  Found:    Vintage Graphic Hoodie — Faded Black — $26.0 on depop
```

And when the retry is empty too (`designer ballgown size XXS under $5`), the message says so:

```
[3] search_listings (via MCP, retry)
      in:  call_tool('search_listings', {'description': 'designer ballgown', 'size': None, 'max_price': 5.0})
      out: [] (empty)
      →    retry dropped size XXS: still empty, stopping before suggest_outfit
```

**What it changed.** `size medium hoodie` used to be a dead end ("No listings matched…"). Now it finds the only hoodie in the data. But I should be honest about why the first search failed: "medium" isn't parsed as `M`. And the hoodie it finds is a size L, not an M, so the retry works around my parsing bug without fixing it. That's why the output says the size was dropped and what size the item is, so the user isn't misled into thinking it's their size.

## What's Still Broken

<!-- For each criterion still missed: what you'd do, and why you stopped where
     you did. "I ran out of time" is fine if it's true. Pretending nothing is
     left is not. -->

After the fix, none of my five criteria are missed. But that's partly because four of them test plumbing that was always going to work, and the problems I know about are ones my criteria don't reach:

**The search can't find things that are really there.** From `notes_for_unit4.md`: `Levis jeans size 30` returns nothing, even though Levi's 501s in `W30 L30` are in the data. `size medium hoodie` used to return nothing, because "medium" never becomes `M`. The retry stretch below now finds a hoodie by dropping the size, but it's a size L, so the real bug is still there. `black boots` returns a flannel shirt, because a color word counts as much as the item. These sit in two places: `agent.py::parse_query` only takes sizes in the data's exact format, and `tools.py::search_listings` scores every shared word the same and compares whole words exactly. I'd fix the size first, mapping "small/medium/large" to S/M/L and a bare number to `W30` for jeans, because that one turns a real match into "no results". I stopped because the unit allows one improvement, and the measured miss was criterion 4. My criterion 1 test query copied the listing's own words, so it never caught these. Testing criterion 1 on five real phrasings would.

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

---

## Capstone

**What This Extends**

FitFindr, my Unit 3/4 agent (`agent.py::run_agent`: parse the query, `search_listings` over MCP, then `suggest_outfit` and `create_fit_card` on the model). Until now it only ran as a one-shot command (`python app.py ask '...'`) and left no record behind once the terminal scrolled away. What's new is the operational layer: `serve.py` runs the same `run_agent()` behind HTTP, and every request it handles, good or bad, writes one structured record to `logs/requests.jsonl` saying what came in, what came out, how long it took, and what it cost in model calls and tokens.

**The Shape**

**A — Deploy and instrument**, on **Path B (local with logs)**. The extension is the run path (one documented command that starts the server), the structured log around every request, and the numbers I can get out of that log: latency, tokens per run, and how failures show up.

Out of scope, on purpose:
- **No change to the agent's behaviour.** I'm not touching `parse_query`, the search scoring, or the prompts, even though `notes_for_unit4.md` lists real search bugs (`medium` isn't read as `M`, `black boots` finds a flannel). Fixing those is Shape C, and it would mix "the system got better" into numbers that are meant to describe the system as it is.
- **No hosting (Path A).** FitFindr starts `mcp_server.py` as a second Python process on every search, and I'd rather spend the unit on testing than on a host signup.
- **No concurrency.** `serve.py` handles one request at a time behind a lock, because the MCP subprocess and `generate.py`'s rate limiter both assume one caller. I'm keeping that and measuring it, not replacing it with a queue.

**Stretch (declared before building): latency breakdown.** Each log record will also carry how long each stage took (`parse`, `search` over MCP, `suggest_outfit`, `create_fit_card`), so I can say where the time in one run actually goes, measured rather than guessed.

**Stretch (declared before building, added after the criteria were committed and while the before run was going): a second measured improvement and a load observation.**
- *Second improvement:* after the first improvement and its after run, a second change aimed at a different miss. Expected: criterion 4, which I already know fails, since a broken key comes back as HTTP 200. The change would make `serve.py` return 503 when the agent stopped on `model_unavailable`. Then a third run log, three trials, the same table.
- *Load observation:* my normal rate is one request at a time, each sent after the last one answers. At ten times that, 10 matching requests are sent at once. I'll report what changed against a one-at-a-time batch: end-to-end latency, time spent queued for the lock (`wait_ms`), errors, and tokens per run, all from the log.

**Running It**

Path B, local with logs. One command, from the repo root: `AI201_CACHE=0 PORT=5055 .venv/bin/python serve.py`, then `POST /ask` with `{"query": "..."}`. Everything else (Python version, the pinned `requirements-lock.txt`, the key, measured memory, and a note from cloning it into an empty folder and following my own instructions) is in [RUNNING.md](RUNNING.md), under *Capstone run path*. I didn't try a host: FitFindr starts `mcp_server.py` as a second Python process on every search, and I'd rather spend the time on the test half.

**Instrumentation**

`serve.py::ask` writes one JSON line per request to `logs/requests.jsonl` through `runlog.py::write`. Every way out of the route goes through one `finish()` helper, so 400s, empty searches, model failures and 500s are logged the same as successes. Each record holds:

- `ts`, `request_id` (also sent back as the `X-Request-Id` header), `route`, `status`
- `outcome`: `fit_card` / `no_results` / `model_unavailable` / `mcp_error` / `bad_request` / `crash` (the agent now records `session["error_kind"]`, so this isn't guessed from the error text)
- what came in: `query`, `parsed`, `wardrobe_items`
- what came out: `selected_id`, `selected_price`, `dropped` (the size the retry removed), `fit_card`, `error`
- how long: `duration_ms` (arrival to response), `wait_ms` (queued behind another request), `stages_ms` (parse / search / retry / outfit / fit_card, timed inside `agent.py::run_agent`)
- added by the improvement (commit `881c424`): `rate_limit_wait_ms` (time `generate.py` slept for the rate limiter) and `model_wait_ms` (time inside the model API call). The records pasted below were written before it, so they don't have these two fields; the after-run records under *The Improvement* do.
- what it cost: `model_calls`, `cache_hits`, `prompt_tokens`, `output_tokens`, `total_tokens` (before/after differences of `generate.py`'s counters, taken inside the lock so no other request can move them), `model`

`python log_summary.py` reads it back. The first real session, Nov 17, cache off: twelve real queries (the course examples plus the ones from `notes_for_unit4.md`), then deliberate failures: an impossible query, a whitespace-only query, a body that isn't JSON, and the server restarted with a broken `GEMINI_API_KEY`. All 16 records, exactly as written to `logs/requests.jsonl`:

```
{"ts": "2026-11-18T05:17:36.658+00:00", "request_id": "d9ab24f4", "route": "/ask", "status": 200, "outcome": "fit_card", "query": "vintage graphic tee under $30", "parsed": {"description": "vintage graphic tee", "size": null, "max_price": 30.0}, "wardrobe_items": 10, "selected_id": "lst_002", "selected_price": 18.0, "dropped": null, "fit_card": "Score this buttery-soft butterfly tee on depop for only $18 and I am never taking it off. I love styling it with baggy dark wash jeans and chunky sneakers for that ultimate Y2K street style. It also looks so cute tucked into khaki trousers with combat boots for when I want that sweet-yet-edgy contrast.", "error": null, "duration_ms": 3512.8, "wait_ms": 0.0, "stages_ms": {"parse": 0.5, "search": 460.0, "outfit": 1426.1, "fit_card": 1625.1}, "model_calls": 2, "cache_hits": 0, "prompt_tokens": 516, "output_tokens": 169, "total_tokens": 685, "model": "gemini-3.5-flash-lite"}
{"ts": "2026-11-18T05:17:40.192+00:00", "request_id": "52a06801", "route": "/ask", "status": 200, "outcome": "fit_card", "query": "90s track jacket in size M", "parsed": {"description": "90s track jacket", "size": "M", "max_price": null}, "wardrobe_items": 10, "selected_id": "lst_004", "selected_price": 45.0, "dropped": null, "fit_card": "Score this vintage Champion track jacket on Poshmark for only $45 and I'm honestly obsessed with how versatile it is. I've been living in it lately, whether I'm keeping it casual with baggy jeans and sneakers or mixing it up with wide-leg trousers and combat boots for that effortless high-low streetwear vibe.", "error": null, "duration_ms": 2385.8, "wait_ms": 0.0, "stages_ms": {"parse": 0.2, "search": 244.3, "outfit": 1289.1, "fit_card": 851.8}, "model_calls": 2, "cache_hits": 0, "prompt_tokens": 487, "output_tokens": 147, "total_tokens": 634, "model": "gemini-3.5-flash-lite"}
{"ts": "2026-11-18T05:17:42.603+00:00", "request_id": "727bd1e4", "route": "/ask", "status": 200, "outcome": "fit_card", "query": "silk slip dress in midi length under $40", "parsed": {"description": "silk slip dress midi length", "size": null, "max_price": 40.0}, "wardrobe_items": 10, "selected_id": "lst_013", "selected_price": 30.0, "dropped": null, "fit_card": "Found this gorgeous floral silk slip on depop for only $30 and I'm obsessed with the 90s cottagecore vibe. I wore it over a white ribbed tank with chunky sneakers for an easy daytime look, but I can't wait to layer it with combat boots and an oversized crewneck for chilly nights.", "error": null, "duration_ms": 1887.8, "wait_ms": 0.0, "stages_ms": {"parse": 0.0, "search": 247.7, "outfit": 785.0, "fit_card": 854.6}, "model_calls": 2, "cache_hits": 0, "prompt_tokens": 511, "output_tokens": 154, "total_tokens": 665, "model": "gemini-3.5-flash-lite"}
{"ts": "2026-11-18T05:17:44.508+00:00", "request_id": "1df65a3e", "route": "/ask", "status": 200, "outcome": "fit_card", "query": "platform sneakers size 8", "parsed": {"description": "platform sneakers", "size": "8", "max_price": null}, "wardrobe_items": 10, "selected_id": "lst_019", "selected_price": 48.0, "dropped": null, "fit_card": "Finally scored these chunky platform sneakers on Poshmark for $48 and I am so obsessed with how they pull my whole Y2K streetwear vibe together. I've been styling them with baggy dark wash denim and a ribbed tank for the ultimate effortless look, but they're just as good with wide-leg trousers. Honestly such a good thrift find for the rotation.", "error": null, "duration_ms": 2933.3, "wait_ms": 0.0, "stages_ms": {"parse": 0.0, "search": 242.9, "outfit": 1465.8, "fit_card": 1224.1}, "model_calls": 2, "cache_hits": 0, "prompt_tokens": 507, "output_tokens": 174, "total_tokens": 681, "model": "gemini-3.5-flash-lite"}
{"ts": "2026-11-18T05:17:47.460+00:00", "request_id": "b1441c1b", "route": "/ask", "status": 200, "outcome": "fit_card", "query": "denim jacket under $50", "parsed": {"description": "denim jacket", "size": null, "max_price": 50.0}, "wardrobe_items": 10, "selected_id": "lst_007", "selected_price": 42.0, "dropped": null, "fit_card": "Score! Snagged this vintage Wrangler cropped denim jacket on poshmark for only $42 and I'm already obsessed. I love throwing it over a white ribbed tank with baggy dark wash jeans and combat boots for the ultimate grunge double-denim look. It also pairs amazingly with wide-leg khaki trousers and chunky sneakers for an easy, balanced streetwear vibe.", "error": null, "duration_ms": 2176.5, "wait_ms": 0.0, "stages_ms": {"parse": 0.0, "search": 252.8, "outfit": 921.1, "fit_card": 1002.1}, "model_calls": 2, "cache_hits": 0, "prompt_tokens": 506, "output_tokens": 179, "total_tokens": 685, "model": "gemini-3.5-flash-lite"}
{"ts": "2026-11-18T05:17:49.656+00:00", "request_id": "5ce8bf4c", "route": "/ask", "status": 200, "outcome": "fit_card", "query": "flannel shirt under $25", "parsed": {"description": "flannel shirt", "size": null, "max_price": 25.0}, "wardrobe_items": 10, "selected_id": "lst_003", "selected_price": 22.0, "dropped": null, "fit_card": "Scored this vintage Woolrich flannel on thredUp for only $22, and it's basically the ultimate 90s grunge staple. I've been living in it layered over a simple white tank with baggy jeans, but it also looks so good thrown over a cropped hoodie for a more structured streetwear vibe.", "error": null, "duration_ms": 1549.6, "wait_ms": 0.0, "stages_ms": {"parse": 0.0, "search": 268.8, "outfit": 671.6, "fit_card": 608.6}, "model_calls": 2, "cache_hits": 0, "prompt_tokens": 528, "output_tokens": 172, "total_tokens": 700, "model": "gemini-3.5-flash-lite"}
{"ts": "2026-11-18T05:17:51.224+00:00", "request_id": "5608f224", "route": "/ask", "status": 200, "outcome": "fit_card", "query": "jacket $50", "parsed": {"description": "jacket", "size": null, "max_price": 50.0}, "wardrobe_items": 10, "selected_id": "lst_004", "selected_price": 45.0, "dropped": null, "fit_card": "Score! I found this vintage Champion track jacket on Poshmark for only $45 and I'm obsessed with the sporty 90s streetwear vibe. I've been styling it over a white ribbed tank with baggy dark wash jeans and chunky sneakers for the ultimate retro look. It's in amazing condition and seriously the easiest throw-on piece for running errands in style.", "error": null, "duration_ms": 2406.8, "wait_ms": 0.0, "stages_ms": {"parse": 0.0, "search": 243.9, "outfit": 629.9, "fit_card": 1532.3}, "model_calls": 2, "cache_hits": 0, "prompt_tokens": 516, "output_tokens": 185, "total_tokens": 701, "model": "gemini-3.5-flash-lite"}
{"ts": "2026-11-18T05:17:53.651+00:00", "request_id": "93bd80dc", "route": "/ask", "status": 200, "outcome": "fit_card", "query": "something cute for a date under $40", "parsed": {"description": "cute date", "size": null, "max_price": 40.0}, "wardrobe_items": 10, "selected_id": "lst_002", "selected_price": 18.0, "dropped": null, "fit_card": "Scored this butterfly baby tee on depop for only $18 and I am so obsessed with how it looks with baggy jeans and chunky sneakers for that ultimate nostalgic everyday fit. It also looks super cool dressed down with khaki trousers and combat boots for a nice mix of y2k and earthy tones.", "error": null, "duration_ms": 45711.1, "wait_ms": 0.0, "stages_ms": {"parse": 0.0, "search": 250.1, "outfit": 613.7, "fit_card": 44846.6}, "model_calls": 2, "cache_hits": 0, "prompt_tokens": 502, "output_tokens": 147, "total_tokens": 649, "model": "gemini-3.5-flash-lite"}
{"ts": "2026-11-18T05:18:39.392+00:00", "request_id": "b8cc5c2b", "route": "/ask", "status": 200, "outcome": "fit_card", "query": "black boots", "parsed": {"description": "black boots", "size": null, "max_price": null}, "wardrobe_items": 10, "selected_id": "lst_003", "selected_price": 22.0, "dropped": null, "fit_card": "Scored this vintage Woolrich flannel on thredUp for only $22 and I am so obsessed with the 90s grunge streetwear vibe. I love wearing it open over a basic tank with baggy denim and combat boots for that effortless, slouchy look. It's officially my new favorite layering piece for chilly days.", "error": null, "duration_ms": 6230.0, "wait_ms": 0.0, "stages_ms": {"parse": 0.0, "search": 381.4, "outfit": 1730.1, "fit_card": 4117.6}, "model_calls": 2, "cache_hits": 0, "prompt_tokens": 544, "output_tokens": 189, "total_tokens": 733, "model": "gemini-3.5-flash-lite"}
{"ts": "2026-11-18T05:18:45.645+00:00", "request_id": "061443df", "route": "/ask", "status": 200, "outcome": "fit_card", "query": "size medium hoodie", "parsed": {"description": "hoodie", "size": "MEDIUM", "max_price": null}, "wardrobe_items": 10, "selected_id": "lst_015", "selected_price": 26.0, "dropped": "size MEDIUM", "fit_card": "Score this faded black graphic hoodie on depop for only $26 and I am obsessed with the grunge energy. I’ve been living in it with baggy straight-leg jeans and combat boots for the ultimate effortless streetwear fit. Can't wait to style it with khaki trousers next for a high-low casual look.", "error": null, "duration_ms": 2172.4, "wait_ms": 0.0, "stages_ms": {"parse": 0.0, "search": 319.5, "retry_without_size": 262.5, "outfit": 811.6, "fit_card": 778.2}, "model_calls": 2, "cache_hits": 0, "prompt_tokens": 475, "output_tokens": 142, "total_tokens": 617, "model": "gemini-3.5-flash-lite"}
{"ts": "2026-11-18T05:18:47.836+00:00", "request_id": "4ee888fe", "route": "/ask", "status": 200, "outcome": "fit_card", "query": "cheap sneakers", "parsed": {"description": "cheap sneakers", "size": null, "max_price": null}, "wardrobe_items": 10, "selected_id": "lst_019", "selected_price": 48.0, "dropped": null, "fit_card": "Score these platform sneakers on Poshmark for just $48 and I am already obsessed. I love styling them with baggy dark wash jeans and a vintage black denim jacket for that ultimate Y2K streetwear vibe. They also look so effortless with wide-leg khaki trousers and a cropped zip hoodie for running errands around the city.", "error": null, "duration_ms": 4423.7, "wait_ms": 0.0, "stages_ms": {"parse": 0.0, "search": 252.7, "outfit": 3571.2, "fit_card": 599.2}, "model_calls": 2, "cache_hits": 0, "prompt_tokens": 481, "output_tokens": 138, "total_tokens": 619, "model": "gemini-3.5-flash-lite"}
{"ts": "2026-11-18T05:18:52.286+00:00", "request_id": "244f00d3", "route": "/ask", "status": 200, "outcome": "fit_card", "query": "denim jaket", "parsed": {"description": "denim jaket", "size": null, "max_price": null}, "wardrobe_items": 10, "selected_id": "lst_001", "selected_price": 38.0, "dropped": null, "fit_card": "Score these vintage Levi's on depop for just $38 and I am never taking them off. They have the absolute best wash for everyday wear, so I paired them with a ribbed tank, black denim jacket, and chunky sneakers for the ultimate casual vibe. For a little edge, I also love dressing them down with an oversized grey crewneck and combat boots.", "error": null, "duration_ms": 1900.4, "wait_ms": 0.0, "stages_ms": {"parse": 0.2, "search": 300.1, "outfit": 667.4, "fit_card": 930.8}, "model_calls": 2, "cache_hits": 0, "prompt_tokens": 535, "output_tokens": 188, "total_tokens": 723, "model": "gemini-3.5-flash-lite"}
{"ts": "2026-11-18T05:18:54.206+00:00", "request_id": "4c6ffe8d", "route": "/ask", "status": 200, "outcome": "no_results", "query": "designer ballgown size XXS under $5", "parsed": {"description": "designer ballgown", "size": "XXS", "max_price": 5.0}, "wardrobe_items": 10, "selected_id": null, "selected_price": null, "dropped": "size XXS", "fit_card": null, "error": "No listings matched \"designer ballgown\", size XXS, under $5. Try one change at a time: drop the size XXS filter; or raise the $5 limit (listings start at $12); or use fewer or more common words, like a category (tee, jeans, jacket, dress, sneakers) or a style (vintage, y2k, 90s). (I also tried again without the size XXS filter and still found nothing.)", "duration_ms": 463.5, "wait_ms": 0.0, "stages_ms": {"parse": 0.0, "search": 239.1, "retry_without_size": 223.9}, "model_calls": 0, "cache_hits": 0, "prompt_tokens": 0, "output_tokens": 0, "total_tokens": 0, "model": "gemini-3.5-flash-lite"}
{"ts": "2026-11-18T05:18:54.677+00:00", "request_id": "33aedd74", "route": "/ask", "status": 400, "outcome": "bad_request", "query": "   ", "parsed": null, "wardrobe_items": null, "selected_id": null, "selected_price": null, "dropped": null, "fit_card": null, "error": "missing or empty 'query'", "duration_ms": 0.1, "wait_ms": null, "stages_ms": null, "model_calls": null, "cache_hits": null, "prompt_tokens": null, "output_tokens": null, "total_tokens": null, "model": "gemini-3.5-flash-lite"}
{"ts": "2026-11-18T05:18:54.685+00:00", "request_id": "9f52a17d", "route": "/ask", "status": 400, "outcome": "bad_request", "query": null, "parsed": null, "wardrobe_items": null, "selected_id": null, "selected_price": null, "dropped": null, "fit_card": null, "error": "missing or empty 'query'", "duration_ms": 0.1, "wait_ms": null, "stages_ms": null, "model_calls": null, "cache_hits": null, "prompt_tokens": null, "output_tokens": null, "total_tokens": null, "model": "gemini-3.5-flash-lite"}
{"ts": "2026-11-18T05:18:59.740+00:00", "request_id": "577309ab", "route": "/ask", "status": 200, "outcome": "model_unavailable", "query": "vintage graphic tee under $30", "parsed": {"description": "vintage graphic tee", "size": null, "max_price": 30.0}, "wardrobe_items": 10, "selected_id": "lst_002", "selected_price": 18.0, "dropped": null, "fit_card": null, "error": "The search worked and found Y2K Baby Tee — Butterfly Print ($18 on depop), but the AI model couldn't be reached for suggest_outfit, so there's no outfit or fit card. The model said: The model rejected your API key. Check GEMINI_API_KEY in your .env file, or create a fresh key at aistudio.google.com. Fix the key in .env (or check your internet), then ask again.", "duration_ms": 716.8, "wait_ms": 0.0, "stages_ms": {"parse": 0.6, "search": 378.7, "outfit": 336.5}, "model_calls": 1, "cache_hits": 0, "prompt_tokens": 0, "output_tokens": 0, "total_tokens": 0, "model": "gemini-3.5-flash-lite"}
```

The failed runs are the last four: `no_results` (200, the branch stopped before any model call), two `bad_request` (400, logged with the query as sent, `"   "` and a non-JSON body), and `model_unavailable` (broken key). The broken-key run still searched and found the tee before failing at `outfit`, and it was logged with `model_calls: 1, total_tokens: 0`. No request crashed, so there's no `crash` record yet.

**What It Costs**

```
$ python log_summary.py
16 requests

outcome              status  count
fit_card                200     12
bad_request             400      2
no_results              200      1
model_unavailable       200      1

duration (ms)          n     mean   median      p90      max
bad_request            2        0        0        0        0
fit_card              12    6,441    2,396    6,230   45,711
model_unavailable      1      717      717      717      717
no_results             1      464      464      464      464

full runs (fit_card): 12, of which 12 with no cache hits
  per full run, cache off:  2.00 model calls, 509 prompt + 165 output = 674 tokens, 6.44 s
  where the time goes, over 12 runs:
    stage                mean ms  median  share
    parse                      0       0     0%
    search                   289     253     4%
    outfit                  1215     866    19%
    fit_card                4914     966    76%
    retry_without_size        22       0     0%
    (queued for lock)          0
```

**Per full run (cache off, averaged over 12 real runs from the log above): 2.00 model calls, 509 prompt + 165 output = 674 tokens, about 2.4 s median.** Token counts are what the Gemini API reported back on each response (`usage_metadata`, summed by `generate.py::_record_tokens`), differenced per request in `serve.py::ask`. They're measured, not estimated. I used 12 runs rather than 10 because the session had 12 matching queries. Every one had `cache_hits: 0`, so none were free.

In money: my key is on the free tier, so the **actual spend was $0**. At the paid-tier rate for `gemini-3.5-flash-lite` ($0.30 per 1M input tokens, $2.50 per 1M output, the rate quoted by several pricing aggregators; I couldn't open Google's own page), one run is 509 × $0.30/1M + 165 × $2.50/1M = $0.000153 + $0.000413 = **$0.00057**. The output side is 73% of the cost even though it's a quarter of the tokens. An empty search or a bad request costs $0, because they stop before the model.

**A hundred people a day**, one full run each: 100 × $0.00057 = **$0.057 a day**, about $1.70 a month. Money isn't the limit, time is. The free tier allows 15 requests a minute, which is 7.5 runs a minute. My log shows it: the 8th run in a row (`93bd80dc`) waited 43 s in `generate.py::_wait_for_slot` before its fit card call (`[rate limit] 15 requests used this minute. Waiting 43s` in the server output), so its `fit_card` stage took 44,847 ms. That one run pushes the mean to 6.4 s while the median is 2.4 s. A hundred people spread over a day never hit that. A hundred people in the same ten minutes would.

**Where the time goes (stretch: latency breakdown).** From `stages_ms` over the same 12 runs: `search` (MCP subprocess plus keyword scoring) has a median of 253 ms, almost all of it starting a second Python process. `outfit` has a median of 866 ms and `fit_card` 966 ms; those are the two model calls. Parsing is under 1 ms. So about 88% of a typical run (by medians: 866 + 966 out of 2,085 ms) is waiting on the model, and the one slow run was waiting on the rate limiter, not the model.

**Run Log and Verdicts**

Criteria: `criteria.md`, under *Capstone criteria*, committed in `4adfaf7` before any trial ran. Each run is one trial of `capstone_trials.py` (`run_trial` sends the requests, `score` checks them): a fresh `serve.py` with the cache off, 12 matching queries (the first 10 back to back are criterion 2's), 2 impossible queries, criterion 5's 5 malformed bodies, then a restart on a broken key and 5 more queries. That's 24 requests per run. Nothing changed between runs. Raw records are in `results/capstone/before/trialN.jsonl`, the HTTP responses in `trialN_responses.json`, the server's terminal output in `trialN_server.txt`, and the scored report in `results/capstone/before.md`.

*Run log — before*

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Every request leaves exactly one record | 20 of 20 | 20/20 | 20/20 | 20/20 | MET |
| 2. Ten in a row stay under 5 s | 9 of 10 under 5 s | 4/10 | 6/10 | 4/10 | MISSED |
| 3. A slow request explains itself in the log | all slow requests | 0/7 | 0/6 | 0/9 | MISSED |
| 4. Broken key returns 503 | 5 of 5 | 0/5 | 0/5 | 0/5 | MISSED |
| 5. Bad input: 4xx under 200 ms, never a 500 | 5 of 5 | 3/5 | 3/5 | 3/5 | MISSED |

Real output, all from run 1 (`results/capstone/before/trial1.jsonl`, written by `serve.py::ask` through `runlog.py::write`):

*Criterion 1.* 24 records for 24 requests in every run. The response headers (`trial1_responses.json`, recorded by `capstone_trials.py::post`) against the log's `request_id`s, for the five least ordinary requests:

```
impossible  'sequin tuxedo size XXXL under $3'  200  X-Request-Id: 657f9b30
malformed   'blank query'                       400  X-Request-Id: 6e432fb0
malformed   'wardrobe items not a list'         500  X-Request-Id: bd5653cb
malformed   '5,000-character query'             200  X-Request-Id: 3b4f0475
broken_key  'vintage graphic tee under $30'     200  X-Request-Id: 68e318e7
log request_ids, same requests: ['657f9b30', '6e432fb0', 'bd5653cb', '3b4f0475', '68e318e7']
```

*Criterion 2.* `duration_ms` of the ten back-to-back requests:

```
f0a7e786    8275.4  vintage graphic tee under $30
adff79cc    6734.9  90s track jacket in size M
e17e349c    7192.7  silk slip dress in midi length under $40
2fdfe5ea    2291.7  platform sneakers size 8
245207a7    1869.2  denim jacket under $50
c47aef0b    1792.0  flannel shirt under $25
dda63d5d    2103.6  jacket $50
91b22ac6   31683.4  something cute for a date under $40
2cf430e7    7495.9  black boots
a18fb989    6978.3  size medium hoodie
```

*Criterion 3.* The slowest record, whole. It says the 30.5 s went to `fit_card`, and the only field that names a wait, `wait_ms`, is 0:

```
{"ts": "2026-11-18T05:32:33.283+00:00", "request_id": "91b22ac6", "route": "/ask", "status": 200, "outcome": "fit_card", "query": "something cute for a date under $40", "parsed": {"description": "cute date", "size": null, "max_price": 40.0}, "wardrobe_items": 10, "selected_id": "lst_002", "selected_price": 18.0, "dropped": null, "fit_card": "Found this little butterfly tee on depop for $18 and I am so obsessed with the early 2000s pastel print. I love balancing out the super feminine top by styling it with baggy dark wash jeans and a chunky black denim jacket for that ultimate nostalgic streetwear vibe. It honestly fits like a dream and is going to be my go-to piece all season.", "error": null, "duration_ms": 31683.4, "wait_ms": 0.0, "stages_ms": {"parse": 0.0, "search": 244.9, "outfit": 887.1, "fit_card": 30550.8}, "model_calls": 2, "cache_hits": 0, "prompt_tokens": 523, "output_tokens": 184, "total_tokens": 707, "model": "gemini-3.5-flash-lite"}
```

The reason is only in the terminal (`trial1_server.txt`), not the record: `[rate limit] 15 requests used this minute. Waiting 29s. This is normal.`

*Criterion 4.* What the caller got back with the broken key (`trial1_responses.json`):

```
status 200, X-Request-Id 68e318e7
{"error": "The search worked and found Y2K Baby Tee — Butterfly Print ($18 on depop), but the AI model couldn't be reached for suggest_outfit, so there's no outfit or fit card. The model said: The model rejected your API key. Check GEMINI_API_KEY in your .env file, or create a fresh key at aistudio.google.com. Fix the key in .env (or check your internet), then ask again.", "error_kind": "model_unavailable", "fit_card": null}
```

*Criterion 5.* The five malformed bodies' records (fields trimmed to the ones the criterion scores; the long query is cut here, not in the file):

```
{"request_id": "6e432fb0", "status": 400, "outcome": "bad_request", "query": "   ", "duration_ms": 0.1, "error": "missing or empty 'query'"}
{"request_id": "44705f00", "status": 400, "outcome": "bad_request", "query": null, "duration_ms": 0.0, "error": "missing or empty 'query'"}
{"request_id": "852f8cdd", "status": 400, "outcome": "bad_request", "query": "{'query': 42}", "duration_ms": 0.0, "error": "missing or empty 'query'"}
{"request_id": "bd5653cb", "status": 500, "outcome": "crash", "query": "denim jacket", "duration_ms": 221.0, "total_tokens": 0, "error": "TypeError: string indices must be integers, not 'str'"}
{"request_id": "3b4f0475", "status": 200, "outcome": "fit_card", "query": "vintage tee vintage tee vintage tee vintage tee[... 5,000 characters]", "duration_ms": 2269.6, "stages_ms": {"parse": 0.4, "search": 223.3, "outfit": 1036.8, "fit_card": 1008.9}, "total_tokens": 699}
```

*Verdicts and diagnoses*

**1 — MET (20/20, 20/20, 20/20).** All 24 requests in every run left exactly one record whose `request_id` matched the header, including the three 500s and the fifteen broken-key requests. Was the target too low? It's 100%, so it can't be stricter, but it was easier than I expected. Because every way out of `serve.py::ask` goes through one `finish()`, this criterion was really testing that single function. To tighten it I'd make it harder to meet: kill the server mid-request (for example, gunicorn's worker timeout) and require that the request still leaves a record. Today it wouldn't, because the record is written when the response is built.

**2 — MISSED (4/10, 6/10, 4/10).** Two causes, in two different places. The trial-1 timestamps line up with the server output:
- *Stage: `generate.py::_wait_for_slot`, the rate limiter. Mechanism: it allows 15 model calls per rolling 60 seconds per process, and each run makes 2.* A healthy run takes about 2 s, so ten back-to-back runs ask for 20 calls in about 25 s. Call 16 is run 8's fit card, and it has to wait until call 1 is 60 s old: 29 s in run 1, 24 s in run 2, 20 s in run 3. After that, each new call waits for the next-oldest one to age out, so runs 9–11 each waited about 5 s more (`Waiting 5s` three times in `trial1_server.txt`, one before each of `black boots`, `size medium hoodie` and `cheap sneakers`). Once the first 15 calls are spent, the server can't do better than one run every 8 s, which is over my 5 s target by construction. My criterion assumed latency depends on how fast the model is. It actually depends on how many calls were made in the last minute.
- *Stage: the model call itself (`client.models.generate_content` in `generate.py::generate`). Mechanism: the API's own response time.* Runs 1–3 in trial 1 were slow (6.7–8.3 s) before any limiter wait could happen (calls 1–6), and each had one model stage of 5.4–7.1 s. There's no `service pushed back` line, so these weren't 429 retries; the API was just slow to answer. In my M3 session an hour earlier, the median model stage was under 1 s.

So 3 of trial 1's 6 slow requests were the limiter and 3 were the model. **I could only work that out by lining up timestamps against a terminal log, which is exactly criterion 3's miss.**

**3 — MISSED (0/7, 0/6, 0/9).** *Stage: the log record (`serve.py::ask` → `runlog.py`) and the counters it reads from `generate.py`. Mechanism: the only wait field in the record is `wait_ms`, which is time queued for `serve.py`'s lock, and that was 0 every time because requests were sequential.* The limiter's sleep happens inside `generate()`, so its 29 s lands inside `stages_ms.fit_card`, indistinguishable from a slow model answer. And no field separates time spent inside the API call from time spent around it. So the record can say *where* the time went (the `fit_card` stage), but not *why*. This is one problem with two symptoms: criterion 2 missed because of the limiter, and criterion 3 missed because the log can't see the limiter.

**4 — MISSED (0/5, 0/5, 0/5).** *Stage: `serve.py::ask`. Mechanism: it picks the status code only by whether `run_agent()` raised, and `run_agent()` never raises for a bad key.* `agent.py::run_agent` catches `ModelUnavailable` (my Unit 4 handler), writes the message into `session["error"]` and returns normally, so `serve.py` answers 200 for a success, an empty search and a dead model alike. The other half of the criterion held: all 15 bodies name the API key. The record even says `outcome: model_unavailable`. The server knew, and the status code just didn't say so.

**5 — MISSED (3/5, 3/5, 3/5).** The three query checks passed every time (400 in 0.0–0.3 ms). Two bodies failed every time, both because *`serve.py::ask` only checks that `query` is a non-empty string*:
- `{"items": "x"}` → **500 in 216–243 ms.** *Stage: `tools.py::suggest_outfit`. Mechanism:* `serve.py` checks that the wardrobe is a dict but not that `items` is a list of dicts. So the search runs (the ~220 ms is the MCP subprocess), then `suggest_outfit` takes `wardrobe.get("items")` = `"x"`, loops over its characters, and `w['name']` on a string raises `TypeError`. `run_agent` only catches `ModelUnavailable` and `MCPError`, so it reaches `serve.py` as a crash.
- 5,000-character query → **200 with a fit card, 2.3–7.9 s.** *Stage: `serve.py::ask`, which has no length limit, then `agent.py::parse_query`, which keeps all 1,000 words as the description.* The search still finds the tee and both model calls run. It cost 699 tokens, the same as a normal run, because the prompts are built from the listing, not the query. So the damage is time and a wasted search, not money, but it should have been turned away.

**The pattern.** Four misses, two root causes. Criteria 2 and 3 are the rate limiter in `generate.py` and a log that can't see it. Criteria 4 and 5 are `serve.py` treating "didn't raise" as "succeeded" and checking only the query's type. The one improvement follows the first pair, because I can't diagnose a slow request from the log alone, and that's the whole point of the extension.

**The Improvement**

**What I changed (commit `881c424`):** `generate.py` now keeps two running totals: seconds spent *asleep in the rate limiter* (its own pacing in `_wait_for_slot` plus any 429 backoff in `generate`) and seconds spent *inside the API call* (`client.models.generate_content`). `serve.py::ask` reads both before and after each request, inside the lock, and logs the difference as two new fields, `rate_limit_wait_ms` and `model_wait_ms`. Nothing about how the agent runs changed: same calls, same pacing, same prompts.

**Why this one:** it follows the diagnosis of criteria 2 and 3. A slow request's time disappeared into `stages_ms.fit_card`, so the record couldn't say whether the limiter or the model caused it, and I had to line up timestamps against terminal output to find out. Of my four misses, this is the one that undermines the extension itself, because a log that can't explain a slow request can't be used to diagnose one.

*Run log — after (same driver, same requests, three new trials; `results/capstone/after/`, report in `results/capstone/after.md`)*

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Every request leaves exactly one record | 20 of 20 | 20/20 | 20/20 | 20/20 | MET |
| 2. Ten in a row stay under 5 s | 9 of 10 under 5 s | 3/10 | 3/10 | 4/10 | MISSED |
| 3. A slow request explains itself in the log | all slow requests | 9/9 | 9/9 | 9/9 | **MET** |
| 4. Broken key returns 503 | 5 of 5 | 0/5 | 0/5 | 0/5 | MISSED |
| 5. Bad input: 4xx under 200 ms, never a 500 | 5 of 5 | 3/5 | 3/5 | 3/5 | MISSED |

Before and after, side by side:

| Criterion | Before (runs 1/2/3) | After (runs 1/2/3) |
|---|---|---|
| 1 | 20/20, 20/20, 20/20 MET | 20/20, 20/20, 20/20 MET |
| 2 | 4/10, 6/10, 4/10 MISSED | 3/10, 3/10, 4/10 MISSED |
| 3 | 0/7, 0/6, 0/9 MISSED | **9/9, 9/9, 9/9 MET** |
| 4 | 0/5, 0/5, 0/5 MISSED | 0/5, 0/5, 0/5 MISSED |
| 5 | 3/5, 3/5, 3/5 MISSED | 3/5, 3/5, 3/5 MISSED |

The first ten records of after-run 1 (`results/capstone/after/trial1.jsonl`), showing the two new fields: `request_id`, `duration_ms`, `rate_limit_wait_ms`, `model_wait_ms`, query:

```
d8e17152  11081.6     0.0  10396.1  vintage graphic tee under $30
c482ae75   4153.7     0.0   3826.0  90s track jacket in size M
4be29899   7038.8     0.0   6761.9  silk slip dress in midi length
9aa4ad92   1322.5     0.0   1078.8  platform sneakers size 8
24945a98   1785.0     0.0   1542.2  denim jacket under $50
8fe1b670   6382.9     0.0   6144.8  flannel shirt under $25
3a75c1c3   9409.4     0.0   9159.4  jacket $50
680e647d  25097.2     0.0  24804.8  something cute for a date unde
8f9046cc   6814.1  4179.4   2269.1  black boots
2574c8fc   6112.8     0.0   5581.4  size medium hoodie
```

And the slowest one whole. The 25 s that before would have been "slow `outfit` stage, cause unknown" now says it was the model (`model_wait_ms: 24804.8`), not the limiter (`rate_limit_wait_ms: 0.0`):

```
{"ts": "2026-11-18T05:48:54.786+00:00", "request_id": "680e647d", "route": "/ask", "status": 200, "outcome": "fit_card", "query": "something cute for a date under $40", "parsed": {"description": "cute date", "size": null, "max_price": 40.0}, "wardrobe_items": 10, "selected_id": "lst_002", "selected_price": 18.0, "dropped": null, "fit_card": "scored this butterfly baby tee on depop for only $18 and I am completely obsessed with the early-2000s streetwear vibe. I’m leaning into the nostalgia today by styling it with baggy dark wash jeans and chunky white sneakers, but it also looks so good dressed down with khaki trousers and combat boots.", "error": null, "duration_ms": 25097.2, "wait_ms": 0.0, "rate_limit_wait_ms": 0.0, "model_wait_ms": 24804.8, "stages_ms": {"parse": 0.1, "search": 289.3, "outfit": 19300.3, "fit_card": 5506.5}, "model_calls": 2, "cache_hits": 0, "prompt_tokens": 512, "output_tokens": 162, "total_tokens": 674, "model": "gemini-3.5-flash-lite"}
```

**Did it help? Yes, for the criterion it was aimed at.** Criterion 3 went from 0 of 22 slow requests explained to 27 of 27, and that comes straight from the new fields, which `capstone_trials.py::score` reads. The other four criteria didn't move, which is what I expected: the change makes slow requests visible but doesn't make anything faster.

**What it told me that I didn't know.** My before diagnosis put the rate limiter first, because the terminal showed it clearly (29 s, 24 s, 20 s at run 8). With the new fields I can count instead of inferring. In the after run, **23 of the 27 slow requests were model time and only 4 were the limiter** (1, 2 and 1 per run). The model was slower in this run, so fewer calls fit into each minute and the limiter had less to do. The 25 s request above, at run 8 again, is the model, not the limiter. So criterion 2's main cause is the API's response time, which varied from about 1 s to 24 s per run tonight, and the limiter only comes second when the model happens to be fast. I couldn't have told that apart without this change. Criterion 2 also got slightly worse (3, 3, 4 against 4, 6, 4). The change adds two subtractions per request, so that's the model's variance, not the fix.

**What it cost:** nothing measurable. Tokens per full run were 676, 680 and 681 across the after runs, against 674 before. Each record is two numbers longer.

**Stretch — Second Improvement**

**What I changed (commit `ffcacff`):** `serve.py::ask` stops treating "`run_agent()` didn't raise" as success. Three parts of one change:
- A run that ended `model_unavailable` or `mcp_error` returns **503**, with the same session body as before, error message included.
- A wardrobe whose `items` isn't a list of objects with a text `name`, a text `category` and a list of `colors` (exactly what `tools.py::suggest_outfit` reads) gets a **400** before the lock, the search or the model (`serve.py::_wardrobe_problem`).
- A query over 500 characters gets a **400** (`MAX_QUERY_CHARS`). The longest real query in my logs is 40.

**Why this one:** it follows the second pattern in the diagnosis. Criteria 4 and 5 missed for the same reason: `serve.py` chose 200 or 500 only by whether the agent raised, and it only checked that the query was a non-empty string. I declared this stretch expecting it to target criterion 4. Because 4 and 5 shared that one cause, the same change to `serve.py`'s contract covers both, and I'm reporting both.

*Run log — after the second improvement (same driver, same requests; `results/capstone/after2/`, report in `results/capstone/after2.md`)*

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Every request leaves exactly one record | 20 of 20 | 20/20 | 20/20 | 20/20 | MET |
| 2. Ten in a row stay under 5 s | 9 of 10 under 5 s | 0/10 | 0/10 | 1/10 | MISSED |
| 3. A slow request explains itself in the log | all slow requests | 12/12 | 12/12 | 11/11 | MET |
| 4. Broken key returns 503 | 5 of 5 | 5/5 | 5/5 | 5/5 | **MET** |
| 5. Bad input: 4xx under 200 ms, never a 500 | 5 of 5 | 5/5 | 5/5 | 5/5 | **MET** |

All three result sets side by side:

| Criterion | Before | After improvement 1 | After improvement 2 |
|---|---|---|---|
| 1 | 20, 20, 20 /20 MET | 20, 20, 20 /20 MET | 20, 20, 20 /20 MET |
| 2 | 4, 6, 4 /10 MISSED | 3, 3, 4 /10 MISSED | 0, 0, 1 /10 MISSED |
| 3 | 0/7, 0/6, 0/9 MISSED | 9/9, 9/9, 9/9 MET | 12/12, 12/12, 11/11 MET |
| 4 | 0, 0, 0 /5 MISSED | 0, 0, 0 /5 MISSED | **5, 5, 5 /5 MET** |
| 5 | 3, 3, 3 /5 MISSED | 3, 3, 3 /5 MISSED | **5, 5, 5 /5 MET** |

Real output, run 1 (`results/capstone/after2/trial1.jsonl` from `serve.py::ask`; response bodies from `trial1_responses.json`). Criterion 5's five records, then criterion 4's:

```
{"request_id": "6afa69c9", "status": 400, "outcome": "bad_request", "duration_ms": 0.1, "model_calls": null, "error": "missing or empty 'query'"}
{"request_id": "adfe24ee", "status": 400, "outcome": "bad_request", "duration_ms": 0.2, "model_calls": null, "error": "missing or empty 'query'"}
{"request_id": "56f7bf10", "status": 400, "outcome": "bad_request", "duration_ms": 0.0, "model_calls": null, "error": "missing or empty 'query'"}
{"request_id": "34bc921b", "status": 400, "outcome": "bad_request", "duration_ms": 0.0, "model_calls": null, "error": "'wardrobe.items' must be a list"}
{"request_id": "54ccf4d0", "status": 400, "outcome": "bad_request", "duration_ms": 0.0, "model_calls": null, "error": "query is 4999 characters, over 500"}
{"request_id": "431ca92b", "status": 503, "outcome": "model_unavailable", "duration_ms": 747.5, "model_calls": 1, "error": "The search worked and found Y2K Baby Tee — Butterfly Print ($18 on depop), but the AI model couldn't be reached for suggest_outfit, so t[...]
```

```
status 503, X-Request-Id 431ca92b
{"error": "The search worked and found Y2K Baby Tee — Butterfly Print ($18 on depop), but the AI model couldn't be reached for suggest_outfit, so there's no outfit or fit card. The model said: The model rejected your API key. Check GEMINI_API_KEY in your .env file, or create a fresh key at aistudio.google.com. Fix the key in .env (or check your internet), then ask again.", "error_kind": "model_unavailable", "fit_card": null}
```

(The query reads as 4,999 characters because `serve.py` strips whitespace before measuring, and the test string ends in a space.)

**Did it help? Yes, for both criteria it was aimed at.** Criterion 4 went from 0/15 to 15/15 across the three runs, and criterion 5 from 9/15 to 15/15. The bad wardrobe now costs 0.0 ms and no search, against 216–256 ms and a crash before. The long query costs nothing, against 2.1–7.9 s and about 700 tokens before. Criteria 1 and 3 held.

**What it cost, and the trade-off.** One behaviour change for callers: a `wardrobe` that isn't an object, like `"wardrobe": "abc"`, used to fall back silently to the example wardrobe, and is now a 400. I think that's right, since a silent substitute is worse than a clear "no", but a caller that relied on it would break. **Criterion 2 got worse, 0, 0, 1 of 10, but not because of this change.** The new fields show it directly: 34 of the 35 slow requests across the three runs had `model_wait_ms` at least half of `duration_ms`, and the median time per model call was 5.4, 4.6 and 3.5 s, against under 1 s in my first session. This change only touches what happens before and after `run_agent()`, so the model service itself was slower in this run.

**Stretch — Load Observation**

Normal use is one request at a time, each sent when the last one answers. At ten times that rate, all ten requests arrive at once. `load_test.py` runs the same 10 matching queries both ways against a fresh `serve.py` with the cache off, 60 s apart. Records are in `results/capstone/load/normal.jsonl` and `10x.jsonl`, the report in `results/capstone/load.md`:

| Measure | Normal (1 at a time) | 10x (10 at once) |
|---|---|---|
| requests sent / records logged | 10 / 10 | 10 / 10 |
| fit cards returned | 10 | 10 |
| non-200 responses | 0 | 0 |
| wall clock for all 10 | 78.6 s | 78.3 s |
| median duration_ms | 7,319 | 40,836 |
| max duration_ms | 20,059 | 78,300 |
| mean wait_ms (queued for the lock) | 0 | 35,142 |
| max wait_ms | 0 | 72,874 |
| mean rate_limit_wait_ms | 1,718 | 481 |
| mean model_wait_ms | 5,776 | 6,997 |
| tokens per full run | 680 | 673 |

The 10x requests, in the order the lock let them through:

```
request_id  duration   wait_ms  rate_lim    model  query
463cf471        8829         0         0     8095  jacket $50
70719054       15560      8828         0     6468  silk slip dress in midi length under $40
01a37866       21968     15559         0     6153  denim jacket under $50
0fe0fa29       31077     21967         0     8643  size medium hoodie
b7c4d983       37167     31077         0     5772  vintage graphic tee under $30
9d5173e2       44505     37166         0     7079  90s track jacket in size M
fdcb3b05       51913     44505         0     7052  black boots
56bf4279       67536     51913      4325    11038  flannel shirt under $25
f28844f8       72875     67536         0     4995  something cute for a date under $40
b4a3597d       78300     72874       490     4678  platform sneakers size 8
```

**What changed: latency, nothing else.** No errors, no lost records, the same tokens per run, and the same total throughput: all ten took 78 s either way. `serve.py`'s lock runs one agent at a time, so sending ten at once doesn't do the work faster. It moves each person's wait from *between* requests to *inside* theirs. The median request went from 7.3 s to 40.8 s, and the tenth person waited 73 s in the queue before their run even started. `wait_ms` went from 0 to a 35 s average, which is exactly what that field was added to show.

One thing went *down*: rate-limiter waiting (1.7 s to 0.5 s on average). With the lock already spacing runs out, fewer calls landed inside the same minute.

**What this means if it were hosted.** The Render config I wrote (`render.yaml`) gives gunicorn a 120 s timeout. At ten at once, the last request finished at 78 s, inside that. At about fifteen at once it wouldn't be: gunicorn would kill the worker, the caller would get a 502, and `serve.py` would never write that request's record, because the record is written when the response is built. That's the same gap I named under criterion 1.

**What's Still Broken**

**Criterion 2 is still missed (0, 0, 1 of 10 in the last run), and I'm not changing its target.** The improvements gave me a log that says why, and it says the model. In the final run, 34 of 35 slow requests were mostly `model_wait_ms`, with each model call taking a median of 3.5–5.4 s, against under 1 s in my first session. The rate limiter is the second cause, and it only shows up when the model is fast enough to make 15 calls inside a minute. 5 s still seems like the right limit for someone waiting on a shopping answer. What was wrong was my assumption that model time was steady.

What I'd do about it:
- **Make one model call per run instead of two.** `suggest_outfit` and `create_fit_card` each make a separate round trip, but the fit card is written from the outfit and the same item. One prompt that returns both would cut the model time per run roughly in half, and it would halve the rate-limiter pressure too (15 calls a minute becomes 15 *runs* a minute).
- **Put a timeout on the model call** (around 8 s) and return the search result with a "styling is taking a while" message, so a slow API can't hold a request for 25 s.

Why I stopped: both of those change how the agent works, and my scope for this unit (*The Shape*) was the operational layer around an agent I wasn't going to change. I also had one improvement plus one stretch improvement, and I spent them on the two misses that were my own server's fault (criteria 3, then 4 and 5). The model's speed wasn't something I could change in serve.py.

**Criterion 1 is met but weaker than it looks.** Every response goes through `finish()`, so the record is written when the response is built. If the process is killed mid-request (a gunicorn timeout on a host, or Ctrl-C), that request leaves no record. I'd write a "started" record when the request arrives and an "ended" record when it finishes, so a request with only a start record is a request that died. I'd tighten the criterion to require that too. I stopped because nothing in my trials killed a request, so I couldn't have measured it.

**The first thing I'd do with another unit: merge the two model calls into one.** It's the only change that attacks both causes of my one remaining miss at once (round trips to a slow model, and calls counted by the limiter). The load test says it matters more than it looks, because with one agent at a time, every second saved per run is saved again for every person waiting in the queue.

**How I Used AI**

I used Claude (in VS Code, through Claude Code) for most of the building and testing in this unit, and I'm being specific about where the judgment came from.

**Moment 1: the criteria.** I asked Claude to suggest criteria and said I'd choose. That isn't what the brief recommends; it says to write them yourself and only ask a model whether they're testable. Claude flagged that first, then built the server and the log, and gave me eight candidates based on what my first logged session actually showed (the 43 s rate-limit stall, the 200 on a broken key). I picked five: every request logged, ten in a row under 5 s, a slow request explains itself, broken key returns 503, bad input gets a 4xx and never a 500. Claude drafted the wording in my criteria.md style, and I read and approved them before they were committed in `4adfaf7`, before anything ran. The part I'd own most is the choice: I took the set where three of five were likely to miss rather than the safe ones, because the brief says five safe criteria make a unit with nothing to learn.

**Moment 2: pushing for more passes, and what I didn't change.** After the before run, four of five were missed, and I asked Claude to fix criterion 3 and then criterion 5 so I'd have more than one pass. Claude said the honest way to do that was to fix the system, not the targets: lowering criterion 2's 5 s to whatever I got would be the kind of revision the brief says doesn't count. It pointed out that 4 and 5 had the same cause in my diagnosis (`serve.py` only deciding the status by whether the agent raised), so one change could address both. So I made the first improvement for criterion 3 and the second for 4 and 5, and left criterion 2 missed. The first improvement also corrected Claude's first diagnosis: it had blamed the rate limiter for criterion 2 based on the terminal output, and once the log recorded model time separately, 23 of 27 slow requests turned out to be the model. I kept both diagnoses in this README instead of rewriting the first one, because the change is the evidence that the log works.

**What I checked myself:** that criteria.md was committed before any results (`git log` shows `4adfaf7` before `d814f19`), that the pasted log lines are real lines from the files named, and that the verdicts follow from my own targets.
