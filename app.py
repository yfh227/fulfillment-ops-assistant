from pathlib import Path

import streamlit as st
import streamlit_authenticator as stauth
import yaml

import core
import stats
import usage_log

st.set_page_config(page_title="Fulfillment Ops Assistant", layout="wide")

st.title("Fulfillment Ops Assistant")


# --------------------------------------------------------------------------
# Authentication
#
# Everything below the login gate is unreachable until a user authenticates,
# including the S3 document load - an anonymous visitor should not be able to
# make the app fetch the corpus at all.
# --------------------------------------------------------------------------

AUTH_CONFIG_PATH = Path(__file__).parent / "auth_config.yaml"


def build_authenticator() -> stauth.Authenticate:
    """Construct the authenticator fresh on each rerun.

    Deliberately not wrapped in st.cache_resource: Authenticate owns the cookie
    controller and mutates its own credentials dict on login and logout, so a
    cached instance would leak one session's state into the next.
    """
    with open(AUTH_CONFIG_PATH, encoding="utf-8") as f:
        config = yaml.safe_load(f)
    return stauth.Authenticate(
        config["credentials"],
        config["cookie"]["name"],
        config["cookie"]["key"],
        config["cookie"]["expiry_days"],
    )


def current_role() -> str:
    """The role this session acts under.

    streamlit-authenticator stores roles as a list. Every test user has exactly
    one except admin, which carries all of them; taking the first entry makes
    admin resolve to ROLE_ADMIN rather than depending on list order downstream.
    """
    roles = st.session_state.get("roles") or []
    return roles[0] if roles else ""


try:
    authenticator = build_authenticator()
except FileNotFoundError:
    st.error(
        f"No {AUTH_CONFIG_PATH.name} found. Generate one with "
        "`python make_auth_config.py`."
    )
    st.stop()

authenticator.login(location="main")

if st.session_state.get("authentication_status") is False:
    st.error("Username or password is incorrect.")
    st.stop()

if st.session_state.get("authentication_status") is None:
    st.info("Log in to continue.")
    st.stop()

role = current_role()
if role not in core.ROLES:
    st.error(
        f"Signed in, but the account has no recognised role ({role!r}). "
        "Check the roles field in auth_config.yaml."
    )
    st.stop()

with st.sidebar:
    st.caption(f"Signed in as **{st.session_state.get('name')}**")
    st.caption(f"Role: `{role}`")
    authenticator.logout("Log out", "sidebar")


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
    """Display an answer, stripped of the machine-readable self-report and
    escaped so Streamlit doesn't parse currency as LaTeX.

    The system prompt requires a trailing "REFUSED: yes|no" line for the eval
    grader. It is not for the reader, so it is removed here — the only place
    an answer reaches a human.

    Rate and invoice figures come back as paired amounts ("$250 - $2,500"),
    which Streamlit would otherwise treat as inline math and mangle.
    """
    st.markdown(core.strip_self_report(answer).replace("$", r"\$"))


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
    st.session_state.feedback = None
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
            st.session_state.last_result = None
            st.session_state.last_error = str(e)
        else:
            st.session_state.last_log_id = usage_log.log_call(
                question, result=result, documents=documents
            )
            st.session_state.last_result = result
            st.session_state.last_error = None

# Everything below is driven by session state rather than the Ask block, so it
# survives the rerun that clicking a feedback button triggers. Rendered inside
# the Ask block, the answer and its buttons would disappear on the first click.
if st.session_state.get("last_error"):
    st.error(f"Request failed: {st.session_state.last_error}")

last_result = st.session_state.get("last_result")
if last_result:
    render_answer(last_result["answer"])
    st.caption(
        f"{last_result['latency_ms']} ms · "
        f"{last_result['input_tokens']:,} in / "
        f"{last_result['output_tokens']:,} out tokens"
    )

    log_id = st.session_state.get("last_log_id")
    if log_id is not None:
        up, down, _ = st.columns([1, 1, 10])
        if up.button("👍", key="feedback_up"):
            usage_log.record_feedback(log_id, "up")
            st.session_state.feedback = "up"
        if down.button("👎", key="feedback_down"):
            usage_log.record_feedback(log_id, "down")
            st.session_state.feedback = "down"

        if st.session_state.get("feedback"):
            st.caption(
                f"Feedback recorded: {st.session_state.feedback} (row {log_id})"
            )


# Rendered last on purpose. st.sidebar places content in the sidebar wherever
# it is called from, so running after the Ask block means these figures include
# the question just logged rather than trailing it by one.
with st.sidebar:
    st.subheader("Usage")
    usage = stats.summary_stats()
    if not usage["answered"]:
        st.caption("No usage recorded yet.")
    else:
        st.metric("Questions asked", f"{usage['answered']:,}")
        st.metric("Flagged for review", f"{usage['pct_flagged']}%")
        st.metric("Refused", f"{usage['pct_refused']}%")
        st.metric(
            "Avg latency",
            f"{usage['avg_ms']:,.0f} ms" if usage["avg_ms"] is not None else "—",
        )


if __name__ == "__main__":
    pass
