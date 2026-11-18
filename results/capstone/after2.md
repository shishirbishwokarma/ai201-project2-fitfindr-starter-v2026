# Capstone run log — after2

Produced by `capstone_trials.py` (`run_trial`, `score`). Raw records: `results/capstone/after2/trialN.jsonl`; server output: `trialN_server.txt`.

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Every request leaves exactly one record | 20 of 20 | 20/20 | 20/20 | 20/20 | MET |
| 2. Ten in a row stay under 5 s | 9 of 10 < 5 s | 0/10 ✗ | 0/10 ✗ | 1/10 ✗ | MISSED |
| 3. A slow request explains itself in the log | all slow ones | 12/12 | 12/12 | 11/11 | MET |
| 4. Broken key returns 503 | 5 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 5. Bad input: 4xx under 200 ms, no 500 | 5 of 5 | 5/5 | 5/5 | 5/5 | MET |

## Run 1 detail
- 1: 24 records for 24 requests sent
- 2: slow: [('vintage graphic tee under $30', 11128.3), ('90s track jacket in size M', 9178.9), ('silk slip dress in midi length under $40', 11946.8), ('platform sneakers size 8', 16685.0), ('denim jacket under $50', 10705.9), ('flannel shirt under $25', 11398.6), ('jacket $50', 10428.8), ('something cute for a date under $40', 13242.7), ('black boots', 12342.6), ('size medium hoodie', 11026.9)]
- 3: 12 slow requests
    - d509ed10 'vintage graphic tee under $30' 11128 ms, best cause field model_wait_ms=10393.0 → PASS
    - c826778d '90s track jacket in size M' 9179 ms, best cause field model_wait_ms=8839.0 → PASS
    - a7022341 'silk slip dress in midi length under $40' 11947 ms, best cause field model_wait_ms=11610.2 → PASS
    - 9928c6f7 'platform sneakers size 8' 16685 ms, best cause field model_wait_ms=16328.2 → PASS
    - e89cf03e 'denim jacket under $50' 10706 ms, best cause field model_wait_ms=10393.5 → PASS
    - df83da18 'flannel shirt under $25' 11399 ms, best cause field model_wait_ms=10973.1 → PASS
    - 11c7677e 'jacket $50' 10429 ms, best cause field model_wait_ms=10028.9 → PASS
    - 1f716004 'something cute for a date under $40' 13243 ms, best cause field model_wait_ms=12919.2 → PASS
    - 9fccf068 'black boots' 12343 ms, best cause field model_wait_ms=11990.3 → PASS
    - 5c52b9d7 'size medium hoodie' 11027 ms, best cause field model_wait_ms=10462.3 → PASS
    - a8797ca2 'cheap sneakers' 9960 ms, best cause field model_wait_ms=9640.9 → PASS
    - 8a335656 'denim jaket' 11566 ms, best cause field model_wait_ms=11226.4 → PASS
- 4: 503 key-named=True; 503 key-named=True; 503 key-named=True; 503 key-named=True; 503 key-named=True
- 5: blank query: 400, 0.1 ms, bad_request; not JSON: 400, 0.2 ms, bad_request; query is a number: 400, 0.0 ms, bad_request; wardrobe items not a list: 400, 0.0 ms, bad_request; 5,000-character query: 400, 0.0 ms, bad_request

## Run 2 detail
- 1: 24 records for 24 requests sent
- 2: slow: [('vintage graphic tee under $30', 6780.3), ('90s track jacket in size M', 6127.4), ('silk slip dress in midi length under $40', 11778.4), ('platform sneakers size 8', 7905.4), ('denim jacket under $50', 21800.1), ('flannel shirt under $25', 11973.9), ('jacket $50', 17124.7), ('something cute for a date under $40', 23657.7), ('black boots', 9444.9), ('size medium hoodie', 6343.3)]
- 3: 12 slow requests
    - af6fccfa 'vintage graphic tee under $30' 6780 ms, best cause field model_wait_ms=6097.8 → PASS
    - 59f87d9b '90s track jacket in size M' 6127 ms, best cause field model_wait_ms=5860.7 → PASS
    - 71896a28 'silk slip dress in midi length under $40' 11778 ms, best cause field model_wait_ms=11504.6 → PASS
    - 7ef56392 'platform sneakers size 8' 7905 ms, best cause field model_wait_ms=7550.2 → PASS
    - 54bfb31a 'denim jacket under $50' 21800 ms, best cause field model_wait_ms=21411.3 → PASS
    - 5750a8a3 'flannel shirt under $25' 11974 ms, best cause field model_wait_ms=11654.4 → PASS
    - 4b51a5cf 'jacket $50' 17125 ms, best cause field model_wait_ms=16754.3 → PASS
    - b533d8e4 'something cute for a date under $40' 23658 ms, best cause field model_wait_ms=23326.1 → PASS
    - 1aa5d368 'black boots' 9445 ms, best cause field model_wait_ms=9084.5 → PASS
    - 1cf28f86 'size medium hoodie' 6343 ms, best cause field model_wait_ms=5806.8 → PASS
    - 92574bbb 'cheap sneakers' 5778 ms, best cause field model_wait_ms=5505.6 → PASS
    - 07cb3223 'denim jaket' 9622 ms, best cause field model_wait_ms=9377.4 → PASS
- 4: 503 key-named=True; 503 key-named=True; 503 key-named=True; 503 key-named=True; 503 key-named=True
- 5: blank query: 400, 0.1 ms, bad_request; not JSON: 400, 0.0 ms, bad_request; query is a number: 400, 0.0 ms, bad_request; wardrobe items not a list: 400, 0.0 ms, bad_request; 5,000-character query: 400, 0.0 ms, bad_request

## Run 3 detail
- 1: 24 records for 24 requests sent
- 2: slow: [('vintage graphic tee under $30', 8095.4), ('90s track jacket in size M', 11953.4), ('silk slip dress in midi length under $40', 5680.2), ('platform sneakers size 8', 5913.5), ('denim jacket under $50', 6087.2), ('flannel shirt under $25', 7776.1), ('something cute for a date under $40', 11380.2), ('black boots', 12780.0), ('size medium hoodie', 9999.0)]
- 3: 11 slow requests
    - ed485b61 'vintage graphic tee under $30' 8095 ms, best cause field model_wait_ms=7390.9 → PASS
    - ac78ef71 '90s track jacket in size M' 11953 ms, best cause field model_wait_ms=11696.2 → PASS
    - 444ab03d 'silk slip dress in midi length under $40' 5680 ms, best cause field model_wait_ms=5215.9 → PASS
    - 0bbe82c3 'platform sneakers size 8' 5914 ms, best cause field model_wait_ms=5592.1 → PASS
    - e1e52cfb 'denim jacket under $50' 6087 ms, best cause field model_wait_ms=5783.8 → PASS
    - ba3f39d3 'flannel shirt under $25' 7776 ms, best cause field model_wait_ms=7454.1 → PASS
    - 2f8e9927 'something cute for a date under $40' 11380 ms, best cause field rate_limit_wait_ms=8181.5 → PASS
    - ea7078d4 'black boots' 12780 ms, best cause field model_wait_ms=8994.8 → PASS
    - 8d2abcc2 'size medium hoodie' 9999 ms, best cause field model_wait_ms=8065.8 → PASS
    - 65155e38 'cheap sneakers' 7310 ms, best cause field model_wait_ms=7033.8 → PASS
    - 610f126a 'denim jaket' 7153 ms, best cause field model_wait_ms=6872.3 → PASS
- 4: 503 key-named=True; 503 key-named=True; 503 key-named=True; 503 key-named=True; 503 key-named=True
- 5: blank query: 400, 0.1 ms, bad_request; not JSON: 400, 0.1 ms, bad_request; query is a number: 400, 0.1 ms, bad_request; wardrobe items not a list: 400, 0.0 ms, bad_request; 5,000-character query: 400, 0.0 ms, bad_request
