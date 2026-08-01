# Onboarding Case Note — Fernpost Paper (Standard)

> Fictional reference document — Meridian Fulfillment Co.

**Document ID:** ONB-CASE-2026-058
**Client:** Fernpost Paper
**Tier:** Standard
**Onboarding Specialist:** T. Nakamura
**Support:** Pooled queue (no named Account Manager — standard tier)
**Signature date:** 2026-04-06
**Target first live order:** 2026-05-05 (21 business days per SOP-ONB-001)
**Actual first live order:** 2026-05-04 — **1 business day early**
**Facility:** Columbus
**Status:** Closed, active client — **escalated post-go-live, see below**

---

## Summary

Fernpost Paper is a stationery and greeting-card brand, approximately 2,400 orders/month,
Standard tier.

**Onboarding finished a day early with every checklist item complete.** By the measure
SOP-ONB-001 uses, this is Meridian's best onboarding of 2026.

Six weeks later, Fernpost raised an S2 and threatened to leave.

This case note exists because the first two case notes in this series document
onboardings that ran late and ended well. This one ran on time and ended badly, and the
contrast identifies something the checklist measures poorly: **the checklist verifies
that steps were completed, not that the client understood what they were agreeing to.**

---

## Client profile at signature

| | |
|---|---|
| Category | Stationery, greeting cards, gift wrap |
| Orders/month at signature | ~2,400 |
| SKU count | 892 |
| Lot-tracked SKUs | 0 |
| Integration | Shopify |
| Storage profile | Bin and shelf |
| Contracted tier | Standard |
| Rate schedule | **FIN-RATE-2026-01** (standard card, unnegotiated) |
| Support model | Pooled queue, self-service portal |

---

## Onboarding timeline

Brief, because it was uneventful.

| Phase | Standard | Actual | Notes |
|---|---|---|---|
| 1 — Account setup | Days 1–3 | Days 1–3 ✅ | Escalation contact captured day 2 |
| 2 — Systems | Days 3–8 | Days 3–7 ✅ | Shopify, standard connector, no issues |
| 3 — Product setup | Days 5–12 | Days 5–11 ✅ | 892 SKUs; 34 flagged for missing dimensions, resolved day 9 |
| 4 — Inbound | Days 10–18 | Days 12–17 ✅ | 9 pallets, ASN matched, no discrepancy |
| 5 — Go live | Days 18–21 | Days 18–20 ✅ | First live order day 20 |
| 6 — Handoff | Day 21+ | Day 20 ✅ | Account file complete, 30-day review scheduled |

All 61 checklist items completed. Onboarding retro logged: *"No delays. Client responsive.
Model onboarding."*

The 10-SKU physical spot check from ONB-CASE-2026-031 was in force by this date and was
performed on day 12. All ten matched. Dimensions were correct.

---

## What happened next

**2026-06-01:** first invoice issued, covering May.

**2026-06-03:** Fernpost's founder submits a Zendesk ticket, tagged `billing-dispute` per
POL-FIN-003. Disputed amount **$1,847** against a total invoice of $4,206 — 44% of the
invoice.

**Disputed lines:**

| Line | Amount | Client position |
|---|---|---|
| Storage — 68 pallet positions | $1,904 | "We were told this would be around $600" |
| Manual order entry, 214 orders @ $3.50 | $749 | "All our orders come through Shopify" |
| Monthly account minimum | $500 | "Nobody mentioned a minimum" |

**2026-06-04:** acknowledged within 1 business day per POL-FIN-003. ✅

**2026-06-09:** substantive response, within the 5-business-day target. ✅

**Investigation findings, per POL-FIN-003 Step 1 (reproduce the charge from source
records):**

**Storage — charge correct.** Storage bills on **peak occupancy** during the period, not
average or month-end, per FIN-RATE-2026-01 at $28.00 per pallet position per month.
Fernpost's inbound landed 68 pallets on 2026-05-14. They sold down to 31 positions by
2026-05-31. Peak was 68. Charge: 68 × $28.00 = $1,904. Correct per contract.

Classification: **client misunderstanding**. No credit due.

**Manual order entry — charge correct, but symptomatic.** 214 of 2,390 May orders arrived
outside the Shopify integration. Investigation found Fernpost's wholesale orders are
entered in a separate system and emailed to Meridian as spreadsheets. Nobody at Meridian
had asked about wholesale during onboarding; nobody at Fernpost had thought to mention it,
since "orders are orders."

Per POL-FIN-003's guidance on manual order entry fees — *"usually indicates an integration
failure the client hasn't noticed — investigate the root cause, don't just explain the
fee"* — this was investigated rather than merely explained. Classification: **client
misunderstanding** on the charge, with a genuine process gap underneath.

**Account minimum — charge correct.** $500 monthly minimum, stated in FIN-RATE-2026-01 and
in the signed agreement. Fernpost's May activity billed $4,206, above the minimum, so the
minimum did not actually apply — the line appeared on the invoice as an informational
zero-dollar entry and the client read it as a charge.

Classification: **invoice presentation defect.** No credit due, but the invoice is
genuinely misleading.

**2026-06-09:** response sent. All three lines explained with worked figures per
POL-FIN-003's requirement to explain *how* a charge was calculated rather than merely that
it is correct.

**2026-06-10:** Fernpost's founder replies. Escalates. Quoted in full because the wording
matters:

> "I understand the maths. What I don't understand is why nobody explained peak-occupancy
> billing to me before I sent you 68 pallets. I would have sent them in two shipments.
> You had three weeks to tell me and my invoice is double what I budgeted. If this is how
> it works I need to look at other options."

**2026-06-10:** classified **S2** under POL-ESC-001 — *"any client threatening contract
termination"* is listed under immediate-escalation conditions, and the Client Operations
Manager was contacted directly, bypassing the normal sequence, as that section requires.

**2026-06-11:** Client Operations Manager calls the founder.

**2026-06-13:** resolution.

- **$400 goodwill credit** issued. Approved by the Client Operations Manager — within the
  $250–$2,500 band per POL-FIN-003, and correctly recorded as **goodwill, not error**,
  since no Meridian error occurred. The distinction matters for trend reporting and was
  applied correctly here, unlike in INC-2025-0417 where four tickets were initially
  miscoded.
- Inbound scheduling guidance provided: split large inbounds across billing periods where
  the sell-down profile supports it.
- Wholesale orders moved to a CSV integration, eliminating the manual entry fee. Setup
  waived.
- Invoice template amended so zero-dollar minimum lines do not render.

**2026-06-13:** Fernpost confirms they are staying. Still active as of this document.

---

## Root cause

**The onboarding checklist has one line covering commercial explanation:**

> `[ ] Billing cycle and first invoice date explained`

It was checked. Truthfully. The billing cycle *was* explained — invoices issue on the 1st
for the prior calendar month, net 30. That is what the line asks for and that is what was
delivered.

**Nothing in the checklist requires explaining how any charge is calculated.**

Specifically absent:

- Peak-occupancy storage billing — named in FIN-RATE-2026-01 as *"the most frequently
  misunderstood line on the invoice"* and in POL-FIN-003 as *"the single most disputed
  line."*
- What triggers manual order entry fees.
- What the account minimum is and when it applies.
- The +8% peak surcharge and its service-date basis — not yet relevant to Fernpost but
  arriving in week 46.

Meridian's own documents identify peak-occupancy storage as the number-one source of
disputes across the entire client base. **That knowledge has never been connected to the
onboarding process.** It lives in the rate card and the dispute policy — documents the
client does not read and the Onboarding Specialist has no reason to open.

**Why Standard tier is where this bites hardest:**

- Enterprise and Growth clients negotiate their rate schedules, so a commercial
  conversation happens by necessity. A negotiation *is* an explanation.
- Standard clients take the published card. No negotiation, therefore no conversation.
- Standard clients have **no named Account Manager** — pooled support only. There is no
  one whose job is to notice a client about to make an expensive mistake.
- Standard clients are the most likely to be first-time outsourcers and the least likely
  to know that peak-occupancy billing is an industry norm.

**44 of Meridian's 87 clients are Standard tier.** This gap applies to all of them.

---

## Would the outcome have differed with a named Account Manager?

The review considered this and concluded: probably, but not reliably.

Fernpost's 68-pallet inbound was scheduled through the receiving team on 2026-05-08 for
delivery 2026-05-14. A named Account Manager reviewing that schedule against a mid-month
delivery date and a monthly peak-occupancy billing basis *might* have flagged it.

But nothing instructs an Account Manager to look at inbound schedules through a billing
lens, and Growth-tier AMs carry roughly 3.4 accounts each with no such review step. The
control does not exist at any tier; Enterprise and Growth are protected by the
negotiation conversation, which is incidental rather than designed.

---

## Recommendations

Submitted to the Client Operations Manager 2026-06-18.

1. **Add a mandatory commercial walkthrough to Phase 5**, covering peak-occupancy storage
   with a worked example using the client's own projected volumes, manual order entry
   triggers, the account minimum, and the peak surcharge. **Status: accepted, added to
   SOP-ONB-001 in the 2026-07 revision.**
2. **Ask about order channels explicitly in Phase 2.** "Do you have any orders that will
   not come through the integration — wholesale, B2B, phone, marketplace?" One question
   would have caught the 214 manual orders. **Status: accepted.**
3. **Add an inbound-timing advisory** for the first inbound of any new client, explaining
   that a large single inbound sets the peak for the whole month. **Status: accepted.**
4. **Fix the invoice template** so zero-dollar lines do not render. **Status: complete
   2026-06-30.**
5. **Review whether Standard tier should have a named contact for the first 90 days.**
   **Status: under review — resourcing implications, 44 clients.**

---

## Honest assessment

This onboarding scored perfectly on every metric Meridian tracks and produced a client who
threatened to leave within six weeks. The retro note — *"Model onboarding"* — was written
in good faith and was wrong in a way nothing in the process could have detected.

The specialist is the same person who ran the Lumen onboarding (ONB-CASE-2026-031) and who
identified the dimension-definition gap there. She is a strong performer. The checklist
told her she was done and she reasonably believed it.

**What makes this the most useful of the three case notes:** the other two failed visibly
and were fixed. This one succeeded by its own measure. If Meridian only reviews
onboardings that ran late, this failure mode is invisible — and it applies to the 44
Standard-tier clients who generate the most disputes and receive the least attention.

The $400 credit is the cheapest thing about this incident. The expensive part is that
Fernpost is one of 44, and only one of them complained.

---

## Related documents

SOP-ONB-001 (Client Onboarding Checklist) · FIN-RATE-2026-01 (Billing Rate Card —
Standard Tier) · POL-FIN-003 (Billing Disputes and Adjustments) · POL-ESC-001
(Escalation Matrix) · ONB-CASE-2025-114 · ONB-CASE-2026-031
