from pathlib import Path

import streamlit as st
import streamlit_authenticator as stauth
import yaml

import core
import make_auth_config
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


def auth_secrets() -> tuple:
    """Demo credentials supplied through Streamlit secrets.

    Streamlit Community Cloud rebuilds from a clean checkout and has no shell,
    so make_auth_config.py can never be run against a deployment. Secrets are
    the one channel that both survives a rebuild and can be set without one,
    which is why they are the source here rather than a committed file.

    Expected shape, set locally in .streamlit/secrets.toml or in the Cloud
    dashboard under Settings -> Secrets:

        [auth]
        billing = "..."
        warehouse = "..."
        account = "..."
        admin = "..."
        cookie_key = "..."   # optional; keeps sessions alive across restarts

    Returns (passwords, cookie_key), either of which may be None.
    """
    # Deliberately broad: a missing secrets file, a missing section and a
    # malformed one should all degrade to "no secrets supplied" rather than
    # take the app down before the login gate renders.
    try:
        section = st.secrets["auth"]
    except Exception:
        return None, None
    passwords = {u: section.get(u) for u in make_auth_config.USERS}
    return passwords, section.get("cookie_key")


def current_role() -> str:
    """The role this session acts under.

    streamlit-authenticator stores roles as a list. Every test user has exactly
    one except admin, which carries all of them; taking the first entry makes
    admin resolve to ROLE_ADMIN rather than depending on list order downstream.
    """
    roles = st.session_state.get("roles") or []
    return roles[0] if roles else ""


# auth_config.yaml is gitignored, so a fresh deploy never has one and there is
# no shell to run make_auth_config.py in. Build it here instead, on every cold
# start, from whatever credentials the environment supplies.
try:
    auth_source = make_auth_config.ensure_config(AUTH_CONFIG_PATH, *auth_secrets())
except Exception as e:
    st.error(f"Could not create {AUTH_CONFIG_PATH.name}: {e}")
    st.stop()

if auth_source == "missing":
    # Checked before build_authenticator so the message is this one, not a
    # bare FileNotFoundError. Nothing was written, so this reappears on every
    # rerun rather than vanishing once a file exists.
    #
    # No published-default fallback on purpose: this login gates Bedrock calls
    # billed to whoever deployed it, so a publicly known password on a public
    # URL is an open tab on their AWS account.
    st.error(
        f"No `{AUTH_CONFIG_PATH.name}` and no `[auth]` section in secrets, so "
        "there are no credentials to log in with. Add the section below under "
        "**Settings → Secrets**, then reboot the app."
    )
    st.code(
        "[auth]\n"
        + "\n".join(f'{u} = "choose-a-password"' for u in make_auth_config.USERS)
        + '\ncookie_key = "any-long-random-string"',
        language="toml",
    )
    st.stop()

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

# Everything downstream reads `visible`, never `documents`, so a restricted
# document cannot re-enter the context by accident further down the file.
visible = core.get_documents_for_role(role, documents)

st.caption(
    f"Answering as `{role}` from {len(visible)} of {len(documents)} documents "
    f"in s3://{core.DOCS_BUCKET}"
)
with st.expander(f"Documents visible to {role}"):
    if not visible:
        st.write("This role has access to no documents.")
    for key, text in visible:
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
                core.build_context(visible),
                get_bedrock_client(),
                role=role,
            )
        except Exception as e:
            st.session_state.last_log_id = usage_log.log_call(
                question, error=e, documents=visible
            )
            st.session_state.last_result = None
            st.session_state.last_error = str(e)
        else:
            st.session_state.last_log_id = usage_log.log_call(
                question, result=result, documents=visible
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
    if last_result.get("access_denied"):
        # Deliberately not rendered as an answer. A refusal is the assistant
        # reporting on the documents; this is the system reporting on the
        # user's permissions. Showing them identically is the silent failure
        # this part exists to remove, so they differ in wording and in shape.
        st.warning(last_result["answer"])
        st.caption("No model call was made for this question.")
    else:
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
