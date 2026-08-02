# Baseline — Prompt Caching

**Measured:** 2026-08-02
**Corpus:** 23 documents, 77,339 tokens, `s3://yfh227-fulfillment-ops-docs`
**Model:** `us.anthropic.claude-sonnet-4-6` (Bedrock, US geo cross-region)
**Method:** identical 24-call eval, `cachePoint` after the document context block.
**Companion to:** `baseline_direct_context.md` (uncached)

---

## Verdict

**Prompt caching removes 82% of the cost, for a one-line change, with
no measurable quality loss.**

Cost per 100 questions falls from **$27.20** to **$4.86**. Eval holds
at 8/8 across three runs. Latency improves slightly.

**This should be evaluated seriously before committing a week to retrieval.**
Retrieval attacks the same input-token term and would likely land in a similar
cost range, but costs far more to build, adds a failure mode caching does not
have (retrieving the wrong documents), and must be tuned and re-evaluated.
Caching is a `cachePoint` in one dict.

What caching does **not** solve is covered in *Limits* below — it is not a
substitute for retrieval at every corpus size.

---

## Headline comparison

All three columns use the hardened system prompt (sha `33edc49de255`), so the
only variable is caching.

| Metric | Uncached | Cached | Delta |
|---|---|---|---|
| Eval pass rate | 8/8, 8/8, 8/8 | 8/8, 8/8, 8/8 | no change |
| Mean total input tokens | 79,506 | 79,505 | ~same |
| Mean *billed-at-full-rate* input | 79,506 | 20.8 | -100.0% |
| Mean latency | 15,352 ms | 14,472 ms | -5.7% |
| Min latency | 2,834 ms | 2,164 ms | |
| Max latency | 28,011 ms | 27,197 ms | |
| **Cost per call** | **$0.27200** | **$0.04859** | **-82.1%** |
| **Cost per 100 questions** | **$27.20** | **$4.86** | **-82.1%** |
| Cost per 1,000 questions | $272.00 | $48.59 | |
| Context window used | 7.95% | 7.95% | unchanged |

Caching does not reduce context consumed — the model still processes the full
prompt. It changes what you are **billed** for.

---

## Cached runs — reported separately

### Cached run 1 — 8/8 PASSED

| Case | Latency | Billed input | Output | Cache read | Cache write |
|---|---|---|---|---|---|
| Documented internal process | 25,752 ms | 18 | 1,038 | 0 | 79,484 |
| Documented financial decision | 25,718 ms | 26 | 1,074 | 79,484 | 0 |
| Topic absent from documents | 2,538 ms | 17 | 46 | 79,484 | 0 |
| Mixed coverage | 6,756 ms | 21 | 228 | 79,484 | 0 |
| Cross-document synthesis | 21,185 ms | 22 | 833 | 79,484 | 0 |
| False premise correction | 10,801 ms | 25 | 387 | 79,484 | 0 |
| Exact figure recall | 7,671 ms | 16 | 335 | 79,484 | 0 |
| Client-facing, non-financial | 19,005 ms | 21 | 816 | 79,484 | 0 |
| **Totals** | **119,426 ms** | **166** | **4,757** | **556,388** | **79,484** |

### Cached run 2 — 8/8 PASSED

| Case | Latency | Billed input | Output | Cache read | Cache write |
|---|---|---|---|---|---|
| Documented internal process | 25,920 ms | 18 | 1,153 | 79,484 | 0 |
| Documented financial decision | 19,623 ms | 26 | 787 | 79,484 | 0 |
| Topic absent from documents | 2,164 ms | 17 | 38 | 79,484 | 0 |
| Mixed coverage | 5,146 ms | 21 | 162 | 79,484 | 0 |
| Cross-document synthesis | 21,698 ms | 22 | 964 | 79,484 | 0 |
| False premise correction | 8,075 ms | 25 | 275 | 79,484 | 0 |
| Exact figure recall | 7,133 ms | 16 | 292 | 79,484 | 0 |
| Client-facing, non-financial | 21,064 ms | 21 | 905 | 79,484 | 0 |
| **Totals** | **110,823 ms** | **166** | **4,576** | **635,872** | **0** |

### Cached run 3 — 8/8 PASSED

| Case | Latency | Billed input | Output | Cache read | Cache write |
|---|---|---|---|---|---|
| Documented internal process | 27,197 ms | 18 | 1,211 | 79,484 | 0 |
| Documented financial decision | 20,737 ms | 26 | 862 | 79,484 | 0 |
| Topic absent from documents | 2,279 ms | 17 | 49 | 79,484 | 0 |
| Mixed coverage | 4,577 ms | 21 | 150 | 79,484 | 0 |
| Cross-document synthesis | 26,582 ms | 22 | 1,082 | 79,484 | 0 |
| False premise correction | 7,513 ms | 25 | 249 | 79,484 | 0 |
| Exact figure recall | 7,176 ms | 16 | 289 | 79,484 | 0 |
| Client-facing, non-financial | 21,013 ms | 21 | 916 | 79,484 | 0 |
| **Totals** | **117,074 ms** | **166** | **4,808** | **635,872** | **0** |

### Cache behaviour

| | Value |
|---|---|
| Cache writes across 24 calls | **1** |
| Cache reads across 24 calls | **23** |
| Tokens written | 79,484 |
| Tokens read | 1,828,132 |
| Billed-at-full-rate input, 24 calls | 498 |

**One write, twenty-three reads.** The write occurred on the very first call of
run 1. Runs 2 and 3 recorded zero writes — the 5-minute TTL refreshes on every
hit, and the runs were back to back, so the cache never went cold.

Billed-at-full-rate input dropped to **16–26 tokens per call** — the question text
alone. Everything else is served from cache at one tenth the rate.

---

## Cost derivation

Rates for `us.anthropic.claude-sonnet-4-6`, including the 10% cross-region
surcharge on the `us.` geo prefix:

| Token type | Multiplier | Rate |
|---|---|---|
| Input (uncached) | 1.0x | $3.30/M |
| Cache write (5-min TTL) | 1.25x | $4.125/M |
| Cache read | 0.10x | $0.33/M |
| Output | — | $16.50/M |

**Measured 24-call totals, cached:**

| Component | Tokens | Rate | Cost |
|---|---|---|---|
| Billed input | 498 | $3.30/M | $0.001643 |
| Cache read | 1,828,132 | $0.33/M | $0.603284 |
| Cache write | 79,484 | $4.125/M | $0.327871 |
| Output | 14,141 | $16.50/M | $0.233327 |
| **Total (24 calls)** | | | **$1.166125** |
| **Per call** | | | **$0.04859** |

**Uncached, same 24 calls:**

| Component | Tokens | Rate | Cost |
|---|---|---|---|
| Input | 1,908,138 | $3.30/M | $6.296855 |
| Output | 14,012 | $16.50/M | $0.231198 |
| **Total (24 calls)** | | | **$6.528053** |
| **Per call** | | | **$0.27200** |

---

## Sensitivity — how often does the cache have to be written?

The measured figure amortizes one write across 24 calls. Real traffic is
lumpier: an idle gap longer than 5 minutes expires the cache and the next call
pays a write.

| Write frequency | Cost/call | Cost/100 | vs uncached |
|---|---|---|---|
| every call (worst case) | $0.33766 | $33.77 | +24.1% |
| every 2 calls | $0.18684 | $18.68 | -31.3% |
| every 5 calls | $0.09635 | $9.63 | -64.6% |
| every 10 calls | $0.06618 | $6.62 | -75.7% |
| every 24 calls | $0.04859 | $4.86 | -82.1% |
| every 50 calls | $0.04205 | $4.21 | -84.5% |
| every 100 calls | $0.03904 | $3.90 | -85.6% |

**Even in the worst case — a cache write on every single call, meaning the cache
never hits — caching costs $33.77 per 100 versus
$27.20 uncached.** That is the pathological case and it is still only
+24% against baseline.

At any realistic cadence — a support tool with more than one question per five
minutes during working hours — the cache stays warm and the figure sits near the
$4.86 measured result.

---

## Latency

| | Uncached | Cached |
|---|---|---|
| Mean | 15,352 ms | 14,472 ms |
| Median | 13,518 ms | 14,903 ms |
| Min | 2,834 ms | 2,164 ms |
| Max | 28,011 ms | 27,197 ms |

Mean latency improved **-5.7%**. This is real but modest, and smaller
than the run-to-run variance in either condition. Latency here is dominated by
output generation, not input processing — the fastest case (refusal, ~40 output
tokens) runs ~2.2s cached versus ~2.9s uncached, while the slowest (synthesis,
~1,000 output tokens) is ~25s in both.

**Do not adopt caching for latency.** Adopt it for cost.

---

## Quality

| | Run 1 | Run 2 | Run 3 |
|---|---|---|---|
| Uncached | 8/8 | 8/8 | 8/8 |
| Cached | 8/8 | 8/8 | 8/8 |

**No quality difference.** Caching changes how the prefix is processed, not what
the model sees. Six consecutive 8/8 runs across both conditions.

Mean output length was near-identical (uncached 584 tokens, cached 589), which is the
expected result and a useful sanity check that the restructured content blocks
did not change model behaviour.

---

## Limits — what caching does not fix

1. **It does not reduce context consumed.** Still 7.93% of the 1M window. The
   corpus can grow ~12x before the window binds, and caching does not extend that.
2. **It does not reduce output cost.** Output is now **20%** of the cached bill, up from
   4% uncached. Further
   cost work would have to attack answer length, not retrieval.
3. **It does not help a cold cache.** First call after any 5-minute idle gap pays
   a write. An assistant used a few times a day, not continuously, sees a worse
   effective rate than the measured figure.
4. **It does not scale indefinitely.** At 10x the corpus (~800K tokens) the
   window becomes the constraint and no caching strategy helps. Retrieval is the
   answer at that scale — just not at this one.
5. **Sonnet 4.6 supports 5-minute TTL only.** The 1-hour option available on
   Sonnet 4.5 and Opus 4.5 would suit intermittent traffic better and is not
   available here.
6. **Cross-region inference can force extra writes.** AWS documents that under
   high demand, cross-region routing 'may lead to increased cache writes'. The
   `us.` prefix means this applies. Not observed in these runs, but it makes the
   sensitivity table above the honest way to read the result.

---

## Recommendation

**Adopt caching now.** It is a one-line change worth 82% of cost
with no measured downside.

**Then decide whether retrieval is still worth building.** The case for it after
caching is narrower than before:

- Cost is already down to $4.86/100 questions. Retrieval might reach
  $2-4 by cutting input further, but the remaining headroom is small in absolute
  terms and output cost sets a floor caching cannot cross.
- Retrieval's real argument is **corpus scale**, not cost. When the corpus
  outgrows the context window, retrieval becomes necessary rather than merely
  economical. At 77K tokens against a 1M window, that is roughly 12x away.
- Retrieval adds a failure mode caching does not have: retrieving the wrong
  documents produces a confidently wrong answer, where direct context cannot.
  The eval would need new cases for retrieval quality itself.

---

## Reproduce

```bash
./venv/Scripts/python.exe eval.py
```

```bash
EVAL_PROMPT_CACHE=1 ./venv/Scripts/python.exe eval.py
```

Caching is off by default. `core.ask(..., use_cache=True)` places the
`cachePoint` after the document context block.

## Method notes

1. **Cache multipliers (1.25x write, 0.10x read, 5-min TTL) are the documented
   Anthropic-on-Bedrock rates.** Verified against AWS documentation and pricing
   summaries; the Bedrock prompt-caching page states these explicitly for GPT-5.6
   and refers to the pricing page for Claude.
2. **The three cached runs ran back to back**, which is why the cache never went
   cold. A deliberately cold-start measurement was not taken; the sensitivity
   table models it arithmetically instead.
3. **The uncached comparison uses the hardened prompt**, not the original
   committed baseline, so caching is the only variable. Against the *original*
   uncached baseline ($0.27229/call, 7/8, 8/8, 7/8) the saving is
   82%.
4. **No retrieval code was written or modified.**
