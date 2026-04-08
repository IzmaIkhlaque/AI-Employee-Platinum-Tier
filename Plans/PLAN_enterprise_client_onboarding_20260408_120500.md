---
task: Enterprise Client Onboarding Proposal
source: Needs_Action/email/EMAIL_client_inquiry_live.md
created: 2026-04-08T12:05:00
status: in_progress
estimated_steps: 9
completed_steps: 1
---

# Plan: Enterprise Client Onboarding Proposal

## Objective

Deliver a complete, professional onboarding proposal to a new enterprise client — covering a scheduled discovery call, structured needs assessment, custom pricing package, and a ready-to-sign contract draft.

## Context

This plan was triggered by: `Needs_Action/email/EMAIL_client_inquiry_live.md`

**Client:** Ahmed Khan, CEO — Khan Industries (50-person manufacturing company, Lahore)
**Request:** Pricing breakdown and case study for AI automation services
**Status:** Initial reply drafted → `Pending_Approval/email/PENDING_email_reply_ahmed_khan_20260408_120000.md`
**Odoo:** New prospect — not yet in Odoo. Add after first contact confirmed.

---

## Steps

- [x] Step 1: Detect and classify inbound inquiry  ✅ Completed 2026-04-08T12:00:00
  - Requires approval: no
  - File: `Needs_Action/email/EMAIL_client_inquiry_live.md` → classified HIGH priority

- [ ] Step 2: Send initial response email (discovery questions + service overview)
  - Requires approval: **yes** (email to external contact)
  - Approval file: `Pending_Approval/email/PENDING_email_reply_ahmed_khan_20260408_120000.md`
  - Action: Human moves to `/Approved` → Local Agent sends via Gmail MCP
  - Blocker: Waiting for human approval

- [ ] Step 3: Schedule discovery call
  - Requires approval: **yes** (calendar invite + follow-up email to client)
  - Once client replies with availability, create Google Calendar event via `gcal_create_event`
  - Draft confirmation email to client with Zoom/Meet link
  - Create approval file: `Pending_Approval/email/PENDING_discovery_call_invite_ahmed_khan.md`

- [ ] Step 4: Conduct discovery call — capture needs assessment notes
  - Requires approval: no (internal document)
  - Create `Plans/DISCOVERY_NOTES_khan_industries_{timestamp}.md` with:
    - Current pain points (manual processes, bottlenecks)
    - Existing tech stack (ERP, CRM, spreadsheets)
    - Team size and tech-readiness
    - Budget range and timeline
    - Success criteria from client's perspective

- [ ] Step 5: Run Odoo cross-reference and research
  - Requires approval: no (read-only)
  - Call `odoo search_customers` — confirm still a new prospect
  - Research manufacturing-sector AI use cases relevant to Khan Industries
  - Check `Done/DONE_EMAIL_service_inquiry_20260405_143000.md` for comparable client precedent

- [ ] Step 6: Build custom pricing proposal document
  - Requires approval: no (internal draft)
  - Create `Drafts/PROPOSAL_khan_industries_{timestamp}.md`
  - Structure:
    - Executive Summary (1 page)
    - Recommended Package (Phase 1 + Phase 2 options)
    - Pricing Table (flat-fee, no hourly billing per NovaMind policy)
    - ROI estimate for manufacturing workflow automation
    - Case Study (anonymized comparable client)
    - Timeline and Milestones
  - Reference: `Business_Goals.md` revenue streams and value proposition

- [ ] Step 7: Send pricing proposal to client
  - Requires approval: **yes** (email with pricing to external contact)
  - Create approval file: `Pending_Approval/email/PENDING_proposal_email_khan_industries.md`
  - Attach or inline the proposal document
  - Human reviews → moves to `/Approved` → Local Agent sends via Gmail MCP

- [ ] Step 8: Draft contract
  - Requires approval: no (internal draft)
  - Create `Drafts/CONTRACT_khan_industries_{timestamp}.md`
  - Sections:
    - Scope of Work (based on agreed proposal)
    - Payment Terms (milestone-based, flat-fee)
    - Delivery Timeline
    - IP ownership (client owns deliverables)
    - Support / Retainer terms (optional add-on)
    - Governing Law (Pakistan)
  - Flag for human legal review before sending

- [ ] Step 9: Send contract draft for client review
  - Requires approval: **yes** (contract to external contact — financial document)
  - Create approval file: `Pending_Approval/email/PENDING_contract_email_khan_industries.md`
  - Human reviews contract + email → moves to `/Approved` → Local Agent sends
  - Add Odoo write request: create Khan Industries as customer record
    - Create `Pending_Approval/accounting/PENDING_odoo_new_customer_khan_industries.md`

---

## Completion Criteria

- [ ] Discovery call completed and notes documented
- [ ] Needs assessment captured in structured document
- [ ] Custom pricing proposal sent to client (approved + sent)
- [ ] Contract draft sent to client (approved + sent)
- [ ] Khan Industries added to Odoo as a customer
- [ ] All emails logged in `Logs/audit.jsonl`
- [ ] Dashboard updated with all activity
- [ ] Source email item archived in `/Done`

---

## Approval Checkpoints Summary

| Step | Action | Approval File |
|------|--------|---------------|
| Step 2 | Send initial reply | `Pending_Approval/email/PENDING_email_reply_ahmed_khan_20260408_120000.md` |
| Step 3 | Send discovery call invite | `Pending_Approval/email/PENDING_discovery_call_invite_ahmed_khan.md` |
| Step 7 | Send pricing proposal | `Pending_Approval/email/PENDING_proposal_email_khan_industries.md` |
| Step 8 | Human legal review of contract | Manual review required |
| Step 9 | Send contract draft | `Pending_Approval/email/PENDING_contract_email_khan_industries.md` |
| Step 9 | Add to Odoo as customer | `Pending_Approval/accounting/PENDING_odoo_new_customer_khan_industries.md` |

---

## Notes

- **Target conversion:** Per `Business_Goals.md`, proposal conversion rate goal is ≥ 30%. Personalize at every step.
- **Response time SLA:** Email responses must be < 4 hours (Business_Goals.md).
- **Pricing policy:** Flat-fee only — no hourly billing. Be explicit in the proposal.
- **Client privacy:** Do not mention Khan Industries in any social media post without written permission.
- **Odoo write rule:** Do not add to Odoo until client confirms engagement — HITL required for any Odoo write.
