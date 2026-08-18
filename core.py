"""Core logic for the fulfillment ops assistant.

Deliberately free of any Streamlit dependency, so it can be driven from
scripts, tests, or a different front end. Credentials are passed in rather
than read from Streamlit secrets; when omitted, boto3's default credential
chain applies.
"""

import re
import time

import boto3

AWS_REGION = "us-east-1"
# Geo (US) cross-region inference profile ID — keeps data in US/Canada regions.
MODEL_ID = "us.anthropic.claude-sonnet-4-6"

DOCS_BUCKET = "yfh227-fulfillment-ops-docs"

SYSTEM_PROMPT = """You are an internal operations assistant for a third-party \
logistics (3PL) fulfillment company. You answer questions from the warehouse \
and account teams using ONLY the reference documents provided below.

Rules you must follow on every answer:

1. GROUNDING. Answer only from the provided documents. Do not use outside \
knowledge, do not infer policy that is not written down, and do not fill gaps \
with what is typical in the industry. If the documents state something, that \
is the answer even if it seems unusual.

2. CITATION. Cite the document filename you drew each part of your answer \
from, e.g. "(02_billing_rate_card.md)". If you combine several documents, cite \
each one at the point you use it.

   The citation MUST be the .md filename shown in the document separator, and \
never the document's internal identifier. The documents carry internal IDs in \
their headers (for example "Document ID: POL-FIN-003") and refer to each other \
by those IDs throughout. Those IDs are content, not citations. Citing \
"POL-FIN-003" or "SOP-REC-004" instead of "06_billing_dispute_policy.md" or \
"01_receiving_discrepancy_sop.md" is wrong, even though the surrounding \
documents cite each other that way. Follow this instruction over the \
convention you observe in the documents. You may mention an internal ID in \
your prose, but every citation must still carry the .md filename.

3. ADMITTING GAPS. If the documents do not cover the question, or cover it \
only partially, say "I don't know" plainly and state what is missing. A \
partial answer must clearly separate what the documents support from what they \
do not. Never guess to seem helpful.

4. HUMAN REVIEW FLAG. If the question touches anything client-facing (external \
communications, commitments to a client, service credits, onboarding promises) \
or anything money-related (billing, rates, invoices, disputes, refunds, \
charges), end your response with a clearly marked line:

   ⚠️ NEEDS HUMAN REVIEW — <one line on why>

   Apply this whenever money or a client is involved, even if the documents \
answer the question fully and even if you are confident. Err toward flagging.

5. SELF-REPORT. Make the very last line of your response exactly one of:

   REFUSED: yes
   REFUSED: no

   Answer **yes** if any part of the question could not be answered from the \
documents — including when you answered part of it and had to state that the \
rest is not covered, and including when you corrected a false premise because \
the documents do not support it.

   Answer **no** when the documents answered what was actually asked. Noting \
in passing what the documents happen not to contain, or which details a \
decision would still depend on, does not make it a yes if you answered the \
question. The test is whether the question was answered, not whether you \
added a caveat.

   This line is read by an automated check. It must be the final line, on its \
own, with no other text after it."""


# --------------------------------------------------------------------------
# Roles
#
# Canonical role identifiers. Defined here because three separate things need
# to agree on them - the auth config that assigns a role to a user, the app
# that reads it back out of session state, and the role-to-document mapping.
# Two copies of a role name drift the moment either one is edited, and the
# failure is silent: a typo'd role matches no documents and simply sees
# nothing, which looks identical to a role that is legitimately restricted.
# --------------------------------------------------------------------------

ROLE_BILLING = "billing_analyst"
ROLE_WAREHOUSE = "warehouse_lead"
ROLE_ACCOUNT = "account_manager"
ROLE_ADMIN = "admin"

# Admin is deliberately excluded: it is an all-access testing identity, not a
# role the document mapping is defined against.
CONTENT_ROLES = (ROLE_BILLING, ROLE_WAREHOUSE, ROLE_ACCOUNT)
ROLES = CONTENT_ROLES + (ROLE_ADMIN,)

# The role-to-document mapping, derived from each document's own header
# metadata (Owner, Distribution, Attendees, Negotiated by) rather than from
# topic. The full derivation, including which assignments are metadata-backed
# and which are judgment calls, is in v4_role_based_access.md - that file is
# the source of truth and this dict must match its table.
#
# 14_onboarding_case_standard_fernpost.md appears in no list on purpose. It
# states it has no named Account Manager, so it belongs to no role in this
# model, and it is the deliberate access-denied test case for all three.
ROLE_DOCUMENTS = {
    ROLE_BILLING: frozenset({
        "00_company_profile.md",
        "02_billing_rate_card.md",
        "06_billing_dispute_policy.md",
        "10_incident_2026-01-22_integration_failure.md",
        "11_incident_2026-03-08_mixed_client_inventory.md",
        "19_inventory_accuracy_report_2026_q2.md",
        "22_inventory_accuracy_report_2026_q3.md",
    }),
    ROLE_WAREHOUSE: frozenset({
        "00_company_profile.md",
        "01_receiving_discrepancy_sop.md",
        "04_cycle_count_policy.md",
        "07_reno_putaway_sop.md",
        "08_peak_season_operating_procedures.md",
        "09_incident_2025-12-01_wms_outage.md",
        "10_incident_2026-01-22_integration_failure.md",
        "11_incident_2026-03-08_mixed_client_inventory.md",
        "19_inventory_accuracy_report_2026_q2.md",
        "20_new_hire_training_certification.md",
        "21_putaway_sop_richmond_columbus.md",
        "22_inventory_accuracy_report_2026_q3.md",
    }),
    ROLE_ACCOUNT: frozenset({
        "00_company_profile.md",
        "03_escalation_matrix.md",
        "05_client_onboarding_checklist.md",
        "09_incident_2025-12-01_wms_outage.md",
        "10_incident_2026-01-22_integration_failure.md",
        "11_incident_2026-03-08_mixed_client_inventory.md",
        "12_onboarding_case_enterprise_northwind.md",
        "13_onboarding_case_growth_lumen.md",
        "15_carrier_management_policy.md",
        "16_vendor_and_temporary_labour_policy.md",
        "17_enterprise_rate_schedule_northwind.md",
        "18_growth_rate_schedule_lumen.md",
        "20_new_hire_training_certification.md",
    }),
}


def permitted_sources(role: str) -> frozenset | None:
    """Filenames a role may see. None means unrestricted.

    Only ROLE_ADMIN is unrestricted. An unrecognised role gets the empty set
    rather than everything - this fails closed, so a typo'd or renamed role
    sees nothing instead of the whole corpus.
    """
    if role == ROLE_ADMIN:
        return None
    return ROLE_DOCUMENTS.get(role, frozenset())


def get_documents_for_role(role: str, all_docs: list) -> list:
    """Filter (filename, text) pairs down to what `role` is permitted to see.

    Order is preserved. This covers the direct-context path only; the
    retrieval path draws from the embedded index instead and is restricted
    separately, in retrieve_context(). Both are required - filtering one and
    not the other leaks the whole corpus whenever the other mode is active.
    """
    permitted = permitted_sources(role)
    if permitted is None:
        return list(all_docs)
    return [(key, text) for key, text in all_docs if key in permitted]


# --------------------------------------------------------------------------
# Answer analysis
#
# Shared by eval.py (scoring) and usage_log.py (logging). Kept here, in the
# one module both import, so the two can never drift apart - a change to what
# counts as a refusal must apply identically to grading and to logging.
# --------------------------------------------------------------------------

FLAG_MARKER = "NEEDS HUMAN REVIEW"

# Any of these appearing in an answer counts as a refusal / admitted gap.
REFUSAL_PHRASES = (
    "i don't know",
    "i do not know",
    "don't know",
    "do not know",
    "not covered",
    "does not cover",
    "doesn't cover",
    "do not cover",
    "does not contain",
    "doesn't contain",
    "do not contain",
    "does not address",
    "doesn't address",
    "do not address",
    "not addressed",
    "does not mention",
    "doesn't mention",
    "do not mention",
    "not mentioned",
    "does not specify",
    "doesn't specify",
    "do not specify",
    "silent on",
    "no information",
    "outside the scope",
    "not in the provided documents",
    "not in the reference documents",
    # Added from sampled misses: the model sometimes moves the negation off the
    # documents ("the documents do not mention X") and onto the thing itself
    # ("there is no mention of X" / "no X mentioned anywhere in the documents").
    # These two are disjoint - neither alone covers both shapes. "anywhere in
    # the" is deliberately truncated so an inserted adjective ("provided",
    # "reference") still matches. Validated over 20 sampled answers: together
    # they caught 3/3 previously-missed refusals with no false positive on the
    # complete-answer cases, and neither appears in the source documents.
    "no mention of",
    "anywhere in the",
    # Added from case 6 sampling: correcting a false premise, the model often
    # attaches the negation to its own search rather than to the documents
    # ("I cannot find any policy that...") and never says "I don't know".
    # Present in 9 of 10 sampled case 6 answers, so it carries detection rather
    # than patching a single sample.
    "cannot find any",
)

# A refusal phrase in a long, complete answer is not a refusal. It is either a
# scope caveat ("what the documents do not cover") or a clarifying preamble
# ("I don't know which tier this client is") ahead of a full answer. Length
# separates the two cleanly; position does not.
#
# Measured over 40 stored answers (eval_corpus.json): genuine refusals ran
# 26-259 words, while complete answers containing a refusal phrase ran 484-721.
# 400 sits in that 225-word gap, 141 above the longest refusal and 84 below the
# shortest false positive.
#
# An earlier version also counted a phrase appearing in the first 15% of any
# answer. That clause was removed after measurement: across the same corpus it
# uniquely caught one true positive (a 259-word refusal) and caused one false
# positive (a 721-word complete answer whose preamble said "I don't know which
# tier"). Widening the length threshold captures the former without the latter.
REFUSAL_MAX_WORDS = 400


# Tolerant of markdown emphasis the model may add around the field
# ("**REFUSED:** yes", "> REFUSED: no"). The whole line is matched so it can
# be stripped cleanly before display.
SELF_REPORT_RE = re.compile(
    r"^[\s>*_#`-]*REFUSED[:\s*_`]*\s*(yes|no)\b.*$", re.I | re.M)


def self_reported_refusal(answer: str) -> bool | None:
    """Read the model's REFUSED: self-report. None if absent.

    The last occurrence wins — the line is specified as final, and an earlier
    mention would be the model discussing the field rather than emitting it.
    """
    found = SELF_REPORT_RE.findall(answer)
    if not found:
        return None
    return found[-1].lower() == "yes"


def strip_self_report(answer: str) -> str:
    """Remove the self-report line for display. See app.render_answer."""
    return SELF_REPORT_RE.sub("", answer).rstrip()


def refused_by_phrase(answer: str) -> bool:
    """Legacy prose heuristic. Retained only as a fallback.

    Length-dependent, and that dependency is the known defect: the threshold
    was calibrated on direct-context answers (complete 484-721 words, refusals
    26-259) and does not transfer to retrieval, where complete answers run
    143-352 words and sit entirely inside the refusal band.
    """
    lowered = answer.lower()
    if not any(phrase in lowered for phrase in REFUSAL_PHRASES):
        return False
    return len(answer.split()) < REFUSAL_MAX_WORDS


def refused(answer: str) -> bool:
    """True when the answer declined, wholly or partly, to answer from source.

    Prefers the model's structured self-report, which carries no dependency on
    answer length and therefore transfers between the direct-context and
    retrieval regimes. Falls back to the prose heuristic only when the field is
    absent — older stored answers, or a response that ignored rule 5.
    """
    reported = self_reported_refusal(answer)
    if reported is not None:
        return reported
    return refused_by_phrase(answer)


def review_flagged(answer: str) -> bool:
    """True when the answer carries the human-review marker."""
    return FLAG_MARKER in answer


def cited_docs(answer: str, known_docs) -> list[str]:
    """Filenames from known_docs that appear in the answer.

    Matches only against the caller-supplied document list, so a hallucinated
    or malformed filename in the answer is never counted as a citation.
    """
    return [name for name in known_docs if name in answer]


def _client(service: str, access_key_id: str = None, secret_access_key: str = None):
    """Build a boto3 client, falling back to the default credential chain."""
    kwargs = {"region_name": AWS_REGION}
    if access_key_id and secret_access_key:
        kwargs["aws_access_key_id"] = access_key_id
        kwargs["aws_secret_access_key"] = secret_access_key
    return boto3.client(service, **kwargs)


def get_bedrock_client(access_key_id: str = None, secret_access_key: str = None):
    return _client("bedrock-runtime", access_key_id, secret_access_key)


def get_s3_client(access_key_id: str = None, secret_access_key: str = None):
    return _client("s3", access_key_id, secret_access_key)


def load_documents(client=None) -> list[tuple[str, str]]:
    """Fetch every .md object in the docs bucket as (filename, text)."""
    client = client or get_s3_client()
    docs = []
    paginator = client.get_paginator("list_objects_v2")
    for page in paginator.paginate(Bucket=DOCS_BUCKET):
        for obj in page.get("Contents", []):
            key = obj["Key"]
            if not key.lower().endswith(".md"):
                continue
            body = client.get_object(Bucket=DOCS_BUCKET, Key=key)["Body"].read()
            docs.append((key, body.decode("utf-8")))
    return sorted(docs)


def build_context(docs: list[tuple[str, str]]) -> str:
    blocks = []
    for key, text in docs:
        blocks.append(
            f"===== BEGIN DOCUMENT: {key} =====\n"
            f"{text.strip()}\n"
            f"===== END DOCUMENT: {key} ====="
        )
    return "\n\n".join(blocks)


# --------------------------------------------------------------------------
# Retrieval
# --------------------------------------------------------------------------

# Tuned against the eval over K = 6, 10, 14, 18, 24 with three runs each.
# K=14 was the most consistent (7/7/7 where every other K varied), stabilised
# case 8, and costs $1.87 per 100 questions against $4.86 for prompt-cached
# direct context. Higher K bought nothing: cases 2 and 4 regressed at K=24 as
# extra context produced more caveats, and the relevance floor caps context
# regardless — at most 32 chunks clear 0.30 for any eval question. Full curve
# in retrieval_vs_caching.md.
RETRIEVAL_K = 14

# Chunks scoring below this are dropped even if that returns fewer than K.
#
# Chosen from measured scores across the eight eval questions, not from the
# two-query sanity check that suggested a 0.23/0.69 split — that gap did not
# survive contact with the real question set:
#
#   should-refuse cases   topic absent 0.254, false premise 0.258  (rank 1)
#   must-answer cases     mixed coverage 0.345, client-facing 0.348 (rank 6)
#
# The usable gap is 0.258-0.345, and 0.30 sits near its centre: 0.042 above
# the highest score any out-of-corpus question achieved, 0.045 below the
# lowest score a legitimate supporting chunk needed. A floor at the midpoint
# of the original 0.23-0.69 range would have discarded every chunk for two
# cases that must answer.
RELEVANCE_FLOOR = 0.30

NO_MATCH_CONTEXT = (
    "No documents in the reference set matched this question closely enough "
    "to be considered relevant."
)


def retrieve_context(question: str, client=None, k: int = RETRIEVAL_K,
                     floor: float = RELEVANCE_FLOOR,
                     query_vec=None, role: str = None) -> tuple[str, list]:
    """Assemble context from the top-k chunks that clear the relevance floor.

    Returns (context, hits). Chunks are grouped under their source document
    using the same ===== BEGIN DOCUMENT: filename ===== structure as the
    full-corpus path, so the citation rule needs no change: the model sees
    filenames in exactly the form it is asked to cite.

    `role` restricts which documents may contribute chunks. role=None means
    unrestricted, which is what the eval and tuning scripts want; the app
    always passes a real role.

    Imported lazily so core.py stays importable without numpy or a built
    index — app.py, stats.py and eval.py all import this module.
    """
    from vector_store import embed_query, load_index, search_vec

    embeddings, payload, _ = load_index()

    # Restrict the candidate set BEFORE ranking, never after.
    #
    # Filtering the returned hits instead would leave the whole corpus
    # competing for the k slots, so a role would silently receive fewer than k
    # chunks every time a document it cannot see outranked one it can - the
    # restriction would look like it worked while quietly degrading recall.
    # Cutting candidates first means all k come from permitted documents.
    #
    # Both operations copy, so the lru_cached index is never mutated.
    permitted = permitted_sources(role) if role is not None else None
    if permitted is not None:
        keep = [i for i, chunk in enumerate(payload)
                if chunk["source"] in permitted]
        if not keep:
            return NO_MATCH_CONTEXT, []
        embeddings = embeddings[keep]
        payload = [payload[i] for i in keep]
    # query_vec lets a caller reuse an embedding across repeated retrievals of
    # the same question — sweeping K, for instance, where the vector is
    # identical and only the cut-off changes.
    if query_vec is None:
        query_vec = embed_query(question, client)
    hits = search_vec(query_vec, k, embeddings, payload)
    kept = [h for h in hits if h.score >= floor]

    if not kept:
        return NO_MATCH_CONTEXT, []

    # Group by source, best-scoring document first, preserving each
    # document's own chunk order within its block.
    order, grouped = [], {}
    for h in kept:
        if h.source not in grouped:
            grouped[h.source] = []
            order.append(h.source)
        grouped[h.source].append(h)

    blocks = []
    for src in order:
        body = "\n\n".join(h.text for h in grouped[src])
        blocks.append(
            f"===== BEGIN DOCUMENT: {src} =====\n"
            f"{body}\n"
            f"===== END DOCUMENT: {src} ====="
        )
    return "\n\n".join(blocks), kept


def ask(question: str, context: str = None, client=None,
        use_cache: bool = True, use_retrieval: bool = False,
        role: str = None) -> dict:
    """Ask a grounded question; return the answer plus call metrics.

    Returns a dict with keys: answer, latency_ms, input_tokens, output_tokens,
    cache_read_tokens, cache_write_tokens, total_input_tokens.

    Caching is ON by default: the document context goes in its own content
    block followed by a cachePoint, so the stable prefix (system prompt +
    corpus) is served from Bedrock's prompt cache while the question varies
    freely. Sonnet 4.6 supports a 5-minute TTL only, refreshed on each hit.
    Measured at 82% cheaper than uncached with no quality change — see
    baseline_prompt_caching.md. Pass use_cache=False to reproduce the uncached
    baseline.

    Note: when caching is active Bedrock reports `inputTokens` as the
    NON-cached portion only, so total input is inputTokens + cacheRead +
    cacheWrite. `total_input_tokens` does that sum; `input_tokens` is left as
    Bedrock reported it.
    """
    client = client or get_bedrock_client()

    hits = None
    if use_retrieval:
        # Retrieval replaces the caller's context entirely, so the role has to
        # be enforced here too. The caller filtering its document list only
        # protects the direct-context path - without this, turning retrieval on
        # would quietly restore access to the full corpus.
        context, hits = retrieve_context(question, client, role=role)
    elif context is None:
        raise ValueError("context is required when use_retrieval is False")

    if use_cache:
        content = [
            {"text": f"Here are the reference documents:\n\n{context}"},
            {"cachePoint": {"type": "default"}},
            {"text": f"---\n\nQuestion: {question}"},
        ]
    else:
        content = [{
            "text": f"Here are the reference documents:\n\n{context}\n\n"
                    f"---\n\nQuestion: {question}"
        }]

    start = time.perf_counter()
    response = client.converse(
        modelId=MODEL_ID,
        system=[{"text": SYSTEM_PROMPT}],
        messages=[{"role": "user", "content": content}],
    )
    latency_ms = round((time.perf_counter() - start) * 1000)
    usage = response.get("usage", {})
    read = usage.get("cacheReadInputTokens") or 0
    write = usage.get("cacheWriteInputTokens") or 0
    plain = usage.get("inputTokens") or 0
    return {
        "answer": response["output"]["message"]["content"][0]["text"],
        "latency_ms": latency_ms,
        "input_tokens": usage.get("inputTokens"),
        "output_tokens": usage.get("outputTokens"),
        "cache_read_tokens": read,
        "cache_write_tokens": write,
        "total_input_tokens": plain + read + write,
        "retrieved": None if hits is None else [
            {"source": h.source, "section": h.section,
             "score": round(h.score, 4)} for h in hits
        ],
        "retrieved_docs": None if hits is None else sorted(
            {h.source for h in hits}),
    }
