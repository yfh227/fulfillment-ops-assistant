# Policy: Carrier Management, Claims, and Performance

> Fictional reference document — Meridian Fulfillment Co.

**Document ID:** CAR-POL-001
**Owner:** VP Operations (M. Reyes)
**Last reviewed:** 2026-06-11
**Applies to:** All facilities, all client tiers

---

## Scope

Governs carrier selection, rate shopping, claims, performance management, and the
handling of carrier-originated charges that pass through to clients.

Does not govern: client-owned carrier accounts beyond the configuration rules in
Section 3, or freight brokerage for inbound, which sits with the receiving function.

---

## 1. Carrier panel

Meridian maintains contracts with five carriers. Rate shopping runs through
ShipStation/EasyPost at label generation.

| Carrier | Services used | Primary use | Contract expiry |
|---|---|---|---|
| **Continental Parcel (CPX)** | Ground, 2-Day, Overnight | Primary DTC ground | 2027-03-31 |
| **Anchor Freight** | Ground, Economy | Secondary DTC, zone 5–8 | 2026-12-31 |
| **Redline Express** | Overnight, 2-Day | Expedited, hazmat-capable | 2027-06-30 |
| **Postal (USPS)** | Priority, Ground Advantage | Lightweight under 1 lb | Published rates |
| **Cardinal LTL** | LTL, partial truckload | B2B and retail | 2026-10-31 |

### Selection logic

Rate shopping evaluates, in order:

1. **Client-mandated carrier**, where the client contract specifies one. Overrides everything.
2. **Service level required** by the order — expedited orders exclude Ground.
3. **Restrictions** — hazmat, oversize, signature, residential.
4. **Landed cost** including all known accessorials.
5. **Published transit time** to the destination zone.

Where landed cost is within 4%, the carrier with the better trailing 30-day on-time
performance to that zone wins. This tiebreak was added 2026-02 after analysis showed
Meridian was routinely selecting a carrier that was $0.11 cheaper and 6 percentage points
worse on time.

### What rate shopping does not do

Stated because it is a recurring source of misunderstanding internally:

- It does not predict dimensional weight reliably for irregular items. DIM is calculated
  from the *cartonization decision*, and where the packer overrides the suggested carton,
  the shopped rate and the invoiced rate diverge.
- It does not know about carrier surcharges announced mid-cycle. Peak surcharges, fuel
  adjustments, and demand surcharges land on the carrier invoice, not the label quote.
- It does not account for the address-correction risk of a given address.

The gap between shopped cost and invoiced cost averages **3.1%** across 2026 to date and
peaks near 9% in December. This gap is Meridian's cost, not the client's, except where a
charge is explicitly passed through (Section 4).

---

## 2. Cutoffs

Published cutoffs by facility, in local time:

| Carrier | Richmond | Columbus | Reno |
|---|---|---|---|
| Continental Parcel — Ground | 17:00 | 17:30 | 16:00 |
| Continental Parcel — Overnight | 18:00 | 18:00 | 17:00 |
| Anchor Freight | 16:30 | 16:30 | 15:30 |
| Redline Express | 18:30 | 18:30 | 17:30 |
| Postal | 15:00 | 15:00 | 14:30 |
| Cardinal LTL | By appointment | By appointment | By appointment |

**These are carrier pickup cutoffs, not order cutoffs.** Meridian's order cutoff for
same-day shipping is 14:00 local per FIN-RATE-2026-01, tightening to 12:00 local in weeks
48–52 per SOP-PEAK-001. The gap between the two is the pick, pack, and stage window.

**During peak (weeks 46–52), carriers revise published cutoffs with little notice.** The
cutoff calendar is republished every Monday during peak and distributed as PEAK-COMM-05.
Do not rely on this table during peak; rely on the weekly republication.

### Never promise a delivery date

Meridian commits to a **ship date**, which Meridian controls. Delivery is the carrier's
commitment.

This applies in all client communication, at all tiers, at all times, and is not a peak-only
rule — though it matters most during peak, when carrier on-time performance has fallen to
71–84% against published service levels.

Per POL-ESC-001, a resolution timeframe may only be committed when the fix is confirmed and
scheduled. A delivery date is never confirmed and never scheduled by Meridian.

---

## 3. Client-owned carrier accounts

Roughly 30% of clients ship on their own carrier accounts.

**Configuration rules:**

- Credentials are exchanged through the secure channel only, never plain email, consistent
  with SOP-ONB-001 Phase 2.
- Meridian does not hold client carrier billing credentials. Only the shipping API
  credential.
- Client-owned accounts bypass rate shopping entirely. The client's negotiated rates apply
  and Meridian has no visibility into them.
- Meridian bills no markup on client-owned carrier shipments. Pick, pack, and packaging
  charges still apply per the client's schedule.

**What Meridian is not responsible for on client-owned accounts:**

- Rate accuracy. The client owns the negotiation.
- Claims. The client files with their carrier; Meridian supplies documentation within 2
  business days on request.
- Service failures. Meridian's obligation ends at tendering the parcel to the carrier with
  a valid label by the cutoff.

**What Meridian remains responsible for:** correct product, correct quantity, correct
packaging, correct address as supplied, tendered by cutoff. A mis-pick is Meridian's
regardless of whose carrier account carried it.

This boundary is stated in the onboarding SLA review (SOP-ONB-001 Phase 5) and is a
frequent source of confusion when a client-owned shipment is lost in transit.

---

## 4. Pass-through charges

Charges Meridian receives from carriers and passes to clients without markup:

| Charge | Typical amount | Basis |
|---|---|---|
| Address correction | $18.00 | Per carrier tariff, FIN-RATE-2026-01 |
| Residential surcharge | Per tariff | Carrier classification |
| Delivery area surcharge | Per tariff | Carrier zone definition |
| Fuel surcharge | Percentage, varies weekly | Carrier published index |
| Peak/demand surcharge | Per tariff | Carrier announced seasonally |
| Oversize / additional handling | Per tariff | Carrier measurement |
| Return-to-sender | Per tariff | Carrier |

**Pass-through disputes follow POL-FIN-003 and are classified as `Pass-through`.** That
classification carries an extended timeline because Meridian must open a case with the
carrier and carrier response times run 10–20 business days. The client is told this at
acknowledgement, not at day 5 when the standard substantive-response target lapses.

**Dimensional weight is the most disputed pass-through** and is third overall in
POL-FIN-003's dispute frequency list. When a client disputes DIM:

1. Pull the carrier's measured dimensions from the carrier invoice detail.
2. Pull Meridian's cartonization record for the order.
3. Compare. Three outcomes:
   - **Carrier measurement matches our carton:** charge is correct. Show the client the
     carrier's DIM calculation, not merely the result.
   - **Carrier measurement exceeds our carton:** carrier measurement error. Meridian
     disputes with the carrier and credits the client without waiting for carrier
     resolution.
   - **Our carton was larger than necessary:** Meridian's packing error. Credit the
     difference, classified `Meridian error`, and flag the SKU for cartonization review.

The third outcome accounts for roughly 22% of DIM disputes and is the one most often
misclassified as client misunderstanding. **A client who is charged DIM because Meridian
over-boxed is not misunderstanding anything.**

---

## 5. Claims

### Filing window

**48 hours** from discovery for damage or loss identified at receiving, per SOP-REC-004
Step 6. This is the binding constraint and it does not move — the deadline is the
carrier's, not Meridian's, and SOP-PEAK-001 explicitly lists it as never degraded during
peak.

For outbound shipments, filing windows by carrier:

| Carrier | Damage | Loss | Notes |
|---|---|---|---|
| Continental Parcel | 15 days from delivery | 9 months from ship | Photos required for damage |
| Anchor Freight | 10 days from delivery | 6 months from ship | Strictest damage window |
| Redline Express | 21 days from delivery | 9 months from ship | |
| Postal | 60 days | 15 days–6 months by service | Varies by service class |
| Cardinal LTL | 48 hours, noted on BOL | 9 months | **Damage must be noted at delivery** |

**Cardinal LTL is the trap.** Damage not noted on the delivery receipt at the time of
delivery is effectively unrecoverable. Receiving teams must inspect LTL deliveries before
signing, and must note any damage on the BOL even when the extent is unclear. "Subject to
inspection" on the BOL preserves the claim; a clean signature forfeits it.

### Required documentation

Claims are routinely denied for incomplete documentation. Required in all cases:

- Photographs — outer packaging, inner packaging, product, and the shipping label in one
  frame showing tracking
- Bill of lading or tracking number
- Commercial invoice or declared value evidence
- Receiving records where inbound
- Both counts where a quantity discrepancy, per SOP-REC-004 Step 3

**Photographs are mandatory** per SOP-REC-004 Step 2. Claims without them are denied at a
rate above 80%.

### Claim ownership

| Shipment type | Filed by | Credit path |
|---|---|---|
| Inbound to Meridian | Meridian receiving | Client credited on recovery |
| Outbound, Meridian carrier account | Meridian | Client credited on recovery, or per contract |
| Outbound, client carrier account | Client | Meridian supplies documentation only |

### Recovery expectations

Trailing twelve months to 2026-06:

| Carrier | Claims filed | Approved | Recovery rate | Avg days to resolve |
|---|---|---|---|---|
| Continental Parcel | 312 | 241 | 77% | 24 |
| Anchor Freight | 189 | 108 | 57% | 38 |
| Redline Express | 47 | 41 | 87% | 16 |
| Postal | 96 | 44 | 46% | 51 |
| Cardinal LTL | 71 | 39 | 55% | 44 |

Anchor Freight's 57% approval rate against a 10-day damage window is the weakest
performance on the panel and is the primary open item in the 2026-12-31 contract renewal.

**Never tell a client a claim will be approved.** Recovery is not within Meridian's
control, and per POL-ESC-001 no outcome may be committed before it is confirmed. Tell them
the claim is filed, the expected timeline, and that Meridian will credit per contract
regardless of carrier outcome where the contract provides for it.

---

## 6. Performance management

### Metrics tracked monthly

| Metric | Target | Source |
|---|---|---|
| On-time delivery vs published service | ≥ 96% | Carrier scan data |
| Damage rate | ≤ 0.15% of parcels | Claims filed |
| Loss rate | ≤ 0.04% of parcels | Claims filed |
| Billing accuracy | ≥ 98% | Invoice audit |
| Claim approval rate | ≥ 70% | Claims register |
| Average claim resolution | ≤ 30 days | Claims register |

### Current performance, trailing 90 days to 2026-06-30

| Carrier | On-time | Damage | Loss | Billing accuracy |
|---|---|---|---|---|
| Continental Parcel | 96.8% ✅ | 0.11% ✅ | 0.03% ✅ | 98.4% ✅ |
| Anchor Freight | 93.1% ❌ | 0.22% ❌ | 0.06% ❌ | 96.9% ❌ |
| Redline Express | 98.4% ✅ | 0.08% ✅ | 0.02% ✅ | 99.1% ✅ |
| Postal | 94.7% ❌ | 0.19% ❌ | 0.09% ❌ | n/a |
| Cardinal LTL | 91.2% ❌ | 0.31% ❌ | 0.02% ✅ | 97.8% ❌ |

**Anchor Freight is below target on all four measures.** Volume was reduced 40% in
2026-04 pending the renewal decision. The 2026-12-31 expiry will not be renewed on
current terms.

**Cardinal LTL's 91.2%** reflects B2B and retail delivery, which is appointment-based and
where "on-time" depends heavily on the receiving location's dock availability. The figure
is genuinely worse than the others but is not directly comparable.

### Billing audit

Carrier invoices are audited monthly against shipped records. Discrepancies above $50 per
line are disputed with the carrier.

Trailing twelve months: **$84,200** recovered from carriers through billing audit. Anchor
Freight accounts for $41,900 of that, which is consistent with their 96.9% billing
accuracy and is a further argument against renewal.

Recovered amounts are Meridian's, not the client's, **except** where the erroneous charge
was passed through. Passed-through errors are credited to the affected client per
POL-FIN-003 regardless of whether Meridian recovers from the carrier.

---

## 7. Escalation

Carrier issues map to POL-ESC-001 severities:

| Situation | Severity | Rationale |
|---|---|---|
| Carrier refuses pickup at a facility | **S1** | Systemic, affects all clients at that site |
| Carrier system outage blocking label generation | **S1** | Meridian cannot ship |
| Single enterprise client's shipments delayed by carrier | **S2** | One enterprise client materially affected |
| Carrier misses cutoff at one facility, one day | **S2** | Significant, workaround exists (re-tender next day) |
| Individual lost or damaged parcel | **S3** | Contained |
| Client asks about a carrier rate | **S4** | No operational impact |

**A carrier failure is still Meridian's incident.** The client contracted with Meridian.
"The carrier missed pickup" is a root cause, not a defence, and per POL-FIN-003 a
pass-through classification affects who ultimately bears cost, not who owns the client
relationship during the incident.

---

## 8. Known limitations

1. **No carrier holds a service-level guarantee that survives force majeure**, and every
   carrier invokes weather liberally in December. Meridian's peak commitments to clients
   are therefore built on carrier performance Meridian cannot enforce.
2. **Rate shopping's 3.1% cost gap is unrecovered.** It is absorbed into margin. At current
   volume this is roughly $310,000 annually across the network.
3. **Anchor Freight replacement is not scoped** as of this revision, with the contract
   expiring 2026-12-31 — inside peak. Replacing a carrier during weeks 46–52 is not
   feasible, so either the contract extends on poor terms through peak or volume shifts to
   Continental Parcel at higher cost. **This decision is overdue and sits with the VP
   Operations.**
4. **Postal claim recovery at 46%** is poor and the process is manual. The volume is low
   enough that automation has not been justified, which is a self-reinforcing argument.
5. **Cardinal LTL's damage-notation requirement depends entirely on receiving-team
   discipline** at the moment of delivery, under time pressure, with no system enforcement.
   This is the same class of control weakness identified in INC-2026-0104 Finding 2.

---

## Related documents

SOP-REC-004 (Receiving Discrepancies) · FIN-RATE-2026-01 (Billing Rate Card) ·
POL-FIN-003 (Billing Disputes and Adjustments) · POL-ESC-001 (Escalation Matrix) ·
SOP-PEAK-001 (Peak Season Operating Procedures) · VEN-POL-002 (Vendor and Temporary
Labour) · CAR-POL-001 Appendix A (Cutoff Calendar, republished weekly during peak)
