"""Role-based access eval: every role against every question, in both modes.

Separate from eval.py, which grades answer quality against the full corpus.
This grades *access*: whether a role gets an answer, an access denial, or an
ordinary refusal - and, for the answers, whether anything it cited was outside
its permitted set.

Three outcomes are graded, because collapsing any two of them is the failure
this whole part exists to prevent:

    ANSWER   answered normally, no denial, nothing restricted cited
    DENIED   the Part 4 access message, and no model call made
    REFUSE   ordinary "not in any document" refusal - the corpus really is silent

Expectations are written out per role rather than derived from
core.ROLE_DOCUMENTS, so a wrong mapping cannot satisfy the test by agreeing
with itself.

    python eval_roles.py [--mode direct|retrieval|both]
"""

import argparse
import sys
import tomllib
from pathlib import Path

from core import (
    CONTENT_ROLES,
    ROLE_ACCOUNT,
    ROLE_ADMIN,
    ROLE_BILLING,
    ROLE_WAREHOUSE,
    access_denied_message,
    ask,
    build_context,
    cited_docs,
    get_bedrock_client,
    get_s3_client,
    get_documents_for_role,
    load_documents,
    permitted_sources,
    refused,
)

ANSWER, DENIED, REFUSE = "ANSWER", "DENIED", "REFUSE"

# Each question names the document that actually answers it, so a failure is
# traceable to a mapping decision rather than to phrasing.
QUESTIONS = [
    {
        "name": "billing dispute window",
        "source": "06_billing_dispute_policy.md (billing only)",
        "question": "How long does a client have to raise a billing dispute, "
                    "and what happens if they miss that window?",
        "expect": {ROLE_BILLING: ANSWER, ROLE_WAREHOUSE: DENIED,
                   ROLE_ACCOUNT: DENIED, ROLE_ADMIN: ANSWER},
    },
    {
        "name": "cycle count frequency",
        "source": "04_cycle_count_policy.md (warehouse only)",
        "question": "How frequently must cycle counts be performed, and who "
                    "signs off on a variance?",
        "expect": {ROLE_BILLING: DENIED, ROLE_WAREHOUSE: ANSWER,
                   ROLE_ACCOUNT: DENIED, ROLE_ADMIN: ANSWER},
    },
    {
        "name": "escalation tiers",
        "source": "03_escalation_matrix.md (account only)",
        "question": "What are the escalation tiers and the response time "
                    "expected at each one?",
        "expect": {ROLE_BILLING: DENIED, ROLE_WAREHOUSE: DENIED,
                   ROLE_ACCOUNT: ANSWER, ROLE_ADMIN: ANSWER},
    },
    {
        "name": "reno putaway process",
        "source": "07_reno_putaway_sop.md (warehouse only)",
        "question": "What is the putaway process at the Reno facility?",
        "expect": {ROLE_BILLING: DENIED, ROLE_WAREHOUSE: ANSWER,
                   ROLE_ACCOUNT: DENIED, ROLE_ADMIN: ANSWER},
    },
    {
        "name": "northwind negotiated rates",
        "source": "17_enterprise_rate_schedule_northwind.md (account only)",
        "question": "What storage and pick rates were negotiated for Northwind "
                    "Provisions?",
        "expect": {ROLE_BILLING: DENIED, ROLE_WAREHOUSE: DENIED,
                   ROLE_ACCOUNT: ANSWER, ROLE_ADMIN: ANSWER},
    },
    {
        "name": "standard tier rate card",
        "source": "02_billing_rate_card.md (billing only)",
        "question": "What does the standard-tier rate card charge for "
                    "receiving and storage?",
        "expect": {ROLE_BILLING: ANSWER, ROLE_WAREHOUSE: DENIED,
                   ROLE_ACCOUNT: DENIED, ROLE_ADMIN: ANSWER},
    },
    {
        # The deliberate all-roles-restricted case. Doc 14 belongs to no
        # content role, so this is the one question where denial is correct for
        # everyone except admin - and the corpus does contain the answer, which
        # is what separates it from the absent case below.
        "name": "fernpost onboarding escalation",
        "source": "14_onboarding_case_standard_fernpost.md (no role)",
        "question": "Why was Fernpost Paper's onboarding escalated after "
                    "go-live, and what was the resolution?",
        "expect": {ROLE_BILLING: DENIED, ROLE_WAREHOUSE: DENIED,
                   ROLE_ACCOUNT: DENIED, ROLE_ADMIN: ANSWER},
    },
    {
        # The control that proves DENIED and REFUSE are genuinely different.
        # Nothing in the corpus covers this, so every role - admin included -
        # must get the ordinary refusal, never the access message.
        "name": "absent from corpus",
        "source": "not in any document",
        "question": "What is Meridian's parental leave policy for warehouse "
                    "staff?",
        "expect": {ROLE_BILLING: REFUSE, ROLE_WAREHOUSE: REFUSE,
                   ROLE_ACCOUNT: REFUSE, ROLE_ADMIN: REFUSE},
    },
]

ROLES = (*CONTENT_ROLES, ROLE_ADMIN)


def _credentials() -> tuple[str | None, str | None]:
    """Read AWS creds from Streamlit secrets; fall back to boto3's own chain."""
    path = Path(__file__).parent / ".streamlit" / "secrets.toml"
    if not path.exists():
        return None, None
    with open(path, "rb") as f:
        secrets = tomllib.load(f)
    return secrets.get("AWS_ACCESS_KEY_ID"), secrets.get("AWS_SECRET_ACCESS_KEY")


def classify(result: dict, role: str) -> str:
    """What actually came back, in the same vocabulary as `expect`."""
    if result.get("access_denied"):
        return DENIED
    return REFUSE if refused(result["answer"]) else ANSWER


def leaked(answer: str, role: str, all_names: list[str]) -> list[str]:
    """Restricted filenames the answer cited. Must always be empty."""
    permitted = permitted_sources(role)
    if permitted is None:
        return []
    return [d for d in cited_docs(answer, all_names) if d not in permitted]


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("direct", "retrieval", "both"),
                        default="both")
    args = parser.parse_args()
    modes = (("direct", "retrieval") if args.mode == "both" else (args.mode,))

    key_id, secret = _credentials()
    bedrock = get_bedrock_client(key_id, secret)
    documents = load_documents(get_s3_client(key_id, secret))
    all_names = [k for k, _ in documents]

    print(f"documents : {len(documents)}")
    print(f"roles     : {', '.join(ROLES)}")
    print(f"questions : {len(QUESTIONS)}")
    print(f"modes     : {', '.join(modes)}")
    print(f"total runs: {len(QUESTIONS) * len(ROLES) * len(modes)}")

    rows, failures = [], []
    for mode in modes:
        use_retrieval = mode == "retrieval"
        print()
        header = (f"{'QUESTION':<32}{'ROLE':<17}{'EXPECT':<8}{'GOT':<8}"
                  f"{'CALLED':<8}{'LEAK':<6}RESULT")
        print(f"--- {mode.upper()} " + "-" * (len(header) - len(mode) - 5))
        print(header)

        for case in QUESTIONS:
            for role in ROLES:
                visible = get_documents_for_role(role, documents)
                result = ask(
                    case["question"],
                    None if use_retrieval else build_context(visible),
                    bedrock,
                    use_cache=not use_retrieval,
                    use_retrieval=use_retrieval,
                    role=role,
                )
                got = classify(result, role)
                expect = case["expect"][role]
                spill = leaked(result["answer"], role, all_names)
                called = bool(result.get("latency_ms"))

                if expect == DENIED:
                    # A denial must be exact and free: the pre-check returns
                    # before Claude is reached, so any model call is a defect.
                    ok = (got == DENIED and not called and not spill
                          and result["answer"] == access_denied_message(role))
                elif expect == ANSWER:
                    # Graded on ACCESS, not completeness: the question must
                    # reach the model and cite nothing restricted.
                    #
                    # Whether the model then self-reports partial coverage is
                    # answer quality, which eval.py owns. Under retrieval a
                    # partial self-report is expected rather than wrong - the
                    # model sees fragments of a long SOP instead of the whole
                    # document. Measured on the Reno putaway question: 4 of 5
                    # retrieval runs self-report REFUSED: yes while answering
                    # substantively and citing correctly, against 0 of 5 in
                    # direct context. Failing those would be grading the
                    # known direct-vs-retrieval difference as an access bug.
                    ok = got != DENIED and not spill
                else:  # REFUSE - genuine absence must not read as a denial
                    ok = got == REFUSE and not spill

                rows.append((mode, case, role, expect, got, spill, called, ok,
                             result))
                if not ok:
                    failures.append((mode, case, role, expect, got, spill,
                                     called, result))

                print(f"{case['name'][:31]:<32}{role:<17}{expect:<8}{got:<8}"
                      f"{('yes' if called else 'no'):<8}"
                      f"{(str(len(spill)) if spill else '-'):<6}"
                      f"{'PASS' if ok else 'FAIL'}")

    if failures:
        print("\n" + "=" * 72)
        print("FAILURE DETAIL")
        print("=" * 72)
        for mode, case, role, expect, got, spill, called, result in failures:
            print(f"\n[{mode}] {case['name']} as {role}")
            print(f"  source   : {case['source']}")
            print(f"  Q        : {case['question']}")
            print(f"  expected : {expect}   got: {got}   model called: {called}")
            if spill:
                print(f"  LEAKED   : {spill}")
            print("  --- answer ---")
            for line in result["answer"].strip().splitlines()[:20]:
                print(f"  {line}")

    passed = sum(1 for r in rows if r[7])
    calls = sum(1 for r in rows if r[6])
    tot_in = sum(r[8].get("total_input_tokens") or 0 for r in rows)
    tot_out = sum(r[8].get("output_tokens") or 0 for r in rows)
    any_leak = [r for r in rows if r[5]]

    print("\n" + "=" * 72)
    print(f"{passed}/{len(rows)} PASSED   ·   {calls} model calls   ·   "
          f"{tot_in:,} in / {tot_out:,} out tokens")
    print(f"restricted-document citations: {len(any_leak)} (must be 0)")
    return 0 if passed == len(rows) else 1


if __name__ == "__main__":
    sys.exit(main())
