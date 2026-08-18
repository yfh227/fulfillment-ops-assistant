# V4 Build Layout — Role-Based Access

**The trigger, same as it's always been:** right now every question sees every
document. A billing analyst asking about warehouse procedures gets the same full
corpus as an account manager asking about a client dispute. Locking down the S3
bucket (V1) is infrastructure security — nobody outside the app can read the
documents. This is application-level governance — controlling what a given *user*
can ask for once they're inside.

**Effort:** a weekend, same scope as V2. **Cost:** $0 — this is pure application
logic, no new paid services.

**One thing worth naming before starting:** this needs to be designed against the
*real* 23-document corpus, not the original 7-document plan from when V4 was first
scoped. The role split below is grounded in what's actually in `docs/` now.

---

## Part 1 — Design the role-to-document mapping

This is a real decision, not a coding task, and it should be made explicitly
before any code gets written.

**Three roles, mapped to the actual documents:**

| Role | Documents |
|---|---|
| **Billing Analyst** | Rate card, billing dispute policy, Enterprise/Growth rate schedules, inventory accuracy reports (full documents) |
| **Warehouse Lead** | Receiving discrepancy SOP, Reno putaway SOP, `21_putaway_sop_richmond_columbus.md`, cycle count policy, peak season procedures, inventory accuracy reports |
| **Account Manager** | Company profile, escalation matrix, onboarding checklist, client onboarding case notes, carrier/vendor policies |

> **Scope note — granularity.** Access is enforced at document granularity.
> `get_documents_for_role()` filters a list of whole documents, so a role either
> sees all of a document or none of it. Section-level access — e.g. exposing only
> the billing-relevant parts of the inventory accuracy reports — would require
> filtering at the chunk level and is out of scope for V4.

**Two things worth deciding now, on paper, before they become code:**

- **Should any document be visible to more than one role?** The inventory accuracy
  reports plausibly matter to both Billing and Warehouse — decide explicitly rather
  than let it fall out of however the code happens to get written.
- **What happens to a document nobody's role covers?** If something's missing from
  all three lists, that's a bug waiting to surface as a silent gap. Do a pass to
  confirm all 23 are accounted for.

```
Read every filename in docs/. Propose a role-to-document mapping for
Billing Analyst, Warehouse Lead, and Account Manager, using the table above
as a starting point. Flag any document that fits more than one role, and
flag any document that doesn't cleanly fit any role. Don't write code yet —
just the mapping, for me to confirm before it becomes the source of truth.
```

---

## Part 2 — Simple authentication

Use `streamlit-authenticator` (`mkhorasani/Streamlit-Authenticator` on GitHub)
rather than building login from scratch — it's the library most real Streamlit auth
tutorials build on, and it stores role information in session state, which is
exactly the mechanism this needs.

```
Add streamlit-authenticator to the project. Create a small set of test
users — one per role, plus one admin/all-access user for your own testing.
Store credentials in a config file, hashed, not plaintext, and add that
config file to .gitignore since it'll hold real (test) credentials.

Wire login into app.py: unauthenticated users see a login form and nothing
else. Authenticated users see the existing app, with their role now
available in session state.

Verify: confirm each test user logs in successfully and that the role is
actually readable from session state after login, before building anything
that depends on it.
```

---

## Part 3 — Wire the restriction into document loading

This is the actual access-control logic, and it needs to sit in `core.py` where
`load_documents()` and `build_context()` already live — not duplicated into
`app.py`.

```
Add a function to core.py: get_documents_for_role(role, all_docs) that
filters the full document list down to what that role is permitted to see,
using the mapping confirmed in Part 1.

Update app.py to call this after login, using the role from session state,
before build_context() runs. A Billing Analyst's context should now only
ever contain their permitted documents — verify this by adding a debug line
that prints the filtered document list, then removing it once confirmed.

This must work whether use_retrieval is True or False. If retrieval is on,
the candidate set for embedding search also needs to be limited to the
role's permitted documents, not the full 23 — a role restriction that only
works in direct-context mode isn't actually done.
```

That last instruction matters more than it looks. It would be easy to filter the
direct-context document list and forget that retrieval draws from a separate
embedded index — that's exactly the kind of gap Part 3 of V3 warned about with
citation, just showing up in a new place.

---

## Part 4 — Make the restriction visible, not silent

A system that quietly limits what it can see, without saying so, is worse than one
that's honest about the limit. If someone asks about something outside their role's
documents, the app should say that plainly — not just fail to find an answer and
look broken.

```
Update the system prompt (or add a pre-check before the Claude call) so
that when a question clearly falls outside the role's document set, the
response says so directly — something like "That's outside what a
[role] has access to in this system" — rather than silently returning
"I don't know" the way an out-of-corpus question normally would.

The two failure modes need to look different to the user: "not in any
document" and "not something your role can see" are different situations
and should read differently.
```

---

## Part 5 — Test it like V2 and V3 were tested, not by trusting the code

This is where the project's established discipline actually matters most. Don't
assume the restriction works because the code looks right — prove it the way case 6
and the K-sweep were proven.

```
Add role-based test cases to a new file, eval_roles.py, separate from the
existing eval.py: for each role, one question clearly inside their
document set (should answer normally) and one question clearly outside it
(should get the access-denied message from Part 4, not a normal refusal
and not a normal answer).

Run every role/question combination in both direct-context and retrieval
modes — six roles-times-questions, times two modes. Report full results,
including any case where a role saw something it shouldn't have.

Also re-run the original eval.py's 8 cases as the admin/all-access user, to
confirm the existing regression suite still passes unchanged. Role-based
access should be additive, not a regression on what already worked.
```

---

## Part 6 — Document it

```
Add a section to README.md: the three roles, what each can see, how
access denial is distinguished from a genuine "not in any document"
refusal, and confirmation that the restriction holds in both direct-context
and retrieval modes. Commit and push.
```

---

## Part 1 result — confirmed mapping (source of truth)

Derived from each document's own header metadata (`Owner`, `Distribution`,
`Applies to`, `Attendees`, `Negotiated by`), not from the starting table above.
Where metadata named one of the three roles directly, it was used as-is. Where it
did not, the assignment is marked as a judgment call.

Resolutions applied: owner-wins for rate schedules (both to Account Manager);
company profile universal; incident reviews and the training programme assigned to
every role their metadata names.

| # | File | Billing | Warehouse | Account | Classification | Basis |
|---|---|:-:|:-:|:-:|---|---|
| 00 | `00_company_profile.md` | ● | ● | ● | Universal | no metadata |
| 01 | `01_receiving_discrepancy_sop.md` | | ● | | Judgment call | Owner = Client Ops Mgr (not a role) |
| 02 | `02_billing_rate_card.md` | ● | | | Judgment call | no Owner field; `FIN-RATE` ID + content |
| 03 | `03_escalation_matrix.md` | | | ● | Judgment call | Owner = Client Ops Mgr |
| 04 | `04_cycle_count_policy.md` | | ● | | Metadata match | Owner: Facility Managers |
| 05 | `05_client_onboarding_checklist.md` | | | ● | Judgment call | Owner = Onboarding Specialists |
| 06 | `06_billing_dispute_policy.md` | ● | | | Metadata match | Owner: Billing Analysts / Finance |
| 07 | `07_reno_putaway_sop.md` | | ● | | Metadata match | Owner: Facility Manager, Reno |
| 08 | `08_peak_season_operating_procedures.md` | | ● | | Judgment call | Owner = VP Operations |
| 09 | `09_incident_2025-12-01_wms_outage.md` | | ● | ● | Multi-role (metadata) | Attendees: 3 Facility Mgrs, 2 Senior Account Mgrs |
| 10 | `10_incident_2026-01-22_integration_failure.md` | ● | ● | ● | Multi-role (metadata) | Attendees: Columbus FM, Senior AM, 1 Billing Analyst |
| 11 | `11_incident_2026-03-08_mixed_client_inventory.md` | ● | ● | ● | Multi-role (metadata) | Attendees: Reno FM, 2 AMs, 1 Billing Analyst |
| 12 | `12_onboarding_case_enterprise_northwind.md` | | | ● | Metadata match | Senior Account Manager: J. Baptiste |
| 13 | `13_onboarding_case_growth_lumen.md` | | | ● | Metadata match | Account Manager: P. Oyelaran |
| 14 | `14_onboarding_case_standard_fernpost.md` | | | ● | Judgment call (contested) | header states "no named Account Manager" |
| 15 | `15_carrier_management_policy.md` | | | ● | Judgment call | Owner = VP Operations |
| 16 | `16_vendor_and_temporary_labour_policy.md` | | | ● | Judgment call | Owner = VP Operations |
| 17 | `17_enterprise_rate_schedule_northwind.md` | | | ● | Metadata match (owner-wins) | Negotiated by: Senior Account Manager |
| 18 | `18_growth_rate_schedule_lumen.md` | | | ● | Metadata match (owner-wins) | Negotiated by: Account Manager |
| 19 | `19_inventory_accuracy_report_2026_q2.md` | ● | ● | | Multi-role (metadata) | Distribution: Facility Managers + Finance |
| 20 | `20_new_hire_training_certification.md` | | ● | ● | Multi-role (judgment) | Owner w/ Facility Mgrs; warehouse + client ops |
| 21 | `21_putaway_sop_richmond_columbus.md` | | ● | | Metadata match | Owner: Facility Managers, Richmond & Columbus |
| 22 | `22_inventory_accuracy_report_2026_q3.md` | ● | ● | | Multi-role (metadata) | Distribution: Facility Managers + Finance |

**Totals:** Billing Analyst 7 · Warehouse Lead 12 · Account Manager 14.
All 23 documents covered; no orphans.

**By classification:** 8 metadata match, 8 judgment call, 6 multi-role, 1 universal.

### Open items — resolve before Part 3 encodes this

1. **Billing Analyst cannot see either rate schedule.** Owner-wins sends
   `17_enterprise_rate_schedule_northwind.md` and `18_growth_rate_schedule_lumen.md`
   to Account Manager exclusively, so a Billing Analyst asking about negotiated
   client rates gets access-denied. They see the standard rate card (02) and the
   dispute policy (06), but not client-specific rates. This reverses the starting
   table's Billing row and should be a deliberate choice, not a side effect.

2. **`14_onboarding_case_standard_fernpost.md` is contested.** Assigned to Account
   Manager for consistency with 12 and 13, but the document explicitly states it has
   *no* named Account Manager (standard tier, pooled queue). Under owner-wins it
   would belong to Onboarding Specialist — a role that does not exist in this model.

### Note on the role model

Only one document (`06_billing_dispute_policy.md`) names any of the three roles in
its `Owner` field. The corpus's most common owners are **Client Operations Manager**
(owns 01, 03, 20; chairs all three incident reviews; consolidates both accuracy
reports) and **VP Operations** (owns 08, 15, 16) — neither of which exists in the
three-role model. That gap is why 8 of 23 assignments are judgment calls rather than
metadata matches, and it is worth revisiting if a fourth role is ever added.

---

## What "done" looks like

- Three roles, explicitly mapped to real documents, with edge cases (shared or
  uncovered documents) decided on purpose
- Login works, role is readable from session state
- Document filtering happens in `core.py`, shared logic, not duplicated
- The restriction holds under retrieval too, not just direct context — verified,
  not assumed
- Access-denied and "not in any document" read as genuinely different situations
  to the user
- A dedicated eval file proves the restriction works, for every role, in both modes
- The original 8-case suite still passes unchanged

**The line worth remembering going into this:** this is the step that turns the IAM
story from "I locked down a bucket" into "I designed content governance" — a
meaningfully more senior claim, and one that requires the same
evidence-over-assumption standard the rest of this project has already earned.
