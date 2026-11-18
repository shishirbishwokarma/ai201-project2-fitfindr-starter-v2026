# Load observation

Produced by `load_test.py`. Records: `results/capstone/load/normal.jsonl`, `10x.jsonl`.

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

10x, per request in the order the lock let them through:

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