"""Core logic for the fulfillment ops assistant.

Deliberately free of any Streamlit dependency, so it can be driven from
scripts, tests, or a different front end. Credentials are passed in rather
than read from Streamlit secrets; when omitted, boto3's default credential
chain applies.
"""

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
answer the question fully and even if you are confident. Err toward flagging."""


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


def ask(question: str, context: str, client=None) -> dict:
    """Ask a grounded question; return the answer plus call metrics.

    Returns a dict with keys: answer, latency_ms, input_tokens, output_tokens.
    """
    client = client or get_bedrock_client()
    prompt = (
        f"Here are the reference documents:\n\n{context}\n\n"
        f"---\n\nQuestion: {question}"
    )
    start = time.perf_counter()
    response = client.converse(
        modelId=MODEL_ID,
        system=[{"text": SYSTEM_PROMPT}],
        messages=[{"role": "user", "content": [{"text": prompt}]}],
    )
    latency_ms = round((time.perf_counter() - start) * 1000)
    usage = response.get("usage", {})
    return {
        "answer": response["output"]["message"]["content"][0]["text"],
        "latency_ms": latency_ms,
        "input_tokens": usage.get("inputTokens"),
        "output_tokens": usage.get("outputTokens"),
    }
