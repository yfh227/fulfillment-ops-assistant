# Post-Incident Review — INC-2025-0417

> Fictional reference document — Meridian Fulfillment Co.

**Incident ID:** INC-2025-0417
**Severity:** S1 — Critical
**Title:** WMS unavailable network-wide, 3h47m, Cyber Monday
**Date:** 2025-12-01
**Facilities affected:** Richmond, Columbus, Reno (all)
**Clients affected:** 87 (all active clients)
**Review held:** 2025-12-05 (within the 5 business day requirement)
**Chair:** Client Operations Manager
**Attendees:** Client Ops Mgr, VP Operations, 3 Facility Managers, WMS Engineering Lead,
2 Senior Account Managers
**Status:** Closed 2026-02-19

---

## Severity classification

Classified **S1** under POL-ESC-001: *"systemic failure affects multiple clients"* and
*"WMS down"* — both named conditions in the S1 definition. Classification was made at
06:34, four minutes after the first alert, by the Columbus Facility Manager.

Classification was correct and immediate. This is worth stating because the two
subsequent incidents in this review series both had classification delays.

**Applicable targets:** 30-minute first response · hourly updates · 4-hour target
resolution.

---

## Timeline

All times US Eastern.

| Time | Event |
|---|---|
| 06:12 | Scheduled index maintenance job begins on the WMS primary database. Routine; runs every Monday 06:00. |
| 06:29 | Columbus shift lead reports handhelds returning `SESSION EXPIRED` on scan. Attempts reconnect, fails. |
| 06:30 | Richmond reports the same. Automated monitoring fires: `wms-api p99 latency > 30s`. |
| 06:34 | Columbus FM declares S1. Pages WMS Engineering and Client Ops Mgr. |
| 06:41 | **First client-facing acknowledgement posted to status page.** 29 minutes from declaration — inside the 30-minute target by one minute. |
| 06:48 | WMS Engineering identifies the index job holding an exclusive lock on `inventory_location`. Job shows 42 minutes elapsed against a normal runtime of 4 minutes. |
| 06:55 | Decision made to kill the job. Kill issued. |
| 07:03 | Kill does not complete. Job enters `KILLED` state but lock is not released. Database is in an uninterruptible rollback. |
| 07:15 | Hourly update #1 sent to all clients. Content: outage confirmed, cause under investigation, no ETA. |
| 07:20 | Reno opens, discovers the outage on arrival. No inbound notification had reached them — see Finding 4. |
| 07:41 | Rollback estimated by engineering at "60 to 180 minutes, cannot be accelerated." |
| 07:52 | VP Operations authorizes manual paper-based picking at all three facilities. |
| 08:15 | Hourly update #2. First communication of a range: "restoration expected between 09:00 and 11:00." |
| 08:20–09:30 | Paper picking underway. Richmond achieves roughly 40% of normal rate, Columbus 35%, Reno 22%. |
| 09:15 | Hourly update #3. |
| 09:48 | Rollback completes. Lock released. |
| 09:52 | WMS API recovers. Handhelds reconnect. |
| 10:01 | **Service restored.** 3h47m from declaration. |
| 10:15 | Hourly update #4: restoration confirmed, backlog reconciliation beginning. |
| 10:15–18:40 | Manual pick reconciliation. 1,412 orders picked on paper require system entry. |
| 18:40 | Reconciliation complete. 26 discrepancies identified, all resolved by 2025-12-03. |
| 2025-12-02 09:00 | Written incident summary posted to Zendesk — 23 hours after resolution, inside the 24-hour requirement. |

---

## Impact

| Measure | Value |
|---|---|
| Duration, declaration to restoration | 3h47m |
| Duration, first symptom to restoration | 3h49m |
| Orders delayed | 8,940 |
| Orders shipped same day despite outage | 6,120 (via paper picking) |
| Orders missing carrier cutoff | 2,820 |
| Clients affected | 87 |
| Enterprise clients affected | 12 |
| Inventory adjustments required post-reconciliation | 26 |
| Service credits issued | $18,400 |
| Zendesk tickets generated | 411 |

Resolution came in at 3h47m against a 4-hour target. **The target was met.** This is
recorded plainly because the incident is otherwise a catalogue of failures and it would
be dishonest to lose the one thing that went right — largely because the paper-picking
call at 07:52 was made early and decisively.

### Credit detail

Credits totalled $18,400 across 14 clients. Breakdown:

| Client tier | Clients credited | Total | Approver |
|---|---|---|---|
| Enterprise | 6 | $14,200 | VP Operations |
| Growth | 7 | $3,900 | Client Operations Manager |
| Standard | 1 | $300 | Client Operations Manager |

Two enterprise credits exceeded $2,500 individually and correctly went to VP Operations
per POL-ESC-001 Level 4. The largest single credit was $6,800 to Northwind Provisions
(enterprise, contractual on-time-ship SLA with defined remedy). No credit exceeded
$10,000, so CFO approval was not triggered.

All credits were classified **error**, not goodwill, per POL-FIN-003. This was correct —
the failure was Meridian's — but was initially miscoded as goodwill on four tickets by a
Billing Analyst working from the incident summary rather than the classification
guidance. Corrected 2025-12-11. The distinction matters for trend reporting and the
miscoding would have understated error credits for the quarter by $4,100.

---

## Root cause

**Immediate cause:** a scheduled index rebuild on `inventory_location` acquired an
exclusive lock and ran 10× its normal duration, blocking all WMS reads and writes.

**Why it ran long:** the table had grown 4.1× since the job's parameters were last
tuned in March 2024. Row count went from approximately 2.9M to 11.8M, driven primarily
by the Reno mezzanine locations added in 2023 and by three Growth-tier client onboardings
in Q3 2025. The job's `MAXDOP` and batch-size parameters were sized for the 2024 table.

**Why nobody noticed the growth:** table growth was not monitored. Database monitoring
covered CPU, memory, disk, connection count, and query latency. It did not cover table
row counts or index maintenance job duration. The job had been running progressively
longer for months — retrospective log analysis shows 4m12s in March 2025, 11m in
July, 26m in October, 42m at failure — and this trend was visible in logs nobody read.

**Why it was catastrophic rather than merely slow:** the job ran against the primary
with no read replica in place. Every WMS operation across three facilities depends on
this single database. There is no degraded read-only mode.

**Why it ran at 06:12 on Cyber Monday:** the maintenance window is Monday 06:00 weekly,
set in 2022 when Monday morning was genuinely quiet. It had never been reviewed against
the peak calendar. Per SOP-PEAK-001 (which did not exist at the time), non-urgent WMS
changes now freeze from week 45 — but a *recurring scheduled job* is not a change and
would not have been caught by that freeze even had it existed. See Action 6.

---

## Findings

### Finding 1 — Single point of failure, known and accepted

The WMS primary database has no read replica and no degraded mode. This was a known
architectural limitation, documented in the 2024 infrastructure review, and accepted on
cost grounds. The review estimated replica cost at $31,000 annually.

The incident cost $18,400 in credits alone, plus 2,820 missed cutoffs and the reputational
cost across all 87 clients on the single highest-visibility day of the year.

**This is not a surprise failure. It is an accepted risk that materialized.** The
acceptance was recorded; what was not recorded was any review trigger or expiry on that
acceptance.

### Finding 2 — Monitoring covered symptoms, not causes

Alerting fired on API latency at 06:30, eighteen minutes after the job started and one
minute after operators noticed. Monitoring told us the system was down at approximately
the same moment humans did, which is to say it provided no lead time.

Nothing monitored: table growth, index job duration, lock wait time, long-running
transactions.

### Finding 3 — Maintenance window never reviewed against the business calendar

Monday 06:00 was chosen in 2022 and never revisited. Cyber Monday is the highest-volume
day of the year and always falls on a Monday.

### Finding 4 — Reno was not notified

Reno opens at 07:00 Pacific, which is 10:00 Eastern. The incident began at 06:12 Eastern
— 03:12 Pacific. Nobody paged Reno. The Reno team discovered the outage on arrival at
07:20 Eastern (04:20 Pacific — the FM was travelling and logged in early).

The paging list was built around Eastern-time facilities and had not been updated when
Reno opened in 2021. Reno's Facility Manager was on it; the Reno shift leads were not.

### Finding 5 — Paper picking worked, but only because two people remembered it

Paper-based picking is not documented in any SOP. It was executed from the memory of the
Richmond Facility Manager and one Columbus shift supervisor, both of whom had used it
during a 2019 outage at a previous employer.

Reno's 22% throughput versus Richmond's 40% is almost entirely explained by Reno having
nobody who had done it before. The Reno team improvised a process at 08:20 on the busiest
morning of the year.

### Finding 6 — Client communication was adequate in cadence, poor in content

Hourly updates went out on schedule — 07:15, 08:15, 09:15, 10:15. The cadence requirement
was met.

The content was thin. Updates #1 and #3 said essentially "we are still working on it"
with no operational guidance. Clients asked repeatedly whether they should redirect
orders elsewhere, and no update addressed it until 08:15.

Per POL-ESC-001, root cause must not be stated before investigation concludes — correctly
observed here. But that rule does not prohibit operational guidance, and the team
conflated the two. "We cannot yet tell you why" became "we cannot tell you anything."

### Finding 7 — Two Support Specialists contacted enterprise clients directly

POL-ESC-001 states that for S1 and S2, client contact is by Senior Account Manager or
above, never a Support Specialist. During the 07:00–08:00 window, with 411 tickets
arriving, two Support Specialists responded directly to enterprise client tickets.

Both responses were factually accurate and neither caused harm. The rule exists because
enterprise clients under S1 conditions frequently ask questions whose answers carry
contractual weight, and Support Specialists are not equipped to field them. The
specialists were doing their best in an overwhelmed queue with no instruction to the
contrary.

The failure is the absence of a queue-routing rule that enforces this automatically,
not the judgement of two people under pressure.

---

## Corrective actions

| # | Action | Owner | Due | Status |
|---|---|---|---|---|
| 1 | Add table growth and index-job duration to monitoring, with alerting at 2× baseline | WMS Eng | 2025-12-19 | Complete |
| 2 | Retune index job parameters for current table size | WMS Eng | 2025-12-12 | Complete |
| 3 | Move maintenance window to Sunday 02:00; add peak-calendar exclusion | WMS Eng | 2025-12-15 | Complete |
| 4 | Rebuild paging list; add Reno shift leads and all-facility escalation group | Client Ops Mgr | 2025-12-10 | Complete |
| 5 | Write paper-picking contingency SOP, train at all three facilities | VP Ops | 2026-02-28 | Complete — SOP-CONT-003 |
| 6 | Review all recurring scheduled jobs against the peak calendar annually in week 40 | WMS Eng | 2026-10-02 | Open — recurring |
| 7 | Business case for read replica, resubmitted with this incident's cost | VP Ops | 2026-01-31 | Complete — **approved 2026-02-19**, replica live 2026-05-08 |
| 8 | Zendesk routing rule: enterprise + S1/S2 auto-assigns to Senior AM queue | Client Ops Mgr | 2026-01-16 | Complete |
| 9 | Incident communication template library with operational-guidance prompts | Client Ops Mgr | 2026-01-30 | Complete — PEAK-COMM and INC-COMM series |
| 10 | Write peak season SOP | VP Ops | 2026-07-31 | Complete — SOP-PEAK-001 |

Action 7 is the substantive one. The read replica business case had been declined in
2024 on cost. It was approved eleven weeks after this incident. The deciding argument was
not the $18,400 in credits but the 2,820 missed cutoffs on Cyber Monday and what a repeat
would do to enterprise renewal conversations.

---

## What went well

Recorded deliberately. A review that lists only failures teaches the wrong lesson.

- **Classification was immediate and correct.** Four minutes from first symptom.
- **The paper-picking decision was made at 07:52,** roughly 80 minutes into the incident
  and before the rollback estimate was known. Waiting for certainty would have cost
  another 90 minutes and several thousand more orders.
- **6,120 orders shipped on the busiest day of the year with no system.**
- **The 4-hour target was met.**
- **Reconciliation found only 26 discrepancies across 1,412 manually picked orders** — an
  error rate of 1.8% on an improvised paper process, which is better than anyone expected.
- **The written summary was posted inside 24 hours** despite the reconciliation running
  to 18:40 that day.

---

## Disagreement recorded

The review did not reach consensus on Finding 1.

The WMS Engineering Lead's position: the replica was declined on cost in 2024 by the same
function that later approved it, and characterizing this as an engineering failure is
inaccurate — engineering identified and escalated the risk correctly and was overruled.

The VP Operations' position: the risk acceptance in 2024 was reasonable on the
information available, and the missing control is the absence of any review trigger on
accepted risks, not the acceptance itself.

Both positions are recorded because the review could not resolve them and because the
disagreement is more useful than a forced consensus. The resulting action — annual review
of accepted infrastructure risks — was agreed by both and assigned to the VP Operations.

---

## Related documents

POL-ESC-001 (Escalation Matrix) · POL-FIN-003 (Billing Disputes and Adjustments) ·
SOP-PEAK-001 (Peak Season Operating Procedures) · SOP-CONT-003 (Paper-Based Picking
Contingency) · INC-2026-0038 · INC-2026-0104
