# Capstone run log — after

Produced by `capstone_trials.py` (`run_trial`, `score`). Raw records: `results/capstone/after/trialN.jsonl`; server output: `trialN_server.txt`.

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Every request leaves exactly one record | 20 of 20 | 20/20 | 20/20 | 20/20 | MET |
| 2. Ten in a row stay under 5 s | 9 of 10 < 5 s | 3/10 ✗ | 3/10 ✗ | 4/10 ✗ | MISSED |
| 3. A slow request explains itself in the log | all slow ones | 9/9 | 9/9 | 9/9 | MET |
| 4. Broken key returns 503 | 5 of 5 | 0/5 ✗ | 0/5 ✗ | 0/5 ✗ | MISSED |
| 5. Bad input: 4xx under 200 ms, no 500 | 5 of 5 | 3/5 ✗ | 3/5 ✗ | 3/5 ✗ | MISSED |

## Run 1 detail
- 1: 24 records for 24 requests sent
- 2: slow: [('vintage graphic tee under $30', 11081.6), ('silk slip dress in midi length under $40', 7038.8), ('flannel shirt under $25', 6382.9), ('jacket $50', 9409.4), ('something cute for a date under $40', 25097.2), ('black boots', 6814.1), ('size medium hoodie', 6112.8)]
- 3: 9 slow requests
    - d8e17152 'vintage graphic tee under $30' 11082 ms, best cause field model_wait_ms=10396.1 → PASS
    - 4be29899 'silk slip dress in midi length under $40' 7039 ms, best cause field model_wait_ms=6761.9 → PASS
    - 8fe1b670 'flannel shirt under $25' 6383 ms, best cause field model_wait_ms=6144.8 → PASS
    - 3a75c1c3 'jacket $50' 9409 ms, best cause field model_wait_ms=9159.4 → PASS
    - 680e647d 'something cute for a date under $40' 25097 ms, best cause field model_wait_ms=24804.8 → PASS
    - 8f9046cc 'black boots' 6814 ms, best cause field rate_limit_wait_ms=4179.4 → PASS
    - 2574c8fc 'size medium hoodie' 6113 ms, best cause field model_wait_ms=5581.4 → PASS
    - 0f52e06f 'cheap sneakers' 9382 ms, best cause field model_wait_ms=7020.1 → PASS
    - 6a6e5a37 'denim jaket' 5973 ms, best cause field model_wait_ms=5715.0 → PASS
- 4: 200 key-named=True; 200 key-named=True; 200 key-named=True; 200 key-named=True; 200 key-named=True
- 5: blank query: 400, 0.2 ms, bad_request; not JSON: 400, 0.1 ms, bad_request; query is a number: 400, 0.0 ms, bad_request; wardrobe items not a list: 500, 256.1 ms, crash; 5,000-character query: 200, 2144.8 ms, fit_card

## Run 2 detail
- 1: 24 records for 24 requests sent
- 2: slow: [('90s track jacket in size M', 12422.5), ('silk slip dress in midi length under $40', 6567.0), ('platform sneakers size 8', 9656.9), ('denim jacket under $50', 11315.3), ('jacket $50', 11715.8), ('something cute for a date under $40', 8660.9), ('size medium hoodie', 9251.3)]
- 3: 9 slow requests
    - 2f0bc6d2 '90s track jacket in size M' 12422 ms, best cause field model_wait_ms=12186.4 → PASS
    - ea2d89aa 'silk slip dress in midi length under $40' 6567 ms, best cause field model_wait_ms=6239.8 → PASS
    - 5cab96d2 'platform sneakers size 8' 9657 ms, best cause field model_wait_ms=9305.5 → PASS
    - c1d45f13 'denim jacket under $50' 11315 ms, best cause field model_wait_ms=10991.8 → PASS
    - d26877a6 'jacket $50' 11716 ms, best cause field model_wait_ms=11475.8 → PASS
    - bafe1489 'something cute for a date under $40' 8661 ms, best cause field model_wait_ms=8353.9 → PASS
    - 42bdb0ac 'size medium hoodie' 9251 ms, best cause field model_wait_ms=6524.3 → PASS
    - 587a642f 'cheap sneakers' 6891 ms, best cause field rate_limit_wait_ms=4588.4 → PASS
    - 6bba5c91 'denim jaket' 14394 ms, best cause field rate_limit_wait_ms=7325.9 → PASS
- 4: 200 key-named=True; 200 key-named=True; 200 key-named=True; 200 key-named=True; 200 key-named=True
- 5: blank query: 400, 0.1 ms, bad_request; not JSON: 400, 0.0 ms, bad_request; query is a number: 400, 0.0 ms, bad_request; wardrobe items not a list: 500, 223.0 ms, crash; 5,000-character query: 200, 4971.5 ms, fit_card

## Run 3 detail
- 1: 24 records for 24 requests sent
- 2: slow: [('vintage graphic tee under $30', 9275.7), ('90s track jacket in size M', 7959.1), ('denim jacket under $50', 10035.8), ('flannel shirt under $25', 5122.6), ('something cute for a date under $40', 47499.9), ('black boots', 8589.9)]
- 3: 9 slow requests
    - 51846ce3 'vintage graphic tee under $30' 9276 ms, best cause field model_wait_ms=8547.7 → PASS
    - 23d31661 '90s track jacket in size M' 7959 ms, best cause field model_wait_ms=7725.7 → PASS
    - 3af4b2ed 'denim jacket under $50' 10036 ms, best cause field model_wait_ms=9780.8 → PASS
    - 1ea5feb0 'flannel shirt under $25' 5123 ms, best cause field model_wait_ms=4767.4 → PASS
    - cc7f4e70 'something cute for a date under $40' 47500 ms, best cause field rate_limit_wait_ms=38751.4 → PASS
    - b4ca4c9f 'black boots' 8590 ms, best cause field model_wait_ms=8238.4 → PASS
    - 34f8f2f1 'cheap sneakers' 5438 ms, best cause field model_wait_ms=5190.1 → PASS
    - 733424fa 'denim jaket' 5804 ms, best cause field model_wait_ms=5547.5 → PASS
    - 145bf912 'vintage tee vintage tee vintage tee v...' 5419 ms, best cause field model_wait_ms=5203.5 → PASS
- 4: 200 key-named=True; 200 key-named=True; 200 key-named=True; 200 key-named=True; 200 key-named=True
- 5: blank query: 400, 0.1 ms, bad_request; not JSON: 400, 0.1 ms, bad_request; query is a number: 400, 0.0 ms, bad_request; wardrobe items not a list: 500, 210.1 ms, crash; 5,000-character query: 200, 5419.2 ms, fit_card
