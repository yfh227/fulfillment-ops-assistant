# Peak Season Operating Procedures — Weeks 46–52

> Fictional reference document — Meridian Fulfillment Co.

**Document ID:** SOP-PEAK-001
**Owner:** VP Operations (M. Reyes)
**Last reviewed:** 2026-07-15
**Applies to:** All facilities, all client tiers
**Active period:** Week 46 Monday 00:00 through Week 52 Sunday 23:59, local facility time

---

## Purpose and honest framing

The company profile lists, as a known operational pain point, that ticket volume spikes
every year in weeks 46–52 without corresponding staffing. That is accurate and this
document does not pretend to solve it.

What this document does is make the shortfall **predictable and triaged** rather than
chaotic. The staffing gap is a budget decision made above the operations function. Given
that gap, these procedures define what gets protected, what degrades, and who decides.

Three prior peaks (2023, 2024, 2025) were run without a written peak SOP. Each produced
the same pattern: the first two weeks went well, week 48 broke, and weeks 49–52 were
managed by individual heroics with no consistency between facilities or shifts. The
2025 peak generated 4 S1 incidents and 31 S2s, against 2 S1s and 19 S2s across the
entire remainder of that year.

---

## What changes during peak

| Dimension | Normal | Peak |
|---|---|---|
| Pick/pack surcharge | — | +8% (per FIN-RATE-2026-01) |
| Order cutoff for same-day | 14:00 local | 12:00 local, weeks 48–52 |
| Receiving appointments | Same-day slots available | Appointment required, 72 hours notice |
| Cycle count cadence | Per SOP-INV-002 | Class A only; B and C suspended |
| New client go-lives | Any date | Frozen weeks 46–52 |
| SKU setup turnaround | 2 business days | 5 business days |
| Non-urgent WMS changes | Weekly release | Frozen from week 45 Friday |
| Standard-tier first response | Per POL-ESC-001 | Per POL-ESC-001, but see triage below |

The surcharge is +8% on pick and pack, applied to the **service date** not the invoice
date. Week 52 orders bill in January carrying the surcharge. This is the second most
common billing dispute per POL-FIN-003 and the single most predictable one. Account
Managers are required to send the peak-billing advisory (template PEAK-COMM-02) to every
client by **week 44 Friday** — before the surcharge is incurred, not after it appears on
an invoice.

---

## Volume expectations

Based on 2023–2025 actuals, indexed against the trailing eight-week average:

| Week | Order volume index | Ticket volume index | Notes |
|---|---|---|---|
| 45 | 1.15 | 1.10 | Build-up; last chance for changes |
| 46 | 1.40 | 1.25 | Surcharge begins |
| 47 | 1.85 | 1.60 | US Thanksgiving week |
| 48 | **2.60** | **2.30** | Cyber weekend; historically the break point |
| 49 | 2.20 | 2.45 | Ticket peak lags order peak by one week |
| 50 | 1.95 | 2.10 | Last reliable ground shipping |
| 51 | 1.30 | 1.85 | Volume falls, tickets do not |
| 52 | 0.75 | 1.70 | Low volume, high anxiety |
| 1 (Jan) | 0.85 | **2.15** | Returns + peak invoice disputes |

Two observations that operators consistently get wrong:

**Ticket volume peaks in week 49, not week 48.** Orders peak on Cyber Monday; the
questions about those orders arrive three to eight days later when they have not
arrived. Staffing the support queue to the order curve is a mistake made in 2023 and
2024.

**Week 1 of January is the second-worst support week of the year.** Returns volume and
peak-surcharge invoice disputes land simultaneously. Peak staffing arrangements that end
on 31 December leave the hardest support week uncovered. In 2025 this produced a
five-day first-response time on standard-tier tickets against a two-business-day target.

Peak daily order volume across the network is approximately 19,000 at normal run rate.
Week 48 has historically peaked near 49,000 in a single day (2025-12-01, Cyber Monday),
against a network design capacity of 44,000. That gap is closed with overtime and
temporary labour, not with process.

---

## Staffing

### What is actually approved

| Function | Normal headcount | Peak approved | Gap to modeled need |
|---|---|---|---|
| Warehouse — pick/pack | 148 | +62 temporary | −18 |
| Warehouse — receiving | 22 | +8 temporary | −3 |
| Client Support Specialists | 14 | +4 seasonal | **−11** |
| Billing Analysts | 6 | 0 | −2 |
| Account Managers | 9 | 0 | −4 |
| Onboarding Specialists | 4 | 0 | 0 (go-lives frozen) |

The modeled need is derived from the volume indices above applied to normal-run
productivity. The Client Support gap of 11 heads is the material one and is the origin
of the pain point named in the company profile.

**This gap is not closeable within the current budget.** It has been raised in each of
the last three annual planning cycles. The procedures below are written on the
assumption that it persists.

### Warehouse temporary labour

- Sourced through Cascade Staffing (Richmond, Columbus) and High Desert Labor Partners
  (Reno). Both are covered under VEN-POL-002.
- **Onboarding closes week 44.** A temporary worker who has not completed the 6-hour
  induction by week 45 Friday does not work peak. This rule was introduced after 2024,
  when eleven workers were placed on the floor in week 47 with abbreviated training and
  accounted for a disproportionate share of that year's pick errors.
- Temporary workers are **not permitted** to perform: cycle counts, putaway to
  mezzanine locations at Reno, returns disposition, or any task on serialized or
  lot-tracked SKUs.
- Ratio limit: no more than 2 temporary workers per 1 permanent worker on any shift in
  any zone. Where the ratio cannot be met, the zone runs short rather than exceeding it.

### Client Support coverage

With four seasonal additions against a modeled need of fifteen, the queue cannot be
worked normally. The triage model below is mandatory, not advisory.

Seasonal support staff handle **S4 only**, and only from a scripted response library
(PEAK-COMM series). They do not contact enterprise clients under any circumstances. They
do not commit to timeframes. Escalation from a seasonal specialist goes to a permanent
Client Support Specialist, never directly to an Account Manager.

---

## Peak triage model

This is the core of the document. During weeks 46–52, the standard first-response
targets in POL-ESC-001 remain the official commitment, but capacity does not exist to
meet them across the full queue. The triage model defines what is protected.

### Protected — targets met without exception

- All **S1** incidents, any tier. 30-minute first response, hourly updates, 4-hour
  target resolution. No degradation. If capacity is insufficient, capacity is taken from
  lower tiers.
- All **S2** incidents from **enterprise** clients. 2-hour first response.
- Any **safety, security, or regulatory** matter, any tier, any severity — these bypass
  triage entirely per POL-ESC-001.
- Any client **threatening contract termination.**

### Managed — targets met on a best-effort basis, degradation communicated

- **S2** from Growth-tier clients. Target remains 2 hours; realistic expectation during
  weeks 48–50 is 4–6 hours. The Account Manager sets expectations proactively rather
  than letting the target silently slip.
- **S3** from enterprise clients. Note these are worked at S2 targets under the standard
  enterprise uplift in POL-ESC-001, and that uplift is preserved during peak.

### Degraded — explicitly relaxed, with client notification

- **S3** from Growth and Standard tiers. Target moves from 1 business day first response
  to **2 business days** for weeks 47–52.
- **S4**, all tiers. Target moves from 2 business days to **4 business days** for weeks
  47–52.

**Degradation requires notification.** The peak service advisory (template PEAK-COMM-01)
goes to all Growth and Standard clients by week 45 Friday, stating the temporarily
extended response targets and the date normal targets resume (week 3 of January).

A degraded target that the client was told about is a managed expectation. The same
degradation without notice is an SLA breach and, for any client with contractual response
terms, a credit exposure. The notification is the entire difference and it is the step
most often skipped under pressure.

### What is never degraded

Recorded explicitly because these have been informally deprioritized in past peaks and
should not be:

- **Written incident summaries** for S1 and S2 within 24 hours of resolution. The
  temptation to defer these to January is strong and every year some are never written.
- **Post-incident reviews** for S1 incidents, within 5 business days.
- **Carrier claim filing within 48 hours** per SOP-REC-004. Missing this window forfeits
  the claim entirely; the deadline is external and does not move for our staffing.
- **Blind recount** on receiving discrepancies. Under time pressure, teams have
  historically skipped the second count. This converts a caught discrepancy into an
  inventory variance that surfaces in January.

---

## Facility operating changes

### Receiving

- **Appointment required**, 72 hours advance notice, weeks 46–52. Unscheduled arrivals
  are received only if dock capacity permits; otherwise the carrier is turned away and
  the client's Account Manager is notified same day.
- **Container unloads are not scheduled weeks 48–50** at Richmond or Reno. Columbus
  retains limited capacity. Clients with container inbounds must land them by week 47 or
  accept a week 51 slot.
- Receiving discrepancy handling **does not change**. SOP-REC-004 applies in full. The
  2% / 50-unit variance thresholds, the blind recount, the 48-hour carrier claim window,
  and the escalation triggers all hold.
- **Overages are still held entirely.** Peak pressure creates a strong temptation to
  absorb an unexplained overage into sellable stock. Do not. It is frequently another
  client's inventory and the January reconciliation is significantly worse than the
  week-48 inconvenience.

### Storage

Storage bills on peak occupancy per FIN-RATE-2026-01, at $28.00 per pallet position per
month for Standard tier. During weeks 44–47 most clients build inventory hard, which
means **the peak-occupancy figure for November and December is set by the build, not the
sell-through.**

This is the single most disputed line on the invoice year-round, and peak makes it
worse: a client who builds to 400 pallets in week 45 and sells down to 90 by week 52
still bills 400 for the period. This is correct per contract. It is also the least
intuitive outcome on the invoice.

Account Managers send the storage advisory (PEAK-COMM-03) in week 43, before the build,
explaining peak-occupancy billing with a worked example. Sending it after the build has
started is materially less effective — the client has already committed the inventory.

The long-term storage surcharge (+25% at 181 days, +50% at 365) applies at the SKU-lot
level. Post-peak, unsold seasonal inventory crosses the 181-day threshold in roughly
late May. Flagging this in January gives clients time to act; flagging it in June does not.

### Cycle counts

Class A counts continue monthly. Class B and C counts are **suspended weeks 46–52** and
resume week 2 of January.

Trigger counts are **not suspended.** Negative on-hand, pick shortages, two or more
variances in one aisle within 30 days, and client-reported discrepancies all still
require a count. Suspending scheduled counts while continuing trigger counts is
deliberate: scheduled counts are preventive and can wait, trigger counts are diagnostic
and cannot.

At Reno specifically, the mezzanine restrictions in SOP-PUT-007 remain in force through
peak, including the second-shift pairing requirement after 19:00. Peak volume is not
grounds for waiving them; the accuracy problem they address is worse under volume, not
better.

### Shipping

- **Carrier cutoffs tighten weekly** from week 48. The carrier cutoff calendar
  (CAR-POL-001 Appendix A) is republished every Monday during peak because carriers
  revise their published cutoffs mid-season more often than not.
- **Do not promise a delivery date to a client.** Ever, but especially during peak.
  Promise a ship date, which Meridian controls. Delivery is the carrier's commitment and
  in weeks 50–51 carrier on-time performance has historically fallen to 71–84% against
  published service levels.
- Address correction charges ($18.00, passed through) spike during peak because gift
  shipping to unfamiliar addresses is common. Expect and pre-explain these.

---

## Communication templates and schedule

| Template | Content | Sent by | Audience |
|---|---|---|---|
| PEAK-COMM-01 | Service advisory: temporary response targets | Week 45 Fri | Growth, Standard |
| PEAK-COMM-02 | Billing advisory: +8% surcharge, service-date basis | Week 44 Fri | All |
| PEAK-COMM-03 | Storage advisory: peak-occupancy worked example | Week 43 Fri | All |
| PEAK-COMM-04 | Receiving advisory: appointment requirement | Week 43 Fri | All |
| PEAK-COMM-05 | Cutoff calendar | Week 46, then weekly | All |
| PEAK-COMM-06 | Post-peak: normal targets resume | Week 2 Jan | Growth, Standard |

Enterprise clients receive all of the above **plus** a named conversation with their
Senior Account Manager during week 43. Templates are not sufficient for enterprise; the
monthly business review in October is the correct forum.

---

## Daily peak cadence

Weeks 47–51, every operating day:

| Time | Activity | Attendees |
|---|---|---|
| 07:00 | Facility stand-up: prior-day actuals, today's plan, blockers | Facility Mgr, shift leads |
| 08:30 | Network call: cross-facility capacity, carrier issues | VP Ops, 3 Facility Mgrs, Client Ops Mgr |
| 12:00 | Queue review: aged tickets, escalation risk | Client Ops Mgr, Senior AMs |
| 16:00 | Cutoff check: at-risk orders for today's cutoff | Facility Mgrs |
| 18:00 | Written day summary to VP Ops | Facility Mgrs |

The 08:30 network call is the one that matters most and is the one most often allowed
to lapse after week 49. It is the only forum where capacity is moved between facilities.
In 2025 it stopped being held after 2025-12-08 and two of that year's four S1 incidents
occurred in the following week.

---

## Post-peak

**Week 1 January:** returns surge and invoice disputes arrive together. Support staffing
must be maintained through **week 2 January minimum.** Ending seasonal contracts on
31 December is a recurring error.

**Week 2 January:** normal response targets resume; PEAK-COMM-06 sent. Class B and C
cycle counts resume. WMS change freeze lifts.

**Week 3 January:** peak retrospective, chaired by VP Operations. Required attendees:
all Facility Managers, Client Operations Manager, one Billing Analyst, two shift
supervisors, and at least one seasonal support specialist. The last is deliberate — the
people who worked the degraded queue see things the permanent staff do not.

Output: a written retrospective including, at minimum, actual versus modeled volume,
incident count by severity, SLA attainment by tier, credit total issued, and a ranked
list of what to change before week 43 of the following year.

The 2025 retrospective produced eleven recommendations. Four were implemented. This
document is one of them.

---

## Known limitations

1. **The support staffing gap is unresolved** and this document manages rather than
   fixes it. If order volume grows more than ~12% year over year, the triage model
   degrades from "managed shortfall" to "unmanaged shortfall" and the protected tier
   itself comes under pressure.
2. **The volume indices are drawn from three years of history** across a client base
   that has changed composition significantly. Enterprise clients grew from 8 to 12
   over that period. The indices are directionally reliable and numerically approximate.
3. **Carrier performance is assumed, not contracted.** Meridian holds no service-level
   guarantees from any carrier during peak that survive a force majeure clause, and
   every carrier invokes weather liberally in December.
4. **No facility has surge storage capacity.** Richmond runs at 91% pallet occupancy at
   peak, Columbus 88%, Reno 94%. A single large unplanned inbound in week 47 has nowhere
   to go. This has been raised for three consecutive planning cycles.

---

## Related documents

POL-ESC-001 (Escalation Matrix) · FIN-RATE-2026-01 (Billing Rate Card) ·
POL-FIN-003 (Billing Disputes) · SOP-REC-004 (Receiving Discrepancies) ·
SOP-INV-002 (Cycle Counts) · SOP-PUT-007 (Putaway — Reno) · CAR-POL-001 (Carrier
Management) · VEN-POL-002 (Vendor and Temporary Labour)
