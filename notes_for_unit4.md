# Notes for Unit 4

Things I found by using FitFindr the way a real person would, at the end of
Unit 3 (Oct 28). I left them unfixed on purpose: Unit 4 is test, diagnose,
then make **one** improvement, and these are what I expect to diagnose.

All runs: `python app.py ask '...'` with the example wardrobe.

| What I typed | What came back | Problem |
|---|---|---|
| `jacket $50` | 90s Track Jacket, $45 | fine |
| `something cute for a date under $40` | Y2K Baby Tee, $18 | fine |
| `black boots` | Oversized Flannel Shirt — Plaid Red/Black | matched only on "black" |
| `denim jaket` (typo) | Vintage Levi's 501 Jeans | typo ignored, got jeans not a jacket |
| `size medium hoodie` | no results, "drop the size MEDIUM filter" | "medium" isn't read as `M` |
| `Levis jeans size 30` | no results | "Levis" ≠ "Levi's", "30" ≠ `W30` |
| `medium tee` | Y2K Baby Tee (S/M) | "medium" treated as a word, not a size; got lucky |
| `cheap sneakers` | Platform Sneakers, $48 | "cheap" ignored |

Also seen while building:
- `search_listings('graphic tee', max_price=30)` includes Low-Rise Cargo Pants.
- Two of three fit cards for the same jeans opened with "Scored these".

## Patterns

1. **Search doesn't know item types.** In `tools.py::search_listings`, every
   shared word scores the same, so a color ("black") counts as much as the
   thing you want ("boots"). Same cause as cargo pants for "graphic tee".
2. **Sizes only work in the data's exact format.** `agent.py::parse_query`
   only takes `size X` literally. "medium" never becomes `M`, and "30" never
   becomes `W30`, so `_size_matches` filters everything out.
3. **Near-miss words fail.** "Levis" vs "Levi's", "jaket" vs "jacket". The
   search compares whole words exactly.

Criterion 1's reason ("a different wording can miss") predicted pattern 1 and
pattern 3.

## Possible single improvements for Unit 4

- Size normalising in `parse_query`: "small/medium/large" → S/M/L, a bare
  number next to jeans → `W30`. Fixes pattern 2.
- Weight category words (tee, jeans, boots, jacket…) higher than colors in the
  search score. Fixes pattern 1.
