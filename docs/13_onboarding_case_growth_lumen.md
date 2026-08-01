# Onboarding Case Note — Lumen Bath Co. (Growth)

> Fictional reference document — Meridian Fulfillment Co.

**Document ID:** ONB-CASE-2026-031
**Client:** Lumen Bath Co.
**Tier:** Growth
**Onboarding Specialist:** T. Nakamura
**Account Manager:** P. Oyelaran
**Signature date:** 2026-01-13
**Target first live order:** 2026-02-11 (21 business days per SOP-ONB-001)
**Actual first live order:** 2026-03-04 — **15 business days late**
**Facility:** Richmond
**Status:** Closed, active client

---

## Summary

Lumen Bath Co. is a bath and body brand, approximately 11,000 orders/month, Growth tier.

Onboarding ran 36 business days against a 21-day standard. The delay has a single
dominant cause and it is **the exact cause SOP-ONB-001 already names as "by far the
largest": incomplete SKU dimension data.**

That is what makes this case worth writing up. The checklist warns about this in bold. It
instructs specialists to *"request it in week 1 and validate immediately rather than
accepting the file at face value."* The specialist did request it in week 1. The file
arrived on day 3. It was validated on day 4.

**And the validation passed.** Every SKU had dimensions. Every field was populated. The
data was complete, well-formatted, and wrong.

This case documents a failure mode the checklist does not anticipate: dimension data that
is present and plausible but does not describe the product that arrives.

---

## Client profile at signature

| | |
|---|---|
| Category | Bath, body, home fragrance |
| Orders/month at signature | ~11,000 |
| SKU count | 386 |
| Lot-tracked SKUs | 0 |
| Fragile SKUs | 214 (glass vessels) |
| Integration | Shopify |
| Storage profile | Shelf and bin |
| Contracted tier | Growth |
| Rate schedule | Negotiated — see FIN-RATE-GRW-LBC-2026 |

---

## Timeline against SOP-ONB-001 phases

### Phase 1 — Account setup (standard Days 1–3; actual Days 1–4) ⚠️ +1 day

One-day slip: the escalation contact was not provided until day 4 despite two requests.
The client's founder initially listed herself for all three contact roles — billing,
operations, and escalation. The specialist correctly pushed back, since a single point of
contact defeats the purpose of an escalation path, and a second name was provided on day 4.

Minor, but it is the "frequently missed" item from SOP-ONB-001 surfacing again, in a
different shape: not missing, but not meaningfully distinct.

### Phase 2 — Systems (standard Days 3–8; actual Days 4–9) ✅

Shopify integration, standard connector, no customization. Credentials exchanged day 5
through the secure channel. Test connection day 6. Three test orders flowed end to end
day 7. Inventory sync verified both directions day 8.

Clean. This is what Phase 2 looks like when the integration is a supported one and the
client responds promptly.

*Note: this onboarding completed before the Shopify API deprecation incident
(INC-2026-0038). Lumen does not populate `note_attributes` and was unaffected.*

### Phase 3 — Product setup (standard Days 5–12; actual Days 5–13) ⚠️ +1 day

**Day 3:** SKU master requested.
**Day 3:** SKU master received. Same day. Complete file, correct template, all 386 SKUs.
**Day 4:** Validation run. All 386 SKUs carry dimensions, weight, unit cost, and barcode.
**Zero SKUs flagged.**

The specialist noted in the file: *"Cleanest SKU master I've had. Client clearly has good
data hygiene."*

The one-day slip was unrelated — packaging photographs for three kitted gift sets arrived
late.

**Days 5–13:** storage types assigned per SKU based on the supplied dimensions. 214 SKUs
assigned to shelf, 172 to bin. Slotting plan built. Pick faces allocated in Richmond
zone 6.

### Phase 4 — Inbound (standard Days 10–18; actual Days 14–31) 🔴 **+13 days**

**Day 14 (2026-02-03):** first inbound arrives at Richmond. 14 pallets. ASN quantity
matches. No receiving discrepancy under SOP-REC-004 — the counts were right.

**Day 14, 11:20:** putaway begins. Operator raises a `NO-FIT` on the third pallet. Then a
fourth. Then eleven more.

**Day 14, 14:00:** putaway halted. 61 of 386 SKUs do not fit their assigned locations.

**Day 15:** Richmond inventory clerk physically measures a sample of 40 SKUs. Findings:

| Measurement source | Result |
|---|---|
| Client SKU master | Dimensions of the **product**, unboxed |
| Physical reality | Product ships in a retail carton, then an outer case of 6 or 12 |
| Discrepancy | Cube understated by 40–310% depending on SKU |

The client had supplied **product dimensions**, not **shipping-unit dimensions.** A 250ml
glass diffuser measured 6cm × 6cm × 18cm as a bare bottle. Its retail box is 8 × 8 × 21.
It arrives in a case of 6: 26 × 18 × 23.

Every dimension in the file was accurate. None of them described the thing Meridian would
store or handle.

**Day 15–16:** scope assessed. All 386 SKUs suspect, not just the 61 that failed. The
61 were simply the ones whose error was large enough to break the assigned location.

**Day 16:** decision to remeasure all 386 SKUs on site rather than ask the client to
resupply. Rationale: the client had already supplied what they believed was correct, a
second request would likely produce the same error, and Richmond had physical stock in
hand.

**Days 17–28:** remeasurement. 386 SKUs, two staff, 68 labour hours. Slotting plan
rebuilt. 214 SKUs moved from shelf to a mix of shelf and pallet; 47 moved from bin to shelf.

**Days 28–31:** putaway completed against the corrected plan.

Inbound stock sat in receiving staging for 17 days. Richmond's staging area ran at
capacity for eleven of those days, which constrained two other clients' inbound scheduling
— a knock-on cost not charged to Lumen and not tracked anywhere.

### Phase 5 — Go live (standard Days 18–21; actual Days 32–36) ✅

Test orders day 32. Packaging verification surfaced one further issue: the fragile-handling
requirement had been documented as "fragile — use dunnage," which was accurate but
insufficient. Glass vessels require corner protection, not fill dunnage. Corrected day 34
after a broken-item test ship.

**First live order: 2026-03-04, day 36.**

### Phase 6 — Handoff (Day 36+) ✅

30-day review held 2026-04-07. Client rated onboarding 4/5 — higher than Meridian's own
internal assessment, because from Lumen's side the delay was explained clearly and the
remeasure was absorbed at no charge.

---

## Cost of the delay

| Item | Cost | Borne by |
|---|---|---|
| Remeasurement labour (68 hrs @ $34 loaded) | $2,312 | Meridian |
| Slotting plan rebuild | $890 | Meridian |
| Staging congestion, knock-on to 2 clients | Not quantified | Meridian |
| Client revenue delayed 15 business days | ~$140,000 GMV | Lumen |
| Storage billed during staging | $0 — waived | Meridian |

Meridian absorbed roughly $3,200 in direct cost plus unquantified congestion. No charge
was passed to Lumen, on the reasonable grounds that the SKU master template does not
specify which dimensions are wanted.

**That is the crux: the template says "Length / Width / Height." It does not say of what.**

---

## Root cause

**The SKU master template is ambiguous and the validation only checks completeness.**

The validation step in SOP-ONB-001 Phase 3 checks that dimension fields are populated and
numerically plausible. A 6 × 6 × 18 diffuser is entirely plausible. Nothing in the
validation compares supplied dimensions against anything real.

**Why this client in particular:** Lumen was moving from self-fulfilment out of a
founder's garage. Their product data came from their manufacturer's spec sheets, which
naturally describe the product. A client transitioning from another 3PL would likely have
supplied case dimensions, because their previous provider would have made the same
correction years earlier.

**First-time-outsourcing clients are systematically more likely to make this error**, and
Meridian's Growth tier is where those clients cluster.

---

## Comparison to the checklist's stated expectation

SOP-ONB-001 lists "incomplete SKU dimension data" as the largest delay cause and advises
requesting it in week 1 and validating immediately.

Both were done. The delay happened anyway, and was slightly longer than the average
delay caused by *missing* dimension data (Meridian's trailing average for
missing-dimension delays is 9 business days; this was 15).

**Wrong data is worse than absent data**, because absent data announces itself and wrong
data does not. The checklist optimizes for the wrong failure.

---

## Recommendations

Submitted to the Client Operations Manager 2026-04-10.

1. **Rename the template columns** to `CASE_LENGTH_IN`, `CASE_WIDTH_IN`, `CASE_HEIGHT_IN`,
   `CASE_WEIGHT_LB`, `UNITS_PER_CASE`, with a mandatory `EACH_*` set alongside.
   **Status: accepted, template v4 released 2026-01** — *note: v4 was already in flight
   from ONB-CASE-2025-114 and shipped between this onboarding's start and its close. Lumen
   was onboarded on v3.*
2. **Add a physical spot-check gate:** measure 10 randomly selected SKUs on first inbound
   before releasing putaway. Ten measurements would have caught this on day 14 with 30
   minutes of work instead of 17 days of staging. **Status: accepted, added to
   SOP-ONB-001 Phase 4 in the 2026-05 revision.**
3. **Flag first-time-outsourcing clients** at signature and apply enhanced dimension
   verification. **Status: accepted.**
4. **Do not assign storage types from client-supplied dimensions alone** for any client
   without a prior 3PL history. **Status: under review.**
5. **Track staging congestion as a cost.** The knock-on to two other clients was real,
   invisible, and unbilled. **Status: declined — no mechanism.**

---

## Honest assessment

The specialist did everything the checklist asked, in the right order, ahead of schedule.
The file note on day 4 — *"cleanest SKU master I've had"* — is the detail that stings,
because the data quality was genuinely excellent by every measure available at the time.

The failure was in the instrument, not the operator. A validation that checks for presence
and plausibility cannot detect a systematic definitional error, and the template invited
the error by not defining its terms.

The 10-SKU spot check (Recommendation 2) would have caught this for 30 minutes of work. It
is now in the SOP. It was not proposed before this case because nobody had encountered
this failure mode in a form severe enough to notice — the checklist's own framing had
everyone watching for *missing* data.

---

## Related documents

SOP-ONB-001 (Client Onboarding Checklist) · SOP-REC-004 (Receiving Discrepancies) ·
SOP-PUT-002 (Putaway — Richmond and Columbus) · FIN-RATE-GRW-LBC-2026 ·
ONB-CASE-2025-114 · ONB-CASE-2026-058
