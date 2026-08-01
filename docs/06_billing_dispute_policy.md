# Policy: Billing Disputes and Adjustments

> Fictional reference document — Meridian Fulfillment Co.

**Document ID:** POL-FIN-003
**Owner:** Billing Analysts / Finance
**Last reviewed:** 2026-01-28

---

## Scope

Governs how client invoice disputes are received, investigated, and resolved.

**Dispute window:** 60 days from invoice date. Disputes raised after 60 days are
reviewed at Meridian's discretion but carry no obligation to adjust.

---

## Intake

All disputes enter through Zendesk, tagged `billing-dispute`, regardless of how the
client raised them. If a client raises a dispute verbally or in a meeting, the Account
Manager creates the ticket.

Required at intake:

- Invoice number and date
- Line items disputed
- Amount disputed
- Client's stated reason
- Whether payment is being withheld in whole or in part

---

## Investigation

Target: substantive response within **5 business days**.

### Step 1 — Reproduce the charge

Trace the disputed line back to source records before forming any view:

| Charge type | Source of truth |
|---|---|
| Receiving | WMS receipt record, ASN |
| Storage | WMS peak occupancy report for the period |
| Pick / pack | WMS order records |
| Surcharges | Carrier invoice, WMS order attributes |
| Returns | WMS returns records |

**Never respond to a dispute from the invoice alone.** The invoice is the output
being questioned.

### Step 2 — Classify

| Classification | Meaning | Typical resolution |
|---|---|---|
| **Meridian error** | Charge is incorrect | Full credit |
| **Rate misapplication** | Wrong schedule applied | Credit the difference, correct the account |
| **Client misunderstanding** | Charge correct, explanation needed | No credit, written explanation |
| **Contract ambiguity** | Terms genuinely unclear | Escalate to VP Operations |
| **Pass-through** | Carrier charge disputed | Investigate with carrier; timeline extends |

### Step 3 — Check for systemic cause

**Required on every dispute.** If the cause could affect other accounts — a rate table
error, a misconfigured surcharge, an integration issue — flag it immediately to the
Client Operations Manager before responding to the client.

*One client noticing a problem usually means several clients have it.*

---

## Most common disputes

Presented in order of frequency. Roughly 70% of disputes fall in the first three
categories, and all three are explanation issues rather than errors.

**1. Storage billed higher than expected.**
Storage bills on **peak** occupancy in the period, not average or month-end. A client
who received a large inbound mid-month and sold through by month end still pays on
the peak. This is correct per contract and is the single most disputed line.

**2. Peak surcharge appearing on the January invoice.**
The surcharge applies to the **service date**, not invoice date. Week 52 orders bill
in January carrying the week-52 surcharge.

**3. Dimensional weight charges.**
Applied per carrier tariff when DIM exceeds actual weight. Clients frequently quote
actual weight. Show the carrier calculation.

**4. Manual order entry fees.**
Triggered when orders arrive outside the integration. Usually indicates an integration
failure the client hasn't noticed — investigate the root cause, don't just explain
the fee.

**5. Long-term storage surcharge.**
Applies at 181 days at the SKU-lot level, not the account level. Clients often expect
FIFO to have cycled the stock.

---

## Approval authority

| Credit amount | Approver |
|---|---|
| Under $250 | Billing Analyst |
| $250 – $2,500 | Client Operations Manager |
| $2,501 – $10,000 | VP Operations |
| Above $10,000 | VP Operations and CFO |

Goodwill credits where no Meridian error occurred require Client Operations Manager
approval at any amount, and must be recorded as goodwill rather than error — this
distinction matters for trend reporting.

---

## Client communication

- Acknowledge within **1 business day**, always, even before investigation.
- Never state a conclusion before source records are traced.
- When the charge is correct, explain **how it was calculated**, not merely that it
  is correct. Include the specific figures.
- When Meridian erred, say so plainly, credit it, and state what changed to prevent
  recurrence.
- Never blame the client, even where the cause was on their side.

## Reporting

Monthly to Client Operations and Finance:

- Dispute count and total value, trended
- Classification distribution
- Credit total, split error versus goodwill
- Repeat disputes by client — a client disputing the same line repeatedly indicates a
  documentation or onboarding gap, not a difficult client
