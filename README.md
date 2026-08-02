# Fulfillment Ops Assistant

A Streamlit app that answers warehouse and account-team questions from Meridian's
operating documents, using Claude on Amazon Bedrock. Answers are grounded in the
markdown SOPs stored in S3 — the assistant is instructed to work only from those
documents, cite the file it drew from, say "I don't know" when the documents do
not cover a question, and flag anything client-facing or money-related for human
review.

## Layout

| File | Purpose |
| --- | --- |
| `core.py` | All logic: Bedrock/S3 clients, document loading, the system prompt, `ask()`, and answer analysis. No Streamlit dependency. |
| `app.py` | Streamlit UI only. |
| `eval.py` | Evaluation harness — 8 test cases, mechanically scored. |
| `usage_log.py` | SQLite logging of every question asked. |
| `stats.py` | Reporting queries and the adoption summary generator. |

`core.py` deliberately imports no Streamlit, so the harness and reporting tools
can import it without starting a web server.

## Setup

```bash
python -m venv venv
./venv/Scripts/python.exe -m pip install -r requirements.txt
```

Put AWS credentials in `.streamlit/secrets.toml` (gitignored):

```toml
AWS_ACCESS_KEY_ID = "..."
AWS_SECRET_ACCESS_KEY = "..."
AWS_DEFAULT_REGION = "us-east-1"
```

Run the app:

```bash
./venv/Scripts/streamlit.exe run app.py
```

## Evaluation harness

`eval.py` checks that the assistant's guardrails actually hold. It runs 8 cases
covering documented lookups, questions the documents do not answer, partial
coverage, cross-document synthesis, a false premise, exact figure recall, and a
client-facing drafting request.

Each answer is scored on four checks:

- **Citation** — the expected source filename appears in the answer.
- **Refusal** — a refusal signal is present, or absent, matching what the case
  expects. Checked in both directions: refusing a question the documents *do*
  answer is a failure too.
- **Review flag** — the `NEEDS HUMAN REVIEW` marker appears when it should.
- **Exact content** — a required literal string (e.g. a rate) is present.

Scoring is **mechanical substring matching, not LLM grading**, so a given answer
always produces the same verdict. Two details are load-bearing:

- Refusal detection is *length-aware*. A phrase like "the documents do not
  cover X" appearing deep in a long, complete answer is a scope caveat, not a
  refusal. A phrase only counts when it appears near the start of the answer or
  the answer is short overall.
- The refusal phrase list covers two grammatical shapes, because the model
  alternates between them: negation on the documents ("the documents do not
  mention X") and negation on the subject ("there is no mention of X").

Both rules were derived from sampled model output, not guessed. The thresholds
in `core.py` carry comments explaining the measurements behind them.

```bash
./venv/Scripts/python.exe eval.py
```

Prints a per-case table with latency, ends with `N/8 PASSED`, and exits `1` if
any case fails, so it can gate a build. Model output varies between runs — treat
a single result as a sample, not a verdict.

## Usage logging

Every question is written to `usage.db` (SQLite, gitignored) as one row,
including calls that fail. Captured per row:

| Column | Notes |
| --- | --- |
| `timestamp`, `question`, `answer` | |
| `latency_ms`, `input_tokens`, `output_tokens` | From the Bedrock response |
| `cited_docs` | Only filenames that actually exist in the bucket — a hallucinated filename is never counted |
| `review_flagged`, `refused` | Computed by the same `core.py` functions `eval.py` scores with, so logging and evaluation cannot drift |
| `error` | Exception text on failure; result columns stay NULL |
| `feedback`, `feedback_note` | Set by the 👍/👎 buttons under each answer |

Failed calls are logged rather than dropped, and are excluded from guardrail and
latency figures — averaging a NULL latency as zero would make an outage look
fast.

The app sidebar shows live totals: questions asked, flag rate, refusal rate, and
average latency.

## Reporting

```bash
./venv/Scripts/python.exe stats.py
```

Prints volume and tokens by day, guardrail rates, most-cited documents,
latency spread, error count, and the feedback split — then writes
`adoption_summary.md`.

That file is the short, non-technical brief: questions answered, flag rate,
refusal rate, feedback split, and the three most-referenced documents. Regenerate
it by re-running `stats.py`.

Pass a path to report on a different database:

```bash
./venv/Scripts/python.exe stats.py path/to/other.db
```

## Cost and architecture decisions

The reference corpus grew from 7 documents to 23 — **7,291 to 77,339 tokens, a
10.6x increase in what every call carries**. The assistant passes the whole
corpus as context on every question; there is no retrieval layer. That decision
was measured rather than assumed, and the measurements are committed:

- [baseline_direct_context.md](baseline_direct_context.md) — the uncached "before"
- [baseline_prompt_caching.md](baseline_prompt_caching.md) — caching measured against it

### What it costs

| | Cost per 100 questions | Eval |
|---|---|---|
| Direct context, uncached | **$27.20** | 8/8 |
| Direct context, prompt caching | **$4.86** | 8/8 |

Both rows use the same system prompt, so caching is the only variable. The
direct-context baseline file records **$27.23** rather than $27.20 because it was
captured before a later fix to the citation rule lengthened the prompt by 165
tokens; the difference is the prompt, not the method.

Bedrock prompt caching removed **82% of the cost for a one-line change** — a
`cachePoint` after the document context block — with no measured quality loss
across three runs in each condition. Billed-at-full-rate input fell from 79,506
tokens per call to about 21, the question text alone.

The worst case is bounded and cheap to reason about. If the cache were written on
every call and never hit at all, the cost would be **$33.77/100** versus $27.20
uncached — a 24% penalty, not a cliff. At any cadence above one question per five
minutes the cache stays warm and the figure sits near $4.86. Caching is enabled
per call via `core.ask(..., use_cache=True)`; the harness honours
`EVAL_PROMPT_CACHE=1`.

### What this means for retrieval

**Caching removed the cost argument for building retrieval.** Retrieval attacks
input tokens, and caching has already reduced billed input by 99.97%. Output is
now 20% of the bill (up from 4%), and no retrieval strategy reduces output — that
is a floor neither approach crosses.

**The remaining trigger for retrieval is corpus scale, not cost.** At 77,339
tokens the corpus consumes **7.93% of Sonnet 4.6's 1M context window**. The corpus
could grow roughly **12x** before the window binds. At that point retrieval stops
being an optimization and becomes necessary. Until then it is optional.

**Retrieval also adds a failure mode that direct context structurally cannot
have.** When the whole corpus is in context, the model may reason poorly, but it
cannot fail to see a document that would have answered the question. Retrieval
introduces exactly that: retrieve the wrong documents and the model answers
confidently from an incomplete set, with no signal that anything is missing. The
grounding rules in the system prompt do not protect against this — the model has
no way to know what it was not shown. Adopting retrieval would require new eval
cases measuring retrieval quality itself, separate from the eight that measure
answer quality.

### Current position

**Prompt caching is enabled by default.** `core.ask(..., use_cache=True)` is the
default path, so the app and the harness both cache unless told otherwise. The
uncached baseline no longer depends on the live setting — both baselines are
committed to this repo, and `EVAL_PROMPT_CACHE=0` reproduces the uncached figures
on demand:

```bash
EVAL_PROMPT_CACHE=0 ./venv/Scripts/python.exe eval.py
```

No retrieval layer has been built.
