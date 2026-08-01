# SOP: Receiving Discrepancies

> Fictional reference document — Meridian Fulfillment Co.

**Document ID:** SOP-REC-004
**Owner:** Client Operations Manager
**Last reviewed:** 2026-05-14
**Applies to:** All facilities

---

## Trigger conditions

Follow this procedure when any of the following occurs at receiving:

- Counted quantity does not match the ASN (Advance Shipping Notice) quantity
- Received SKUs are not listed on the ASN
- Product arrives damaged in excess of the 2% acceptable damage threshold
- Lot or expiry data is missing on a lot-tracked SKU
- No ASN exists for an arriving shipment

If none of these apply, use SOP-REC-001 (Standard Receiving).

---

## Step 1 — Quarantine before recording

Move the affected shipment to the discrepancy hold area. **Do not put away and do
not record inventory** until the discrepancy is resolved.

*Why:* once stock enters the sellable pool, isolating the variance requires a full
cycle count. Quarantine first is faster in every case.

## Step 2 — Document the physical state

In the WMS discrepancy module, record:

- ASN number and PO number
- Carrier and tracking or PRO number
- Expected quantity by SKU
- Actual counted quantity by SKU
- Condition of outer packaging (photos required)
- Seal intact — yes or no
- Pallet count received versus expected

**Photos are mandatory** for any damage or seal-integrity issue. Carrier claims are
routinely denied without them.

## Step 3 — Recount

A second team member performs an independent recount before the discrepancy is
escalated. Do not tell them the first count.

*Why:* roughly a third of reported discrepancies at Meridian resolve at recount.
Blind recount prevents anchoring.

Record both counts in the WMS.

## Step 4 — Classify

| Classification | Definition | Route to |
|---|---|---|
| **Count variance** | Quantity mismatch, packaging intact | Step 5 |
| **Transit damage** | Visible damage, seal intact | Step 6 |
| **Transit loss** | Seal broken or pallet count short | Step 6 |
| **Documentation error** | ASN wrong, product correct | Step 7 |
| **Unexpected receipt** | No ASN on file | Step 8 |

## Step 5 — Count variance

- **Variance under 2% and under 50 units:** record actual, note the variance, notify
  the account manager by end of day. No client approval needed.
- **Variance at or above 2%, or 50+ units:** hold. Account manager contacts client
  for written confirmation before putaway.
- **Overage of any size:** hold entirely. Never absorb an unexplained overage into
  sellable inventory — it is frequently another client's stock.

## Step 6 — Damage or loss

1. File the carrier claim within **48 hours**. Claims outside this window are
   generally denied.
2. Attach all photos, the BOL, and both counts.
3. Notify the account manager, who informs the client within one business day.
4. Move damaged product to the damage disposition area pending client instruction.
5. Log the claim number in the WMS discrepancy record.

## Step 7 — Documentation error

If the physical product is correct but the ASN is wrong, the Onboarding or Account
Manager contacts the client to have the ASN corrected and resubmitted. Do not
manually override the ASN in the WMS — overrides break downstream billing reconciliation.

## Step 8 — Unexpected receipt

1. Do not refuse the shipment unless it is clearly misdelivered to the wrong facility.
2. Quarantine and attempt identification via carton markings, packing list, or SKU
   lookup across active clients.
3. If identified, contact that client's account manager to create a retroactive ASN.
4. If unidentified after 5 business days, escalate to the Client Operations Manager.

---

## Escalate immediately, regardless of step

- Variance value exceeds **$10,000**
- Any enterprise-tier client
- Seal broken with quantity shortage — treat as potential theft, notify the Facility
  Manager and Client Operations Manager the same day
- Any suspicion of internal loss

## Definition of done

- Discrepancy record closed in the WMS with classification and resolution
- Client notified where required, with confirmation logged
- Carrier claim filed where applicable, claim number recorded
- Inventory reflects actual counted quantity
- Product released from quarantine or dispositioned

## Related documents

SOP-REC-001 (Standard Receiving) · SOP-INV-002 (Cycle Counts) · POL-ESC-001 (Escalation Matrix)
