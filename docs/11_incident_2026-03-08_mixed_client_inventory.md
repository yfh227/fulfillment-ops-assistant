# Post-Incident Review — INC-2026-0104

> Fictional reference document — Meridian Fulfillment Co.

**Incident ID:** INC-2026-0104
**Severity:** S1 — Critical
**Title:** Client-owned inventory shipped to another client's customers, Reno
**Date:** Discovered 2026-03-08; originated 2026-02-24
**Facility affected:** Reno
**Clients affected:** 2 — Halden Goods (Growth), Peakline Outdoor (Growth)
**Review held:** 2026-03-13
**Chair:** Client Operations Manager
**Attendees:** Client Ops Mgr, VP Operations, Reno Facility Manager, 2 Account Managers,
WMS Engineering Lead, 1 Billing Analyst
**Status:** Closed 2026-05-29

---

## Severity classification

Declared **S1 — Critical** on 2026-03-08 at 15:42 by the Reno Facility Manager.

The S1 definition in POL-ESC-001 covers *"a systemic failure affects multiple clients"*
and lists *"security incident"* among its examples. This incident involved one client's
goods being shipped to a second client's customers — a custody failure affecting two
clients simultaneously, with potential contractual and insurance exposure.

Classification was debated during the incident. The initial instinct was S2, on the basis
that only 43 orders were involved and no client's business was stopped. The Facility
Manager escalated to S1 on the grounds that goods had left Meridian's custody and gone to
third parties, which cannot be reversed by an internal fix.

**The S1 call was correct** and the review endorsed it unanimously. The distinguishing
question is not volume — it is reversibility and whether the failure crosses a custody
boundary.

**Applicable targets:** 30-minute first response · hourly updates · 4-hour target
resolution.

Resolution was declared at 2026-03-08 19:20, 3h38m from declaration — inside the 4-hour
target. "Resolution" here means containment: shipping halted, scope quantified, both
clients notified. Full remediation ran to 2026-05-29.

---

## Timeline

All times US Pacific (Reno local).

| Time | Event |
|---|---|
| **Tue 2026-02-24** | |
| 15:10 | Halden Goods inbound received at Reno. 18 pallets, ASN matched, no discrepancy. |
| 16:35 | Putaway. Six pallets of SKU `HG-4471` (insulated bottle, 750ml) directed to mezzanine `19-C-04-1M`. Operator places them in ground location `19-C-04-1`. Enforcement disabled — system accepts. |
| | *Ground location `19-C-04-1` held Peakline Outdoor SKU `PO-2210`, a visually similar insulated bottle.* |
| **Wed 2026-02-25 → Fri 2026-03-06** | |
| — | 43 Peakline orders pick from `19-C-04-1`. Pickers scan the location, take the top cartons — Halden stock — and ship. Barcodes on the outer cartons were scanned at pick and did not match the order SKU, but the mismatch produced a soft warning, not a block. See Finding 2. |
| **Fri 2026-03-06** | |
| 11:20 | First customer complaint reaches Peakline: wrong product received. Peakline treats it as an isolated error, does not contact Meridian. |
| **Sat 2026-03-07** | |
| — | Four further Peakline customer complaints. |
| **Sun 2026-03-08** | |
| 09:15 | Peakline emails their Account Manager: five customers received the wrong bottle, branded Halden Goods. |
| 10:02 | Account Manager reviews, escalates to Reno FM. |
| 10:30–15:00 | Reno investigates. Physical walk of `19-C-04-1` finds mixed stock: Halden `HG-4471` on top, Peakline `PO-2210` beneath. |
| 15:42 | **S1 declared.** Client Ops Mgr and VP Operations paged. |
| 16:05 | First response to both clients — 23 minutes, inside the 30-minute target. |
| 16:20 | Location frozen. Full-count triggered on aisle 19 per SOP-INV-002 trigger conditions. |
| 16:50 | WMS query identifies all orders picked from `19-C-04-1` since 2026-02-24: **43 orders**, all Peakline. |
| 17:15 | Hourly update #1 to both clients. |
| 17:40 | Halden inventory reconciled: 1,440 units of `HG-4471` received, 1,053 on hand, **387 units unaccounted**. 43 orders × 9 units average = 387. Reconciles exactly. |
| 18:15 | Hourly update #2. |
| 18:40 | Aisle 19 count complete. No other mixed locations found. |
| 19:20 | **Containment declared.** Both clients notified with full scope. |
| **Mon 2026-03-09** | |
| 08:00 | Recovery outreach begins to 43 Peakline end customers. |
| 2026-03-09 → 03-27 | Recovery: 31 of 43 customers return the Halden product. |
| **2026-05-29** | Final remediation action closed. |

---

## Impact

| Measure | Value |
|---|---|
| Duration, declaration to containment | 3h38m |
| Duration, origination to discovery | **12 days** |
| Orders affected | 43 |
| End customers who received wrong product | 43 |
| Halden units shipped in error | 387 |
| Halden units recovered | 279 (31 customers) |
| Halden units written off | 108 |
| Peakline orders requiring reship | 43 |
| Credits issued | $11,850 total |
| Zendesk tickets | 9 |

### Credit detail

| Client | Amount | Classification | Approver | Basis |
|---|---|---|---|---|
| Halden Goods | $4,350 | Meridian error | VP Operations | 108 units written off at $32.50 landed cost, plus handling |
| Peakline Outdoor | $7,500 | Meridian error | VP Operations | 43 reships, expedited freight, customer-service cost |

Combined $11,850. Both individually fell in the $2,501–$10,000 band requiring **VP
Operations** approval per POL-FIN-003. Neither exceeded $10,000 individually, so CFO
approval was not triggered.

The review noted that the *combined* figure exceeds $10,000 and that POL-FIN-003 is
written in terms of individual credit amounts, not incident totals. The Client Operations
Manager raised this as a possible policy gap: a single incident can distribute credits
across clients to stay under the CFO threshold without anyone intending to. Referred to
Finance; see Action 9.

Both credits classified **error**, not goodwill. Unambiguous — Meridian shipped the wrong
client's goods.

---

## Root cause

**Immediate cause:** six pallets of Halden `HG-4471` were placed in a ground location
holding Peakline `PO-2210`, rather than the directed mezzanine location one level above.
Subsequent picks took the wrong client's product from a location the picker had correctly
scanned.

**This is a PUT-01 event** — putaway to wrong location — of exactly the kind documented in
SOP-INV-002 as running elevated at Reno since Q4 2025.

The specific mechanism is the ground/mezzanine label pair identified in the Reno putaway
investigation: directed location `19-C-04-1M`, actual location `19-C-04-1`. The trailing
`M` is the only difference between the two.

**Why it persisted 12 days:**

1. **Directed putaway enforcement was disabled at Reno** and had been since March 2024.
   The system accepted the wrong location without objection.
2. **The SKUs are visually similar.** Both are 750ml insulated bottles in brown corrugated
   cartons of comparable size. Distinguished by the printed SKU and client name on the
   carton end panel.
3. **Pick-time SKU mismatch generated a warning, not a block** (Finding 2).
4. **Neither SKU was due a cycle count.** `HG-4471` is Class B (quarterly), `PO-2210` is
   Class B. Neither is high-value — unit costs $32.50 and $28.90, both below the $250
   threshold that would force monthly counting. No trigger condition fired because no
   negative on-hand or pick shortage occurred; the location had ample stock, just the
   wrong client's.
5. **No cross-client location validation existed.** Nothing in the WMS objected to two
   clients' goods occupying one location.

Point 5 is the most serious. Meridian's location model permits mixed-client locations
because a small number of bin locations legitimately hold multiple clients' slow-moving
SKUs. That exception was never bounded to bin locations, so it applied everywhere.

**Relationship to the Reno putaway investigation:** the formal PUT-01 investigation
(SOP-PUT-007) began 2026-04-06, four weeks *after* this incident. This incident was a
significant input to it and materially accelerated its scope — in particular, the
decision to re-walk misputs physically rather than analyse adjustment records alone came
directly from what the aisle 19 count found here. The enforcement re-enablement
(SOP-PUT-007 Action 1, completed 2026-06-15) is the direct remediation.

---

## Findings

### Finding 1 — Twelve days is the finding

Containment took 3h38m and was competent. Origination to discovery took **twelve days**,
and discovery came from a client's customers, not from any Meridian control.

Every control that could have caught this either did not exist, was disabled, or was not
scheduled to run:

| Control | Status at time of incident |
|---|---|
| Directed putaway enforcement | Disabled since 2024-03 |
| Pick-time SKU verification | Warning only, not a block |
| Cross-client location validation | Did not exist |
| Cycle count on affected SKUs | Not due — both Class B, quarterly |
| Inventory reconciliation | Would have caught at Halden's next count, ~6 weeks out |

### Finding 2 — Pick-time SKU mismatch was a soft warning

When a picker scans a carton whose SKU does not match the order line, the WMS displays
`SKU MISMATCH — CONFIRM?` with a confirm button. It does not block.

The soft warning was implemented in 2022 to handle legitimate cases: repackaged goods,
client SKU renames mid-flight, and multi-pack variants sharing a parent barcode.

Reno pickers confirmed through this warning **an average of 31 times per day** across the
facility. At that frequency it is not a warning; it is a keystroke. Interviews found
pickers were dismissing it without reading, which is the predictable outcome of a control
that fires constantly and is right to be dismissed most of the time.

This is alarm fatigue and it is a design failure, not a picker failure.

### Finding 3 — Mixed-client locations were permitted everywhere

The WMS permits any location to hold multiple clients' inventory. This was intended for a
narrow bin-location case and was never constrained.

Audit across all three facilities found **1,847 locations** holding more than one client's
goods. Of those, 1,309 were bin locations where it is intended. **538 were pallet or shelf
locations where it is not.**

Reno accounted for 402 of the 538 — again, consistent with the enforcement being disabled
there and operators placing product where it fit.

### Finding 4 — Recovery from end customers is slow and incomplete

31 of 43 customers returned the Halden product; 12 did not, despite prepaid labels and two
follow-ups. 108 units, $3,510 at landed cost, written off.

There is no process for recovering goods from a third party's customers because it had
never happened. The outreach was improvised by the two Account Managers over three weeks.

### Finding 5 — Halden was notified appropriately; the sequencing was luck

Both clients were notified at 16:05, inside the 30-minute target, and both received full
scope at 19:20.

The review noted that the *decision* to notify Halden immediately — before knowing how
many units were involved — was made by the Account Manager without consulting anyone,
because Halden's goods had left custody and she judged they had a right to know at once.

That was correct. But POL-ESC-001 gives no guidance on notifying a client whose goods are
implicated in another client's incident, and the outcome depended on one person's
judgement rather than on policy.

### Finding 6 — The Peakline customers were told the truth

Peakline's customer-facing message, drafted jointly with Meridian, stated that a
fulfilment error at the warehouse sent the wrong product and offered a prepaid return
plus the correct item shipped immediately, no return required first.

Meridian's Account Manager pushed for this over a vaguer "shipping error" formulation.
Recorded as a positive finding: the direct version generated fewer follow-up contacts
and Peakline's own customer-service load was lower than modelled.

---

## Corrective actions

| # | Action | Owner | Due | Status |
|---|---|---|---|---|
| 1 | Re-enable directed putaway enforcement at Reno | WMS Eng | 2026-04-30 | Complete 2026-06-15 (see note) |
| 2 | Convert pick-time SKU mismatch from warning to hard block outside a whitelisted exception set | WMS Eng | 2026-04-24 | Complete |
| 3 | Define and enforce single-client locations for all pallet and shelf locations | WMS Eng | 2026-05-15 | Complete |
| 4 | Remediate the 538 non-bin mixed-client locations | Facility Mgrs | 2026-05-29 | Complete |
| 5 | Full physical count, Reno aisles 14–22 | Reno FM | 2026-03-20 | Complete — 3 further mixed locations found |
| 6 | Write cross-client custody incident procedure | Client Ops Mgr | 2026-05-01 | Complete — SOP-CUST-001 |
| 7 | Formal investigation into Reno PUT-01 rate | Reno FM | 2026-06-30 | Complete — SOP-PUT-007 |
| 8 | Add end-customer recovery procedure to SOP-CUST-001 | Client Ops Mgr | 2026-05-01 | Complete |
| 9 | Review POL-FIN-003 approval thresholds for incident-level aggregation | Finance | 2026-06-30 | **Open** |
| 10 | Audit soft warnings across the WMS for alarm fatigue | WMS Eng | 2026-07-31 | **Open** — 14 identified, 6 reviewed |

**Note on Action 1:** originally due 2026-04-30, completed 2026-06-15, six weeks late. The
delay was caused by the discovery during implementation that roughly 900 Reno location
master records had drifted while enforcement was disabled, and enabling enforcement
without correcting them would have blocked legitimate putaway at scale. The correction
work was necessary and unplanned. Recorded as a genuine slip with a legitimate cause.

Actions 9 and 10 remain open as of this document's revision date.

---

## What went well

- **The S1 call was correct and made against instinct.** The initial read was S2 on
  volume; the Facility Manager escalated on custody grounds. Reversibility, not order
  count, is the right test.
- **First response in 23 minutes** against a 30-minute target, to two clients simultaneously.
- **Containment in 3h38m** against a 4-hour target.
- **The reconciliation was exact.** 387 units unaccounted, 43 orders, 9 units average —
  arithmetic that closed cleanly and gave both clients a defensible number within hours.
- **Aisle 19 was counted the same evening** rather than deferred, and the full aisles
  14–22 count followed within twelve days.
- **Both clients retained.** Halden renewed in June 2026. Peakline remains active.

---

## Disagreement recorded

The Reno Facility Manager objected to Finding 1's framing that "every control failed,"
noting that the pick-time SKU warning *did* fire — 43 times — and was dismissed.

The Client Operations Manager's position, which the review adopted: a control dismissed 31
times a day in normal operation is not functioning as a control, and counting it as
"fired" overstates its value.

Both views are recorded. Action 10, the alarm-fatigue audit, came directly out of this
exchange and is the more useful outcome than agreement would have been.

---

## Related documents

POL-ESC-001 (Escalation Matrix) · POL-FIN-003 (Billing Disputes and Adjustments) ·
SOP-INV-002 (Inventory Cycle Counts) · SOP-PUT-007 (Putaway — Reno) ·
SOP-REC-004 (Receiving Discrepancies) · SOP-CUST-001 (Cross-Client Custody Incidents) ·
INV-RPT-2026-Q2 · INC-2025-0417 · INC-2026-0038
