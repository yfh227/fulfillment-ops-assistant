"""Mechanical eval harness for the fulfillment ops assistant.

Scoring is pure substring matching — no LLM grading — so a given answer always
produces the same verdict. All prompt and call logic is imported from core.py;
nothing here duplicates it.

Run:  python eval.py       (exit 0 if all cases pass, 1 otherwise)
"""

import hashlib
import sys
import tomllib
from pathlib import Path

from core import (
    SYSTEM_PROMPT,
    ask,
    build_context,
    get_bedrock_client,
    get_s3_client,
    load_documents,
)

CASES = [
    {
        "name": "Documented internal process",
        "question": "What's the process for a receiving discrepancy?",
        "expect_citation": "01_receiving_discrepancy_sop.md",
        "should_refuse": False,
        "should_flag": False,
        "must_contain": None,
    },
    {
        "name": "Documented financial decision",
        "question": (
            "Should we issue a $15,000 credit to a client disputing a "
            "storage charge?"
        ),
        "expect_citation": "06_billing_dispute_policy.md",
        "should_refuse": False,
        "should_flag": True,
        "must_contain": None,
    },
    {
        "name": "Topic absent from documents",
        "question": "What is the company's parental leave policy?",
        "expect_citation": None,
        "should_refuse": True,
        "should_flag": False,
        "must_contain": None,
    },
    {
        "name": "Mixed coverage",
        "question": "What's the dispute window, and what late fee applies after it?",
        "expect_citation": "06_billing_dispute_policy.md",
        "should_refuse": True,
        "should_flag": True,
        "must_contain": None,
    },
    {
        "name": "Cross-document synthesis",
        "question": (
            "If a receiving discrepancy leads to a billing dispute, what happens?"
        ),
        "expect_citation": "01_receiving_discrepancy_sop.md",
        "should_refuse": False,
        "should_flag": True,
        "must_contain": None,
    },
    {
        "name": "False premise correction",
        "question": (
            "Since we offer free expedited shipping on all enterprise "
            "accounts, how do I apply it?"
        ),
        "expect_citation": None,
        "should_refuse": True,
        # A false premise about free shipping is money-adjacent, so rule 4's
        # "err toward flagging" correctly applies.
        "should_flag": True,
        "must_contain": None,
    },
    {
        "name": "Exact figure recall",
        "question": "What is the monthly pallet storage rate?",
        "expect_citation": "02_billing_rate_card.md",
        "should_refuse": False,
        "should_flag": True,
        # Verbatim from 02_billing_rate_card.md: "| Pallet position | $28.00 / month |"
        "must_contain": "$28.00",
    },
    {
        "name": "Client-facing, non-financial",
        "question": (
            "Draft a message telling a client their inbound shipment "
            "arrived damaged."
        ),
        "expect_citation": None,
        "should_refuse": False,
        "should_flag": True,
        "must_contain": None,
    },
]

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
)

FLAG_MARKER = "NEEDS HUMAN REVIEW"

# A refusal phrase buried deep in a long answer is a scope caveat ("what the
# documents do not cover"), not a refusal. Measured over repeated runs: genuine
# refusals ran 55-188 words, while complete answers that merely note a limit ran
# 441-591. 250 sits in that gap. Position alone cannot separate them - a real
# partial refusal was seen at 40.8% while a false positive appeared at 33.8%.
REFUSAL_MAX_WORDS = 250
REFUSAL_HEAD_FRACTION = 0.15


def _credentials() -> tuple[str | None, str | None]:
    """Read AWS creds from Streamlit secrets; fall back to boto3's own chain."""
    path = Path(__file__).parent / ".streamlit" / "secrets.toml"
    if not path.exists():
        return None, None
    with open(path, "rb") as f:
        secrets = tomllib.load(f)
    return secrets.get("AWS_ACCESS_KEY_ID"), secrets.get("AWS_SECRET_ACCESS_KEY")


def refused(answer: str) -> bool:
    """True only when a refusal phrase signals an actual refusal.

    Counts as a refusal when the phrase appears in the opening of the answer,
    or when the answer is short overall. A phrase appearing late in a long
    answer is treated as a scope caveat within a complete answer.
    """
    lowered = answer.lower()
    positions = [lowered.find(p) for p in REFUSAL_PHRASES if p in lowered]
    if not positions:
        return False
    if len(answer.split()) < REFUSAL_MAX_WORDS:
        return True
    return (min(positions) / len(answer)) <= REFUSAL_HEAD_FRACTION


def grade(case: dict, answer: str) -> dict[str, bool | None]:
    """Return each check's verdict; None means the check does not apply."""
    checks: dict[str, bool | None] = {}

    if case["expect_citation"]:
        checks["cite"] = case["expect_citation"] in answer
    else:
        checks["cite"] = None

    # Checked in both directions: refusing when it shouldn't is also a failure.
    checks["refuse"] = refused(answer) == case["should_refuse"]

    checks["flag"] = (FLAG_MARKER in answer) == case["should_flag"]

    if case["must_contain"]:
        checks["contain"] = case["must_contain"] in answer
    else:
        checks["contain"] = None

    return checks


def mark(verdict: bool | None) -> str:
    if verdict is None:
        return "-"
    return "ok" if verdict else "FAIL"


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    key_id, secret = _credentials()
    s3_client = get_s3_client(key_id, secret)
    bedrock_client = get_bedrock_client(key_id, secret)

    documents = load_documents(s3_client)
    context = build_context(documents)

    prompt_sha = hashlib.sha256(SYSTEM_PROMPT.encode("utf-8")).hexdigest()[:12]
    print(f"documents     : {len(documents)}")
    print(f"context chars : {len(context):,}")
    print(f"prompt sha256 : {prompt_sha} ({len(SYSTEM_PROMPT):,} chars)")
    print()

    header = (
        f"{'CASE':<31} {'CITE':<6} {'REFUSE':<7} {'FLAG':<6} "
        f"{'CONTAIN':<8} {'LATENCY':>8}  RESULT"
    )
    print(header)
    print("-" * len(header))

    results = []
    for case in CASES:
        result = ask(case["question"], context, bedrock_client)
        answer = result["answer"]
        checks = grade(case, answer)
        passed = all(v for v in checks.values() if v is not None)
        results.append((case, checks, passed, answer, result))

        print(
            f"{case['name']:<31} "
            f"{mark(checks['cite']):<6} "
            f"{mark(checks['refuse']):<7} "
            f"{mark(checks['flag']):<6} "
            f"{mark(checks['contain']):<8} "
            f"{result['latency_ms']:>6} ms  "
            f"{'PASS' if passed else 'FAIL'}"
        )

    failures = [r for r in results if not r[2]]
    if failures:
        print()
        print("=" * len(header))
        print("FAILURE DETAIL")
        print("=" * len(header))
        for case, checks, _, answer, _result in failures:
            failed = [name for name, v in checks.items() if v is False]
            print()
            print(f"{case['name']} — failed: {', '.join(failed)}")
            print(f"  Q: {case['question']}")
            if "cite" in failed:
                print(f"  expected citation : {case['expect_citation']} (absent)")
            if "refuse" in failed:
                print(
                    f"  should_refuse     : {case['should_refuse']} "
                    f"but refusal detected = {refused(answer)}"
                )
            if "flag" in failed:
                print(
                    f"  should_flag       : {case['should_flag']} "
                    f"but marker present = {FLAG_MARKER in answer}"
                )
            if "contain" in failed:
                print(f"  must_contain      : {case['must_contain']!r} (absent)")
            print("  --- answer ---")
            for line in answer.strip().splitlines():
                print(f"  {line}")

    passed_count = sum(1 for r in results if r[2])
    total_ms = sum(r[4]["latency_ms"] for r in results)
    total_in = sum(r[4]["input_tokens"] or 0 for r in results)
    total_out = sum(r[4]["output_tokens"] or 0 for r in results)

    print()
    print(
        f"totals: {total_ms:,} ms · {total_in:,} in / {total_out:,} out tokens"
    )
    print(f"{passed_count}/{len(CASES)} PASSED")

    return 0 if passed_count == len(CASES) else 1


if __name__ == "__main__":
    sys.exit(main())
