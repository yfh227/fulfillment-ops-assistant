# Policy: Inventory Cycle Counts

> Fictional reference document — Meridian Fulfillment Co.

**Document ID:** SOP-INV-002
**Owner:** Facility Managers
**Last reviewed:** 2026-03-19

---

## Purpose

Maintain inventory accuracy without full physical inventories, which require shutting
down outbound operations.

**Target:** 99.5% location-level accuracy across all facilities.

---

## Count frequency by velocity class

SKUs are classified quarterly by outbound volume.

| Class | Definition | Count frequency |
|---|---|---|
| **A** | Top 20% of SKUs by volume | Monthly |
| **B** | Next 30% | Quarterly |
| **C** | Remaining 50% | Semi-annually |
| **High-value** | Unit cost above $250 | Monthly, regardless of class |
| **Serialized / lot-tracked** | Any | Monthly, regardless of class |

## Trigger counts

Count outside the schedule when any of these occur:

- Negative on-hand recorded in the WMS
- Pick shortage reported by a picker
- Two or more location variances found in the same aisle within 30 days
- Client reports a discrepancy against their own records
- Following any receiving discrepancy classified as count variance
- Before any client-requested physical inventory

---

## Procedure

**1. Freeze the location.** Set the location to count status in the WMS. No picks or
putaways may occur during the count.

**2. Blind count.** The counter must not see the system quantity. The WMS count screen
suppresses expected quantity by design — do not work around this.

**3. First count.** Record actual quantity by SKU and location.

**4. Variance check.** The WMS compares against system quantity.
- **Zero variance:** release the location, done.
- **Any variance:** proceed to recount.

**5. Blind recount** by a *different* team member.

**6. Resolution.**
- Both counts agree: accept the counted quantity, adjust the system, log the variance.
- Counts disagree: a supervisor performs the third and deciding count.

**7. Adjustment approval.**

| Variance value | Approver |
|---|---|
| Under $500 | Shift supervisor |
| $500 – $5,000 | Facility Manager |
| Above $5,000 | Facility Manager and Client Operations Manager |
| Any serialized item | Facility Manager, regardless of value |

**8. Client notification.** Required for any adjustment above $1,000, or any adjustment
on an enterprise account. Account Manager notifies within one business day.

---

## Root cause coding

Every adjustment requires a cause code. Uncoded adjustments are rejected by the WMS.

| Code | Meaning |
|---|---|
| REC-01 | Receiving count error |
| PIK-01 | Pick error, wrong quantity |
| PIK-02 | Pick error, wrong SKU |
| PUT-01 | Putaway to wrong location |
| DAM-01 | Damage not recorded |
| RET-01 | Return processed incorrectly |
| SYS-01 | System or integration error |
| UNK-01 | Unknown after investigation |

**UNK-01 use above 10% of adjustments in any month triggers a review.** A high unknown
rate means the investigation step is being skipped, not that causes are genuinely
unknowable.

---

## Reporting

- Daily: variance summary to Facility Manager
- Weekly: accuracy by class and by aisle
- Monthly: cause-code distribution, trended
- Quarterly: velocity reclassification, accuracy against the 99.5% target

## Notes

Accuracy at the **Reno facility** has run below target since Q4 2025, currently around
98.9%. Cause-code analysis shows an elevated PUT-01 rate. Under investigation as of
this revision.
