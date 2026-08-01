# Policy: Vendor Management and Temporary Labour

> Fictional reference document — Meridian Fulfillment Co.

**Document ID:** VEN-POL-002
**Owner:** VP Operations (M. Reyes)
**Last reviewed:** 2026-05-22
**Applies to:** All facilities

---

## Scope

Governs selection, onboarding, performance management, and termination of third-party
vendors supplying goods or services to Meridian operations, including temporary labour,
packaging supply, equipment maintenance, and waste handling.

Does not govern: carriers (see CAR-POL-001), software vendors, or professional services.

---

## 1. Vendor categories and current panel

### Temporary labour

| Vendor | Facilities | Contract | Rate structure |
|---|---|---|---|
| Cascade Staffing | Richmond, Columbus | 2026-12-31 | Hourly + 22% markup |
| High Desert Labor Partners | Reno | 2027-04-30 | Hourly + 26% markup |

High Desert's higher markup reflects the Reno labour market, which is materially tighter
than Richmond or Columbus. Attempts to bring Cascade into Reno in 2024 failed — they could
not fill the requirement.

### Packaging supply

| Vendor | Scope | Contract | Notes |
|---|---|---|---|
| Kestrel Packaging | Corrugated, all facilities | 2027-01-31 | Primary |
| Bluewater Supply | Poly mailers, dunnage | 2026-09-30 | Secondary, price-competitive |
| Client-direct | Client-supplied packaging | n/a | No charge per FIN-RATE-2026-01 |

### Equipment and facilities

| Vendor | Scope | Contract |
|---|---|---|
| Ridgeline Material Handling | Forklift lease and maintenance, all sites | 2028-02-28 |
| Talon Systems | Racking inspection and repair | 2026-11-30 |
| Sierra Facilities Group | Janitorial, Reno only | 2026-12-31 |

---

## 2. Temporary labour — the core of this policy

Temporary labour is the highest-risk vendor category because temporary workers handle
client-owned inventory. Everything in this section derives from that.

### Volume

| Period | Temporary headcount | % of warehouse labour |
|---|---|---|
| Normal operations | 18–24 | 12–14% |
| Weeks 46–52 (peak) | +70 approved | ~38% |
| Week 48 (2025 actual) | 94 | 41% |

Per SOP-PEAK-001, peak approval is +62 pick/pack and +8 receiving.

### Induction requirements

**Every temporary worker completes a 6-hour induction before floor access.** No exceptions,
no abbreviated version, no "shadow today and induct tomorrow."

Induction covers:

| Module | Duration | Content |
|---|---|---|
| Safety | 120 min | PPE, powered equipment awareness, aisle discipline, emergency procedures, incident reporting |
| Client inventory custody | 45 min | Whose goods these are, why segregation matters, what to do when unsure |
| WMS handheld basics | 90 min | Login, task acceptance, scanning, task completion, error states |
| Task-specific | 90 min | Pick, pack, or receiving depending on assignment |
| Facility orientation | 15 min | Layout, breaks, escalation, who to ask |

**The custody module is not optional and is not abbreviated.** It was added in 2026-04
following INC-2026-0104, in which one client's goods shipped to another client's customers.
No temporary worker was involved in that incident — the putaway error was made by a
permanent operator — but the review found that no training material anywhere in the
business explained *why* client segregation matters, only that it is required.

### The week 44 rule

**A temporary worker who has not completed induction by week 45 Friday does not work peak.**

Introduced after the 2024 peak, when eleven workers were placed on the floor in week 47
with a 90-minute abbreviated induction. Those eleven accounted for 31% of that year's pick
errors in weeks 47–52 while representing 12% of temporary hours.

This rule is expensive. It means peak temporary hiring closes roughly three weeks before
peak volume arrives, and it has twice resulted in running short rather than inducting late.
It is retained because the 2024 data is unambiguous.

### Task restrictions

Temporary workers are **not permitted** to perform:

- **Cycle counts** — SOP-INV-002 depends on blind counting by trained staff, and the
  variance-resolution path assumes the counter can be re-interviewed weeks later.
- **Mezzanine putaway at Reno** — per SOP-PUT-007, the mezzanine is the highest-error zone
  in the network pending relabeling and lighting remediation.
- **Returns disposition** — requires judgement on sellable/refurbish/discard with direct
  client cost impact.
- **Any task on serialized or lot-tracked SKUs** — traceability obligations, and in
  Northwind's case (ONB-CASE-2025-114) regulatory exposure.
- **Any task on hazmat SKUs** — certification required.
- **Adjustments of any kind in the WMS**, at any value.

**Ratio limit: no more than 2 temporary workers per 1 permanent worker** on any shift in
any zone. Where the ratio cannot be met, the zone runs short. This is stated as an absolute
in SOP-PEAK-001 and is the rule most often challenged during peak.

### Conversion

Temporary workers who complete 480 hours with satisfactory performance are eligible for
permanent conversion. Cascade and High Desert both permit conversion with no fee after 480
hours; conversion before that carries a fee of 18% of first-year salary.

2025 conversions: 14 (9 Richmond, 3 Columbus, 2 Reno). 2026 to date: 11.

Reno's low conversion rate is a persistent issue. The Reno labour market is tight, High
Desert's candidates are more likely to be working multiple assignments, and Reno's
permanent turnover runs at 31% annually against 19% at Richmond. **Reno's staffing
instability is a plausible contributing factor to its inventory accuracy problem** and is
noted as such in SOP-PUT-007's finding that operators with under 90 days tenure accounted
for 29% of PUT-01 events — a disproportionate share, though not the dominant one.

---

## 3. Vendor onboarding

All new vendors complete the following before first engagement:

- [ ] Signed master services agreement
- [ ] Certificate of insurance — general liability minimum $2M, naming Meridian as
      additional insured
- [ ] Workers' compensation certificate where the vendor supplies labour
- [ ] W-9 on file
- [ ] Vendor record created in NetSuite
- [ ] Named account contact and escalation contact — **both required**
- [ ] Payment terms agreed, net 30 default
- [ ] Site-specific safety briefing completed where the vendor works on site
- [ ] Background check attestation where the vendor's staff access client inventory
- [ ] Data handling addendum where the vendor accesses any Meridian system

The escalation-contact requirement mirrors SOP-ONB-001's client onboarding requirement and
is missed at a similar rate. It has been the cause of two service failures where a vendor's
account manager was unreachable and no secondary existed.

---

## 4. Performance management

### Temporary labour metrics

Reviewed monthly per vendor:

| Metric | Target | Cascade (2026 YTD) | High Desert (2026 YTD) |
|---|---|---|---|
| Fill rate against requisition | ≥ 95% | 97.2% ✅ | 88.4% ❌ |
| No-show rate | ≤ 4% | 3.1% ✅ | 7.8% ❌ |
| Induction completion before floor access | 100% | 100% ✅ | 100% ✅ |
| 30-day retention | ≥ 80% | 84% ✅ | 66% ❌ |
| Pick accuracy, temporary workers | ≥ 99.4% | 99.5% ✅ | 99.1% ❌ |
| Safety incidents per 1,000 hours | ≤ 0.8 | 0.6 ✅ | 1.1 ❌ |

High Desert misses five of six targets. This has been raised at three consecutive quarterly
reviews.

**The honest position:** High Desert is underperforming and Meridian has limited leverage.
They are the only viable supplier in the Reno market at the volume required, Cascade
declined to enter in 2024, and terminating without a replacement would close Reno's peak
staffing entirely. The contract runs to 2027-04-30.

Mitigations in place rather than termination:

- Requisitions submitted 3 weeks earlier than at other sites to absorb the fill-rate gap.
- Over-requisition by 12% to absorb no-shows.
- Reno temporary workers excluded from mezzanine putaway (also required by SOP-PUT-007).
- Additional supervisor coverage on second shift, funded by Meridian.

The additional supervisor coverage costs approximately $71,000 annually and is, in effect,
paying twice for the same labour quality other sites get from the base contract.

### Packaging supply metrics

| Metric | Target | Kestrel | Bluewater |
|---|---|---|---|
| On-time delivery | ≥ 97% | 98.1% ✅ | 94.2% ❌ |
| Order accuracy | ≥ 99% | 99.4% ✅ | 98.8% ❌ |
| Price variance vs contract | ≤ 2% | 0.9% ✅ | 3.4% ❌ |
| Quality rejection rate | ≤ 0.5% | 0.3% ✅ | 1.2% ❌ |

Bluewater's 1.2% quality rejection is driven almost entirely by poly mailer seam failures
in a single lot received 2026-03. Excluding that lot, rejection is 0.4%. The lot was
credited in full.

**Packaging quality failures reach the client as damage.** A seam failure in transit
produces a damaged-goods claim, a customer-service contact for the client, and a possible
credit — costs that dwarf the packaging price difference. Bluewater's price advantage over
Kestrel is roughly 6% on poly mailers; a single bad lot erased approximately four months
of that saving.

---

## 5. Vendor-caused incidents

Vendor failures map to POL-ESC-001 severities on the same basis as any other cause — **by
client impact, not by fault.**

| Situation | Severity |
|---|---|
| Temporary labour shortfall closing a shift | **S1** if orders cannot ship; **S2** if degraded |
| Packaging stockout preventing shipping | **S1** |
| Forklift fleet failure limiting throughput | **S2** |
| Racking damage requiring aisle closure | **S2**, or **S1** if a client's entire inventory is inaccessible |
| Single packaging lot quality failure | **S3** |
| Vendor invoice dispute | **S4** |

**"The vendor failed" is never a client-facing explanation.** Per POL-ESC-001, root cause
is not communicated before investigation concludes, and per POL-FIN-003's guidance never to
blame the client, the same principle extends to blaming suppliers: the client contracted
with Meridian.

Internally, vendor fault determines cost recovery. Externally, it changes nothing about
Meridian's obligation.

---

## 6. Termination and transition

Grounds for termination without notice:

- Any safety incident caused by wilful vendor negligence
- Theft or suspected theft — also triggers immediate escalation to the Client Operations
  Manager per POL-ESC-001
- Insurance lapse
- Failure to complete required induction
- Falsified records of any kind

Grounds for termination with notice, per contract:

- Sustained performance failure across two consecutive quarterly reviews
- Material price variance from contract
- Repeated escalation-contact unavailability

**Transition planning is required before termination notice is served.** This was not done
in 2024 when a Columbus janitorial vendor was terminated for performance and no replacement
was in place for eleven days.

The current live example is Anchor Freight (CAR-POL-001), whose contract expires
2026-12-31 with no replacement scoped — the same failure pattern, currently unaddressed and
now inside peak.

---

## 7. Known limitations

1. **High Desert underperforms and cannot practically be replaced.** The mitigations cost
   roughly $71,000 annually and paper over rather than fix the problem. This is the single
   largest unresolved vendor issue.
2. **No vendor scorecard is shared with the vendors themselves.** Performance is tracked
   internally and discussed at quarterly reviews, but vendors do not see the numbers
   between reviews. Cascade has asked for this twice.
3. **Background check attestation is an attestation**, not a verification. Meridian accepts
   the vendor's confirmation that checks were performed and does not audit it. This has
   never been tested by an incident.
4. **Temporary worker training completion is tracked in a spreadsheet**, not in a system.
   During peak, with 90+ temporary workers across three sites, this is fragile. A worker
   whose induction record is missing cannot be distinguished from one who never inducted.
5. **The 2:1 ratio limit has no system enforcement.** It depends on shift supervisors
   scheduling correctly and is checked by audit after the fact. Audits in week 48 of 2025
   found the ratio exceeded on 4 of 21 shift-zones sampled.

Points 4 and 5 are the same class of weakness identified repeatedly elsewhere in this
document set: a documented control with no system enforcement, depending on human
discipline in exactly the conditions where discipline is hardest.

---

## Related documents

SOP-PEAK-001 (Peak Season Operating Procedures) · SOP-PUT-007 (Putaway — Reno) ·
SOP-INV-002 (Inventory Cycle Counts) · POL-ESC-001 (Escalation Matrix) ·
CAR-POL-001 (Carrier Management) · TRN-NEW-001 (New Hire Training and Certification) ·
INC-2026-0104
