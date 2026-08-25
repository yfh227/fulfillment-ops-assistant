from pathlib import Path

import streamlit as st
import streamlit_authenticator as stauth
import yaml

import core
import make_auth_config
import spend_guard
import stats
import usage_log

st.set_page_config(page_title="Fulfillment Ops Assistant", layout="wide")

st.title("Fulfillment Ops Assistant")


# --------------------------------------------------------------------------
# Access tiers
#
# The app is PUBLIC BY DEFAULT. An anonymous visitor acts under ROLE_PUBLIC and
# can use the assistant against the one document that role is permitted to see.
# Signing in elevates to an Executive tier role with a wider document set.
#
# Login is therefore optional elevation, not a gate. This is a deliberate
# reversal: a login wall makes a demo unusable to anyone without credentials,
# and it hides the role-based access story that is the point of the project. A
# visitor who asks the public tier something out of scope sees the access
# notice fire live, which demonstrates the feature better than a password box.
#
# What the login used to protect - Bedrock spend on a public URL - is now
# protected by spend_guard instead. That control ships with this tier rather
# than after it.
# --------------------------------------------------------------------------

AUTH_CONFIG_PATH = Path(__file__).parent / "auth_config.yaml"


def build_authenticator():
    """Construct the authenticator fresh on each rerun, or None if unavailable.

    Deliberately not wrapped in st.cache_resource: Authenticate owns the cookie
    controller and mutates its own credentials dict on login and logout, so a
    cached instance would leak one session's state into the next.

    Returns None when there is no usable config. Missing credentials now mean
    "login is unavailable", not "the app is broken" - the public tier runs
    perfectly well without any auth configured, so a deployment that never
    gets an [auth] section is degraded rather than dead.
    """
    try:
        with open(AUTH_CONFIG_PATH, encoding="utf-8") as f:
            config = yaml.safe_load(f)
        return stauth.Authenticate(
            config["credentials"],
            config["cookie"]["name"],
            config["cookie"]["key"],
            config["cookie"]["expiry_days"],
        )
    except Exception:
        return None


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
    """The role this session acts under, defaulting to the public tier.

    streamlit-authenticator stores roles as a list. Every account has exactly
    one except admin, which carries all of them; taking the first entry makes
    admin resolve to ROLE_ADMIN rather than depending on list order downstream.

    An unauthenticated session is not an error state - it is ROLE_PUBLIC.
    """
    if st.session_state.get("authentication_status") is not True:
        return core.ROLE_PUBLIC
    roles = st.session_state.get("roles") or []
    return roles[0] if roles else core.ROLE_PUBLIC


# auth_config.yaml is gitignored, so a fresh deploy never has one and there is
# no shell to run make_auth_config.py in. Build it here instead, on every cold
# start, from whatever credentials the environment supplies. A failure here is
# not fatal any more: it costs the login, not the app.
try:
    auth_source = make_auth_config.ensure_config(AUTH_CONFIG_PATH, *auth_secrets())
except Exception:
    auth_source = "missing"

authenticator = build_authenticator() if auth_source != "missing" else None

with st.sidebar:
    st.subheader("Access")
    if authenticator is None:
        # Nothing was written, so this reappears on every rerun rather than
        # vanishing once a file exists. No published-default fallback on
        # purpose: an Executive tier password known to the public would undo
        # the restriction it exists to enforce.
        st.caption(
            "Sign-in unavailable — no credentials are configured, so only the "
            "public tier is running."
        )
        with st.expander("Configure sign-in"):
            st.write(
                f"Add an `[auth]` section under **Settings → Secrets**, then "
                f"reboot. It builds `{AUTH_CONFIG_PATH.name}` on the next cold "
                "start."
            )
            st.code(
                "[auth]\n"
                + "\n".join(f'{u} = "choose-a-password"'
                            for u in make_auth_config.USERS)
                + '\ncookie_key = "any-long-random-string"',
                language="toml",
            )
    elif st.session_state.get("authentication_status") is True:
        st.caption(f"Signed in as **{st.session_state.get('name')}**")
        authenticator.logout("Log out", "sidebar")
    else:
        authenticator.login(location="sidebar")
        if st.session_state.get("authentication_status") is False:
            st.error("Username or password is incorrect.")
        st.caption("Browsing as a public viewer. Sign in for the Executive tier.")

role = current_role()
if role not in core.ROLES:
    # Signed in against an account whose role is not recognised. Fail closed to
    # the public tier rather than to nothing, and say so.
    st.warning(
        f"Signed-in account has no recognised role ({role!r}); showing the "
        "public tier. Check the roles field in auth_config.yaml."
    )
    role = core.ROLE_PUBLIC

is_public = role == core.ROLE_PUBLIC


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

tier = "Public tier" if is_public else "Executive tier"
st.caption(
    f"**{tier}** — answering as `{role}` from {len(visible)} of "
    f"{len(documents)} documents in s3://{core.DOCS_BUCKET}"
)
if is_public:
    st.info(
        "You are browsing the public tier, which sees one document. Ask about "
        "anything outside it and the assistant will say so rather than "
        "guessing — that access notice is the point of the demo. Sign in for "
        "the Executive tier."
    )
with st.expander(f"Documents visible to {role}"):
    if not visible:
        st.write("This role has access to no documents.")
    for key, text in visible:
        st.write(f"- `{key}` ({len(text):,} chars)")

st.subheader("Ask Claude")
question = st.text_area("Question")

if is_public:
    remaining = spend_guard.daily_remaining()
    used = st.session_state.get("public_calls", 0)
    st.caption(
        f"Public demo budget: {spend_guard.PUBLIC_SESSION_LIMIT - used} left "
        f"this session, {remaining} left today."
    )

if st.button("Ask") and question.strip():
    init_usage_db()
    st.session_state.feedback = None

    # Spend cap, checked before the model is reached. The public tier is the
    # only one that needs it: every other role required a credential to get
    # here, and that credential is the accountability.
    allowed, why = (True, "")
    if is_public:
        allowed, why = spend_guard.check_public(st.session_state.get("public_calls", 0))

    if not allowed:
        st.session_state.last_result = None
        st.session_state.last_error = None
        st.session_state.last_log_id = None
        st.session_state.budget_message = why
    else:
        st.session_state.budget_message = None
        with st.spinner("Asking Claude..."):
            try:
                result = core.ask(
                    question,
                    core.build_context(visible),
                    get_bedrock_client(),
                    role=role,
                    max_tokens=(spend_guard.PUBLIC_MAX_OUTPUT_TOKENS
                                if is_public else None),
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
                # Counted only on a call that actually reached the model. A
                # denied question costs nothing, so it must not consume budget.
                if is_public and not result.get("access_denied"):
                    st.session_state.public_calls = (
                        st.session_state.get("public_calls", 0) + 1
                    )

if st.session_state.get("budget_message"):
    st.warning(st.session_state.budget_message)

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
