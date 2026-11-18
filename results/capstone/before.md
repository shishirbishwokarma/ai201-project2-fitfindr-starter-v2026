# Capstone run log — before

Produced by `capstone_trials.py` (`run_trial`, `score`). Raw records: `results/capstone/before/trialN.jsonl`; server output: `trialN_server.txt`.

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Every request leaves exactly one record | 20 of 20 | 20/20 | 20/20 | 20/20 | MET |
| 2. Ten in a row stay under 5 s | 9 of 10 < 5 s | 4/10 ✗ | 6/10 ✗ | 4/10 ✗ | MISSED |
| 3. A slow request explains itself in the log | all slow ones | 0/7 ✗ | 0/6 ✗ | 0/9 ✗ | MISSED |
| 4. Broken key returns 503 | 5 of 5 | 0/5 ✗ | 0/5 ✗ | 0/5 ✗ | MISSED |
| 5. Bad input: 4xx under 200 ms, no 500 | 5 of 5 | 3/5 ✗ | 3/5 ✗ | 3/5 ✗ | MISSED |

## Run 1 detail
- 1: 24 records for 24 requests sent
- 2: slow: [('vintage graphic tee under $30', 8275.4), ('90s track jacket in size M', 6734.9), ('silk slip dress in midi length under $40', 7192.7), ('something cute for a date under $40', 31683.4), ('black boots', 7495.9), ('size medium hoodie', 6978.3)]
- 3: 7 slow requests
    - f0a7e786 'vintage graphic tee under $30' 8275 ms, best cause field wait_ms=0.0 → FAIL
    - adff79cc '90s track jacket in size M' 6735 ms, best cause field wait_ms=0.0 → FAIL
    - e17e349c 'silk slip dress in midi length under $40' 7193 ms, best cause field wait_ms=0.0 → FAIL
    - 91b22ac6 'something cute for a date under $40' 31683 ms, best cause field wait_ms=0.0 → FAIL
    - 2cf430e7 'black boots' 7496 ms, best cause field wait_ms=0.0 → FAIL
    - a18fb989 'size medium hoodie' 6978 ms, best cause field wait_ms=0.0 → FAIL
    - 457f1d09 'cheap sneakers' 6907 ms, best cause field wait_ms=0.0 → FAIL
- 4: 200 key-named=True; 200 key-named=True; 200 key-named=True; 200 key-named=True; 200 key-named=True
- 5: blank query: 400, 0.1 ms, bad_request; not JSON: 400, 0.0 ms, bad_request; query is a number: 400, 0.0 ms, bad_request; wardrobe items not a list: 500, 221.0 ms, crash; 5,000-character query: 200, 2269.6 ms, fit_card

## Run 2 detail
- 1: 24 records for 24 requests sent
- 2: slow: [('vintage graphic tee under $30', 6008.4), ('silk slip dress in midi length under $40', 13733.5), ('something cute for a date under $40', 25770.4), ('black boots', 5676.2)]
- 3: 6 slow requests
    - e9d15de0 'vintage graphic tee under $30' 6008 ms, best cause field wait_ms=0.0 → FAIL
    - 06b58b06 'silk slip dress in midi length under $40' 13734 ms, best cause field wait_ms=0.0 → FAIL
    - 8bacbdcf 'something cute for a date under $40' 25770 ms, best cause field wait_ms=0.0 → FAIL
    - 26f7f1e8 'black boots' 5676 ms, best cause field wait_ms=0.0 → FAIL
    - 9649951e 'cheap sneakers' 14220 ms, best cause field wait_ms=0.0 → FAIL
    - 4f4e9a07 'vintage tee vintage tee vintage tee v...' 7900 ms, best cause field wait_ms=0.0 → FAIL
- 4: 200 key-named=True; 200 key-named=True; 200 key-named=True; 200 key-named=True; 200 key-named=True
- 5: blank query: 400, 0.1 ms, bad_request; not JSON: 400, 0.0 ms, bad_request; query is a number: 400, 0.0 ms, bad_request; wardrobe items not a list: 500, 242.8 ms, crash; 5,000-character query: 200, 7899.6 ms, fit_card

## Run 3 detail
- 1: 24 records for 24 requests sent
- 2: slow: [('vintage graphic tee under $30', 8728.3), ('silk slip dress in midi length under $40', 8230.5), ('denim jacket under $50', 5463.4), ('flannel shirt under $25', 5267.0), ('something cute for a date under $40', 23634.2), ('black boots', 12036.0)]
- 3: 9 slow requests
    - 7fbc7cfc 'vintage graphic tee under $30' 8728 ms, best cause field wait_ms=0.0 → FAIL
    - d5d6834a 'silk slip dress in midi length under $40' 8230 ms, best cause field wait_ms=0.0 → FAIL
    - 0058409f 'denim jacket under $50' 5463 ms, best cause field wait_ms=0.0 → FAIL
    - e2d21b3d 'flannel shirt under $25' 5267 ms, best cause field wait_ms=0.0 → FAIL
    - 46d6f963 'something cute for a date under $40' 23634 ms, best cause field wait_ms=0.0 → FAIL
    - 7c253646 'black boots' 12036 ms, best cause field wait_ms=0.0 → FAIL
    - 7555e95a 'cheap sneakers' 9917 ms, best cause field wait_ms=0.0 → FAIL
    - ff5ce4fd 'denim jaket' 9799 ms, best cause field wait_ms=0.0 → FAIL
    - 189634a6 'vintage tee vintage tee vintage tee v...' 5538 ms, best cause field wait_ms=0.0 → FAIL
- 4: 200 key-named=True; 200 key-named=True; 200 key-named=True; 200 key-named=True; 200 key-named=True
- 5: blank query: 400, 0.1 ms, bad_request; not JSON: 400, 0.3 ms, bad_request; query is a number: 400, 0.0 ms, bad_request; wardrobe items not a list: 500, 216.4 ms, crash; 5,000-character query: 200, 5537.5 ms, fit_card
