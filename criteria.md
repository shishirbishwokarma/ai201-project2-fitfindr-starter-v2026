# Acceptance criteria — FitFindr

Five criteria that say what "working" means for this agent, written in unit 3
**before** any results existed.

An acceptance criterion names a target: a number, a count, a rate, or something
a person could plainly observe. *"The agent handles errors"* is an opinion.
*"When search returns nothing, the agent stops before calling the second tool,
in 5 of 5 tries"* is a criterion.

Under each one, write a sentence or two on **why that target** and not a
stricter one. A reason that says something about your tools, your loop, or the
data earns credit; *"80% seemed reasonable"* does not.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

**Two are written for you. You write three.**

---

## 1. A matching query completes all three tools

Given a query that matches at least one listing, the agent completes all three
tool calls and returns a fit card — in at least 4 of 5 tries.

**Why this target:**
<!-- Why 4 of 5 and not 5 of 5? Something about your search, probably —
     "my search is a plain keyword match and some phrasings will miss" is a
     real answer. -->
Sometimes it will say it didn't find anything even when a matching listing
exists, because my search only matches exact words, and a different wording
can miss. So I'm not expecting 5 of 5.

---

## 2. An impossible query stops before the second tool

Given a query that matches no listings, the agent stops before calling
`suggest_outfit` and returns a message naming what to change — 5 of 5 tries.

**Why this target:**
<!-- Why is 5 of 5 reasonable here when criterion 1 isn't? What's different
     about this path? -->
If the search comes back empty, the loop stops right there and doesn't call
the other tools. No model is involved in that check, so it should happen every
time. And stopping is the right thing to do when nothing matches.

---

## 3. Something about state

<!-- YOU WRITE THIS ONE.

     How would you know that the item your search found is the same item the
     next tool received? Name something countable or observable.

     This is the criterion people find hardest, because state failure doesn't
     look like state failure — it looks like a tool problem. Something that
     compares session["selected_item"] against what actually reached
     suggest_outfit is the shape you're after. -->

Given a query that matches at least one listing, the `id` in
`session["selected_item"]` is the same `id` as the item `suggest_outfit`
actually received — in 5 of 5 tries.

**Why this target:**
The item goes straight from the session into `suggest_outfit`, so nothing
should be able to change it on the way. That matters because the outfit has to
be about the item the search actually found for that query, every time.


---

## 4. Something about the fit card

<!-- YOU WRITE THIS ONE.

     The fit card calls a model, so the same input can produce different words
     each time. That's not a bug — it's the nature of the tool. So what would
     make it acceptable?

     Think about what you'd actually be unhappy to see. A caption that never
     mentions the price? Two different items producing the same opening
     sentence? A card longer than a caption anyone would post? Any of those can
     be turned into a number. -->

Given a query that matches at least one listing, the fit card states the
selected item's price (e.g. "$18") and mentions no brand name from
`data/listings.json` other than the selected item's own `brand` (none at all if
its `brand` is None) — in at least 4 of 5 tries.

**Why this target:**
Some clothes don't have a brand, so the model might make one up to fill the
gap, or forget the price. The caption is written by a model, not by code, so I
allow one miss out of five.


---

## 5. Your choice

<!-- YOU WRITE THIS ONE TOO.

     Pick something you actually care about getting right. Speed, the empty
     wardrobe path, what happens when the model can't be reached, whether the
     search respects a price ceiling — anything, as long as it names a number
     or an observable outcome. -->

Given a query with a price limit (e.g. "under $30"), every listing in
`session["search_results"]` has a `price` at or below that limit — in 5 of 5
tries.

**Why this target:**
The whole point is staying within budget, so a result over the limit is
useless. The price check is a plain comparison in my code, not the model's
judgment, so it should hold every time.


---

<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 4 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath it, like this:

         ## 4. Something about the fit card

         The fit card is different every time.

         **Why this target:** ...

         > **Revised in unit 4:** For 5 different items, the 5 fit cards share
         > no opening sentence.
         >
         > **Why revised:** "different" wasn't checkable — two cards that
         > differed by one word still counted. The new version is something I
         > can actually score.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "I said the empty search stops it 5 of 5 times, but I got 3 of 5,
            so 3 of 5 is more realistic."

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.
     ───────────────────────────────────────────────────────────────────────── -->

---
---

# Capstone criteria — FitFindr served over HTTP, with a structured log

Written in the capstone unit, **before** any trial runs. The five above are
Unit 3's and stay as they were. These five are about the extension: `serve.py`
answering over HTTP and writing one record per request to
`logs/requests.jsonl`. Numbers 1, 4 and 5 are about the bad path.

What I already knew when I wrote these, from the Milestone 3 session in the
README: a full run takes about 2.4 s (median) and 674 tokens, and one run of
twelve took 45.7 s.

**How a trial works.** Each trial starts the server fresh with
`AI201_CACHE=0`, sends a batch of requests, and scores them from the log file
and the HTTP responses. Three trials for each criterion, changing nothing in
between.

---

## Capstone 1. Every request leaves exactly one record

In one trial of 20 requests — 12 matching queries, 2 impossible queries, the
5 malformed bodies from criterion 5, and 1 query with a broken API key — the
log has exactly one record for each request (20 of 20), and each record's
`request_id` matches the `X-Request-Id` header that request got back.

**Why this target:**
The log is the only way to find out later what happened. A request that left
no record is invisible, and failures are the ones most likely to go missing,
so this has to be 20 of 20, not most of them. The header check is what proves
a record belongs to the request I think it does, rather than just counting
lines.

---

## Capstone 2. Ten requests in a row stay under 5 seconds

With the server just started, 10 matching queries sent one after another (each
as soon as the last one answers): at least 9 of 10 have a `duration_ms` under
5,000.

**Why this target:**
The median run in my first session was 2.4 s, and nearly all of it is the two
model calls, so 5 s is twice a normal run. Someone shopping won't wait much
longer than that. I'm allowing one slow request because the model's own
response time varies, but more than one means something in my system is
making people wait, not the model.

---

## Capstone 3. A slow request explains itself in the log

For every request in criteria 1 and 2's trials with `duration_ms` over 5,000,
its log record alone has a field that names the cause of the wait (for
example, time spent waiting on the rate limiter), and that field's value is at
least half of `duration_ms`. Target: all of them.

**Why this target:**
Knowing *which stage* was slow isn't enough. `stages_ms` already says that,
and it can't tell a slow model from my own rate limiter making the request
wait. The terminal output says why, but it's gone once the server stops. If I
can't explain a slow request from its record, the log hasn't done its job.
"At least half" makes it a number two people would score the same way.

---

## Capstone 4. A model failure is an error, not a success

With the server started on a broken `GEMINI_API_KEY`, 5 matching queries all
come back with HTTP status 503 (not 200), with a body that says the API key
is the problem — 5 of 5.

**Why this target:**
Anything calling FitFindr over HTTP checks the status code first. A 200 tells
it everything worked when the user got no outfit and no fit card. The bad key
fails the same way every time and doesn't depend on the model's wording, so
it should be 5 of 5.

---

## Capstone 5. Bad input is turned away fast, never a 500

Five malformed bodies — a blank query, a body that isn't JSON, `{"query": 42}`,
a wardrobe that isn't a list (`{"query": "denim jacket", "wardrobe": {"items": "x"}}`),
and a 5,000-character query — each get a 4xx status with a `duration_ms`
under 200, and none gets a 500. Target: 5 of 5.

**Why this target:**
Bad input should be refused before it reaches the MCP search or the model, so
it shouldn't cost a search (about 250 ms, which is why the limit is 200) or
any tokens. A 500 means my code crashed on something a caller sent, which is
my bug, not theirs. Each body fails the same way every time, so nothing
justifies missing one.
