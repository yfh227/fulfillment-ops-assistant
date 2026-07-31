import streamlit as st

import core
import usage_log

st.set_page_config(page_title="Fulfillment Ops Assistant", layout="wide")

st.title("Fulfillment Ops Assistant")


@st.cache_resource
def get_bedrock_client():
    return core.get_bedrock_client(
        st.secrets["AWS_ACCESS_KEY_ID"],
        st.secrets["AWS_SECRET_ACCESS_KEY"],
    )


@st.cache_resource
def get_s3_client():
    return core.get_s3_client(
        st.secrets["AWS_ACCESS_KEY_ID"],
        st.secrets["AWS_SECRET_ACCESS_KEY"],
    )


@st.cache_data(show_spinner="Loading reference documents...")
def load_documents() -> list[tuple[str, str]]:
    return core.load_documents(get_s3_client())


@st.cache_resource
def init_usage_db() -> bool:
    usage_log.init()
    return True


def render_answer(answer: str) -> None:
    """Display an answer, escaping $ so Streamlit doesn't parse it as LaTeX.

    Rate and invoice figures come back as paired amounts ("$250 - $2,500"),
    which Streamlit would otherwise treat as inline math and mangle.
    """
    st.markdown(answer.replace("$", r"\$"))


try:
    documents = load_documents()
except Exception as e:
    st.error(f"Could not load documents from s3://{core.DOCS_BUCKET}: {e}")
    st.stop()

if not documents:
    st.error(f"No .md documents found in s3://{core.DOCS_BUCKET}.")
    st.stop()

st.caption(f"Answering from {len(documents)} documents in s3://{core.DOCS_BUCKET}")
with st.expander("Loaded documents"):
    for key, text in documents:
        st.write(f"- `{key}` ({len(text):,} chars)")

st.subheader("Ask Claude")
question = st.text_area("Question")

if st.button("Ask") and question.strip():
    init_usage_db()
    with st.spinner("Asking Claude..."):
        try:
            result = core.ask(
                question,
                core.build_context(documents),
                get_bedrock_client(),
            )
        except Exception as e:
            st.session_state.last_log_id = usage_log.log_call(
                question, error=e, documents=documents
            )
            st.error(f"Request failed: {e}")
        else:
            st.session_state.last_log_id = usage_log.log_call(
                question, result=result, documents=documents
            )
            render_answer(result["answer"])
            st.caption(
                f"{result['latency_ms']} ms · "
                f"{result['input_tokens']:,} in / "
                f"{result['output_tokens']:,} out tokens"
            )


if __name__ == "__main__":
    pass
