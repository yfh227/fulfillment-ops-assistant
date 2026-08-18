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
| `eval_roles.py` | Role-access harness — 8 questions × 4 roles × 2 modes. Grades access, not answer quality. |
| `make_auth_config.py` | Generates the gitignored `auth_config.yaml` with bcrypt-hashed test users. |
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
  cover X" appearing in a long, complete answer is a scope caveat, not a
  refusal. A phrase only counts when the answer is under 400 words.
- The refusal phrase list covers three grammatical shapes, because the model
  moves between them: negation on the documents ("the documents do not mention
  X"), negation on the subject ("there is no mention of X"), and negation on
  the model's own search ("I cannot find any policy that...").

Both rules were derived from sampled model output, not guessed. The thresholds
in `core.py` carry comments explaining the measurements behind them.

```bash
./venv/Scripts/python.exe eval.py
```

Prints a per-case table with latency, ends with `N/8 PASSED`, and exits `1` if
any case fails, so it can gate a build. Model output varies between runs — treat
a single result as a sample, not a verdict.

### Known limitations of refusal detection

The weakest part of the harness is the refusal check, and it is worth stating
plainly what it can get wrong.

**It is substring matching over prose.** The model writes an answer in natural
language and a hand-maintained phrase list decides whether that answer counts as
a refusal. That has failed in both directions on real output:

- **False negative.** Correcting a false premise, the model wrote *"I cannot find
  any such policy in the documents provided"* and never used a listed phrase.
  A textbook refusal scored as a non-refusal. Fixed by adding `cannot find any`,
  which appeared in 9 of 10 sampled answers for that case.
- **False positive.** A complete 721-word draft opened with *"I don't know which
  tier this client is or how severe the damage is"* — a clarifying aside, not a
  refusal — and the rule counted it. Fixed by removing the head-position clause.

Both were found by sampling, not by reasoning about the rule.

**The current rule is length-only: a refusal phrase counts if the answer is under
400 words.** That threshold comes from a measured separation gap, not intuition:

| | Word range |
|---|---|
| Genuine refusals | 26–259 |
| *gap: 225 words* | |
| Complete answers containing a refusal phrase | 484–721 |

400 sits 141 words above the longest measured refusal and 84 below the shortest
false positive.

**Known blind spot: a refusal longer than 400 words would be missed.** The
longest measured is 259, so there is headroom, but a case that produces a long
partial refusal — extensive explanation of what the documents *do* cover before
admitting a gap — would score as a non-refusal. No current case does this.

**The more robust fix is a structured self-report from the model rather than
pattern-matching its prose** — asking it to emit a machine-readable field
declaring whether it refused, and grading that. This removes the phrase list
entirely and with it both failure modes above. The cost is an extra call per
case if the self-report is graded separately, or a change to the user-facing
answer format if the field is embedded in the answer itself. **Evaluated, not
built** — the current rule is clean across the whole evidence base, and the
substring approach keeps scoring deterministic, which LLM-based grading does
not.

### Evidence base

[eval_corpus.json](eval_corpus.json) holds 40 stored answers across cases 2, 3,
4, 6 and 8 — both the refusals that must be caught and the complete answers that
must not be. Every rule change and phrase addition above was tested against it
before shipping.

Each entry is tagged with `regime`: `v2-7docs-original` (18 answers, captured
against the 7-document corpus with the pre-hardening prompt) and
`v3-23docs-hardened` (22 answers, current corpus and prompt). The tagging matters
because a candidate phrase validated only against old-regime answers proves
little about current behaviour — the corpus and the system prompt have both
changed since.

Keeping the file in the repo is what makes testing a new candidate free: it
costs no Bedrock calls.

## Role-based access

Until V4 every question saw every document: a billing analyst asking about
warehouse procedures got the same full corpus as an account manager asking about
a client dispute. Locking down the S3 bucket is infrastructure security — nobody
outside the app can read the documents. This is application-level governance:
what a given *user* may ask for once they are inside.

Login is handled by `streamlit-authenticator`, which stores the signed-in user's
role in session state. Everything downstream reads a role-filtered document list.

### The three roles

The mapping was derived from each document's own header metadata — `Owner`,
`Distribution`, `Attendees`, `Negotiated by` — rather than from topic. The full
derivation, including which assignments are metadata-backed and which are
judgment calls, is in
[v4_role_based_access.md](v4_role_based_access.md).

**Billing Analyst — 7 documents**

`00_company_profile.md` · `02_billing_rate_card.md` ·
`06_billing_dispute_policy.md` · `10_incident_2026-01-22_integration_failure.md` ·
`11_incident_2026-03-08_mixed_client_inventory.md` ·
`19_inventory_accuracy_report_2026_q2.md` ·
`22_inventory_accuracy_report_2026_q3.md`

**Warehouse Lead — 12 documents**

`00_company_profile.md` · `01_receiving_discrepancy_sop.md` ·
`04_cycle_count_policy.md` · `07_reno_putaway_sop.md` ·
`08_peak_season_operating_procedures.md` ·
`09_incident_2025-12-01_wms_outage.md` ·
`10_incident_2026-01-22_integration_failure.md` ·
`11_incident_2026-03-08_mixed_client_inventory.md` ·
`19_inventory_accuracy_report_2026_q2.md` ·
`20_new_hire_training_certification.md` ·
`21_putaway_sop_richmond_columbus.md` ·
`22_inventory_accuracy_report_2026_q3.md`

**Account Manager — 13 documents**

`00_company_profile.md` · `03_escalation_matrix.md` ·
`05_client_onboarding_checklist.md` · `09_incident_2025-12-01_wms_outage.md` ·
`10_incident_2026-01-22_integration_failure.md` ·
`11_incident_2026-03-08_mixed_client_inventory.md` ·
`12_onboarding_case_enterprise_northwind.md` ·
`13_onboarding_case_growth_lumen.md` · `15_carrier_management_policy.md` ·
`16_vendor_and_temporary_labour_policy.md` ·
`17_enterprise_rate_schedule_northwind.md` ·
`18_growth_rate_schedule_lumen.md` ·
`20_new_hire_training_certification.md`

**admin — all 23.** An all-access identity for regression runs, not a content
role; the mapping is not defined against it.

Three properties are deliberate rather than incidental:

- **`00_company_profile.md` is universal** — the only document all three roles
  share by design.
- **`14_onboarding_case_standard_fernpost.md` belongs to no role.** The document
  states it has no named Account Manager (standard tier, pooled queue), so
  assigning it to Account Manager would assert something the document denies.
  It is visible only to admin, and is the test case where access denial and
  genuine absence can be told apart with certainty.
- **Billing cannot see either rate schedule.** `17` and `18` record who
  negotiated them — Senior Account Manager and Account Manager — and that stated
  ownership governs, not the fact that the content is rate data. A billing
  analyst asking about negotiated client rates is denied. This is a decision,
  not an oversight.

An unrecognised role **fails closed**: `get_documents_for_role()` returns the
empty set, so a typo'd or renamed role sees nothing rather than everything.

### Enforcement holds in both modes

Direct context and retrieval are restricted separately, because they draw from
different places — the document list and the embedded index. Filtering only the
first would leak the whole corpus whenever `use_retrieval` is `True`.

The retrieval candidate set is cut **before** ranking, never after.
Post-filtering would leave the full corpus competing for the K slots, so a role
would silently receive fewer than K chunks whenever a document it cannot see
outranked one it can — the restriction would look correct while quietly
degrading recall.

### Access denial vs. genuine "not in any document"

These are different situations and must not read the same way:

| Situation | Response |
|---|---|
| The corpus covers this, but not in your documents | *"That's outside what a Billing Analyst has access to in this system."* |
| The corpus does not cover this at all | The ordinary "I don't know" refusal |

A pre-check in `ask()` decides which, before any context is assembled and before
Claude is called — so a denial costs no model call. It consults the embedded
index rather than whichever context was assembled, which is why it gives the
same verdict in both modes.

**The rule: deny when the *best* relevant evidence is forbidden, not when *all*
of it is.** An earlier version denied only when nothing permitted was relevant,
and that was too weak — an account manager asking about the Fernpost onboarding
case surfaced the Northwind and Lumen case notes, which are permitted and clear
the floor, so the question read as allowed and would have been answered about
one client out of another client's file. Adjacent material is not the answer.

#### `DENIAL_FLOOR = 0.48`

Denial needs a higher bar than retrieval. `RELEVANCE_FLOOR` (0.30) answers *"is
this chunk worth putting in context"*, which is the wrong question for access —
*"does the answer actually live here"*. Reusing it told a billing analyst asking
about parental leave, absent from the corpus entirely, that the topic was outside
their access, because `16_vendor_and_temporary_labour_policy.md` scored 0.4524 on
the word "labour" alone. Claiming information exists and is withheld, when it
does not exist, is its own kind of dishonesty.

Measured over 10 genuinely-absent questions and the 22 role/question denial
decisions in `eval_roles.py`:

| | Top-1 similarity |
|---|---|
| Absent from corpus | 6 of 10 clear nothing at all; the 4 that clear `RELEVANCE_FLOOR` peak at **0.4524** |
| *gap: 0.0524* | |
| True denials | **0.5048** (standard-tier rate card) rising to 0.7130 (escalation matrix) |

0.48 sits near the centre of that gap: 0.0276 above the highest score any absent
question reached, 0.0248 below the lowest a real denial needed. Same derivation
style as `RELEVANCE_FLOOR` and `REFUSAL_MAX_WORDS` — a measured separation, not
an intuition.

**This threshold governs which message is shown, never what is retrievable.**
Document filtering in `get_documents_for_role()` and `retrieve_context()` is
unconditional in both modes and does not consult `DENIAL_FLOOR` at all. A
misjudgement here costs accuracy of explanation, never access.

### Verification

```bash
./venv/Scripts/python.exe eval_roles.py --mode both
```

`eval_roles.py` grades *access*, where `eval.py` grades answer quality. Expected
outcomes are written out per role rather than derived from `ROLE_DOCUMENTS`, so a
wrong mapping cannot satisfy the test by agreeing with itself.

**64/64 passing** — 8 questions × 4 roles × 2 modes, with real question
embeddings and real Claude calls:

- **Zero restricted-document citations** across all 64 runs.
- **Denials short-circuit before any model call** — 34 calls for 64 runs; every
  denial returned the exact expected message with no Bedrock request.
- The Fernpost question is denied for all three content roles and answered for
  admin.
- A genuinely-absent question refuses for every role, admin included — never the
  access message.

One eval-design note worth keeping: `ANSWER` cases are graded on access
(reached the model, cited nothing restricted), not on completeness. Under
retrieval the model self-reports `REFUSED: yes` while answering substantively —
measured at 4 of 5 runs on the Reno putaway question against 0 of 5 in direct
context, because retrieval shows it fragments of a long SOP rather than the whole
document. Failing those would be grading the known direct-vs-retrieval difference
as an access bug.

### Setup

Two generated files are gitignored and absent from a fresh checkout.

**`auth_config.yaml`** holds the bcrypt-hashed credentials. Generate it:

```bash
./venv/Scripts/python.exe make_auth_config.py
```

That writes one test user per role plus an all-access admin, prints the random
passwords **once**, and stores them nowhere in plaintext. Lost passwords mean
re-running with `--force`, which mints new ones. The app refuses to start without
this file and says so.

**`vector_index.npz`** is built by `embed_chunks.py`. The access pre-check now
depends on it in **both** modes, not just retrieval — direct context previously
made no embedding call and now makes one per question.

**Without the index, enforcement holds but the explanation degrades.** Document
filtering has already happened and `retrieve_context()` still restricts its
candidates, so no restricted content is reachable. What is lost is the *message*:
a restricted question falls back to the ordinary "I don't know" refusal instead
of the access notice, which is exactly the silent failure this part exists to
remove. Rebuild the index rather than run without it.

### Known-marginal case

`eval.py`'s **"Mixed coverage"** case fails intermittently on the `REFUSED:`
self-report. The model answers the documented half, explicitly states the late
fee is not covered, flags for review — then self-reports `REFUSED: no`, where
rule 5 specifies `yes`.

**This is independent of V4 on structural grounds.** `eval.py:201` calls `ask()`
with no `role` argument, so `role=None`, so the access pre-check guard is false
and `retrieve_context()` is unrestricted. The code path is identical before and
after V4 — the pre-V4 `ask()` has no `role` parameter at all.

It tracks answer length, consistent with `REFUSAL_MAX_WORDS`: observed passing
runs were 68–113 words, the failing run 200+ with extensive multi-document
citation.

**Not empirically confirmed.** A 5-run check at the pre-V4 commit `ae347dc`
returned 0 failures in 5, against 1 failure in 6 observations on `main` — but 5
samples cannot detect a roughly 1-in-6 event. If the rate were identical at both
commits, the chance of seeing zero failures in 5 runs is (5/6)⁵ ≈ 40%. That check
discriminated nothing, and is reported here as inconclusive rather than as
support. Settling it empirically would need roughly 25–30 samples per commit.

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
10.6x increase in what every call carries**. By default the assistant passes the
whole corpus as context on every question rather than retrieving against it —
retrieval exists but is off by default. That decision was measured rather than
assumed, and the measurements are committed:

- [baseline_direct_context.md](baseline_direct_context.md) — the uncached "before"
- [baseline_prompt_caching.md](baseline_prompt_caching.md) — caching measured against it
- [retrieval_vs_caching.md](retrieval_vs_caching.md) — retrieval built and tuned
  against both

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

### Retrieval, measured

Retrieval was subsequently built and tuned against the eval. At K=14 with a
0.30 relevance floor it costs **$1.87 per 100 questions against $4.86** for
prompt-cached direct context, and runs 39% faster.

It is **not** the default. `use_retrieval` defaults to `False`, because the
comparison is closer than the cost figures suggest: direct context cannot fail
to see a relevant document, and retrieval can. Full curve, the case-1
check-migration finding, and the result that the relevance floor — not K —
bounds context size are in
[retrieval_vs_caching.md](retrieval_vs_caching.md).

### Current position

**Prompt caching is enabled by default.** `core.ask(..., use_cache=True)` is the
default path, so the app and the harness both cache unless told otherwise. The
uncached baseline no longer depends on the live setting — both baselines are
committed to this repo, and `EVAL_PROMPT_CACHE=0` reproduces the uncached figures
on demand:

```bash
EVAL_PROMPT_CACHE=0 ./venv/Scripts/python.exe eval.py
```

**Retrieval is built and tuned, but is not the default** — `use_retrieval`
defaults to `False`. See *Retrieval, measured* above for the figures and the
reasoning, and *Role-based access* for how the restriction is enforced on the
retrieval path as well as on direct context.
