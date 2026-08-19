"""Tool-use agent for fulfillment exception handling (V5 Phase 1).

The agent investigates a stuck order by calling tools rather than answering
from context, then either resolves it directly or drafts an escalation for a
human to approve. Diagnose -> decide -> act, not a single Q&A turn.

Three things are load-bearing and none are a later hardening pass:

1. ROLE IS NEVER IN A TOOL SCHEMA. The model populates `input` from its own
   reasoning over conversation text, and the corpus is full of documents that
   name roles - "the Warehouse Lead should verify putaway location" is exactly
   the kind of sentence that could be pattern-matched into a role argument.
   If role were a schema property the model would be choosing the caller's
   identity, which is privilege escalation straight through the guardrail.
   The executor injects role from the session; the model never sees or supplies
   it.

2. TOOLS ARE THE THIRD PATH AROUND ROLE ACCESS. V4 Part 3 caught this shape
   once already: document filtering worked while retrieval was an unrestricted
   way around it. A tool that reads operational data without knowing the caller
   would hand a Billing Analyst warehouse data that ROLE_DOCUMENTS denies them
   through the corpus. Every tool takes `role` as a required parameter - not
   optional, not defaulted to None, because a default recreates the situation
   where a guard silently never fires.

3. THE LOOP IS BOUNDED. A tool-calling loop with no turn cap can run away on
   cost. MAX_TURNS ends it and says so rather than looping.
"""

import json
import time

import core
import ops_data

# --------------------------------------------------------------------------
# Tool names
# --------------------------------------------------------------------------

TOOL_ORDER_STATUS = "get_order_status"
TOOL_CHECK_INVENTORY = "check_inventory"
TOOL_DRAFT_ESCALATION = "draft_escalation"

ALL_TOOLS = (TOOL_ORDER_STATUS, TOOL_CHECK_INVENTORY, TOOL_DRAFT_ESCALATION)


# --------------------------------------------------------------------------
# Role -> tool permissions
#
# A second mapping, deliberately separate from core.ROLE_DOCUMENTS. That one
# maps roles to .md filenames; order records are not documents, and forcing
# operational data into a document-name mapping would be the wrong shape.
# Written down explicitly rather than inferred, same as the V4 mapping.
#
# Derivation, mirroring the ownership logic V4 used on document metadata:
#
#   get_order_status   A per-order operational record. Owned by facility
#                      operations (Warehouse Lead) and by client-facing account
#                      handling (Account Manager). Billing is denied: its
#                      corpus scope is the rate card, the dispute policy and
#                      periodic accuracy reports, none of which are per-order
#                      operational records - and it holds no receiving,
#                      putaway or peak-season SOP in ROLE_DOCUMENTS either.
#
#   check_inventory    A live stock position at a facility, owned by Facility
#                      Managers -> Warehouse Lead only. Billing holds the
#                      inventory accuracy *reports* (19, 22, distributed to
#                      Finance), but a quarterly report is not a live stock
#                      query. Account Manager holds no inventory document at
#                      all.
#
#   draft_escalation   Produces text for a human to approve and commits
#                      nothing, so every content role may use it. It is the
#                      guardrail's output path, not a data source.
# --------------------------------------------------------------------------

ROLE_TOOLS = {
    core.ROLE_WAREHOUSE: frozenset(
        {TOOL_ORDER_STATUS, TOOL_CHECK_INVENTORY, TOOL_DRAFT_ESCALATION}),
    core.ROLE_ACCOUNT: frozenset({TOOL_ORDER_STATUS, TOOL_DRAFT_ESCALATION}),
    core.ROLE_BILLING: frozenset({TOOL_DRAFT_ESCALATION}),
    core.ROLE_ADMIN: frozenset(ALL_TOOLS),
}


def permitted_tools(role: str) -> frozenset:
    """Tools `role` may invoke. Unknown roles get nothing.

    Fails closed, consistent with core.permitted_sources: a typo'd or renamed
    role reaches no tool rather than all of them.
    """
    return ROLE_TOOLS.get(role, frozenset())


# --------------------------------------------------------------------------
# Tool schemas
#
# Note what is absent: `role`. See point 1 in the module docstring.
# --------------------------------------------------------------------------

TOOL_CONFIG = {
    "tools": [
        {"toolSpec": {
            "name": TOOL_ORDER_STATUS,
            "description": (
                "Look up the current status of a fulfillment order, including "
                "its hold reason, SLA position, value and last event."),
            "inputSchema": {"json": {
                "type": "object",
                "properties": {
                    "order_id": {
                        "type": "string",
                        "description": "Order identifier, e.g. ORD-4417.",
                    },
                },
                "required": ["order_id"],
            }},
        }},
        {"toolSpec": {
            "name": TOOL_CHECK_INVENTORY,
            "description": (
                "Check the live stock position for a SKU: on hand, allocated "
                "and available units at its facility."),
            "inputSchema": {"json": {
                "type": "object",
                "properties": {
                    "sku": {
                        "type": "string",
                        "description": "SKU identifier, e.g. MER-8821.",
                    },
                },
                "required": ["sku"],
            }},
        }},
        {"toolSpec": {
            "name": TOOL_DRAFT_ESCALATION,
            "description": (
                "Draft an escalation for human approval. Commits nothing and "
                "notifies nobody - it returns text a person must review and "
                "approve before any action is taken."),
            "inputSchema": {"json": {
                "type": "object",
                "properties": {
                    "issue_summary": {
                        "type": "string",
                        "description": "What is wrong, in one or two sentences.",
                    },
                    "recommended_action": {
                        "type": "string",
                        "description": "The specific action being recommended.",
                    },
                    "order_id": {
                        "type": "string",
                        "description": "The order this concerns, if applicable.",
                    },
                },
                "required": ["issue_summary", "recommended_action"],
            }},
        }},
    ]
}


# --------------------------------------------------------------------------
# Guardrail
# --------------------------------------------------------------------------

# Cost threshold above which a recommendation needs human sign-off. Defined
# here rather than only in the prompt so the eval and the instructions share
# one number instead of drifting apart.
ESCALATION_VALUE_THRESHOLD = 1000.0

AGENT_SYSTEM_PROMPT = f"""You are an operations agent for a third-party \
logistics (3PL) fulfillment company. You investigate stuck or exceptional \
orders and either resolve them directly or draft an escalation for a human.

Work by calling the tools available to you. Do not answer from memory or \
assumption - if you need an order's status or a stock position, call the tool. \
Never invent an order, a SKU, a quantity or a value.

HOW TO DECIDE:

1. Gather what you need. Start with the order. If the problem looks like a \
stock issue, check the SKU as well.

2. Then decide between two outcomes:

   RESOLVE DIRECTLY - state the finding and the next step, no escalation. Use \
this when the order needs no intervention (already delivered, cancelled, or \
in transit inside its SLA) or when the fix is low-stakes: under \
${ESCALATION_VALUE_THRESHOLD:,.0f} in value, inside SLA, and no client credit, \
claim or carrier loss involved.

   DRAFT AN ESCALATION - call draft_escalation. Use this when the order value \
is ${ESCALATION_VALUE_THRESHOLD:,.0f} or more, OR the SLA is breached or at \
risk, OR a client credit, damage claim or carrier loss is implied. When in \
doubt, escalate.

3. An escalation is a request for approval, not an action. It notifies nobody \
and changes nothing. Never state or imply that you have resolved, released, \
credited, reshipped or escalated anything for real - say that a draft is ready \
for review.

IF A TOOL IS REFUSED: you will get an error saying the role lacks access. \
Report that plainly and stop pursuing that line. Do not guess what the data \
would have said, and do not work around it with another tool.

A refusal does not cancel the decision in step 2. Judge the escalation \
criteria on the information you actually retrieved:

- If what you did retrieve already meets the criteria, draft the escalation \
and state what you could not check and why. Being blocked from a follow-up \
lookup is never a reason to leave a qualifying order unflagged.

- If the refusal left you with no order information at all, do not draft an \
escalation - there are no findings to escalate yet. Report the access problem \
and say who should look instead.

Be brief. Operations staff read these while doing something else."""


# --------------------------------------------------------------------------
# Tool implementations
#
# `role` is the first parameter of every tool and has no default. The executor
# supplies it from the session; it never arrives from model output.
# --------------------------------------------------------------------------

def get_order_status(role: str, order_id: str) -> dict:
    if TOOL_ORDER_STATUS not in permitted_tools(role):
        raise PermissionError(TOOL_ORDER_STATUS)
    row = ops_data.get_order(order_id)
    if row is None:
        return {"found": False, "order_id": order_id,
                "message": "No such order in the operational system."}
    return {"found": True, **row}


def check_inventory(role: str, sku: str) -> dict:
    if TOOL_CHECK_INVENTORY not in permitted_tools(role):
        raise PermissionError(TOOL_CHECK_INVENTORY)
    row = ops_data.get_sku(sku)
    if row is None:
        return {"found": False, "sku": sku,
                "message": "No such SKU in the operational system."}
    return {"found": True, **row}


def draft_escalation(role: str, issue_summary: str, recommended_action: str,
                     order_id: str = None) -> dict:
    """Return a draft. Commits nothing, notifies nobody.

    The pending-approval status is set here, in code, rather than left to the
    model to declare. The model decides *whether* to escalate - that is the
    judgement being tested - but it cannot decide that an escalation is
    already approved.
    """
    if TOOL_DRAFT_ESCALATION not in permitted_tools(role):
        raise PermissionError(TOOL_DRAFT_ESCALATION)
    return {
        "status": "DRAFT_PENDING_APPROVAL",
        "order_id": order_id,
        "issue_summary": issue_summary,
        "recommended_action": recommended_action,
        "raised_by_role": role,
        "committed": False,
        "note": "Draft only. No notification sent and no action taken.",
    }


DISPATCH = {
    TOOL_ORDER_STATUS: get_order_status,
    TOOL_CHECK_INVENTORY: check_inventory,
    TOOL_DRAFT_ESCALATION: draft_escalation,
}


# --------------------------------------------------------------------------
# Executor and loop
# --------------------------------------------------------------------------

MAX_TURNS = 6


def _execute(name: str, args: dict, role: str) -> tuple[dict, bool]:
    """Run one tool call. Returns (payload, denied).

    Permission is checked before dispatch, so a refused call reaches no data
    at all. Unlike the corpus path, this cannot short-circuit before the model
    call - by the time a tool is refused the model has already decided to call
    it, so a denial here costs one round trip. That is a real difference from
    core.ask()'s pre-check, not an oversight.
    """
    if name not in DISPATCH:
        return {"error": f"No such tool: {name}"}, False
    if name not in permitted_tools(role):
        return ({"error": "access_denied",
                 "message": (f"The {core.ROLE_LABELS.get(role, role)} role is "
                             f"not permitted to call {name}."),
                 "tool": name}, True)
    try:
        return DISPATCH[name](role, **args), False
    except PermissionError:
        # Belt and braces: the tool re-checks, so a future caller that bypasses
        # this executor still cannot reach data.
        return ({"error": "access_denied",
                 "message": f"Not permitted to call {name}.",
                 "tool": name}, True)
    except TypeError as e:
        return {"error": "bad_arguments", "message": str(e)}, False


def run_agent(question: str, role: str, client=None,
              max_turns: int = MAX_TURNS) -> dict:
    """Run the agent loop for one question as one role.

    Returns answer, the tool calls made, whether a human approval is pending,
    and token counts. `role` is required and is never taken from model output.
    """
    client = client or core.get_bedrock_client()
    messages = [{"role": "user", "content": [{"text": question}]}]

    calls, denials, steps = [], [], []
    tokens_in = tokens_out = 0
    stop_reason = None
    start = time.perf_counter()

    for turn in range(max_turns):
        response = client.converse(
            modelId=core.MODEL_ID,
            system=[{"text": AGENT_SYSTEM_PROMPT}],
            messages=messages,
            toolConfig=TOOL_CONFIG,
        )
        usage = response.get("usage", {})
        tokens_in += usage.get("inputTokens") or 0
        tokens_out += usage.get("outputTokens") or 0

        out = response["output"]["message"]
        messages.append(out)
        stop_reason = response["stopReason"]

        # The model's own text for this turn - what it concluded before deciding
        # to call a tool, or its final answer. Recorded as a reasoning step so a
        # run can be reconstructed later rather than only its tool calls.
        reasoning = "".join(c.get("text", "") for c in out["content"]).strip()
        if reasoning:
            steps.append({"turn": turn + 1, "kind": "reasoning",
                          "text": reasoning, "tool": None, "input": None,
                          "denied": None, "status": None})

        if stop_reason != "tool_use":
            break

        results = []
        for block in out["content"]:
            if "toolUse" not in block:
                continue
            use = block["toolUse"]
            payload, denied = _execute(use["name"], use.get("input") or {}, role)
            status = "error" if denied or "error" in payload else "success"
            calls.append({"tool": use["name"], "input": use.get("input") or {},
                          "denied": denied})
            steps.append({"turn": turn + 1, "kind": "tool_call",
                          "text": None, "tool": use["name"],
                          "input": use.get("input") or {},
                          "denied": denied, "status": status})
            if denied:
                denials.append(use["name"])
            results.append({"toolResult": {
                "toolUseId": use["toolUseId"],
                "content": [{"json": payload}],
                "status": status,
            }})
        messages.append({"role": "user", "content": results})
    else:
        # Loop cap reached with the model still asking for tools.
        return {
            "answer": ("Stopped after the maximum number of tool-calling turns "
                       "without reaching a conclusion."),
            "role": role,
            "question": question,
            "tool_calls": calls,
            "steps": steps,
            "denied_tools": denials,
            "requires_approval": False,
            "hit_turn_cap": True,
            "turns": max_turns,
            "stop_reason": stop_reason,
            "latency_ms": round((time.perf_counter() - start) * 1000),
            "input_tokens": tokens_in,
            "output_tokens": tokens_out,
        }

    answer = "".join(c.get("text", "") for c in out["content"]).strip()
    return {
        "answer": answer,
        "role": role,
        "question": question,
        "tool_calls": calls,
        "steps": steps,
        "denied_tools": denials,
        "requires_approval": any(
            c["tool"] == TOOL_DRAFT_ESCALATION and not c["denied"] for c in calls),
        "hit_turn_cap": False,
        "turns": turn + 1,
        "stop_reason": stop_reason,
        "latency_ms": round((time.perf_counter() - start) * 1000),
        "input_tokens": tokens_in,
        "output_tokens": tokens_out,
    }


if __name__ == "__main__":
    import sys
    import tomllib
    from pathlib import Path

    path = Path(__file__).parent / ".streamlit" / "secrets.toml"
    secrets = {}
    if path.exists():
        with open(path, "rb") as f:
            secrets = tomllib.load(f)
    bedrock = core.get_bedrock_client(secrets.get("AWS_ACCESS_KEY_ID"),
                                      secrets.get("AWS_SECRET_ACCESS_KEY"))

    role = sys.argv[1] if len(sys.argv) > 1 else core.ROLE_WAREHOUSE
    question = (" ".join(sys.argv[2:]) if len(sys.argv) > 2
                else "Order ORD-4417 is stuck. What's going on and what should we do?")

    # run_agent stays pure and the caller logs, matching core.ask/app.py.
    import usage_log

    try:
        result = run_agent(question, role, bedrock)
    except Exception as exc:
        usage_log.log_agent_run(question=question, role=role, error=exc)
        raise

    run_id = usage_log.log_agent_run(result)
    print(f"logged as run    : {run_id}")
    print(f"role             : {result['role']}")
    print(f"turns            : {result['turns']}  stop: {result['stop_reason']}")
    print(f"tool calls       : "
          f"{[c['tool'] + ('(denied)' if c['denied'] else '') for c in result['tool_calls']]}")
    print(f"requires approval: {result['requires_approval']}")
    print(f"tokens           : {result['input_tokens']:,} in / "
          f"{result['output_tokens']:,} out")
    print("--- answer ---")
    print(result["answer"])
