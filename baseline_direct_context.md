# Baseline — Direct Context (Pre-Retrieval)

**Measured:** 2026-08-02
**Corpus:** 23 documents, 77,339 tokens (chars/3.5 estimate), `s3://yfh227-fulfillment-ops-docs`
**Model:** `us.anthropic.claude-sonnet-4-6` (Bedrock, US geo cross-region)
**Method:** entire corpus passed as context on every call. No retrieval.

This is the **"before"** half of the V3 comparison. Every number here is what
retrieval has to beat.

---

## Headline

| Metric | V2 (7 docs) | V3 baseline (23 docs) | Delta |
|---|---|---|---|
| Documents | 7 | 23 | +229% |
| Corpus tokens (est.) | 7,291 | 77,339 | +960% |
| Mean input tokens/call | 7,493 | 79,341 | +958.9% |
| Mean latency | 11,723 ms | 16,400 ms | +39.9% |
| Cost per call | $0.03314 | $0.27229 | +721.6% |
| Cost per 100 questions | $3.31 | $27.23 | +721.6% |
| Context window used | 0.75% | 7.93% | +958.9% |
| Eval pass rate | 8/8, 8/8, 8/8 | **7/8, 8/8, 7/8** | **regression** |

---

## Eval runs — reported separately, not averaged

### Run 1 — 7/8 PASSED

| Case | Result | Latency | Input | Output |
|---|---|---|---|---|
| Documented internal process | PASS | 26,008 ms | 79,338 | 1,078 |
| Documented financial decision | PASS | 24,496 ms | 79,346 | 992 |
| Topic absent from documents | PASS | 3,696 ms | 79,337 | 74 |
| Mixed coverage | PASS | 7,767 ms | 79,341 | 213 |
| Cross-document synthesis | **FAIL** | 28,450 ms | 79,342 | 1,205 |
| False premise correction | PASS | 10,016 ms | 79,345 | 328 |
| Exact figure recall | PASS | 8,979 ms | 79,336 | 354 |
| Client-facing, non-financial | PASS | 16,055 ms | 79,341 | 565 |
| **Totals** | | **125,467 ms** | **634,726** | **4,809** |

Failed: **Cross-document synthesis (cite)**

### Run 2 — 8/8 PASSED

| Case | Result | Latency | Input | Output |
|---|---|---|---|---|
| Documented internal process | PASS | 26,848 ms | 79,338 | 1,104 |
| Documented financial decision | PASS | 16,046 ms | 79,346 | 598 |
| Topic absent from documents | PASS | 2,730 ms | 79,337 | 37 |
| Mixed coverage | PASS | 6,506 ms | 79,341 | 189 |
| Cross-document synthesis | PASS | 34,055 ms | 79,342 | 1,434 |
| False premise correction | PASS | 11,200 ms | 79,345 | 375 |
| Exact figure recall | PASS | 6,857 ms | 79,336 | 225 |
| Client-facing, non-financial | PASS | 26,968 ms | 79,341 | 1,075 |
| **Totals** | | **131,210 ms** | **634,726** | **5,037** |

### Run 3 — 7/8 PASSED

| Case | Result | Latency | Input | Output |
|---|---|---|---|---|
| Documented internal process | PASS | 28,664 ms | 79,338 | 1,245 |
| Documented financial decision | **FAIL** | 25,633 ms | 79,346 | 1,041 |
| Topic absent from documents | PASS | 2,930 ms | 79,337 | 40 |
| Mixed coverage | PASS | 6,588 ms | 79,341 | 189 |
| Cross-document synthesis | PASS | 35,199 ms | 79,342 | 1,482 |
| False premise correction | PASS | 8,956 ms | 79,345 | 278 |
| Exact figure recall | PASS | 8,245 ms | 79,336 | 298 |
| Client-facing, non-financial | PASS | 20,707 ms | 79,341 | 798 |
| **Totals** | | **136,922 ms** | **634,726** | **5,371** |

Failed: **Documented financial decision (cite)**

### Variance across the three runs

| | Run 1 | Run 2 | Run 3 |
|---|---|---|---|
| Pass rate | 7/8 | 8/8 | 7/8 |
| Total latency | 125,467 ms | 131,210 ms | 136,922 ms |
| Total input | 634,726 | 634,726 | 634,726 |
| Total output | 4,809 | 5,037 | 5,371 |

**Input tokens are identical across all three runs** (634,726 each). The context
is fixed, so input cost is perfectly predictable — the one genuine advantage of
the direct-context approach.

---

## Aggregate across all 24 calls

### Input tokens

| | Value |
|---|---|
| Mean | 79,340.8 |
| Worst case (max) | 79,346 |
| Min | 79,336 |
| Spread (max − min) | 10 tokens |

The 10-token spread is the question text alone. Everything else is fixed corpus.

### Latency

| | Value |
|---|---|
| Mean | 16,400 ms |
| Min | 2,730 ms |
| Max | 35,199 ms |
| Spread | 32,469 ms (12.9x) |

Latency tracks output length, not input — input is constant. The 2.7s minimum is
the refusal case (37–74 output tokens); the 35.2s maximum is cross-document
synthesis (1,482 output tokens).

### Cost

Bedrock cross-region rates for `us.anthropic.claude-sonnet-4-6`:
**$3.30/M input, $16.50/M output** (base $3.00/$15.00 + 10% cross-region surcharge,
applicable because the model ID carries the `us.` geo prefix).

| | Value |
|---|---|
| Mean input cost/call | $0.26182 |
| Mean output cost/call | $0.01046 |
| **Mean total cost/call** | **$0.27229** |
| Worst-case cost/call | $0.28629 |
| **Cost per 100 questions** | **$27.23** |
| Cost per 1,000 questions | $272.29 |

Input is **96.2%** of cost. Retrieval
attacks exactly this term.

### Context window

| | Value |
|---|---|
| Window (Sonnet 4.6) | 1,000,000 tokens |
| Mean consumed | 79,341 (7.93%) |
| Headroom | 920,659 tokens |
| Corpus growth before exhaustion | ~12.6x |

**The window is not the binding constraint.** At 7.9% consumed, the corpus could
grow roughly 12x before hitting the limit. The constraints that bite first are
cost and latency — and, as the eval shows, retrieval accuracy.

---

## Comparison against the V2 baseline in usage.db

Pre-expansion rows logged during V2, before the corpus grew:

| id | Question | Latency | Input | Output |
|---|---|---|---|---|
| 1 | (V2-era) | 22,117 ms | 7,486 | 1,016 |
| 2 | (V2-era) | 2,440 ms | 7,491 | 89 |

| Metric | V2 | V3 baseline | Delta |
|---|---|---|---|
| Input tokens/call | ~7,490 | 79,341 | +959.3% (**10.6x**) |
| Eval total input (8 calls) | 59,942 | 634,726 | +958.9% |
| Mean latency | 11,723 ms | 16,400 ms | +39.9% |
| Cost/call | $0.03314 | $0.27229 | +721.6% |
| Cost/100 questions | $3.31 | $27.23 | +721.6% |
| Context consumed | 0.75% | 7.93% | +958.9% |

**Input tokens rose 10.6x; cost per call rose 8.5x.** Cost rose less than tokens
because output length barely changed — output is question-driven, not corpus-driven.

---

## FINDING — eval regressed from 8/8 to 7/8, 8/8, 7/8

**This is a real regression caused by the corpus expansion, not run-to-run noise.**

Two of three runs failed one case each, both on the **citation check**, both with
the same mechanism:

| Run | Case | Expected | Model cited instead |
|---|---|---|---|
| 1 | Cross-document synthesis | `01_receiving_discrepancy_sop.md` | `SOP-REC-004` (6x) |
| 3 | Documented financial decision | `06_billing_dispute_policy.md` | `POL-FIN-003` (9x) |

Both failing answers cited **exclusively by document ID** and contained **zero**
filename citations. The answers were otherwise correct, well-grounded, and
correctly flagged for human review.

### Root cause

The 16 new documents each carry a `**Document ID:**` header and cross-reference
each other by ID (`SOP-REC-004`, `POL-FIN-003`, `FIN-RATE-ENT-NWP-2025`). At 7
documents this convention was faint. At 23 it is the dominant citation style in
context, and it now competes with the system prompt's instruction to cite the
filename.

**The model is following the corpus convention over the prompt instruction.**

### Why it matters for V3

1. **The eval's citation check is now measuring format compliance, not grounding.**
   Both failing answers cited the correct source document — in the wrong notation.
   A grader that fails a correct citation is measuring the wrong thing.
2. **This will confound the retrieval comparison.** If V3 shows 8/8 against this
   7/8-8/8 baseline, part of that delta could be citation-format luck rather than
   retrieval quality. The baseline is noisy in a way V2's was not.
3. **It is fixable three ways**, and the choice should be made before V3 runs:
   accept document IDs in the citation check; strengthen the prompt to require
   filenames explicitly; or strip `Document ID` headers from the corpus.

**No fix has been applied.** This document records the baseline as measured.

---

## Method notes and limitations

1. **Corpus token count is a chars/3.5 estimate** (77,339). Bedrock's actual
   tokenization reports 79,341 input tokens per call, which includes the
   1,454-char system prompt, document separators, and the question. The measured
   figure is the authoritative one for cost.
2. **Three runs is a small sample.** Two failures in three runs establishes the
   regression is real but not its rate. The underlying cause is deterministic
   (corpus convention); which case trips is stochastic.
3. **No prompt caching.** Bedrock supports prompt caching for this model (min
   1,024 tokens, 5-min and 1-hour TTL). A fixed 79K-token prefix is close to the
   ideal caching case and would cut input cost substantially. **This baseline does
   not use it**, so the cost figures represent the uncached worst case. Caching is
   a genuine alternative to retrieval and has not been evaluated.
4. **Latency excludes S3 document loading**, which is cached per-process in the
   app and per-run in the harness. Cold load adds roughly 2-3s.
5. **Cost rates are as supplied** ($3.30/$16.50 per M). Not independently verified
   against the Bedrock pricing page.

---

## Reproduce

```bash
./venv/Scripts/python.exe eval.py
```

Corpus state: 23 objects in `s3://yfh227-fulfillment-ops-docs`, matching `docs/`
at commit `0a2a649`.
