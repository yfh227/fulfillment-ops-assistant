# SOP: Putaway — Richmond and Columbus

> Fictional reference document — Meridian Fulfillment Co.

**Document ID:** SOP-PUT-002
**Owner:** Facility Managers, Richmond (S. Vantieghem) and Columbus (A. Ferreira)
**Last reviewed:** 2026-08-21
**Applies to:** Richmond VA and Columbus OH facilities
**Does not apply to:** Reno NV, which operates under SOP-PUT-007

---

## Scope and relationship to SOP-PUT-007

This is the general putaway procedure. Reno operates under a separate document
(SOP-PUT-007) because of site-specific conditions — a mezzanine labeling scheme, lighting
below standard, and a period during which directed putaway enforcement was disabled — that
produced an elevated PUT-01 rate requiring its own treatment.

**Richmond and Columbus have never had enforcement disabled.** Directed putaway has been a
hard block at both sites since the WMS control was introduced in 2021. This is the single
largest procedural difference between this document and SOP-PUT-007, and it is why this
SOP is shorter: most of SOP-PUT-007 is remediation for a condition that does not exist here.

**This revision (2026-08-21) is the first substantive update since 2024.** It was prompted
by INV-RPT-2026-Q2 Action 7, which required Columbus's mezzanine to be audited for the same
labeling weakness found at Reno. That audit is covered in Section 8 and its findings are the
reason several rules below are new.

---

## 1. Facility context

| | Richmond | Columbus |
|---|---|---|
| Opened | 2016 (HQ site) | 2018 |
| Pallet positions | 14,200 | 12,800 |
| Mezzanine | No | Yes — added 2021 |
| Peak pallet occupancy | 91% | 88% |
| Putaway operators | 24 | 21 |
| Permanent turnover, annual | 19% | 23% |
| Temporary labour vendor | Cascade Staffing | Cascade Staffing |
| Q2 2026 location accuracy | 99.62% | 99.58% |
| Q2 2026 PUT-01 adjustments | 218 | 241 |

Both sites met the 99.5% accuracy target in Q2 2026 and have met it in every quarter on
record.

**Columbus's PUT-01 count of 241 is the highest of any non-Reno cause code** in Q2. It is
proportional to volume and does not indicate a problem — but it is the number that made the
Columbus mezzanine audit a priority rather than a formality.

---

## 2. Location naming

### Richmond

Single-level rack throughout. Locations read `AA-B-CC-D`:

```
07-C-12-3
│  │  │  └── Level (1 = floor, ascending)
│  │  └───── Bay
│  └──────── Rack side (A–D)
└─────────── Aisle
```

No ambiguity is possible. Richmond has never recorded a labeling-related misput.

### Columbus

Ground level uses the same scheme as Richmond. **The mezzanine, added in 2021, uses a
trailing `M` suffix** — the same scheme that caused Reno's problem:

| Zone | Format | Example |
|---|---|---|
| Ground | `AA-B-CC-D` | `11-B-08-2` |
| Mezzanine | `AA-B-CC-DM` | `11-B-08-2M` |

**This is a known latent weakness.** It is the identical construction that SOP-PUT-007
identifies as Cause 1 of Reno's elevated PUT-01 rate, where the trailing character is the
only difference between a ground location and the mezzanine location directly above it.

It has not produced errors at Columbus at anything like Reno's rate. Section 8 explains
why, and why "has not" is not the same as "will not."

---

## 3. Procedure

### Step 1 — Receive the task

Accept on the handheld. The screen shows LPN, SKU and description, quantity, directed
location, client, and any special-handling flag.

**Read the directed location aloud or subvocalize it before travelling.** Adopted network-wide
from the SOP-PUT-007 observation study, which found operators who verbalized the location
misread it at roughly a third the rate of those who did not. The finding came from Reno but
the mechanism is not site-specific.

### Step 2 — Confirm the zone (Columbus only)

At Columbus, check whether the directed location is ground or mezzanine before travelling.
The trailing `M` is the only difference.

The handheld's location detail screen — press and hold the location field — states `GROUND`
or `MEZZ` explicitly. Use it whenever the aisle has a mezzanine above it (aisles 8–15).

Richmond operators skip this step; there is no mezzanine.

### Step 3 — Travel and scan the location barcode

**Scan the location before scanning the LPN.** The system should know where you are standing
before it knows what you are holding, so it can reject a wrong location before the product
is committed.

### Step 4 — Handle a mismatch

Scanning a location other than the directed one raises a **hard block**. It has always been
a hard block at these sites. Three options:

**Option A — Go to the correct location.** Default, and correct in the large majority of cases.

**Option B — Request a re-direct.** Use when the directed location is genuinely unusable.
Press `RE-DIRECT` and select a reason:

| Reason code | Use when |
|---|---|
| `OCCUPIED` | Another LPN already in the location |
| `NO-FIT` | Product physically does not fit |
| `BLOCKED` | Inaccessible — equipment, spill, damage |
| `DAMAGED` | Location itself damaged — rack or beam |

**Re-direct is the normal path when the direction is wrong, not an exception path.**
Re-directs are expected and are not counted against the operator.

Target re-direct rate is **2–6%**. Richmond runs 3.4%, Columbus 3.9% — both healthy. A rate
near zero would indicate operators working around the system rather than using the sanctioned
path, which is precisely the pattern that developed at Reno while enforcement was disabled.

`NO-FIT` re-directs are reviewed weekly. A `NO-FIT` almost always means the SKU dimension
record is wrong — see Step 7.

**Option C — Supervisor override.** Requires a supervisor badge scan. Reserved for cases
where the system state is wrong in a way `RE-DIRECT` cannot resolve.

**Override discipline is the control most worth protecting.** INV-RPT-2026-Q2 found that at
Reno, 14 of 43 post-enforcement PUT-01 events involved an override that should not have been
granted — a control being used as a pressure valve. Richmond and Columbus average 0.4 and
0.6 overrides per shift respectively, against a threshold of 1.0.

Every override generates a line in the daily exception report reviewed by the Facility
Manager. **From 2026-09-01, overrides at both sites require written justification**, matching
the control applied at Reno under INV-RPT-2026-Q2 Action 4.

### Step 5 — Scan the LPN and confirm quantity

Confirm the on-screen quantity matches what you physically have.

If quantity differs, **do not adjust it here.** Set the LPN down in the location, mark it
`COUNT-PENDING`, and notify your supervisor. Quantity corrections at putaway bypass the
blind-count protection in SOP-INV-002 and are a known source of masked variance.

### Step 6 — Place the product

In priority order:

1. **Label facing the aisle.** Non-negotiable. Cycle counters cannot count what they cannot
   read, and an unreadable label produces a variance costing far more time than turning the
   pallet.
2. **Heaviest at the bottom** for multi-tier locations.
3. **No overhang** beyond the location footprint. On the Columbus mezzanine this is a safety
   issue, not a tidiness one.
4. **Lot-tracked product:** verify the lot on the LPN matches the physical cartons before
   placing. Mixed lots in one location defeat FEFO picking.
5. **Serialized product:** never mix serial ranges in a location.
6. **Single-client locations.** Pallet and shelf locations hold one client's goods only.

**Rule 6 is enforced by the WMS** as of 2026-05-15, following INC-2026-0104 in which one
client's goods were placed in a location holding another client's stock and subsequently
shipped to 43 of that client's end customers.

The audit accompanying that remediation found **538 non-bin locations network-wide holding
more than one client's goods** — 402 at Reno, and **136 across Richmond and Columbus.** All
were remediated by 2026-05-29.

The 136 at these two sites is the detail worth noticing. Enforcement was never disabled here,
and the sites were at accuracy target throughout, and mixed-client locations still
accumulated. Being at target is not evidence that a specific control exists.

### Step 7 — Close the task

Confirm on the handheld. Inventory moves from receiving-staging to the location in real time.

If you used `NO-FIT`, the SKU is flagged for dimension review. The facility inventory clerk
measures it during the next business day and submits a correction to the client's Account
Manager.

**Do not skip this.** A wrong dimension record generates the same `NO-FIT` for every
subsequent receipt of that SKU indefinitely. This is the mechanism behind the Lumen Bath Co.
onboarding delay (ONB-CASE-2026-031), where 386 SKUs carried product dimensions rather than
case dimensions and 61 failed at putaway on first inbound.

---

## 4. Columbus mezzanine rules

Aisles 8–15. Introduced in this revision following the Section 8 audit.

- **Verify the zone indicator before travelling**, not on arrival.
- **Report any mezzanine `NO-FIT` verbally to the supervisor same shift**, in addition to the
  system flag. The mezzanine has the least slack in the building.
- **Do not stage product in mezzanine aisles.** Columbus mezzanine aisles are 48 inches —
  wider than Reno's 42 — but staged product still forces operators to approach a bay from the
  wrong end, which is where several of the misputs sampled at Reno originated.
- **Lighting is at standard.** Columbus mezzanine measures 310–340 lux against the Meridian
  standard of 300. Reno's 180–220 lux is the condition that makes its suffix scheme
  genuinely hazardous; Columbus does not share it.

**There is no pairing restriction at Columbus.** SOP-PUT-007 restricts solo mezzanine putaway
at Reno after 19:00 on second shift because of lighting. That restriction is lighting-driven
and does not transfer.

---

## 5. Temporary labour

Per VEN-POL-002, temporary workers may perform putaway at Richmond and Columbus after
completing the 6-hour induction, including the client inventory custody module.

Temporary workers **may not**:

- Perform putaway on serialized or lot-tracked SKUs
- Perform putaway on hazmat SKUs
- Make any WMS adjustment at any value
- Exercise a supervisor override (they cannot — badge level does not permit it)

**Temporary workers may perform Columbus mezzanine putaway.** This differs from Reno, where
VEN-POL-002 prohibits it. The prohibition at Reno is driven by the lighting and dual-scheme
conditions documented in SOP-PUT-007, neither of which applies at Columbus.

**Ratio limit: no more than 2 temporary workers per 1 permanent worker** on any shift in any
zone, per VEN-POL-002 and SOP-PEAK-001. Where the ratio cannot be met, the zone runs short.

Audits in week 48 of 2025 found the ratio exceeded on 4 of 21 shift-zones sampled. There is
no system enforcement; it depends on shift supervisors scheduling correctly.

---

## 6. Peak season variations

Weeks 46–52, per SOP-PEAK-001:

- Putaway volume rises with the receiving curve, peaking in week 47 as clients complete
  their builds.
- **Richmond runs 91% pallet occupancy at peak, Columbus 88%.** Above roughly 92%, directed
  putaway begins failing more often because the WMS cannot find a suitable open location, and
  `OCCUPIED` re-directs rise sharply.
- **Expect re-direct rates of 8–14% during weeks 47–50.** This is above the normal 2–6% band
  and is not a discipline problem. Do not treat elevated peak re-directs as an exception to
  investigate.
- **Override discipline does not relax.** The written-justification requirement applies
  through peak.
- Class B and C cycle counts are suspended weeks 46–52, which means a putaway error made
  during peak is materially less likely to be caught before January.

That last point is the reason override discipline matters more during peak, not less.

---

## 7. Metrics

Reported monthly by each Facility Manager to the Client Operations Manager.

| Metric | Target | Richmond Q2 2026 | Columbus Q2 2026 |
|---|---|---|---|
| PUT-01 per 1,000 putaways | < 1.5 | 0.9 | 1.1 |
| Location-level accuracy | 99.5% | 99.62% | 99.58% |
| Re-direct rate | 2–6% | 3.4% | 3.9% |
| `NO-FIT` unresolved after 5 business days | 0 | 2 | 4 |
| Supervisor overrides per shift | < 1.0 | 0.4 | 0.6 |

Both sites meet every target except unresolved `NO-FIT` counts, where Columbus's 4 is a
minor but persistent miss. Cause: the Columbus inventory clerk role has been vacant since
2026-04 and measurement duties are being absorbed by the shift supervisors.

---

## 8. Columbus mezzanine audit — 2026-08-14

Conducted under INV-RPT-2026-Q2 Action 7, which required Columbus's mezzanine to be examined
for the labeling weakness identified at Reno. That action originated in SOP-PUT-007's own
statement that its Reno-only scope was *"the one most likely to age badly."*

### Method

Mirrored the Reno investigation at reduced scale: 18 months of Columbus PUT-01 adjustments
(N = 1,412) mapped to originating and intended locations, plus 22 physically re-walked
misputs and 6 observed putaway cycles.

### Findings

**The latent condition is present. The failure is not.**

| Condition | Reno | Columbus |
|---|---|---|
| Suffix labeling scheme (`M`) | Yes | **Yes** |
| Ground/mezzanine pairs differing by one character | Yes | **Yes** |
| Mezzanine lighting below 300 lux standard | Yes (180–220) | No (310–340) |
| Directed putaway enforcement | Disabled 2024-03 to 2026-06 | **Never disabled** |
| Mezzanine aisle width | 42 in | 48 in |
| PUT-01 concentrated in mezzanine aisles | 61% | **17%** |
| Ground/mezzanine pairs among sampled misputs | 41 of 60 (68%) | **3 of 22 (14%)** |

Columbus's mezzanine accounts for 14% of pick faces and 17% of PUT-01 events — very close to
proportional, against Reno's 18% / 61%.

**Conclusion:** the labeling scheme is a genuine weakness at Columbus, and enforcement is
what prevents it from producing errors. An operator who misreads `11-B-08-2M` as `11-B-08-2`
travels to the wrong level, scans, and is blocked. The misread still happens; it costs a
walk rather than an inventory error.

This is the clearest available evidence for the SOP-PUT-007 conclusion that Reno's problem
was **enforcement, not labeling** — the labeling created the misread, but enforcement is what
determines whether a misread becomes a misput. Columbus is the control group.

### Recommendations

| # | Recommendation | Status |
|---|---|---|
| 1 | Do not relabel the Columbus mezzanine at this time | **Accepted** |
| 2 | Add zone-verification step to this SOP (Section 2, Step 2) | Complete — this revision |
| 3 | Add mezzanine-specific rules (Section 4) | Complete — this revision |
| 4 | Extend written-justification requirement for overrides to both sites | Complete — effective 2026-09-01 |
| 5 | If enforcement is ever disabled at Columbus for any reason, relabeling becomes mandatory before it is disabled | **Accepted — recorded as a standing condition** |
| 6 | Fill the Columbus inventory clerk vacancy | Open — with HR since 2026-05 |

**Recommendation 1 will look wrong if Columbus ever loses enforcement.** It is accepted
because relabeling 1,340 Columbus locations costs an estimated 210 labour hours and would
create the same dual-scheme transition hazard currently live at Reno, in a facility that is
at target with a proportional error distribution.

Recommendation 5 exists precisely because Recommendation 1 depends on a control that was
disabled at Reno in 2024 for a legitimate operational reason and then left off for
twenty-six months because nobody owned turning it back on.

**Recommendation 5 is the substantive output of this audit.** The rest is documentation.

---

## 9. Known limitations

1. **The Columbus suffix scheme remains** and this SOP mitigates it with a verification step
   rather than eliminating it, on the explicit judgement that enforcement is a sufficient
   control. That judgement is correct today and is contingent on a configuration setting.
2. **Recommendation 5 is a standing condition with no system enforcement.** It is a sentence
   in a document. The exact failure mode at Reno was a facility-level configuration change
   that appeared in no change review — since remediated by SOP-PUT-007 Action 5, which added
   facility config to change review. That remediation is what makes Recommendation 5
   plausible rather than aspirational.
3. **Richmond was audited less thoroughly than Columbus.** Single-level rack, no mezzanine,
   no labeling ambiguity, best accuracy in the network. The audit was scoped to the
   Columbus-specific question. Richmond's 218 Q2 PUT-01 events have not been characterized
   by cause.
4. **The Columbus inventory clerk vacancy is degrading `NO-FIT` resolution** and has been
   open since 2026-04. Four unresolved `NO-FIT` records against a target of zero is small,
   but each one is a SKU that will fail again on next receipt.
5. **This SOP has no equivalent of SOP-PUT-007's metric review trigger.** SOP-PUT-007 commits
   to reopening its investigation if Reno accuracy has not reached 99.3% by 2026-09-30. This
   document sets no comparable condition, because both sites are at target and no one
   specified what "getting worse" would mean.

Limitation 5 is the same class of gap as the accepted-risk-with-no-review-trigger finding in
INC-2025-0417.

---

## Related documents

SOP-PUT-007 (Putaway — Reno) · SOP-INV-002 (Inventory Cycle Counts) · SOP-REC-004
(Receiving Discrepancies) · SOP-REC-001 (Standard Receiving) · VEN-POL-002 (Vendor and
Temporary Labour) · SOP-PEAK-001 (Peak Season Operating Procedures) · TRN-NEW-001 (New Hire
Training and Certification) · INV-RPT-2026-Q2 · INV-RPT-2026-Q3 · INC-2026-0104 ·
ONB-CASE-2026-031
