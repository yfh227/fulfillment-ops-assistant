# SOP: Putaway — Reno Facility

> Fictional reference document — Meridian Fulfillment Co.

**Document ID:** SOP-PUT-007
**Owner:** Facility Manager, Reno (D. Okonkwo)
**Last reviewed:** 2026-06-30
**Applies to:** Reno NV facility only. Richmond and Columbus continue under SOP-PUT-002.
**Supersedes:** Local practice; no prior Reno-specific putaway SOP existed.

---

## Why this document exists

SOP-INV-002 (Inventory Cycle Counts) records that Reno has run below the 99.5%
location-level accuracy target since Q4 2025, sitting near 98.9%, with an elevated
PUT-01 (putaway to wrong location) rate. That document lists the cause as under
investigation.

The investigation is complete. This SOP is its output.

**Finding:** the elevated PUT-01 rate at Reno is not a training problem and not a
personnel problem. It is a consequence of three site-specific conditions that the
generic putaway SOP does not address, compounded by a workaround the Reno team
adopted in good faith and which nobody wrote down.

This document states what was found, then defines the corrected procedure.

---

## Investigation summary

Conducted 2026-04-06 through 2026-06-12 by the Reno Facility Manager with support
from the Client Operations Manager and two WMS developers.

### Method

- Pulled all 1,847 Reno inventory adjustments coded PUT-01 between 2025-10-01 and
  2026-05-31.
- Mapped each to the originating location, the intended location, the operator, the
  shift, the SKU, and the client.
- Re-walked 60 sampled misputs physically on the floor.
- Observed 14 full putaway cycles across all three shifts without intervening.
- Interviewed 11 of the 19 Reno putaway operators.

### What the data showed

PUT-01 adjustments were not distributed evenly. They concentrated sharply:

| Dimension | Concentration |
|---|---|
| Aisles 14–22 (the mezzanine overflow zone) | 61% of all PUT-01 events |
| Second shift (14:00–22:30) | 54% |
| SKUs with a location assigned in the prior 30 days | 47% |
| Clients onboarded since 2025-09 | 38% |
| Operators with under 90 days tenure | 29% |

The concentration in aisles 14–22 was the strongest single signal and the one that
broke the investigation open. Those aisles account for roughly 18% of Reno's pick
faces but 61% of misputs.

### Root causes identified

**Cause 1 — Location label ambiguity in the mezzanine overflow zone.**

Reno's mezzanine was added in 2023 when the site took on three Growth-tier clients
at once. The location naming scheme was extended rather than redesigned. Ground-level
aisle 14 contains locations labeled `14-A-03-2`. The mezzanine directly above it
contains `14-A-03-2M`. The trailing `M` is the only difference.

On the WMS handheld, the location field renders in a fixed-width font at 11 point,
and the trailing character sits at the right edge of the field. Under the mezzanine
lighting — which is original to the 2023 build and measured at 180–220 lux against a
Meridian standard of 300 — operators reported the `M` being genuinely hard to see.

Of the 60 misputs re-walked physically, **41 were ground/mezzanine pairs of the same
aisle-bay-level.** The product was within twelve feet of where it belonged, one floor
off.

This is not operator carelessness. Two operators, told what to look for, still
misread the label under working conditions during the observation sessions.

**Cause 2 — Directed putaway is advisory at Reno, not enforced.**

The WMS directs putaway to a suggested location. At Richmond and Columbus, scanning a
different location raises a hard block requiring supervisor override.

At Reno, that enforcement was disabled in March 2024. The reason was legitimate: during
the mezzanine build, roughly 900 locations were physically inaccessible for eleven
weeks while the deck was being finished, and the WMS location master had not been
updated to reflect it. Operators were being blocked from putting product anywhere
usable. Disabling enforcement was the correct call at the time.

**It was never re-enabled.** The build finished in June 2024. Nobody owned turning it
back on, and because the setting lives in a facility-level configuration table rather
than in the deployment pipeline, it did not appear in any change review.

For twenty-six months, Reno operators could scan any location and the system accepted it.

**Cause 3 — New-SKU location assignment happens at the wrong moment.**

For a newly onboarded SKU, the WMS assigns a home location the first time the SKU is
received. That assignment uses SKU dimensions from the client's SKU master.

Per SOP-ONB-001, incomplete SKU dimension data is the single most common cause of
onboarding delay. When dimensions are missing, Onboarding Specialists have historically
entered placeholder values to unblock the account, intending to correct them after the
first receipt shows actual cube.

The placeholder in common use was 12" × 12" × 12". That fits a standard shelf location.
Actual product frequently did not. Operators arriving at the directed location with a
pallet that visibly would not fit put it somewhere it did fit, and — with enforcement
disabled — the system accepted it.

This explains the 47% concentration in SKUs located within the prior 30 days, and the
38% concentration in clients onboarded since 2025-09.

### What was not a cause

Stated explicitly, because these were the leading hypotheses before the data came in
and each had advocates:

- **Not training.** Operators with over 90 days tenure accounted for 71% of PUT-01
  events. If training were the driver, the distribution would invert.
- **Not headcount or rate pressure.** Putaway units-per-hour at Reno tracks within 4%
  of Columbus across the period. Operators were not rushing.
- **Not the handheld hardware.** Reno runs the same Zebra TC52 units as the other two
  sites, on the same firmware.
- **Not a specific operator.** No individual accounted for more than 9% of events. The
  three highest-volume operators were also among the highest-volume putaway performers
  generally; their absolute counts were high because their throughput was high. Their
  error *rate* was near median.

The last point matters and is recorded deliberately. An early cut of this analysis
ranked operators by raw PUT-01 count and drew exactly the wrong conclusion. Rate, not
count, is the correct measure.

---

## Corrective actions

| # | Action | Owner | Status | Target |
|---|---|---|---|---|
| 1 | Re-enable directed putaway enforcement at Reno | WMS team | **Complete** 2026-06-15 | — |
| 2 | Relabel mezzanine locations to `M14-A-03-2` (prefix, not suffix) | Reno FM | In progress, 640 of 1,120 done | 2026-08-31 |
| 3 | Raise mezzanine lighting to 300 lux minimum | Facilities | Quoted, awaiting capex | 2026-09-30 |
| 4 | Block placeholder SKU dimensions at onboarding | WMS team | **Complete** 2026-05-20 | — |
| 5 | Add facility config settings to change review | Client Ops Mgr | **Complete** 2026-06-01 | — |
| 6 | This SOP written and trained out | Reno FM | **Complete** | — |

Action 2 is the long pole. Relabeling is being done aisle by aisle during second-shift
downtime to avoid a freeze. Until it completes, the mezzanine remains the highest-risk
zone in the building and the verification step below applies with no exceptions.

---

## Procedure

### Step 1 — Receive the putaway task

Accept the task on the handheld. The screen shows:

- Licence plate number (LPN)
- SKU and description
- Quantity
- **Directed location**
- Client name
- Any special handling flag

Do not begin travel until you have read the directed location aloud or subvocalized it.
This sounds trivial. It was the single highest-yield intervention in the observation
sessions: operators who verbalized the location before travelling misread it at roughly
a third the rate of those who did not.

### Step 2 — Confirm the zone before you travel

Check whether the directed location is ground or mezzanine.

- **Ground locations** read `14-A-03-2`.
- **Mezzanine locations** currently read `14-A-03-2M` (old scheme) or `M14-A-03-2`
  (new scheme, being rolled out).

**Until relabeling completes, both schemes are live in the building simultaneously.**
This is genuinely confusing and there is no way to avoid it during the transition. If
you are unsure which zone a location is in, the handheld's location detail screen
(press and hold the location field) states `GROUND` or `MEZZ` explicitly. Use it.

### Step 3 — Travel and scan the location barcode

Scan the location barcode **before** scanning the LPN. This order is deliberate and is
the reverse of what several operators were doing.

Scanning location first means the WMS knows where you are standing before it knows what
you are holding, and can reject a wrong location before the product is committed.
Scanning LPN first was the habit that developed while enforcement was disabled, because
in that state the order made no practical difference.

### Step 4 — Handle a mismatch

If the scanned location does not match the directed location, the handheld now raises
a hard block. You have three options:

**Option A — Go to the correct location.** Default. Use this unless B or C genuinely applies.

**Option B — Request a re-direct.** Use when the directed location is physically
unusable: it is occupied, blocked, damaged, or the product does not fit. Press
`RE-DIRECT` on the block screen and select a reason:

| Reason code | Use when |
|---|---|
| `OCCUPIED` | Another LPN is already in the location |
| `NO-FIT` | Product physically does not fit the location |
| `BLOCKED` | Location inaccessible — equipment, spill, damage |
| `DAMAGED` | Location itself is damaged, rack or beam issue |

The WMS assigns a new location and logs the reason. **This is not an exception path.
It is the normal path when the direction is wrong.** Re-directs are expected and are
not counted against you. What is counted is putting product somewhere the system did
not sanction.

`NO-FIT` re-directs are reviewed weekly, because a `NO-FIT` almost always means the SKU
dimension record is wrong. See Step 7.

**Option C — Supervisor override.** Requires a shift supervisor to scan their badge.
Reserved for cases where the system state is wrong in a way `RE-DIRECT` cannot resolve.
Each override generates a line in the daily exception report reviewed by the Facility
Manager.

Overrides ran at 3–4 per shift in the two weeks after enforcement was re-enabled. As of
week beginning 2026-06-22 they average 0.7 per shift. The early spike was almost entirely
location master data that had drifted during the enforcement-disabled period, which is
exactly what re-enabling was expected to surface.

### Step 5 — Scan the LPN and confirm quantity

With the location confirmed, scan the LPN. Confirm the quantity on screen matches what
you physically have.

If quantity differs, do not adjust it here. Set the LPN down in the location, mark it
`COUNT-PENDING` on the handheld, and notify your supervisor. Quantity corrections at
putaway bypass the blind-count protection in SOP-INV-002 and have historically been a
source of masked variance.

### Step 6 — Place the product

Placement rules, in priority order:

1. **Label facing the aisle.** Non-negotiable. Cycle counters cannot count what they
   cannot read, and an unreadable label produces a variance that costs far more time
   than turning the pallet.
2. **Heaviest at the bottom** for multi-tier locations.
3. **Do not overhang** the location footprint. Overhang in the mezzanine is a safety
   issue, not merely a tidiness one.
4. **Lot-tracked product:** verify the lot on the LPN matches the lot on the physical
   cartons before placing. Mixed lots in one location defeat FEFO picking.
5. **Serialized product:** never mix serial ranges in a location.

### Step 7 — Close the task

Confirm on the handheld. The task closes and inventory moves from receiving-staging to
the location in real time.

If you used `NO-FIT`, the SKU is automatically flagged for dimension review. The Reno
inventory clerk measures the SKU during the next business day and submits a correction
to the client's Account Manager. Do not skip this — a wrong dimension record will
generate the same `NO-FIT` for every subsequent receipt of that SKU indefinitely.

---

## Mezzanine-specific rules

Until relabeling completes (target 2026-08-31), these apply to any putaway in aisles
14–22:

- **Verify the zone indicator on the handheld before travelling.** Not after arrival.
- **Second shift: no solo mezzanine putaway after 19:00.** Lighting is the known
  weakness and it is worst in the last three hours of shift. Work in pairs or defer to
  third shift. This restriction lifts when Action 3 (lighting) completes.
- **Any mezzanine `NO-FIT` is reported to the supervisor verbally, same shift,** in
  addition to the system flag. The mezzanine has the least slack in the building and a
  blocked location there cascades faster than on the ground.
- **Do not stage product in mezzanine aisles.** Ever. The aisles are 42 inches and staged
  product forces operators to travel the long way, which is where several of the sampled
  misputs originated — the operator arrived at the right aisle from the wrong end and
  counted bays in the wrong direction.

---

## Metrics and review

Reported weekly by the Reno Facility Manager to the Client Operations Manager:

| Metric | Target | Baseline (2026-05) |
|---|---|---|
| PUT-01 adjustments per 1,000 putaways | < 1.5 | 6.8 |
| Location-level accuracy, Reno | 99.5% | 98.9% |
| Re-direct rate | 2–6% (a rate near zero suggests operators are not using it) | 1.1% |
| `NO-FIT` re-directs unresolved after 5 business days | 0 | n/a — new metric |
| Supervisor overrides per shift | < 1.0 | 3.4 |

**On the re-direct target:** a low re-direct rate is not a good sign. It means either
the directed locations are perfect — implausible — or operators are working around the
system rather than using the sanctioned exception path. The 1.1% baseline was measured
while enforcement was disabled and operators had no reason to re-direct, since they
could simply place product wherever it fit. A rise toward 2–6% is the expected and
desired outcome.

Full review of this SOP scheduled for 2026-09-30, after lighting and relabeling complete.
If accuracy has not reached 99.3% by then, the investigation reopens with the WMS
location master as the primary hypothesis.

---

## Known limitations of this document

Recorded honestly rather than omitted:

1. **The two labeling schemes coexisting is a real hazard** and this SOP mitigates it
   with a verification step rather than eliminating it. The step depends on operator
   discipline in exactly the conditions where discipline is hardest. This is a
   compromise driven by the impossibility of freezing the mezzanine for a single
   cutover during peak build-up.
2. **The lighting remediation is unfunded** as of this revision. It is quoted at
   $47,000 and sits with the VP Operations. If it does not fund, the pairing
   restriction on second shift becomes permanent rather than temporary, with a
   throughput cost of roughly 6% on mezzanine putaway.
3. **Placeholder SKU dimensions are blocked going forward but historical records were
   not backfilled.** Approximately 2,300 Reno SKUs carry dimension data of unknown
   provenance. These surface one at a time through `NO-FIT`. A bulk remeasure was
   scoped at 340 labour hours and deferred.
4. **This SOP is Reno-only.** Richmond and Columbus were not audited to the same depth.
   Their accuracy is at target, so the priority was low, but "at target" is not the same
   as "verified free of the same causes." Columbus also has a mezzanine, added 2021,
   using the suffix labeling scheme.

Point 4 is the one most likely to age badly.

---

## Related documents

SOP-INV-002 (Inventory Cycle Counts) · SOP-REC-004 (Receiving Discrepancies) ·
SOP-PUT-002 (Putaway — Richmond and Columbus) · SOP-ONB-001 (Client Onboarding
Checklist) · INV-RPT-2026-Q2 (Inventory Accuracy Report)
