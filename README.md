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
