# Escalation Matrix

> Fictional reference document — Meridian Fulfillment Co.

**Document ID:** POL-ESC-001
**Owner:** Client Operations Manager
**Last reviewed:** 2026-04-02

---

## Severity definitions

| Severity | Definition | Examples |
|---|---|---|
| **S1 — Critical** | Client's business is stopped, or a systemic failure affects multiple clients | Facility outage, WMS down, all orders for a client failing, security incident |
| **S2 — High** | Significant impact with a workaround, or one enterprise client materially affected | SLA breach in progress, integration failure, inventory unavailable for a launch |
| **S3 — Medium** | Contained impact, no immediate revenue risk | Single order issue, billing dispute, reporting discrepancy |
| **S4 — Low** | Question or request, no operational impact | Rate inquiry, report request, general question |

---

## Response and resolution targets

| Severity | First response | Update cadence | Target resolution |
|---|---|---|---|
| S1 | 30 minutes | Hourly | 4 hours |
| S2 | 2 hours | Every 4 hours | 1 business day |
| S3 | 1 business day | Daily | 3 business days |
| S4 | 2 business days | — | 5 business days |

Enterprise-tier clients receive one severity level of priority handling — an S3
from an enterprise client is worked at S2 targets.

---

## Escalation path

**Level 1 — Client Support Specialist / Account Manager**
Handles S3 and S4. Escalates when the target response time is at risk, or immediately
for anything meeting S1 or S2 criteria.

**Level 2 — Senior Account Manager**
Handles S2. Owns client communication for enterprise accounts. Escalates S1 immediately.

**Level 3 — Client Operations Manager**
Handles S1. Coordinates across facilities and functions. Authorizes service credits
up to $2,500.

**Level 4 — VP Operations**
Systemic issues, multi-client impact, service credits above $2,500, any potential
contract or legal exposure.

---

## Escalate immediately, bypassing sequence

Contact the Client Operations Manager directly, regardless of your level, for:

- Any suspected theft or internal loss
- Any data or security incident
- Any client threatening contract termination
- Any injury or safety incident affecting service
- Any regulatory or compliance matter (hazmat, customs, FDA-regulated product)
- Media or social media attention

Do not wait for the normal path in these cases.

---

## Communication rules

**Who contacts the client**

- S1 and S2: Senior Account Manager or above. Never a Support Specialist.
- S3 and S4: assigned Account Manager or the pooled queue.

**What may be committed without approval**

- Acknowledgement, investigation status, and factual updates: always.
- Resolution timeframe: only when the fix is confirmed and scheduled.
- Service credits: never below Level 3.
- Root cause: never before investigation concludes. State that it is under
  investigation instead.

**Written record**

Every S1 and S2 requires a written incident summary in Zendesk within 24 hours of
resolution: timeline, cause, actions taken, client communications, and preventive
follow-up.

---

## Post-incident review

Required for all S1 incidents and any S2 that breached its resolution target.

Held within 5 business days. Attended by the Client Operations Manager, the owning
Account Manager, and the relevant Facility Manager.

Output: a written review including whether existing SOPs covered the scenario, and
if not, who owns writing the new one and by when.
