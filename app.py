import boto3
import streamlit as st

st.set_page_config(page_title="Fulfillment Ops Assistant", layout="wide")

st.title("Fulfillment Ops Assistant")

BEDROCK_REGION = "us-east-1"
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


@st.cache_resource
def get_bedrock_client():
    return boto3.client(
        "bedrock-runtime",
        region_name=BEDROCK_REGION,
        aws_access_key_id=st.secrets["AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=st.secrets["AWS_SECRET_ACCESS_KEY"],
    )


@st.cache_resource
def get_s3_client():
    return boto3.client(
        "s3",
        region_name=BEDROCK_REGION,
        aws_access_key_id=st.secrets["AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=st.secrets["AWS_SECRET_ACCESS_KEY"],
    )


@st.cache_data(show_spinner="Loading reference documents...")
def load_documents() -> list[tuple[str, str]]:
    """Fetch every .md object in the docs bucket as (filename, text)."""
    client = get_s3_client()
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


def ask_claude(question: str, context: str) -> str:
    client = get_bedrock_client()
    prompt = (
        f"Here are the reference documents:\n\n{context}\n\n"
        f"---\n\nQuestion: {question}"
    )
    response = client.converse(
        modelId=MODEL_ID,
        system=[{"text": SYSTEM_PROMPT}],
        messages=[{"role": "user", "content": [{"text": prompt}]}],
    )
    return response["output"]["message"]["content"][0]["text"]


try:
    documents = load_documents()
except Exception as e:
    st.error(f"Could not load documents from s3://{DOCS_BUCKET}: {e}")
    st.stop()

if not documents:
    st.error(f"No .md documents found in s3://{DOCS_BUCKET}.")
    st.stop()

st.caption(f"Answering from {len(documents)} documents in s3://{DOCS_BUCKET}")
with st.expander("Loaded documents"):
    for key, text in documents:
        st.write(f"- `{key}` ({len(text):,} chars)")

st.subheader("Ask Claude")
question = st.text_area("Question")

if st.button("Ask") and question.strip():
    with st.spinner("Asking Claude..."):
        try:
            answer = ask_claude(question, build_context(documents))
            st.write(answer)
        except Exception as e:
            st.error(f"Request failed: {e}")


if __name__ == "__main__":
    pass
