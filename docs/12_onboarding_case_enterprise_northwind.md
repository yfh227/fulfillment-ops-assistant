# Onboarding Case Note — Northwind Provisions (Enterprise)

> Fictional reference document — Meridian Fulfillment Co.

**Document ID:** ONB-CASE-2025-114
**Client:** Northwind Provisions
**Tier:** Enterprise
**Onboarding Specialist:** R. Adeyemi
**Senior Account Manager:** J. Baptiste
**Signature date:** 2025-08-04
**Target first live order:** 2025-09-02 (21 business days per SOP-ONB-001)
**Actual first live order:** 2025-10-17 — **32 business days late**
**Facility:** Columbus
**Status:** Closed, active client

---

## Summary

Northwind Provisions is a premium pantry and dry-goods brand, approximately 68,000
orders/month at signature, qualifying comfortably for Enterprise tier. Onboarding ran
53 business days against a 21-day standard — the longest enterprise onboarding Meridian
has completed and the second-longest of any tier.

**The overrun was not caused by the standard delay drivers.** SKU dimension data arrived
complete and validated on day 4. Integration credentials were exchanged on day 6.
Escalation contact was captured on day 2. The five common delay causes listed in
SOP-ONB-001 were each avoided.

The overrun was caused by a category the checklist does not cover: **lot-tracking and
FEFO requirements that were understood by both parties to be in scope but were never
specified in enough detail to build against.** Discovery came on day 19, at inbound.

This case note is written primarily to argue that SOP-ONB-001 needs a
requirements-specification gate for enterprise clients that does not currently exist.

---

## Client profile at signature

| | |
|---|---|
| Category | Premium pantry, dry goods, some perishable |
| Orders/month at signature | ~68,000 |
| SKU count | 1,240 |
| Lot-tracked SKUs | 1,190 (96%) |
| Serialized SKUs | 0 |
| Integration | NetSuite → Meridian API |
| Storage profile | Mixed pallet and shelf |
| Contracted tier | Enterprise |
| Rate schedule | Negotiated — see FIN-RATE-ENT-NWP-2025 |
| Contractual SLA | 99.2% on-time ship, defined remedy |

---

## Timeline against SOP-ONB-001 phases

### Phase 1 — Account setup (standard Days 1–3; actual Days 1–3) ✅

Completed on schedule. Notable: the escalation contact was captured on day 2 without
prompting, because the client's implementation lead had been through a 3PL transition
before and volunteered it.

SOP-ONB-001 flags the escalation contact as "required, and frequently missed." It was not
missed here, and the reason was the client, not our process. Worth noting because it
means the process still has the gap even when the outcome is fine.

### Phase 2 — Systems (standard Days 3–8; actual Days 3–11) ⚠️ +3 days

Integration credentials exchanged day 6 via the secure channel. Test connection succeeded
day 7.

Slip cause: NetSuite's order object required a custom field mapping for Northwind's
lot-allocation preference, which Meridian's connector did not support out of the box. Two
days of connector work, plus one day retest.

**This was the first signal of the lot-tracking gap and it was not recognized as such.**
It was logged as a routine integration customization and closed. In hindsight it was the
first of five separate lot-related surprises.

### Phase 3 — Product setup (standard Days 5–12; actual Days 5–14) ⚠️ +2 days

SKU master received day 4 — ahead of schedule — in the correct template, with complete
dimensions, weights, unit costs, and barcodes for all 1,240 SKUs.

**This is the best SKU master Meridian has received from any client.** Northwind's data
team had cleaned it before sending. Zero SKUs flagged for missing dimensions, against a
typical enterprise onboarding rate of 12–20%.

The two-day slip was hazmat classification on 14 SKUs (aerosol cooking sprays) requiring
documentation the client had to obtain from their manufacturer.

Lot tracking was marked "Yes" on 1,190 SKUs in the template. **The template has a
yes/no column and nothing else.** No field for lot format, expiry handling, FEFO vs FIFO,
shelf-life minimums, or allocation rules. It was recorded as "Yes" and considered complete.

### Phase 4 — Inbound (standard Days 10–18; actual Days 10–41) 🔴 **+23 days**

This is where onboarding broke.

**Day 19 (2025-08-29):** first inbound arrives at Columbus. 22 pallets, ASN matched, no
receiving discrepancy. Putaway proceeds normally.

**Day 19, 16:40:** Northwind's implementation lead asks the Account Manager, in passing,
how Meridian will handle their 120-day minimum remaining shelf life on outbound.

Nobody at Meridian had heard of this requirement.

**Day 20:** requirements conversation reveals five distinct lot-handling requirements,
none of which appear anywhere in the signed agreement, the SKU master, or the onboarding
file:

1. **120-day minimum remaining shelf life** on any outbound unit. Product with less must
   not ship and must be reported.
2. **Strict FEFO**, not FIFO. Meridian's WMS defaults to FIFO and FEFO was a
   configuration change per client, not a setting anyone had flipped.
3. **Lot-level customer traceability.** Northwind must be able to answer, for any order,
   which lot shipped. Required for their recall procedure.
4. **No lot commingling in a pick face.** One lot per location, enforced.
5. **Expiry-based automatic quarantine** at 90 days remaining, with a client-facing
   report for markdown decisions.

Requirements 1, 3, and 5 were entirely new to Meridian. Requirement 2 was a
configuration change. Requirement 4 was achievable but had capacity implications —
one-lot-per-location roughly doubled Northwind's pick-face requirement.

**Days 20–24:** scoping. WMS Engineering assesses requirements 1, 3, and 5 as
development work, not configuration. Estimated 4 weeks.

**Day 24:** escalated to VP Operations. Commercial question: Northwind believed these were
in scope. Meridian's agreement was silent.

**Days 25–31:** commercial negotiation. Resolution: Meridian builds requirements 1, 3, and
5 at Meridian's cost; Northwind accepts a revised go-live and pays a one-time $14,000
configuration fee against roughly $46,000 of development cost. Neither party got what they
wanted, which is the usual shape of a fair outcome.

**Days 31–41:** development and testing. Inbound stock sat in quarantine for 22 days.

**Storage during quarantine was not billed.** Per the negotiated agreement, storage
charges were waived from day 19 to day 41. At Northwind's peak occupancy of 340 pallet
positions that would have been material; the Enterprise schedule rates pallet storage at
$24.50/month against the $28.00 Standard-tier rate in FIN-RATE-2026-01, so the waiver
represented roughly $6,100.

### Phase 5 — Go live (standard Days 18–21; actual Days 42–53) ⚠️ +8 days beyond revised

Test orders day 42. Two further issues:

- FEFO allocation worked but the client portal displayed FIFO ordering, confusing
  Northwind's team during UAT. Display fix, 2 days.
- The 120-day shelf-life block worked correctly and immediately blocked 40% of test
  orders — because test inventory was deliberately near-expiry stock the client had sent
  as samples. Not a defect. Cost a day to diagnose.

**First live order: 2025-10-17, day 53.**

### Phase 6 — Handoff (Day 53+) ✅

Account file transferred to J. Baptiste. 30-day review held 2025-11-19. Northwind rated
the onboarding 3/5 — "painful middle, good outcome."

---

## Post-go-live performance

| Period | On-time ship | SLA (99.2%) | Notes |
|---|---|---|---|
| 2025-11 | 99.4% | Met | |
| 2025-12 | 97.1% | **Breached** | INC-2025-0417 (WMS outage) — credit $6,800 |
| 2026-01 | 99.5% | Met | |
| 2026-02 | 99.6% | Met | |
| 2026-03 | 99.3% | Met | |
| 2026-04 | 99.7% | Met | |
| 2026-05 | 99.6% | Met | |
| 2026-06 | 99.5% | Met | |

The December breach was the network-wide WMS outage, not a Northwind-specific failure.
The $6,800 credit was the largest single credit from that incident.

The lot-handling build has performed well. The 90-day quarantine report has prevented an
estimated $180,000 of expired write-off in eight months, per Northwind's own figures —
which is why the client rates the outcome positively despite the process.

---

## What went wrong, precisely

**The checklist verified that a field was filled in, not that a requirement was understood.**

SOP-ONB-001 Phase 3 says: *"Lot or serial tracking requirements confirmed per SKU."* That
line was checked off truthfully. 1,190 SKUs were confirmed as lot-tracked. The
confirmation captured the *existence* of lot tracking and nothing about its *semantics*.

For a Standard-tier client shipping 800 orders a month, "lot-tracked: yes" is probably
sufficient — the default FIFO behaviour will not hurt anyone. For an enterprise food
client with recall obligations, it is nearly meaningless.

**The checklist is tier-blind.** The same 61 checkboxes apply to a 400-order-a-month
Standard client and a 68,000-order-a-month Enterprise client with regulatory exposure.
The company profile notes that enterprise workflows are well documented while standard-tier
edge cases live in individuals' heads. This case suggests the enterprise documentation is
good at *operations* and weak at *requirements discovery*.

**Nobody owned asking "what else?"** Five people touched this onboarding. Each executed
their phase correctly. No phase owns the question of whether the requirements are complete.

---

## Recommendations

Submitted to the Client Operations Manager 2025-11-24.

1. **Add an enterprise requirements-specification gate** between Phases 1 and 2. A
   structured session covering lot/expiry semantics, allocation rules, traceability
   obligations, regulatory constraints, and reporting requirements. Output is a signed
   requirements document, not a checkbox. **Status: accepted, drafted as SOP-ONB-002,
   in review.**
2. **Expand the SKU master template** to capture lot format, shelf-life minimum, FEFO/FIFO
   preference, and commingling rules. **Status: accepted, template v4 released 2026-01.**
3. **Make Phase 4 inbound conditional** on a signed requirements document for enterprise.
   Inbound arriving before requirements are agreed is what turned a scoping problem into
   22 days of quarantined stock. **Status: accepted.**
4. **Tier the checklist.** Standard, Growth, and Enterprise should not share one document.
   **Status: deferred — resourcing.**
5. **Record commercial exposure of scope gaps.** The $46,000 development cost was absorbed
   because the agreement was silent, not because it was free. **Status: accepted,
   reported quarterly.**

---

## Honest assessment

The client's 3/5 rating is fair and possibly generous.

Northwind did everything asked of them, faster than required, with better data than any
client Meridian has onboarded. They were then late to revenue by seven weeks because
Meridian did not ask what their product needed.

The recovery was handled well — the commercial negotiation was fair, the build was
solid, and the client renewed. But the failure was entirely upstream and entirely
avoidable, and it would have been caught by a single structured conversation in week one.

**The most uncomfortable detail:** the requirement surfaced because a client employee
mentioned it in passing on a phone call. Had that conversation not happened on day 19,
the first indication would have been near-expiry product shipping to Northwind's
customers — a food-safety incident rather than a delay.

---

## Related documents

SOP-ONB-001 (Client Onboarding Checklist) · SOP-ONB-002 (Enterprise Requirements
Specification — draft) · FIN-RATE-ENT-NWP-2025 (Northwind rate schedule) ·
POL-ESC-001 · INC-2025-0417 · ONB-CASE-2026-031 · ONB-CASE-2026-058
