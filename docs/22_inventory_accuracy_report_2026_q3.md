# Inventory Accuracy Report — Q3 2026

> Fictional reference document — Meridian Fulfillment Co.

**Document ID:** INV-RPT-2026-Q3
**Period:** 2026-07-01 through 2026-09-30
**Owner:** Facility Managers, consolidated by Client Operations Manager
**Published:** 2026-10-07
**Distribution:** VP Operations, Facility Managers, Client Operations Manager, Finance
**Prior report:** INV-RPT-2026-Q2

---

## Executive summary

**The Reno improvement held.**

INV-RPT-2026-Q2 closed with a fifteen-day post-intervention sample showing Reno at 99.38%
and PUT-01 at 2.2 per 1,000 putaways, and stated plainly that two weeks is not a trend and
that Q3 would be the first quarter capable of answering the question properly.

Q3 answers it. **Reno finished at 99.24%**, up from 98.74% in Q2 — the largest
quarter-on-quarter improvement recorded at any facility, and the first quarter above 99% at
Reno since Q3 2025.

**Reno is still below the 99.5% target.** The gap has narrowed from 76 basis points to 26,
but it has not closed. Reno has now missed target for five consecutive quarters.

Network accuracy was **99.44%**, against the 99.5% target — the closest the network has come
since Q3 2025 and still, marginally, a miss.

Three secondary findings matter more than the headline:

1. **The supervisor override problem predicted in Q2 was real and has been contained.**
   Overrides at Reno fell from 3.4 per shift immediately post-enforcement to 0.5 by
   September, following the written-justification requirement.
2. **The REC-01 / PUT-01 misattribution hypothesis was tested and partially confirmed.**
   Roughly a fifth of Reno receiving errors were misclassified putaway errors.
3. **The Columbus mezzanine audit found the latent condition present and the failure
   absent.** Columbus is, in effect, the control group that validates SOP-PUT-007's
   conclusion.

---

## 1. Network summary

| Facility | Q3 2026 | Q2 2026 | Q1 2026 | Q4 2025 | Q3 2025 | Target | Status |
|---|---|---|---|---|---|---|---|
| Richmond | 99.64% | 99.62% | 99.58% | 99.61% | 99.64% | 99.5% | ✅ |
| Columbus | 99.61% | 99.58% | 99.55% | 99.52% | 99.57% | 99.5% | ✅ |
| **Reno** | **99.24%** | **98.74%** | **98.81%** | **98.90%** | **99.44%** | 99.5% | ❌ |
| **Network** | **99.44%** | **99.31%** | **99.31%** | **99.34%** | **99.55%** | 99.5% | ❌ |

Reno's five-quarter decline reversed. The facility has recovered roughly two thirds of the
ground lost between Q3 2025 and Q2 2026, in one quarter.

Richmond and Columbus both improved marginally and both remain comfortably at target.
Neither movement is significant; both are within normal quarterly variation.

---

## 2. Reno — did it hold?

### Monthly progression

| Month | Accuracy | PUT-01 count | PUT-01 per 1,000 putaways | Notes |
|---|---|---|---|---|
| 2026-06 (15–30) | 99.38% | 43 | 2.2 | Q2 post-intervention sample |
| 2026-07 | 99.11% | 97 | 2.6 | First full month post-enforcement |
| 2026-08 | 99.22% | 84 | 2.1 | Relabeling completed 2026-08-27 |
| 2026-09 | 99.39% | 61 | 1.6 | |
| **Q3 average** | **99.24%** | **242** | **2.1** | vs Q2: 745 events, 6.8 per 1,000 |

**July was worse than the June sample.** This is the most important line in the report and
the one most likely to be misread.

The June 15–30 sample ran at 2.2 per 1,000. July ran at 2.6 — a regression of roughly 18%
against the sample that Q2 presented as evidence the intervention was working.

Two explanations, and the honest answer is that both contribute and the split is unknown:

- **The June sample was flattering.** Fifteen days, immediately after a highly visible
  intervention, with supervisors watching closely. A Hawthorne effect is the obvious
  candidate and cannot be excluded.
- **July included residual location-master correction.** Enabling enforcement surfaced
  drifted location records, and correction continued into July at a declining rate.

August and September then improved steadily, ending at 1.6 per 1,000 — approaching but not
reaching the target of under 1.5.

**The trend is real. The June figure was optimistic.** Q2's caution about a two-week sample
was warranted, and the caution should be repeated here: three months is better evidence
than two weeks, and Q4 will be run under peak conditions that Q3 was not.

### Corrective action status, per SOP-PUT-007

| # | Action | Q2 status | Q3 status |
|---|---|---|---|
| 1 | Re-enable directed putaway enforcement | Complete 2026-06-15 | Holding |
| 2 | Relabel mezzanine to prefix scheme | 57% (640 of 1,120) | **Complete 2026-08-27** |
| 3 | Raise mezzanine lighting to 300 lux | Unfunded | **Funded 2026-09-12; install Q4** |
| 4 | Block placeholder SKU dimensions | Complete 2026-05-20 | Holding |
| 5 | Facility config in change review | Complete 2026-06-01 | Holding |
| 6 | SOP written and trained | Complete | Holding |

**Action 2 completed 2026-08-27**, four days before its 2026-08-31 target. Both labeling
schemes are no longer live simultaneously; all 1,120 mezzanine locations now use the prefix
scheme (`M14-A-03-2`).

The dual-scheme transition hazard flagged in SOP-PUT-007's limitations is closed. September's
improvement to 1.6 per 1,000 is partly attributable to it, though the effect cannot be
isolated from the general trend.

**Action 3 was funded on 2026-09-12 at $47,000**, following the quantified business case
required by INV-RPT-2026-Q2 Action 3. The number that unlocked it: the second-shift pairing
restriction was costing an estimated **$38,400 annually** in lost mezzanine putaway
throughput — a payback under fifteen months on a control that also removes a documented
error source.

That figure had never been calculated before Q3. The capex had been deferred twice for lack
of a business case, and the business case was absent because nobody owned producing it. This
is worth recording as a process lesson independent of the lighting itself.

Installation is scheduled for Q4, **outside weeks 46–52** per SOP-PEAK-001's change freeze.
The pairing restriction remains in force until installation completes and lux is verified.

### Post-enforcement PUT-01 categorization

The 43 post-intervention events in Q2 were categorized to understand what enforcement does
not catch. Repeating that categorization across Q3's 242 events:

| Category | Q2 (15 days) | Q3 (full quarter) | Q3 % |
|---|---|---|---|
| Supervisor override, later found incorrect | 14 (33%) | 38 | **15.7%** |
| Location master data wrong | 19 (44%) | 51 | 21.1% |
| Genuine misput despite enforcement | 6 (14%) | 129 | **53.3%** |
| Unclassified | 4 (9%) | 24 | 9.9% |

**The composition has inverted, and this is the expected and desired outcome.**

Location-master errors fell from 44% to 21% as residual drift was corrected. Incorrect
overrides fell from 33% to 16% following Action 4. What remains is predominantly **genuine
misputs that enforcement structurally cannot catch** — the operator scans the correct
location and physically places the product in an adjacent bay.

Enforcement verifies the scan, not the placement. 53.3% of remaining events are in the
category no configuration change will address.

**This sets the ceiling on the current approach.** If genuine misputs are 129 events per
quarter and enforcement cannot reduce them, Reno's floor under the present control set is
roughly 1.1 PUT-01 per 1,000 putaways — below the 1.5 target, but only just, and with no
margin.

Further improvement requires either lighting (Action 3, Q4), physical verification at
placement, or accepting the floor. This is discussed in Section 7.

---

## 3. Supervisor overrides

Q2 identified overrides as the emerging failure mode: a control that can be bypassed will be
bypassed under pressure.

| Period | Reno overrides/shift | Richmond | Columbus |
|---|---|---|---|
| 2026-06-15 → 06-30 | 3.4 | 0.4 | 0.6 |
| 2026-07 | 1.4 | 0.4 | 0.6 |
| 2026-08 | 0.8 | 0.4 | 0.5 |
| 2026-09 | **0.5** | 0.3 | 0.5 |
| Target | < 1.0 | < 1.0 | < 1.0 |

Reno came within target in August and finished September at 0.5.

**The intervention was Action 4 from INV-RPT-2026-Q2:** weekly override review with written
justification required, effective 2026-07-13. The requirement was extended to Richmond and
Columbus effective 2026-09-01 under SOP-PUT-002 Recommendation 4 — not because those sites
had a problem, but because the control is cheap and its absence is what allowed Reno's
override rate to go unexamined.

Written justifications reviewed in Q3 (N = 312 at Reno) categorize as:

| Justification category | Count | Assessment |
|---|---|---|
| Location master genuinely wrong | 178 | Legitimate |
| Physical obstruction not in system | 61 | Legitimate |
| Product damaged, needed immediate placement | 21 | Legitimate |
| "Faster" / "location was full" / no detail | 38 | **Not legitimate — should have been RE-DIRECT** |
| Blank or illegible | 14 | **Not assessable** |

The 38 illegitimate overrides map closely to the 38 incorrect-override PUT-01 events, which
suggests the categorization is capturing the right population.

**The 14 blank justifications are a control weakness.** The field is mandatory but accepts
any input including a single character. Requiring free text does not require meaningful free
text, and there is no downstream check.

---

## 4. REC-01 / PUT-01 misattribution — hypothesis tested

INV-RPT-2026-Q2 Action 5 required testing the hypothesis that some Reno receiving errors are
actually misattributed putaway errors: product counted correctly at receipt, misplaced at
putaway, then discovered missing and coded REC-01 because that is where the trail appeared to
start.

### Method

100 Reno REC-01 adjustments sampled from 2026-07-01 to 2026-09-15. For each, the receiving
record, ASN, putaway task history, and subsequent location history were traced.

### Result — hypothesis partially confirmed

| Classification on re-examination | Count |
|---|---|
| Genuine receiving count error | 61 |
| **Putaway error misattributed as REC-01** | **19** |
| Damage not recorded at receipt (DAM-01) | 8 |
| Indeterminate — insufficient trail | 12 |

**19% of sampled Reno REC-01 adjustments were putaway errors.**

Applied to Q3's Reno REC-01 volume of 186, this suggests roughly 35 adjustments per quarter
are misclassified — which would raise Reno's true PUT-01 count from 242 to approximately 277,
about 14% higher than reported.

**This does not change the trend.** The same misattribution rate presumably applied in Q2 and
earlier, so the quarter-on-quarter improvement stands. It means Reno's absolute PUT-01 rate
has been understated throughout, and the facility's putaway problem was somewhat worse than
the numbers showed.

It also partially addresses the company profile's long-standing observation that receiving
discrepancies at Reno run above the other two sites with the cause not yet isolated. **A
fifth of that gap is putaway, not receiving.** The remaining four fifths are not explained by
this analysis and the observation stands.

### Cause of misattribution

Cause coding is assigned by the person resolving the adjustment, who is frequently the person
who discovered it. A cycle counter finding stock missing from a location has no visibility
into whether it was never put there or was put somewhere else. REC-01 is the intuitive
default.

This is the limitation INV-RPT-2026-Q2 flagged as *"the one that would most change the
picture if wrong."* It was wrong, in the direction and roughly the magnitude suspected.

---

## 5. Counts and cause codes

### Counts performed

| Facility | Scheduled | Trigger | Total | Coverage |
|---|---|---|---|---|
| Richmond | 3,488 | 202 | 3,690 | 41.9% |
| Columbus | 3,241 | 188 | 3,429 | 40.4% |
| Reno | 2,977 | **341** | 3,318 | 42.7% |
| **Network** | **9,706** | **731** | **10,437** | **41.7%** |

**Reno trigger counts fell from 487 to 341**, a 30% reduction, consistent with fewer variances
generating fewer "two or more variances in the same aisle within 30 days" triggers.

Reno trigger volume remains above the network average but the gap has narrowed substantially
— from 2.3× to 1.7× per location.

### Cause code distribution, network

| Code | Meaning | Q3 count | Q3 % | Q2 % |
|---|---|---|---|---|
| PIK-01 | Pick error, wrong quantity | 771 | 24.0% | 20.8% |
| **PUT-01** | **Putaway to wrong location** | **698** | **21.7%** | **31.8%** |
| REC-01 | Receiving count error | 498 | 15.5% | 13.5% |
| PIK-02 | Pick error, wrong SKU | 422 | 13.1% | 11.4% |
| DAM-01 | Damage not recorded | 331 | 10.3% | 8.9% |
| RET-01 | Return processed incorrectly | 268 | 8.3% | 7.3% |
| SYS-01 | System or integration error | 138 | 4.3% | 3.7% |
| UNK-01 | Unknown after investigation | 88 | **2.7%** | 2.5% |
| **Total** | | **3,214** | | |

**PUT-01 is no longer the largest cause code network-wide.** PIK-01 overtook it. Total
adjustments fell from 3,784 to 3,214, a 15% reduction, driven almost entirely by Reno.

UNK-01 at 2.7% remains well within the 10% threshold that triggers review under SOP-INV-002.

### PUT-01 by facility

| Facility | Q3 PUT-01 | Q2 PUT-01 | Change | Q3 % of network |
|---|---|---|---|---|
| Richmond | 224 | 218 | +2.8% | 32.1% |
| Columbus | 232 | 241 | −3.7% | 33.2% |
| **Reno** | **242** | **745** | **−67.5%** | **34.7%** |

**Reno's share of network PUT-01 fell from 61.9% to 34.7%** — now proportional to its share
of volume, matching every other cause code at the facility.

This is the clearest single statement of the result: Reno no longer has a distinctive
putaway problem. It has a residual gap to target, shared with the network.

---

## 6. Adjustment values, approvals, and notifications

| Band | Approver | Count | Total value |
|---|---|---|---|
| Under $500 | Shift supervisor | 2,671 | $355,180 |
| $500 – $5,000 | Facility Manager | 478 | $661,840 |
| Above $5,000 | Facility Manager + Client Ops Mgr | 59 | $498,110 |
| Serialized (any value) | Facility Manager | 6 | $15,290 |
| **Total** | | **3,214** | **$1,530,420** |

Net inventory shrink for Q3 was **$58,910** network-wide, or 0.031% of inventory value, down
from $71,340 in Q2.

As in Q2, gross adjustment value is dominated by product moving from where the system thought
it was to where it actually is. The money that left the building is the net figure.

### Client notifications

| Facility | Required | Sent within 1 business day | Compliance | Q2 |
|---|---|---|---|---|
| Richmond | 79 | 79 | 100% | 100% |
| Columbus | 74 | 73 | 98.6% | 97.5% |
| Reno | **94** | **91** | **96.8%** | **90.1%** |
| Network | 247 | 243 | 98.4% | 94.9% |

**Reno improved from 90.1% to 96.8%** but still misses. Three late notifications, none more
than two business days late, all Growth or Standard tier. No enterprise notification was
missed at any facility.

The improvement is attributable to lower notification volume (131 → 94) rather than to any
process change. **Action 6 — WMS automation of client adjustment notifications — remains open**
with a 2026-10-31 due date. Until it lands, compliance depends on manual effort scaling
inversely with adjustment volume, which is exactly backwards.

---

## 7. Findings

### Finding 1 — The improvement held, and the June sample was optimistic

Q3 at 99.24% confirms the direction. July at 2.6 per 1,000 was worse than the June 15–30
sample at 2.2, and anyone forecasting from that fifteen-day window would have been wrong.

Q2's stated caution was correct and is repeated: **Q4 runs under peak, Q3 did not.**

### Finding 2 — Enforcement has reached its structural ceiling

53.3% of residual Reno PUT-01 events are genuine misputs where the operator scanned correctly
and placed incorrectly. No configuration change addresses this.

The implied floor is roughly 1.1 per 1,000 under current controls. The target is 1.5, so the
floor is adequate — but Reno is at 1.6 and the remaining margin comes from lighting (Q4) and
from the last of the location-master correction.

**If Reno is still above 1.5 by Q1 2027 with lighting installed, the current control set has
been exhausted** and further improvement requires a different intervention class — placement
verification, pick-face redesign, or accepting the rate.

### Finding 3 — Override justification is mandatory but not meaningful

14 of 312 justifications were blank or illegible. The field accepts any input. A mandatory
field with no quality check is a mandatory field, not a control.

### Finding 4 — REC-01 misattribution confirmed at 19%

Reno's true putaway error rate has been understated by roughly 14% throughout. The trend is
unaffected; the absolute level was worse than reported.

### Finding 5 — Columbus is the control group and validates the Reno diagnosis

The SOP-PUT-002 audit found Columbus carries the identical suffix labeling scheme, with
ground/mezzanine pairs differing by one character, and shows 17% mezzanine PUT-01
concentration against Reno's 61%.

The difference is enforcement, which Columbus has never lost. **This is the strongest
available evidence that SOP-PUT-007's root-cause analysis was correct** — that labeling
created the misread and enforcement determined whether a misread became a misput.

### Finding 6 — The lighting business case took nine months to produce

The capex was deferred twice for want of a business case. The business case required one
number — the annualized throughput cost of the pairing restriction, $38,400 — which took
under a day to calculate once assigned.

Nobody owned producing it. That is the finding, not the lighting.

---

## 8. Actions for Q4

| # | Action | Owner | Due |
|---|---|---|---|
| 1 | Install mezzanine lighting; verify 300 lux; lift pairing restriction | Reno FM | 2026-12-15 |
| 2 | Continue weekly Reno PUT-01 reporting through peak | Reno FM | Ongoing |
| 3 | Add quality check to override justification field; reject under 15 characters | WMS Eng | 2026-11-14 |
| 4 | Complete WMS automation of client adjustment notifications | WMS Eng | 2026-10-31 |
| 5 | Re-run REC-01 sample at Richmond and Columbus to test whether misattribution is Reno-specific | Client Ops Mgr | 2026-12-31 |
| 6 | Characterize Richmond's PUT-01 events by cause — never done | Richmond FM | 2027-01-31 |
| 7 | Fill Columbus inventory clerk vacancy | HR | 2026-11-30 |
| 8 | Assess whether Reno warrants continued separate SOP or can merge into SOP-PUT-002 | Client Ops Mgr | 2027-03-31 |

**Action 5 matters more than its priority suggests.** If REC-01 misattribution runs at 19%
everywhere, then network PUT-01 is understated across all three sites and every facility's
putaway performance is somewhat worse than reported. Reno was sampled because Reno was the
problem; the sampling design assumes the effect is Reno-specific and that assumption is
untested.

**Action 1 falls partly inside weeks 46–52.** Installation is scheduled to complete
2026-12-15, which is week 51. SOP-PEAK-001 freezes non-urgent WMS changes from week 45 but
does not govern facilities work. The Reno Facility Manager has confirmed the work is
confined to second-shift downtime in aisles already covered by the pairing restriction.
**This is a judgement call and it carries risk during the highest-volume period of the year.**

---

## 9. Known limitations

1. **Q3 contained no peak conditions.** Reno's improvement was achieved at normal volume with
   normal staffing. Weeks 46–52 add roughly 38% temporary labour network-wide, and Class B
   and C cycle counts suspend — meaning a Q4 putaway error is materially less likely to be
   detected before January. **Q4 is the real test.**
2. **Coverage remains 41.7%.** Class C SKUs count semi-annually. The true accuracy figure is
   unknown and is probably lower than reported at every facility.
3. **Cause coding is still self-assigned** with no independent verification. Finding 4
   demonstrates this produces material error. UNK-01's low rate remains as likely to indicate
   confident guessing as genuine investigation.
4. **No client-level shrink reporting exists.** Net shrink of $58,910 is a network figure.
   Clients disproportionately affected cannot be identified — unchanged from Q2 and no action
   is scheduled.
5. **The $38,400 pairing-restriction cost is an estimate** built from average mezzanine
   putaway throughput and a 6% degradation assumption originating in SOP-PUT-007. It was not
   measured directly and it justified a $47,000 capex.
6. **Richmond has still never been characterized.** Action 6 addresses this with a 2027-01-31
   due date, which is the third quarter in which Richmond's PUT-01 events have gone
   unexamined on the grounds that the facility is at target.

Limitation 6 is the same reasoning that left Columbus unaudited until Reno forced the
question, and Columbus turned out to carry the identical latent condition.

---

## Related documents

SOP-INV-002 (Inventory Cycle Counts) · SOP-PUT-007 (Putaway — Reno) · SOP-PUT-002 (Putaway —
Richmond and Columbus) · SOP-REC-004 (Receiving Discrepancies) · SOP-PEAK-001 (Peak Season
Operating Procedures) · VEN-POL-002 · INV-RPT-2026-Q2 · INV-RPT-2026-Q1 · INC-2026-0104 ·
00_company_profile
