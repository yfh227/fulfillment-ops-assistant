import uuid
from pathlib import Path

import streamlit as st
import streamlit_authenticator as stauth
import yaml

import core
import make_auth_config
import spend_guard
import stats
import training
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


AWS_SECRET_KEYS = ("AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY")


def missing_aws_secrets() -> list[str]:
    """Which AWS keys are absent from secrets, if any.

    Checked explicitly rather than left to surface as a KeyError from inside
    the S3 call. A misconfigured deployment is a configuration problem with a
    known fix, and it should read as one - not as a raw stack-trace message
    with a docs link, which is what an unconfigured deploy showed to every
    visitor before this. Same treatment the missing-[auth] path already gets.
    """
    missing = []
    for key in AWS_SECRET_KEYS:
        try:
            if not st.secrets[key]:
                missing.append(key)
        except Exception:
            missing.append(key)
    return missing


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


# Checked before the S3 call so a deployment with no AWS credentials explains
# itself, rather than surfacing the KeyError raised from inside boto3 setup.
_missing_aws = missing_aws_secrets()
if _missing_aws:
    st.error(
        "This deployment is not finished being configured — its AWS "
        "credentials are missing, so the reference documents cannot be "
        "loaded. Nothing is broken in the application itself."
    )
    with st.expander("Configure AWS access"):
        st.write(
            f"Missing from secrets: {', '.join(f'`{k}`' for k in _missing_aws)}. "
            "Add the keys below under **Settings → Secrets** (append them — do "
            "not replace an existing `[auth]` section), then reboot the app."
        )
        st.code(
            'AWS_ACCESS_KEY_ID = "..."\n'
            'AWS_SECRET_ACCESS_KEY = "..."\n'
            'AWS_DEFAULT_REGION = "us-east-1"',
            language="toml",
        )
    st.stop()

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

def run_ask(question: str) -> dict:
    """Ask the assistant once, under every control the app applies.

    The one path to core.ask, shared by the Ask tab and the training tasks, so
    a question asked during training is capped, logged and access-checked
    exactly like any other. Returns {result, error, log_id, budget_message};
    at most one of result/error/budget_message is set.
    """
    init_usage_db()

    # Spend cap, checked before the model is reached. The public tier is the
    # only one that needs it: every other role required a credential to get
    # here, and that credential is the accountability.
    if is_public:
        allowed, why = spend_guard.check_public(st.session_state.get("public_calls", 0))
        if not allowed:
            return {"result": None, "error": None, "log_id": None,
                    "budget_message": why}

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
            log_id = usage_log.log_call(question, error=e, documents=visible)
            return {"result": None, "error": str(e), "log_id": log_id,
                    "budget_message": None}

    log_id = usage_log.log_call(question, result=result, documents=visible)
    # Counted only on a call that actually reached the model. A denied
    # question costs nothing, so it must not consume budget.
    if is_public and not result.get("access_denied"):
        st.session_state.public_calls = st.session_state.get("public_calls", 0) + 1
    return {"result": result, "error": None, "log_id": log_id,
            "budget_message": None}


def show_result(result: dict) -> None:
    """Render one core.ask result: an answer, or the access notice."""
    if result.get("access_denied"):
        # Deliberately not rendered as an answer. A refusal is the assistant
        # reporting on the documents; this is the system reporting on the
        # user's permissions. Showing them identically is the silent failure
        # this part exists to remove, so they differ in wording and in shape.
        st.warning(result["answer"])
        st.caption("No model call was made for this question.")
        return
    render_answer(result["answer"])
    # Bedrock's inputTokens excludes cached tokens, so showing it alone
    # understated the prompt by the whole cached corpus.
    cached = result.get("cache_read_tokens") or 0
    st.caption(
        f"{result['latency_ms']} ms · "
        f"{result['total_input_tokens']:,} in"
        + (f" ({cached:,} from cache)" if cached else "")
        + f" / {result['output_tokens']:,} out tokens"
    )


# Budget lines are reserved where they appear and filled at the very end of
# the script. Filled in place, a line would be computed before a click further
# down - in either tab - was counted, and run one question behind.
budget_slots = []

ask_tab, training_tab = st.tabs(["Ask Claude", "Training"])

with ask_tab:
    question = st.text_area("Question")
    budget_slots.append(st.empty())

    if st.button("Ask") and question.strip():
        st.session_state.feedback = None
        out = run_ask(question)
        st.session_state.last_result = out["result"]
        st.session_state.last_error = out["error"]
        st.session_state.last_log_id = out["log_id"]
        st.session_state.budget_message = out["budget_message"]

    if st.session_state.get("budget_message"):
        st.warning(st.session_state.budget_message)

    # Everything below is driven by session state rather than the Ask block, so
    # it survives the rerun that clicking a feedback button triggers. Rendered
    # inside the Ask block, the answer and its buttons would disappear on the
    # first click.
    if st.session_state.get("last_error"):
        st.error(f"Request failed: {st.session_state.last_error}")

    last_result = st.session_state.get("last_result")
    if last_result:
        show_result(last_result)

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


# --------------------------------------------------------------------------
# Training
#
# Module content lives in training_modules.json and the checks in training.py;
# this section only lays them out and records attempts. A task is a real
# question through run_ask, so it is capped and logged like any other. A
# rubric-graded written answer is a model call of its own: it is checked
# against the same public cap first and counted against it after.
# --------------------------------------------------------------------------

@st.cache_data
def load_course() -> dict:
    return training.load_course()


course = load_course()
course_ids = training.module_ids(course)
visible_names = [name for name, _ in visible]

if "training_session_id" not in st.session_state:
    # Random per browser session - counts learners without identifying anyone.
    st.session_state.training_session_id = uuid.uuid4().hex
progress = st.session_state.setdefault("training", {})


def module_state(module_id: str) -> dict:
    return progress.setdefault(module_id, {
        "task_passed": False, "task_result": None, "task_message": None,
        "task_pass_result": None, "reflection": None, "reflection_passed": False,
        "budget_message": None, "error": None,
    })


def module_done(module_id: str) -> bool:
    s = module_state(module_id)
    return s["task_passed"] and s["reflection_passed"]


def log_attempt(module_id, step, passed, graded_by, detail=None, metrics=None,
                error=None):
    init_usage_db()
    usage_log.log_training(
        st.session_state.training_session_id, role, module_id, step, passed,
        graded_by, detail=detail, metrics=metrics, error=error,
    )


with training_tab:
    st.subheader(course["course"])
    st.caption(course["intro"])
    n_done = sum(module_done(m) for m in course_ids)
    st.progress(n_done / len(course_ids),
                text=f"{n_done} of {len(course_ids)} modules complete")
    budget_slots.append(st.empty())

    titles = {m["id"]: m["title"] for m in course["modules"]}
    # Labels stay fixed. When they carried the completion mark, a module
    # finishing changed its label, and the browser then showed no option
    # selected while the server kept rendering the old one - seen on the live
    # deployment. Completion is shown on its own line instead.
    module_id = st.radio(
        "Module",
        course_ids,
        format_func=lambda m: f"{course_ids.index(m) + 1}. {titles[m]}",
        key="training_module",
    )
    st.caption("  ·  ".join(
        f"{'✅' if module_done(m) else '○'} {course_ids.index(m) + 1}"
        for m in course_ids))
    module = next(m for m in course["modules"] if m["id"] == module_id)
    state = module_state(module_id)
    was_done = module_done(module_id)

    st.markdown(f"#### {module['title']}")
    st.markdown(module["lesson"])

    if module["check"] == "access_denied" and role == core.ROLE_ADMIN:
        st.info(
            "Admin can see every document, so no question can raise the access "
            "notice for this account. Sign out to take this module on the "
            "public tier."
        )

    st.markdown(f"**Task.** {module['task']}")
    task_q = st.text_area("Your question", key=f"task_q_{module_id}",
                          placeholder=f"For example: {module['suggestion']}")
    if st.button("Ask", key=f"task_ask_{module_id}") and task_q.strip():
        out = run_ask(task_q)
        state["budget_message"] = out["budget_message"]
        state["error"] = out["error"]
        state["task_result"] = out["result"]
        if out["result"] is not None:
            ok, msg = training.check_task(module["check"], out["result"], visible_names)
            state["task_message"] = (ok, msg)
            log_attempt(module_id, "task", ok, "code",
                        detail={"question": task_q, "check": module["check"],
                                "explanation": msg})
            if ok:
                # Sticky: a later failed try does not undo a pass, and the
                # passing result is kept because the quote check needs the
                # documents that answer cited.
                state["task_passed"] = True
                state["task_pass_result"] = out["result"]

    if state["budget_message"]:
        st.warning(state["budget_message"])
    if state["error"]:
        st.error(f"Request failed: {state['error']}")
    if state["task_result"] is not None:
        show_result(state["task_result"])
        ok, msg = state["task_message"]
        (st.success if ok else st.warning)(f"{'Task passed' if ok else 'Not yet'}: {msg}")

    if state["task_passed"]:
        st.markdown(f"**Written answer.** {module['reflection']}")
        cited = []
        if module["grading"] == "quote":
            pass_result = state["task_pass_result"]
            cited = core.cited_docs(pass_result["answer"], visible_names)
            texts = dict(visible)
            for name in cited:
                with st.expander(f"Open {name}"):
                    st.markdown(texts[name].replace("$", r"\$"))

        reflection = st.text_area("Your answer", key=f"reflection_{module_id}")
        label = "Check my quote" if module["grading"] == "quote" else "Submit for grading"
        if st.button(label, key=f"reflect_{module_id}") and reflection.strip():
            if module["grading"] == "quote":
                ok, msg = training.check_quote(reflection, cited, visible)
                state["reflection"] = {"passed": ok, "message": msg, "criteria": [],
                                       "feedback": ""}
                log_attempt(module_id, "reflection", ok, "code",
                            detail={"cited": cited, "message": msg})
            else:
                reason = training.precheck_reflection(reflection)
                allowed, why = (True, "")
                if reason is None and is_public:
                    allowed, why = spend_guard.check_public(
                        st.session_state.get("public_calls", 0))
                if reason is not None:
                    ok = False
                    state["reflection"] = {"passed": False, "message": reason,
                                           "criteria": [], "feedback": ""}
                    log_attempt(module_id, "reflection", False, "code",
                                detail={"precheck": reason})
                elif not allowed:
                    ok = False
                    state["reflection"] = {"passed": False, "message": why,
                                           "criteria": [], "feedback": ""}
                else:
                    with st.spinner("Claude is grading your answer..."):
                        try:
                            g = training.grade_reflection(module, reflection,
                                                          get_bedrock_client())
                        except Exception as e:
                            g = {"passed": False, "criteria": [], "feedback": "",
                                 "error": str(e)}
                    if is_public:
                        st.session_state.public_calls = (
                            st.session_state.get("public_calls", 0) + 1)
                    ok = g["passed"]
                    message = (f"Grading failed, so this attempt was not counted "
                               f"as a pass: {g['error']}" if g["error"] else
                               "Passed - every criterion met." if ok else
                               "Not yet - see what was missing below.")
                    state["reflection"] = {"passed": ok, "message": message,
                                           "criteria": g["criteria"],
                                           "feedback": g["feedback"]}
                    log_attempt(module_id, "reflection", ok, "model",
                                detail={"criteria": g["criteria"],
                                        "feedback": g["feedback"]},
                                metrics=g, error=g["error"])
            if ok:
                state["reflection_passed"] = True

        r = state["reflection"]
        if r:
            (st.success if r["passed"] else st.warning)(r["message"])
            for c in r["criteria"]:
                st.markdown(f"{'✅' if c['met'] else '❌'} {c['label']}"
                            + (f' — *"{c["evidence"]}"*' if c["met"] else ""))
            if r["feedback"]:
                st.caption(f"Feedback from Claude: {r['feedback']}")

    if module_done(module_id) != was_done:
        # The progress bar and the module checkmarks above were drawn before
        # this click completed the module. Every result shown here lives in
        # session state, so a rerun redraws them current and loses nothing.
        st.rerun()
    if module_done(module_id):
        st.success("Module complete.")


if is_public:
    used = st.session_state.get("public_calls", 0)
    for slot in budget_slots:
        slot.caption(
            f"Public demo budget: {spend_guard.PUBLIC_SESSION_LIMIT - used} left "
            f"this session, {spend_guard.daily_remaining()} left today."
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
    t = stats.training_summary(course_ids)
    if t["learners"]:
        st.metric("Training: courses completed",
                  f"{t['course_completions']} of {t['learners']} learners")


# --------------------------------------------------------------------------
# Footer
#
# Rendered for every role, public included. A visitor who reaches this page
# from a link has no other way to find the companion project, and the contrast
# between the two - the same access rule enforced at different boundaries
# because the runtimes differ - is the part worth seeing.
# --------------------------------------------------------------------------

st.divider()
st.markdown(
    "**Companion project — "
    "[fulfillment-ops-mcp](https://github.com/yfh227/fulfillment-ops-mcp)**  \n"
    "A Model Context Protocol server in TypeScript exposing six role-mapped "
    "tools over stdio, so an AI client like Claude Desktop can call them "
    "directly. Each role sees only its permitted tools, and every tool checks "
    "the role again before returning data."
)
st.caption(
    "It carries the same constraint as this app: whoever calls a tool controls "
    "that tool's inputs, so the caller's role is never a tool parameter. This "
    "app injects role from an authenticated session; the MCP server has no "
    "session layer, so it fixes the role at the process boundary from the "
    "environment instead. Same rule, different enforcement point."
)
st.caption(
    "Source for this app: "
    "[fulfillment-ops-assistant](https://github.com/yfh227/fulfillment-ops-assistant)"
)


if __name__ == "__main__":
    pass
