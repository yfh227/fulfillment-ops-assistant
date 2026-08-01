# Post-Incident Review — INC-2026-0038

> Fictional reference document — Meridian Fulfillment Co.

**Incident ID:** INC-2026-0038
**Severity:** S2 — High (declared S3, reclassified — see below)
**Title:** Shopify integration silently dropping orders, Alder & Vine, 61 hours
**Date:** 2026-01-20 through 2026-01-22
**Facility affected:** Columbus
**Client affected:** Alder & Vine (Enterprise tier)
**Review held:** 2026-01-28
**Chair:** Client Operations Manager
**Attendees:** Client Ops Mgr, Senior Account Manager (J. Baptiste), WMS Engineering
Lead, Columbus Facility Manager, 1 Billing Analyst
**Status:** Closed 2026-03-06

---

## Severity classification — and the delay in getting it right

Initially logged **S3 — Medium** on 2026-01-20 at 11:14, on the reasonable-seeming basis
that a small number of orders appeared to be missing and no systemic failure was
evident.

Reclassified **S2 — High** on 2026-01-22 at 08:30, 45 hours later.

The correct classification was S2 from the outset. POL-ESC-001 defines S2 as *"significant
impact with a workaround, or one enterprise client materially affected"* and names
*"integration failure"* as an example. Alder & Vine is enterprise tier. The condition was
met on day one.

**The 45-hour misclassification is the central finding of this review.** Everything that
follows downstream — the delayed response, the size of the backlog, the credit — flows
from it.

### Why it was misclassified

The first ticket said: *"a couple of orders from yesterday don't seem to be in your
system."* Two order numbers were named. Two missing orders is genuinely an S3 — contained
impact, no immediate revenue risk.

Nobody asked the follow-up question: *are these two orders, or are these the two the
client happened to notice?*

They were the two the client happened to notice.

### Applicable targets

| | S3 (as logged) | S2 (correct) |
|---|---|---|
| First response | 1 business day | 2 hours |
| Update cadence | Daily | Every 4 hours |
| Target resolution | 3 business days | 1 business day |

Alder & Vine is enterprise tier, which under POL-ESC-001 receives one severity level of
priority handling. The S3 should therefore have been worked at S2 targets even as logged
— **and it was not.** The enterprise uplift was not applied. This is a second,
independent failure and is discussed at Finding 3.

---

## Timeline

All times US Eastern.

| Time | Event |
|---|---|
| **Mon 2026-01-19** | |
| ~14:00 | Shopify pushes a scheduled API version deprecation. Meridian's connector begins receiving `422` on a subset of order payloads. Connector logs the error and continues polling. No alert is raised. |
| **Tue 2026-01-20** | |
| 09:47 | Alder & Vine ops coordinator emails their Account Manager: two orders from Monday not visible in the portal. |
| 11:14 | Ticket created, tagged `integration`, logged **S3**. Assigned to pooled queue. |
| 16:30 | Support Specialist responds: asks client to confirm the order numbers and check their Shopify export. First response inside the S3 target of 1 business day. |
| **Wed 2026-01-21** | |
| 10:20 | Client replies confirming order numbers, adds "there might be more, we're checking." |
| 14:05 | Support Specialist reproduces: both orders absent from WMS. Escalates to WMS Engineering as a data question, not as an incident. |
| 17:50 | WMS Engineering finds `422` responses in connector logs. Volume "looks higher than normal" but no count is taken. End of day. |
| **Thu 2026-01-22** | |
| 07:55 | Client emails the Senior Account Manager directly: *"we're now seeing 300+ orders unaccounted for since Monday. This is a serious problem."* |
| 08:30 | **Reclassified S2.** Senior AM takes ownership. WMS Engineering paged. |
| 08:44 | Root cause identified: connector rejecting orders containing the `note_attributes` field under the deprecated API version. |
| 09:15 | Full impact quantified: **1,847 orders** dropped across 61 hours. |
| 09:30 | First S2-standard client communication, from Senior AM. |
| 10:40 | Connector patched to the current API version. Deployed. |
| 11:05 | Backfill begins from Shopify order history. |
| 13:20 | Backfill complete. 1,847 orders ingested. |
| 13:20–2026-01-23 22:00 | Columbus works the backlog alongside normal volume. |
| **Fri 2026-01-23** | |
| 22:00 | Backlog cleared. All 1,847 orders shipped. |
| **Sat 2026-01-24** | |
| 16:30 | Written incident summary posted — 42.5 hours after resolution. **Missed the 24-hour requirement.** |

---

## Impact

| Measure | Value |
|---|---|
| Duration, first symptom to resolution | 61 hours (integration), 89 hours (backlog cleared) |
| Duration, correct classification to resolution | 5h20m |
| Orders dropped | 1,847 |
| Orders shipped outside client SLA | 1,203 |
| Client tier | Enterprise |
| Service credit issued | $9,400 |
| Zendesk tickets | 14 (client raised 9 separately before escalating) |

The 5h20m figure is worth dwelling on. **From the moment the incident was correctly
classified, it was resolved in under six hours** — comfortably inside the S2 one-business-day
target. The technical fix was straightforward. The 61-hour duration is almost entirely
classification and ownership delay, not technical difficulty.

### Credit detail

$9,400, classified **Meridian error** under POL-FIN-003. Approved by **VP Operations**,
correct for the $2,501–$10,000 band. Did not require CFO approval.

The client initially requested $14,000, calculated on their own lost-margin estimate.
The negotiated figure of $9,400 was based on Alder & Vine's contractual on-time-ship
remedy, which is defined in their agreement as a per-order credit rather than a
consequential-loss claim. The Senior Account Manager held that line correctly.

Per POL-ESC-001, service credits may never be committed below Level 3. The Support
Specialist working the ticket on 2026-01-21 was asked directly by the client whether
they would be compensated and correctly declined to answer, deferring to the Account
Manager. That was the right call under pressure and is noted here as such.

---

## Root cause

**Immediate cause:** Shopify deprecated an API version on 2026-01-19. Meridian's
connector, pinned to the deprecated version, received `422 Unprocessable Entity` for any
order payload containing populated `note_attributes`. Alder & Vine uses that field for
gift messaging, which appears on roughly 34% of their orders in January.

**Why it was silent:** the connector's error handling logged failures at `WARN` and
continued polling. There was no alert on error rate, no dead-letter queue, and no
reconciliation between orders in Shopify and orders in the WMS. A dropped order simply
did not exist as far as Meridian was concerned.

**Why the deprecation was missed:** Shopify announced it 2025-10-14, ninety-seven days
ahead, via developer changelog and a notification to the registered app contact address.
That address was a personal mailbox of a developer who left Meridian in August 2025. The
mailbox was deactivated per offboarding policy. The notification bounced. Nobody owned
the app registration.

**Why only Alder & Vine:** eleven Meridian clients run Shopify. Only Alder & Vine
populates `note_attributes` at meaningful volume. Two other clients had small numbers of
orders affected — 3 and 7 respectively — which were caught in the same backfill and
neither client noticed. Both were notified proactively; this is recorded because the
instinct not to raise it was expressed in the review and was overruled.

---

## Findings

### Finding 1 — The severity question was never re-asked

The initial S3 was defensible on the information available at 11:14 on 2026-01-20. It
became indefensible by 14:05 on 2026-01-21, when the Support Specialist confirmed both
orders were genuinely absent and the client had said "there might be more."

Nothing in the process prompts a re-evaluation of severity as facts change. Severity is
set at intake and, in practice, only ever revised upward when a client escalates loudly.

**A client should not be the mechanism by which severity gets corrected.**

### Finding 2 — "How many?" was not asked for 45 hours

At 17:50 on 2026-01-21, WMS Engineering observed that `422` volume "looks higher than
normal." No count was taken. The count took under four minutes when it was finally run
at 09:15 the following morning.

Had it been run at 17:50, the incident would have been reclassified that evening and
roughly 900 fewer orders would have been dropped.

### Finding 3 — The enterprise uplift was not applied

Alder & Vine is enterprise tier. POL-ESC-001 states enterprise clients receive one
severity level of priority handling: an S3 from an enterprise client is worked at S2
targets — 2-hour first response, updates every 4 hours.

The ticket sat in the pooled queue for 5h16m before first response, and received no
update on 2026-01-21 at all.

The uplift is documented policy and was simply not applied. There is no automation
enforcing it; it depends on whoever picks up the ticket knowing the client's tier and
remembering the rule. The pooled queue does not display tier.

### Finding 4 — Nobody owned the app registration

The Shopify app registration contact was an individual's mailbox. When that individual
left, offboarding deactivated the mailbox — correctly — but no process existed to
reassign integration ownership.

A subsequent audit found **nine** third-party integrations registered to individual
mailboxes, three of them to people no longer employed.

### Finding 5 — No order-count reconciliation exists

Meridian had, and until Action 5 completed had no way to detect, a discrepancy between
orders placed in a client's storefront and orders present in the WMS. Detection depended
entirely on a human noticing.

For a fulfilment provider this is a significant gap. It was not identified in any prior
review because integrations "work" — until an API contract changes underneath them.

### Finding 6 — Written summary missed the 24-hour requirement by 18.5 hours

POL-ESC-001 requires a written incident summary in Zendesk within 24 hours of resolution
for every S1 and S2. Resolution was 2026-01-23 22:00; the summary posted 2026-01-24 16:30.

Contributing factor: the incident was S3 for most of its life, and the 24-hour
requirement attaches to S2. The person who would normally write it did not initially
realize it applied. Not an excuse — the reclassification was 39 hours before resolution —
but it is the actual reason.

---

## Corrective actions

| # | Action | Owner | Due | Status |
|---|---|---|---|---|
| 1 | Alert on connector error rate > 1% over 15 min, paging WMS Eng | WMS Eng | 2026-02-06 | Complete |
| 2 | Dead-letter queue for rejected order payloads, with daily review | WMS Eng | 2026-02-20 | Complete |
| 3 | Move all integration registrations to shared role mailboxes | WMS Eng | 2026-03-06 | Complete — 9 migrated |
| 4 | Subscribe integration role mailbox to all vendor deprecation channels | WMS Eng | 2026-02-13 | Complete |
| 5 | Nightly order-count reconciliation, storefront vs WMS, exception report | WMS Eng | 2026-04-10 | Complete |
| 6 | Display client tier prominently in the Zendesk queue view | Client Ops Mgr | 2026-02-13 | Complete |
| 7 | Auto-apply enterprise uplift: enterprise tickets inherit next-higher targets | Client Ops Mgr | 2026-03-20 | Complete |
| 8 | Add mandatory severity re-check at 24h and 48h on any open incident | Client Ops Mgr | 2026-03-20 | Complete |
| 9 | Add "quantify before you characterize" to incident triage training | Client Ops Mgr | 2026-04-30 | Complete — TRN-INC-002 |

Action 5 is the one that would have caught this independently of anyone's judgement. It
now runs nightly across all clients and has since caught two further discrepancies, both
small, both resolved before the client noticed.

Action 8 addresses Finding 1 directly and is the cheapest of the nine.

---

## What went well

- **Once correctly classified, resolution took 5h20m** against a one-business-day target.
  The technical response was fast and competent.
- **The Support Specialist correctly refused to commit to a credit** when asked directly
  by the client, deferring to the Account Manager per POL-ESC-001. Under pressure, with
  an unhappy enterprise client, this is not easy.
- **The Senior Account Manager held the credit at the contractual remedy** rather than
  the client's larger consequential-loss figure, while keeping the relationship intact.
- **The two other affected clients were notified proactively** despite neither noticing
  and despite an argument in the review that raising it would create alarm. Per
  POL-FIN-003's systemic-cause requirement, this was correct.
- **Alder & Vine renewed** in March 2026 for a further two years.

---

## Client feedback, recorded verbatim

From Alder & Vine's Director of Operations, in the 2026-02-04 review call:

> "The fix was fast once you knew. What worries me is the two days where nobody asked
> how big it was. We told you something was wrong on Tuesday morning. We had to tell you
> it was serious on Thursday. That's the part I need to not happen again."

The review chair judged this a fair characterization and it is reproduced without
softening.

---

## Related documents

POL-ESC-001 (Escalation Matrix) · POL-FIN-003 (Billing Disputes and Adjustments) ·
SOP-ONB-001 (Client Onboarding Checklist) · TRN-INC-002 (Incident Triage) ·
INC-2025-0417 · INC-2026-0104
