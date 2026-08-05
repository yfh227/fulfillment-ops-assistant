# Retrieval vs Prompt Caching

> Measured comparison of the two architectures, and what tuning K actually did.
> Companion to [baseline_direct_context.md](baseline_direct_context.md) and
> [baseline_prompt_caching.md](baseline_prompt_caching.md).

**Corpus:** 23 documents, 363 chunks, ~77,000 tokens
**Model:** `us.anthropic.claude-sonnet-4-6` · **Embeddings:** `amazon.titan-embed-text-v2:0`, 1024d normalized
**Method:** 8-case eval, three runs per configuration, 120 calls for the sweep

---

## Verdict

**Retrieval wins on cost and latency. Direct context wins on completeness.**

| | Direct, cached | Retrieval, K=14 |
|---|---|---|
| Cost per 100 questions | $4.86 | **$1.87** |
| Input tokens per call | 79,667 | **3,194** |
| Latency | 15,352 ms | **9,295 ms** |
| Eval, three runs | 7/8, 6/8, 5/8 | **8/8, 7/8, 8/8** |

Retrieval is **62% cheaper and 39% faster**, and after the case 1 expectation
fix it is also the more *stable* configuration. That last part was not the
expected result and is explained below.

**But the caveat that matters:** retrieval can only answer from what it
retrieves. Direct context cannot fail to see a relevant document; retrieval
can, and does. The eval measures whether the answer is grounded, cited and
correctly flagged — it does not measure what a question would have needed that
retrieval never surfaced.

---

## The full curve

K = 6, 10, 14, 18, 24. Three runs each. Query embeddings computed once per
question and reused across every K, so the curve reflects K alone.

| K | Pass (3 runs) | In tok | Out tok | Latency | $/100 | vs cached | chunks | docs |
|---|---|---|---|---|---|---|---|---|
| 6 | 6 / 6 / 8 | 1,684 | 345 | 6,640 ms | $1.13 | −77% | 4.5 | 2.0 |
| 10 | 6 / 5 / 5 | 2,509 | 425 | 7,588 ms | $1.53 | −69% | 7.5 | 2.8 |
| **14** | **7 / 7 / 7** | 3,194 | 494 | 9,295 ms | **$1.87** | −62% | 10.5 | 3.9 |
| 18 | 7 / 7 / 6 | 3,552 | 487 | 10,070 ms | $1.98 | −59% | 12.0 | 4.4 |
| 24 | 8 / 6 / 6 | 4,094 | 520 | 11,618 ms | $2.21 | −55% | 14.2 | 4.9 |
| *direct, uncached* | — | 79,667 | — | 15,352 ms | $27.20 | +460% | — | — |
| *direct, cached* | — | 79,667 | — | 15,352 ms | $4.86 | — | — | — |

*(Pass rates above use the pre-fix case 1 expectation. See the correction below.)*

**The curve is not monotonic.** K=10 is worse than K=6. Two runs reached 8/8 —
K=6 run 3 and K=24 run 1 — and neither repeated. K=14 was the only K where all
three runs agreed, which is why it was chosen: consistency, not peak score.

### Per-case pass rate across the sweep

| Case | K=6 | K=10 | K=14 | K=18 | K=24 |
|---|---|---|---|---|---|
| Documented internal process | 1/3 | 0/3 | 0/3 | 0/3 | 1/3 |
| Documented financial decision | 3/3 | 3/3 | 3/3 | 3/3 | 2/3 |
| Topic absent from documents | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 |
| Mixed coverage | 3/3 | 3/3 | 3/3 | 3/3 | 2/3 |
| Cross-document synthesis | 3/3 | 1/3 | 3/3 | 2/3 | 3/3 |
| False premise correction | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 |
| Exact figure recall | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 |
| Client-facing, non-financial | 1/3 | 0/3 | **3/3** | 3/3 | 3/3 |

**Case 8 behaved exactly as hypothesised:** starved at K=6–10, stable from
K=14 onward. It is the clearest evidence that K was genuinely too low.

**Cases 2 and 4 regress at K=24.** More retrieved context produces more
caveats, and more caveats produce more `REFUSED: yes`. Raising K past 14 makes
the assistant hedge, not improve.

---

## Case 1: the check migrated rather than clearing

The hypothesis was that case 1 fails because a 13-chunk SOP cannot survive
K=6. **That was wrong, and the way it was wrong is the useful finding.**

Case 1 never stabilised at any K: 1/3, 0/3, 0/3, 0/3, 1/3. But the *failing
check moved*:

| K | Failing check |
|---|---|
| 6, 10 | `flag`, `refuse` |
| 14, 18, 24 | `flag` only |

Raising K **did** fix the fragmentation. At K=6 the model wrote *"The documents
provided do not include Step 2. I don't know what it contains."* — a correct
refusal on a shredded procedure. From K=14 the procedure arrives intact and the
refusal clears.

What replaced it: with more of the SOP present, the model sees the client
notification requirement and the 48-hour carrier claim window, and rule 4 fires
on client- and money-adjacent material. **The model was right and the test was
wrong.** The expectation has been corrected to `should_flag: True`.

**Raising K cannot fix case 1, because more context is what causes the second
failure.** A test that fails in opposite directions at opposite ends of a
parameter range is a test-definition problem, not a tuning problem.

---

## The correction, and the regression it caused

Setting `should_flag: True` fixed retrieval and **broke direct context**:

| Regime | Case 1 flag emitted | Eval, three runs |
|---|---|---|
| Retrieval, K=14 | 2 of 3 runs | 8/8, 7/8, 8/8 |
| Direct context, cached | **0 of 3 runs** | 7/8, 6/8, 5/8 |

The model **never** flags case 1 when it has the whole corpus, and usually does
when it has 14 retrieved chunks. Same question, same rule 4, opposite behaviour.

The plausible reading: with the full corpus the model treats a receiving-process
question as internal-procedure lookup, and the client-notification step is one
line among thousands. Under retrieval those chunks are a large fraction of
everything it can see, so they weigh more. **This is unverified** — it is an
inference from behaviour, not a measurement.

**No single `should_flag` value is correct for both regimes.** The current value
is right for retrieval, which is the configuration being tuned, and wrong for
direct context. Options not taken: making the expectation regime-dependent,
which hides the disagreement; or rewording the question until both regimes
agree, which tunes the test to the model.

Direct context also showed unrelated instability in the same runs — case 2
failed `refuse` twice and case 4 once, all self-reporting a gap on questions the
corpus answers. Under retrieval both were 3/3. This was **not** caused by the
expectation change and is discussed under limitations.

---

## The relevance floor bounds context, not K

There is **no cost crossover** within reach. Matching prompt-cached direct
context would require **12,457 input tokens**; K=24 reaches 4,094.

The reason is structural: the 0.30 relevance floor caps how much context K can
deliver. Measured by retrieving all 363 chunks and counting how many clear the
floor:

| Case | Chunks above 0.30 |
|---|---|
| Cross-document synthesis | **32** (ceiling) |
| Documented internal process | 26 |
| Documented financial decision | 24 |
| Mixed coverage / Exact figure recall / Client-facing | 14 |
| Topic absent from documents | **0** |
| False premise correction | **0** |

**Raising K past ~32 returns nothing for any question in the eval.** Every
additional chunk scores below the floor and is discarded. Retrieval therefore
beats cached direct context at every reachable K, and the crossover is
unreachable without lowering the floor.

The two zero-chunk cases are not a defect. Those are the questions the corpus
does not answer, and returning nothing is how they get refused correctly —
the floor is doing guardrail work, not just cost work.

**This reframes the tuning question.** The floor, not K, is now the
consequential parameter: it sets the context ceiling *and* the refusal
behaviour for out-of-corpus questions. K only matters below the ceiling.

---

## Which architecture wins on what

| | Winner | Margin |
|---|---|---|
| Cost per 100 questions | Retrieval | $1.87 vs $4.86 — **62% cheaper** |
| Latency | Retrieval | 9,295 ms vs 15,352 ms — **39% faster** |
| Eval stability (current expectations) | Retrieval | 8/7/8 vs 7/6/5 |
| Completeness guarantee | **Direct context** | cannot fail to see a document |
| Predictable cost | **Direct context** | fixed input; retrieval varies 734–6,468 |
| Implementation cost | **Direct context** | one `cachePoint` vs chunker, embedder, index, floor, K |
| Failure mode when wrong | **Direct context** | degrades visibly; retrieval fails silently |

**The last row is the one that should decide it.** When direct context is
wrong, the model had everything and reasoned poorly — visible in the answer.
When retrieval is wrong, the model answers confidently from an incomplete set
with no signal anything is missing. Case 1 at K=6 is the benign version: the
model noticed and said so. Nothing guarantees it always will.

**Recommendation: retrieval at K=14 is the better default on measured metrics,
but the two are close enough that the choice should rest on operating
conditions rather than the numbers.** Prompt caching already removed the cost
argument that motivated retrieval (see
[baseline_prompt_caching.md](baseline_prompt_caching.md)); retrieval improves
on it by a further $3 per 100 questions. At current volume that is not the
deciding factor. Corpus scale is: retrieval becomes necessary, not merely
cheaper, when the corpus outgrows the context window — roughly 12x from here.

---

## Limitations

1. **Three runs per configuration is a small sample.** Several cases moved
   between 2/3 and 3/3 across the sweep. The curve's shape is reliable; any
   individual cell is not.
2. **Direct context is currently less stable than retrieval on this eval**, on
   the `refuse` check for cases 2 and 4. Both self-report a gap on questions
   the corpus answers. That is a real behaviour worth investigating and it is
   not explained here.
3. **The eval does not measure retrieval recall.** Every case is graded on the
   answer, not on whether retrieval surfaced the right chunks. A case could
   pass while retrieval missed a document that would have changed the answer.
   Testing that needs cases built around documents retrieval is likely to miss.
4. **K=14 was chosen for consistency, not peak score.** K=6 and K=24 each hit
   8/8 once. With three runs, "most consistent" and "luckiest" are not reliably
   distinguishable.
5. **The floor of 0.30 was set once and never tuned.** It is now the parameter
   that bounds context size and drives out-of-corpus refusals, and it has had
   far less scrutiny than K.
6. **Costs use $3.30/M input and $16.50/M output.** Embedding cost is excluded
   — 363 chunks cost $0.0016 to index once, and a query embedding is ~17 tokens.

Limitation 5 is the one most likely to matter next.

---

## Reproduce

```bash
EVAL_RETRIEVAL=1 ./venv/Scripts/python.exe eval.py
```

```bash
./venv/Scripts/python.exe tune_k.py
```

Per-run data in `tuning_k_results.json`. Retrieval defaults to K=14 with a 0.30
floor, set in `core.py`.
