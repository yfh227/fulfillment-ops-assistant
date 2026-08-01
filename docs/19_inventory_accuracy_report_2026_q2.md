# Inventory Accuracy Report — Q2 2026

> Fictional reference document — Meridian Fulfillment Co.

**Document ID:** INV-RPT-2026-Q2
**Period:** 2026-04-01 through 2026-06-30
**Owner:** Facility Managers, consolidated by Client Operations Manager
**Published:** 2026-07-08
**Distribution:** VP Operations, Facility Managers, Client Operations Manager, Finance
**Prior report:** INV-RPT-2026-Q1

---

## Executive summary

Network location-level accuracy for Q2 2026 was **99.31%**, against a target of 99.5% per
SOP-INV-002. This is the fourth consecutive quarter below target at network level, though
the shortfall is entirely attributable to one facility.

**Richmond and Columbus both met target.** Richmond finished at 99.62%, Columbus at 99.58%.

**Reno finished at 98.74%**, which is **worse than the 98.9% recorded in SOP-INV-002's
last revision** and worse than Q1's 98.81%.

The headline is therefore: **the Reno problem got slightly worse this quarter, not better.**

That statement requires immediate qualification, and the qualification is the substance of
this report. The corrective actions from the Reno putaway investigation (SOP-PUT-007) did
not take effect until **2026-06-15**, fifteen days before quarter end. The quarterly
average is dominated by the eleven weeks before the fix.

Segmenting the quarter around that date:

| Period | Reno accuracy | PUT-01 per 1,000 putaways |
|---|---|---|
| 2026-04-01 → 2026-06-14 | 98.66% | 7.1 |
| **2026-06-15 → 2026-06-30** | **99.38%** | **2.2** |

The post-intervention figure is the first time Reno has been above 99.2% in any measured
period since Q3 2025.

**Two weeks is not a trend.** This report does not claim the problem is solved. It claims
the intervention is producing the expected direction and magnitude of change, and that Q3
will be the first quarter capable of answering the question properly.

---

## 1. Network summary

| Facility | Q2 2026 | Q1 2026 | Q4 2025 | Q3 2025 | Target | Status |
|---|---|---|---|---|---|---|
| Richmond | 99.62% | 99.58% | 99.61% | 99.64% | 99.5% | ✅ |
| Columbus | 99.58% | 99.55% | 99.52% | 99.57% | 99.5% | ✅ |
| **Reno** | **98.74%** | **98.81%** | **98.90%** | **99.44%** | 99.5% | ❌ |
| **Network** | **99.31%** | **99.31%** | **99.34%** | **99.55%** | 99.5% | ❌ |

Reno's decline began in Q4 2025 and has continued each quarter since. The Q3 2025 figure of
99.44% — marginally below target but broadly healthy — is the last quarter before the
deterioration.

**Nothing changed at Reno in Q4 2025 that explains the onset.** This has been examined
repeatedly. Directed putaway enforcement was disabled in March 2024, twenty months before
the decline began, so the enforcement gap alone does not explain the timing. The
investigation in SOP-PUT-007 concluded the enforcement gap was necessary but not sufficient:
it created the *conditions* for error, and the Q3-2025 onboarding of three Growth-tier
clients supplied the *volume of new SKUs with unverified dimensions* that converted the
condition into errors at scale.

That interpretation is consistent with the 47% concentration of PUT-01 events in SKUs
located within the prior 30 days, but it remains an interpretation rather than a
demonstrated causal chain.

---

## 2. Counts performed

| Facility | Scheduled counts | Trigger counts | Total | Locations counted | Coverage |
|---|---|---|---|---|---|
| Richmond | 3,412 | 218 | 3,630 | 3,630 | 41.2% |
| Columbus | 3,180 | 194 | 3,374 | 3,374 | 39.8% |
| Reno | 2,940 | **487** | 3,427 | 3,427 | 44.1% |
| **Network** | **9,532** | **899** | **10,431** | **10,431** | **41.6%** |

**Reno's trigger count volume is 2.3× the network average per location.** Trigger counts
fire on the conditions in SOP-INV-002 — negative on-hand, pick shortage, two or more
variances in one aisle within 30 days, client-reported discrepancy, receiving discrepancy
classified as count variance, or before a client-requested physical inventory.

Reno's elevated trigger volume is itself a symptom. The most common trigger at Reno was
"two or more variances in the same aisle within 30 days," which fired 189 times, of which
**134 were in aisles 14–22** — the mezzanine overflow zone identified in SOP-PUT-007 as the
source of 61% of PUT-01 events.

Additionally, Reno ran a **full physical count of aisles 14–22 on 2026-03-20** (Action 5
from INC-2026-0104) which falls in Q1 but whose remediation work extended into April. Three
further mixed-client locations were found during that count.

---

## 3. Cause code distribution

Per SOP-INV-002, every adjustment requires a cause code. Uncoded adjustments are rejected
by the WMS.

### Network, Q2 2026

| Code | Meaning | Count | % of adjustments |
|---|---|---|---|
| PUT-01 | Putaway to wrong location | 1,204 | 31.8% |
| PIK-01 | Pick error, wrong quantity | 786 | 20.8% |
| REC-01 | Receiving count error | 512 | 13.5% |
| PIK-02 | Pick error, wrong SKU | 431 | 11.4% |
| DAM-01 | Damage not recorded | 338 | 8.9% |
| RET-01 | Return processed incorrectly | 276 | 7.3% |
| SYS-01 | System or integration error | 141 | 3.7% |
| UNK-01 | Unknown after investigation | 96 | **2.5%** |
| **Total** | | **3,784** | |

**UNK-01 at 2.5% is well within the 10% threshold** that triggers review under SOP-INV-002.
Network UNK-01 has never exceeded 4.1% in any month on record.

### By facility

| Code | Richmond | Columbus | Reno | Reno % of network total |
|---|---|---|---|---|
| PUT-01 | 218 | 241 | **745** | **61.9%** |
| PIK-01 | 264 | 258 | 264 | 33.6% |
| REC-01 | 148 | 161 | 203 | 39.6% |
| PIK-02 | 139 | 144 | 148 | 34.3% |
| DAM-01 | 112 | 118 | 108 | 32.0% |
| RET-01 | 94 | 101 | 81 | 29.3% |
| SYS-01 | 44 | 51 | 46 | 32.6% |
| UNK-01 | 26 | 31 | 39 | 40.6% |

**Reno accounts for roughly one third of network volume but 61.9% of PUT-01 adjustments.**
Every other cause code sits between 29% and 41% — broadly proportional to volume.

This is the clearest single piece of evidence in the report. Reno is not generally worse at
inventory management. Reno has one specific, isolated, well-characterized problem, and every
other process at the facility performs in line with the network.

**REC-01 at 39.6% is mildly elevated** and worth watching. The company profile notes that
receiving discrepancies at Reno run above the other two sites with the cause not isolated.
That observation predates this report and remains unresolved. It is plausible — but
unproven — that some portion of REC-01 at Reno is actually misclassified PUT-01: product
counted correctly at receipt, misplaced at putaway, then discovered missing and coded as a
receiving error because that is where the trail appeared to start.

**This hypothesis has not been tested.** It is recorded as an open question for Q3.

---

## 4. Reno — detailed analysis

### Monthly progression

| Month | Accuracy | PUT-01 count | PUT-01 per 1,000 putaways | Notes |
|---|---|---|---|---|
| 2026-04 | 98.71% | 289 | 7.4 | Investigation ongoing |
| 2026-05 | 98.68% | 301 | 7.2 | Placeholder-dimension block live 2026-05-20 |
| 2026-06 (1–14) | 98.79% | 112 | 6.6 | |
| **2026-06 (15–30)** | **99.38%** | **43** | **2.2** | **Enforcement re-enabled 2026-06-15** |
| Q2 average | 98.74% | 745 | 6.8 | |

### Corrective action status, per SOP-PUT-007

| # | Action | Status | Effect visible in Q2? |
|---|---|---|---|
| 1 | Re-enable directed putaway enforcement | Complete 2026-06-15 | **Yes — 15 days** |
| 2 | Relabel mezzanine to prefix scheme | 640 of 1,120 (57%) | Partial |
| 3 | Raise mezzanine lighting to 300 lux | **Unfunded** | No |
| 4 | Block placeholder SKU dimensions | Complete 2026-05-20 | Marginal — 41 days |
| 5 | Facility config in change review | Complete 2026-06-01 | Preventive only |
| 6 | SOP written and trained | Complete | Yes |

**Action 1 is doing the work.** The drop from 6.6 to 2.2 PUT-01 per 1,000 putaways
coincides exactly with enforcement re-enablement.

**Action 3 remains unfunded** at $47,000 and sits with the VP Operations. The consequence is
that SOP-PUT-007's second-shift pairing restriction after 19:00 remains in force
indefinitely rather than temporarily, at a throughput cost of approximately 6% on mezzanine
putaway. That cost has not been quantified in dollars and probably should be, since it is
plausibly recurring at a rate that would fund the lighting within two years.

**Action 2 at 57% complete** means both labeling schemes remain live in the building. The
ground/mezzanine confusion documented as Cause 1 in SOP-PUT-007 is mitigated but not
eliminated.

### Post-intervention detail, 2026-06-15 → 2026-06-30

43 PUT-01 events in the post-intervention window. Categorized:

| Category | Count | Note |
|---|---|---|
| Supervisor override, later found incorrect | 14 | Override used to bypass a correct block |
| Location master data wrong | 19 | System directed to an invalid location |
| Genuine misput despite enforcement | 6 | Scanned correct location, placed in adjacent |
| Unclassified | 4 | |

**The 19 location-master errors were expected.** SOP-PUT-007 records that enabling
enforcement surfaced roughly 900 drifted location records, and correcting them delayed the
action by six weeks. Residual drift continues to surface at a declining rate — 14 in week
one post-enforcement, 5 in week two.

**The 14 incorrect supervisor overrides are the concerning category.** Enforcement can be
bypassed by a supervisor badge scan, and in 14 cases it was bypassed to place product
somewhere the system correctly objected to. Supervisor overrides ran 3.4 per shift
immediately post-enforcement against a target of under 1.0, falling to 0.7 by the week
beginning 2026-06-22.

This is the predictable next failure mode: a control that can be overridden will be
overridden under pressure. It is flagged for Q3 monitoring and is the reason the override
metric exists.

**Six genuine misputs despite enforcement** — operators scanned the correct location and
physically placed product elsewhere, typically an adjacent bay. Enforcement cannot catch
this; it verifies the scan, not the placement. Four of the six were in aisles 14–22.

---

## 5. Adjustment values and approvals

Per SOP-INV-002, adjustments require approval by value band.

| Band | Approver | Count | Total value |
|---|---|---|---|
| Under $500 | Shift supervisor | 3,102 | $412,880 |
| $500 – $5,000 | Facility Manager | 604 | $844,210 |
| Above $5,000 | Facility Manager + Client Ops Mgr | 71 | $611,940 |
| Serialized (any value) | Facility Manager | 7 | $18,460 |
| **Total** | | **3,784** | **$1,887,490** |

Net adjustment value is materially smaller than gross — most adjustments pair a negative in
one location with a positive in another, which is the signature of a putaway error rather
than a loss. **Net inventory shrink for Q2 was $71,340 network-wide**, or 0.038% of
inventory value, which is within normal range and unremarkable.

**This distinction is important and is regularly misread by people outside operations.**
$1.89M of gross adjustment looks alarming. It is overwhelmingly product being moved from
where the system thought it was to where it actually is. The money that actually left the
building is $71,340.

### Client notifications

SOP-INV-002 requires client notification for any adjustment above $1,000, or any adjustment
on an enterprise account regardless of value.

| Facility | Notifications required | Sent within 1 business day | Compliance |
|---|---|---|---|
| Richmond | 84 | 84 | 100% |
| Columbus | 79 | 77 | 97.5% |
| Reno | 131 | 118 | **90.1%** |
| Network | 294 | 279 | 94.9% |

**Reno's 90.1% is a compliance failure** and is the second finding of this report. Thirteen
client notifications were late, of which four were more than three business days late.

Cause: Reno's notification volume is 56% higher than Richmond's against comparable client
counts, and the process is manual — the Facility Manager emails the Account Manager, who
notifies the client. Under volume, it slips.

No enterprise-account notification was missed. All thirteen were Growth or Standard tier.
That is fortunate rather than by design; nothing in the process prioritizes by tier.

---

## 6. Findings

### Finding 1 — Reno's Q2 average is worse; Reno's current state is better

The quarterly average declined from 98.81% to 98.74%. Taken alone, this reads as a
deteriorating situation.

Taken with the segmentation, the picture is a flat-to-declining eleven weeks followed by a
sharp improvement in the final two. **Reporting the quarterly average without the
segmentation would be accurate and misleading**, which is why this report leads with both.

The honest position: the intervention appears to be working, the sample is two weeks, and
anyone who claims this is resolved before the Q3 report is overreading the data.

### Finding 2 — Reno client notification compliance is 90.1%

Thirteen late notifications, four more than three business days late. Manual process under
elevated volume. No tier prioritization exists.

### Finding 3 — Supervisor override is the emerging failure mode

14 of 43 post-intervention PUT-01 events involved a supervisor override that should not
have been granted. The control is new and the override path is the obvious pressure valve.

### Finding 4 — The REC-01 / PUT-01 boundary at Reno is untested

Reno's REC-01 rate is elevated at 39.6% of network total. It is plausible that some
receiving errors are misattributed putaway errors. Untested.

### Finding 5 — Lighting remains unfunded and the cost of not funding it is unquantified

$47,000 capex, deferred. The consequence is a permanent 6% throughput cost on mezzanine
putaway plus a persistent error source. Nobody has calculated the annual cost of the
pairing restriction, which makes the capex decision unarguable in either direction.

---

## 7. Actions for Q3

| # | Action | Owner | Due |
|---|---|---|---|
| 1 | Continue weekly Reno PUT-01 reporting; assess trend at 90 days post-enforcement | Reno FM | 2026-09-15 |
| 2 | Complete mezzanine relabeling (480 locations remaining) | Reno FM | 2026-08-31 |
| 3 | Escalate lighting capex with quantified throughput cost | VP Ops | 2026-08-15 |
| 4 | Weekly supervisor override review at Reno; require written justification | Reno FM | Ongoing from 2026-07-13 |
| 5 | Test the REC-01 / PUT-01 misattribution hypothesis on a 100-event sample | Client Ops Mgr | 2026-09-30 |
| 6 | Automate client adjustment notifications from the WMS | WMS Eng | 2026-10-31 |
| 7 | Audit Columbus mezzanine for the same labeling weakness | Columbus FM | 2026-09-30 |

**Action 7 addresses the limitation SOP-PUT-007 flagged as "most likely to age badly."**
Columbus has a mezzanine added in 2021 using the same suffix labeling scheme that caused
Reno's problem. Columbus is at target, which is why it has never been examined — but
"at target" is not evidence of absence, and Columbus's PUT-01 count of 241 is the highest
of any non-Reno cause code.

**Action 3 requires a number nobody has produced.** The lighting decision has been deferred
twice for lack of a business case, and no business case has been built because building one
requires quantifying the pairing restriction's throughput cost, which nobody owns.

---

## 8. Known limitations of this report

1. **The post-intervention sample is 15 days.** It covers one pay period, no month-end
   surge, and no peak conditions. Its predictive value for Q3 is limited.
2. **Accuracy is measured on counted locations only**, at 41.6% quarterly coverage. Class C
   SKUs count semi-annually, so a Class C error can persist for months before detection.
   The true accuracy figure is unknown and is probably lower than reported at every facility.
3. **Cause coding is assigned by the person resolving the adjustment**, who is frequently
   the person who caused it. There is no independent verification. UNK-01's low rate is
   presented as a positive, but a low unknown rate can equally mean people are guessing
   confidently rather than investigating.
4. **Net shrink of $71,340 is a network figure.** It is not broken down by client, and no
   client-level shrink reporting exists. Clients whose inventory is disproportionately
   affected cannot currently be identified.
5. **This report does not cover Q2 receiving discrepancy rates** beyond the REC-01 cause
   code, so the company profile's Reno receiving observation remains unaddressed by any
   dedicated analysis.

Limitation 3 is the one that would most change the picture if wrong.

---

## Related documents

SOP-INV-002 (Inventory Cycle Counts) · SOP-PUT-007 (Putaway — Reno) · SOP-REC-004
(Receiving Discrepancies) · INV-RPT-2026-Q1 · INC-2026-0104 · VEN-POL-002 ·
SOP-PEAK-001 · 00_company_profile
