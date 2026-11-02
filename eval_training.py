"""Tests for the training modules, and the measurement of the grader.

    python eval_training.py                     # both suites
    python eval_training.py --suite offline     # no model, no network
    python eval_training.py --suite grader      # real Bedrock calls
    python eval_training.py --suite grader --repeat 3
    python eval_training.py --suite grader --control always-pass

OFFLINE checks everything decided in code: the task checks, the quote check,
evidence verification, the pre-check, fail-closed grading, the spend cap's
counting, the completion metrics, and the module file itself.

GRADER runs every labelled answer in training_grader_cases.json through the
real grader and compares its verdict with the human label. A false pass - the
grader passing an answer labelled as failing - is the error that matters most,
because it certifies someone who has not shown the understanding. The suite
fails on any disagreement.

--control always-pass swaps in a grader that marks every criterion met with
genuine evidence from the answer. It must make the grader suite FAIL; if it
does not, the labelled set cannot tell a working grader from a broken one.
"""

import argparse
import json
import sys
import tempfile
import tomllib
from pathlib import Path

import core
import spend_guard
import stats
import training
import usage_log

ROOT = Path(__file__).parent
CASES_PATH = ROOT / "training_grader_cases.json"

passed = failed = 0


def check(label: str, ok: bool, detail: str = "") -> None:
    global passed, failed
    if ok:
        passed += 1
    else:
        failed += 1
    print(f"  [{'PASS' if ok else 'FAIL'}] {label}" + (f"  -- {detail}" if not ok and detail else ""))


# --------------------------------------------------------------------------
# Offline suite
# --------------------------------------------------------------------------

def _result(answer="", denied=False):
    return {"answer": answer, "access_denied": denied}


CITED = "Meridian runs 3 facilities (00_company_profile.md).\nREFUSED: no"
REFUSAL = "I don't know. The documents do not cover this.\nREFUSED: yes"
FLAGGED = ("Growth tier (00_company_profile.md).\n⚠️ NEEDS HUMAN REVIEW — client "
           "commitment\nREFUSED: no")
DENIED = core.access_denied_message(core.ROLE_PUBLIC)
VISIBLE = ["00_company_profile.md"]


def offline_task_checks():
    print("\n1. Task checks (what the assistant actually did)")
    t = training.check_task
    check("cite: cited answer passes", t("cited_answer", _result(CITED), VISIBLE)[0])
    check("cite: refusal fails", not t("cited_answer", _result(REFUSAL), VISIBLE)[0])
    check("cite: access notice fails", not t("cited_answer", _result(DENIED, True), VISIBLE)[0])
    check("cite: uncited answer fails",
          not t("cited_answer", _result("Three facilities.\nREFUSED: no"), VISIBLE)[0])
    check("cite: citing a document the role cannot see does not count",
          not t("cited_answer", _result("Rates (02_billing_rate_card.md).\nREFUSED: no"), VISIBLE)[0])
    check("refusal: refusal passes", t("refused", _result(REFUSAL), VISIBLE)[0])
    check("refusal: answer fails", not t("refused", _result(CITED), VISIBLE)[0])
    check("refusal: access notice is not a refusal",
          not t("refused", _result(DENIED, True), VISIBLE)[0])
    check("access: access notice passes", t("access_denied", _result(DENIED, True), VISIBLE)[0])
    check("access: plain refusal fails", not t("access_denied", _result(REFUSAL), VISIBLE)[0])
    check("access: answer fails", not t("access_denied", _result(CITED), VISIBLE)[0])
    check("review: flagged answer passes", t("review_flagged", _result(FLAGGED), VISIBLE)[0])
    check("review: unflagged answer fails", not t("review_flagged", _result(CITED), VISIBLE)[0])
    # The notice text never carries the marker, but the rule is structural:
    # a denial is not an answer, whatever its text.
    check("review: access notice fails even if it contained the marker",
          not t("review_flagged", _result("NEEDS HUMAN REVIEW", True), VISIBLE)[0])
    try:
        t("nonsense", _result(CITED), VISIBLE)
        check("unknown check raises", False)
    except ValueError:
        check("unknown check raises", True)


def offline_quote_checks():
    print("\n2. Quote check (module 'cite')")
    profile = (ROOT / "docs" / "00_company_profile.md").read_text(encoding="utf-8")
    other = ("99_other.md", "The warehouse floor is swept every single evening by the night crew.")
    vis = [("00_company_profile.md", profile), other]
    cited = ["00_company_profile.md"]
    q = training.check_quote
    check("exact sentence passes",
          q("Meridian serves three client tiers, and service levels differ by tier", cited, vis)[0])
    check("table row copied from the rendered page (tabs, no pipes or bold) passes",
          q("Facilities\t3 (Richmond VA, Columbus OH, Reno NV)", cited, vis)[0])
    check("raw markdown table row passes",
          q("| **Facilities** | 3 (Richmond VA, Columbus OH, Reno NV) |", cited, vis)[0])
    check("curly quotes and trailing period tolerated",
          q("“Meridian serves three client tiers, and service levels differ by tier.”", cited, vis)[0])
    check("text not in the document fails",
          not q("Meridian operates five facilities across the western United States", cited, vis)[0])
    check("a real sentence from a document the answer did NOT cite fails",
          not q("The warehouse floor is swept every single evening", cited, vis)[0])
    check("too short fails", not q("Reno NV", cited, vis)[0])
    check("no citation to check against fails",
          not q("Meridian serves three client tiers, and service levels differ by tier", [], vis)[0])


MODULE = {"rubric": [{"id": "a", "label": "A", "criterion": "x"},
                     {"id": "b", "label": "B", "criterion": "y"}]}
REFLECTION = "A guess could be wrong and still get acted on. Ask the owner."


def offline_verification():
    print("\n3. Evidence verification (the grader cannot pass on evidence it cannot point to)")
    v = training.verify_grading
    good = v(MODULE, REFLECTION, {"criteria": [
        {"id": "a", "met": True, "evidence": "could be wrong and still get acted on"},
        {"id": "b", "met": True, "evidence": "Ask the owner"}]})
    check("met with real quotes -> both met", all(c["met"] for c in good))
    fab = v(MODULE, REFLECTION, {"criteria": [
        {"id": "a", "met": True, "evidence": "could be wrong and still get acted on"},
        {"id": "b", "met": True, "evidence": "escalate to a responsible manager"}]})
    check("fabricated evidence -> criterion rejected", not fab[1]["met"] and fab[1]["evidence_rejected"])
    omitted = v(MODULE, REFLECTION, {"criteria": [
        {"id": "a", "met": True, "evidence": "could be wrong"}]})
    check("criterion the grader omitted -> not met", not omitted[1]["met"])
    one_word = v(MODULE, REFLECTION, {"criteria": [
        {"id": "a", "met": True, "evidence": "guess"}, {"id": "b", "met": True, "evidence": "owner"}]})
    check("single-word evidence -> rejected", not any(c["met"] for c in one_word))
    string_true = v(MODULE, REFLECTION, {"criteria": [
        {"id": "a", "met": "true", "evidence": "could be wrong"}]})
    check('met given as the string "true" -> not met', not string_true[0]["met"])
    check("malformed criteria list -> nothing met",
          not any(c["met"] for c in v(MODULE, REFLECTION, {"criteria": "all met"})))

    print("\n4. Pre-check and fail-closed grading")
    check("short reflection rejected before any model call",
          training.precheck_reflection("too short") is not None)
    check("overlong reflection rejected",
          training.precheck_reflection("word " * 400) is not None)
    check("normal reflection accepted", training.precheck_reflection(REFLECTION) is None)

    class Stub:
        def __init__(self, text):
            self.text = text

        def converse(self, **kw):
            self.kw = kw
            return {"output": {"message": {"content": [{"text": self.text}]}},
                    "usage": {"inputTokens": 1, "outputTokens": 1}}

    real = {"rubric": MODULE["rubric"], "title": "t", "reflection": "q"}
    g = training.grade_reflection(real, REFLECTION, Stub("I think this answer is great!"))
    check("unreadable grader reply -> not passed, error recorded",
          g["passed"] is False and g["error"])
    fenced = Stub('```json\n{"criteria": [{"id": "a", "met": true, "evidence": "could be wrong"},'
                  ' {"id": "b", "met": true, "evidence": "Ask the owner"}], "feedback": "ok"}\n```')
    g = training.grade_reflection(real, REFLECTION, fenced)
    check("JSON inside a code fence is read", g["passed"] is True and g["error"] is None)
    check("grader runs at temperature 0 with capped output",
          fenced.kw["inferenceConfig"] == {"maxTokens": training.GRADER_MAX_TOKENS, "temperature": 0})
    check("trainee text is wrapped as data in the prompt",
          f"<trainee_answer>\n{REFLECTION}\n</trainee_answer>" in fenced.kw["messages"][0]["content"][0]["text"])


def offline_metrics():
    print("\n5. Spend cap counting and completion metrics (temporary database)")
    ids = ["cite", "refusal", "access", "review"]
    # ignore_cleanup_errors: the project's `with sqlite3.connect()` commits but
    # does not close, and Windows will not delete a file with an open handle.
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as d:
        db = Path(d) / "t.db"
        log = lambda *a, **k: usage_log.log_training(*a, db_path=db, **k)
        before = spend_guard.calls_today(db)
        log("s1", "public_viewer", "refusal", "reflection", True, "model")
        log("s1", "public_viewer", "cite", "reflection", True, "code")
        log("s1", "public_viewer", "cite", "task", True, "code")
        check("model-graded attempt counts against the daily cap; code-checked ones do not",
              spend_guard.calls_today(db) - before == 1,
              f"counted {spend_guard.calls_today(db) - before}")

        # s1: completes all four, one of them reflection-before-task order
        # and one after a failed first try.
        log("s1", "public_viewer", "refusal", "task", True, "code")
        log("s1", "public_viewer", "access", "task", True, "code")
        log("s1", "public_viewer", "access", "reflection", False, "model")
        log("s1", "public_viewer", "access", "reflection", True, "model")
        log("s1", "public_viewer", "review", "task", True, "code")
        log("s1", "public_viewer", "review", "reflection", True, "model")
        # s2: task passed, reflection never passed; then a grader error.
        log("s2", "public_viewer", "cite", "task", True, "code")
        log("s2", "public_viewer", "cite", "reflection", False, "code")
        log("s3", "public_viewer", "review", "task", True, "code")
        log("s3", "public_viewer", "review", "reflection", False, "model", error="boom")
        t = stats.training_summary(ids, db)
        check("3 learners", t["learners"] == 3, str(t["learners"]))
        check("4 module completions (all s1; s2 and s3 never passed a reflection)",
              t["module_completions"] == 4, str(t["module_completions"]))
        check("1 course completion", t["course_completions"] == 1)
        # s1: refusal, cite, review passed first try; access failed first.
        # s2/cite and s3/review failed. 3 of 6.
        check("first-try written answers: 6 learner-modules, 3 passed first try",
              (t["first_try_reflections"], t["first_try_passed"]) == (6, 3),
              str((t["first_try_reflections"], t["first_try_passed"])))
        check("grader calls 5, errors 1", (t["grader_calls"], t["grader_errors"]) == (5, 1),
              str((t["grader_calls"], t["grader_errors"])))
        check("per-module: review started by 2, completed by 1",
              t["per_module"]["review"] == {"started": 2, "completed": 1})
        out = stats.write_summary(db, Path(d) / "summary.md")
        text = out.read_text(encoding="utf-8")
        check("adoption summary gains a Training section",
              "## Training" in text and "Completed the full course:** 1" in text)
    check("missing database -> zeros, and no file created",
          stats.training_summary(ids, Path(tempfile.gettempdir()) / "nope_x.db")["learners"] == 0
          and not (Path(tempfile.gettempdir()) / "nope_x.db").exists())


def offline_module_file():
    print("\n6. Module file")
    course = training.load_course()
    ids = training.module_ids(course)
    check("four modules, unique ids", len(ids) == 4 and len(set(ids)) == 4, str(ids))
    known = {"cited_answer", "refused", "access_denied", "review_flagged"}
    for m in course["modules"]:
        ok = (m["check"] in known and m.get("suggestion") and m.get("lesson")
              and m["grading"] in ("quote", "rubric")
              and (m["grading"] == "quote" or len(m.get("rubric", [])) >= 2))
        check(f"module '{m['id']}' complete and well-formed", bool(ok))
    cases = json.loads(CASES_PATH.read_text(encoding="utf-8"))["cases"]
    rubric_ids = {m["id"]: {c["id"] for c in m.get("rubric", [])} for m in course["modules"]}
    bad = [c for c in cases if c["module"] not in rubric_ids
           or not set(c["missing"]) <= rubric_ids[c["module"]]
           or c["expect_pass"] == bool(c["missing"])]
    check("every labelled case names a real module and real criteria, and its "
          "label agrees with its missing list", not bad, str(bad[:1]))
    graded = [m["id"] for m in course["modules"] if m["grading"] == "rubric"]
    for mid in graded:
        mc = [c for c in cases if c["module"] == mid]
        check(f"'{mid}' has passing, failing and injection cases",
              any(c["expect_pass"] for c in mc) and any(not c["expect_pass"] for c in mc)
              and any(c["kind"].startswith("injection") for c in mc))


# --------------------------------------------------------------------------
# Grader suite
# --------------------------------------------------------------------------

class AlwaysPass:
    """A grader that marks every criterion met, quoting the answer's own first
    words as evidence - so it survives evidence verification. The worst
    realistic grader: confident, well-formed, and wrong."""

    def __init__(self, module, text):
        self.module, self.text = module, text

    def converse(self, **kw):
        ev = " ".join(self.text.split()[:4])
        body = {"criteria": [{"id": c["id"], "met": True, "evidence": ev}
                             for c in self.module["rubric"]], "feedback": "Great."}
        return {"output": {"message": {"content": [{"text": json.dumps(body)}]}},
                "usage": {"inputTokens": 0, "outputTokens": 0}}


def grader_suite(repeat: int, control: str | None) -> dict:
    course = {m["id"]: m for m in training.load_course()["modules"]}
    cases = json.loads(CASES_PATH.read_text(encoding="utf-8"))["cases"]
    client = None
    if control is None:
        s = tomllib.load(open(ROOT / ".streamlit" / "secrets.toml", "rb"))
        client = core.get_bedrock_client(s["AWS_ACCESS_KEY_ID"], s["AWS_SECRET_ACCESS_KEY"])

    print(f"\nGRADER: {len(cases)} labelled answers x {repeat} run(s)"
          + (f"   [CONTROL: {control}]" if control else ""))
    tally = {"agree": 0, "false_pass": 0, "false_fail": 0, "errors": 0,
             "crit_agree": 0, "crit_total": 0, "evidence_rejected": 0,
             "in_tokens": 0, "out_tokens": 0, "unstable": 0}
    for case in cases:
        module = course[case["module"]]
        verdicts = []
        for _ in range(repeat):
            c = AlwaysPass(module, case["text"]) if control else client
            g = training.grade_reflection(module, case["text"], c)
            tally["in_tokens"] += g.get("input_tokens") or 0
            tally["out_tokens"] += g.get("output_tokens") or 0
            if g["error"]:
                tally["errors"] += 1
            verdicts.append(g["passed"])
            agree = g["passed"] == case["expect_pass"]
            tally["agree"] += agree
            if g["passed"] and not case["expect_pass"]:
                tally["false_pass"] += 1
            if not g["passed"] and case["expect_pass"]:
                tally["false_fail"] += 1
            missing_expected = set(case["missing"])
            for cr in g["criteria"]:
                tally["crit_total"] += 1
                tally["crit_agree"] += (not cr["met"]) == (cr["id"] in missing_expected)
                tally["evidence_rejected"] += cr["evidence_rejected"]
        if len(set(verdicts)) > 1:
            tally["unstable"] += 1
        mark = "ok " if all(v == case["expect_pass"] for v in verdicts) else "XX "
        unmet = [cr["id"] for cr in g["criteria"] if not cr["met"]]
        print(f"  {mark}{case['module']:<8} {case['kind']:<18} expect "
              f"{'PASS' if case['expect_pass'] else 'fail'}  got "
              f"{'/'.join('PASS' if v else 'fail' for v in verdicts):<15} unmet={unmet}"
              + (f"  ERROR {g['error']}" if g["error"] else ""))

    n = len(cases) * repeat
    print(f"\n  pass/fail agreement : {tally['agree']}/{n}")
    print(f"  false passes        : {tally['false_pass']}   (failing answer certified)")
    print(f"  false fails         : {tally['false_fail']}")
    print(f"  criterion agreement : {tally['crit_agree']}/{tally['crit_total']}")
    print(f"  evidence rejected   : {tally['evidence_rejected']}")
    print(f"  unstable cases      : {tally['unstable']} (verdict changed across runs)")
    print(f"  grader errors       : {tally['errors']}")
    print(f"  tokens              : {tally['in_tokens']:,} in / {tally['out_tokens']:,} out")
    check("grader agrees with every label", tally["agree"] == n,
          f"{n - tally['agree']} disagreement(s)")
    check("no grader errors", tally["errors"] == 0)
    return tally


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--suite", choices=("offline", "grader", "all"), default="all")
    p.add_argument("--repeat", type=int, default=1)
    p.add_argument("--control", choices=("always-pass",))
    args = p.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")

    if args.suite in ("offline", "all") and not args.control:
        offline_task_checks()
        offline_quote_checks()
        offline_verification()
        offline_metrics()
        offline_module_file()
    if args.suite in ("grader", "all") or args.control:
        grader_suite(args.repeat, args.control)

    print(f"\n{passed + failed} checks - {passed} passed, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
