---
task: Enterprise Client Onboarding Proposal
source: manual_request
created: 2026-04-06T15:30:00
status: in_progress
priority: high
estimated_steps: 9
completed_steps: 0
---

# Plan: Enterprise Client Onboarding Proposal

## Objective

Deliver a complete, professional onboarding proposal to a new enterprise client — covering a discovery call, structured needs assessment, custom pricing, and a contract draft — aligned with NovaMind Tech Solutions' service tiers and approval rules.

## Context

This plan was triggered by a direct request to prepare a full enterprise client onboarding proposal.

NovaMind's services include: AI Automation Projects, Monthly Retainer, Training Workshops, and Fractional AI Officer. Pricing is flat-fee, project-based. Any email to external contacts and any financial/legal documents sent externally require human approval per `Company_Handbook.md`.

---

## Steps

- [ ] Step 1: Cross-reference client in Odoo
  - Action: Call `search_customers` via Odoo MCP to check if client already exists. If found, pull open invoices and account history to inform the proposal context.
  - Requires approval: no (read-only Odoo query)

- [ ] Step 2: Draft discovery call agenda
  - Action: Create `Drafts/DRAFT_discovery_call_agenda_{timestamp}.md` with structured agenda — intro, pain points, current workflow audit, AI readiness assessment, timeline/budget discussion, and next steps.
  - Requires approval: no

- [ ] Step 3: Send discovery call scheduling email to client
  - Action: Create approval request in `/Pending_Approval/email/`. Draft includes the agenda document attached, proposed 3 time slots, and a brief NovaMind intro.
  - Requires approval: **yes** (email to external contact — Company_Handbook.md Approval Rules)
  - Approval file: `Pending_Approval/email/APPROVAL_discovery_call_invite_{timestamp}.md`

- [ ] Step 4: Compile needs assessment document (post-call)
  - Action: After discovery call, create `Drafts/DRAFT_needs_assessment_{timestamp}.md` documenting: current pain points, manual workflows to automate, team size, tech stack, integration requirements, success metrics, and timeline.
  - Requires approval: no

- [ ] Step 5: Map needs to NovaMind service tiers
  - Action: Match documented needs to one or more of NovaMind's four revenue streams (AI Automation Project, Monthly Retainer, Training Workshop, Fractional AI Officer). Define scope, deliverables, and timeline for each recommended service.
  - Requires approval: no

- [ ] Step 6: Build custom pricing proposal document
  - Action: Create `Drafts/DRAFT_pricing_proposal_{timestamp}.md` with flat-fee line items, project timeline, payment schedule, and optional add-ons. Read `Accounting/Current_Month.md` first to ensure revenue targets are factored in.
  - Requires approval: no

- [ ] Step 7: CEO sign-off on pricing
  - Action: Create approval request in `/Pending_Approval/accounting/`. Present the full pricing breakdown for review before sending to client.
  - Requires approval: **yes** (financial decision — any outbound pricing commitment requires human review)
  - Approval file: `Pending_Approval/accounting/APPROVAL_pricing_signoff_{timestamp}.md`

- [ ] Step 8: Draft contract document
  - Action: Create `Drafts/DRAFT_contract_{timestamp}.md` covering: scope of work, deliverables, milestones, payment terms, IP ownership, confidentiality clause, and termination conditions. Reference approved pricing from Step 7.
  - Requires approval: no (draft only — not sent until Step 9 approved)

- [ ] Step 9: Send full proposal package to client
  - Action: Create approval request in `/Pending_Approval/email/`. Package includes: needs assessment summary, custom pricing proposal, and contract draft. Sent as a professional email with PDF attachments.
  - Requires approval: **yes** (email to external contact with legal/financial documents — Company_Handbook.md Approval Rules)
  - Approval file: `Pending_Approval/email/APPROVAL_proposal_send_{timestamp}.md`

---

## Completion Criteria

- [ ] Odoo checked — existing relationship (if any) documented
- [ ] Discovery call agenda drafted and scheduling email sent (approved)
- [ ] Needs assessment document completed and filed in `/Drafts`
- [ ] Custom pricing proposal drafted and CEO-approved
- [ ] Contract draft created referencing approved pricing
- [ ] Full proposal package sent to client (approved)
- [ ] Audit entry logged to `/Logs/audit.jsonl`
- [ ] Dashboard updated with plan completion

---

## Approval Checkpoints Summary

| Step | Approval File Location | Reason |
|------|----------------------|--------|
| Step 3 | `/Pending_Approval/email/` | Email to external contact |
| Step 7 | `/Pending_Approval/accounting/` | Financial commitment sign-off |
| Step 9 | `/Pending_Approval/email/` | Email with legal/financial docs to external |

---

## Notes

- Do NOT send any email or financial document without a file appearing in `/Approved`
- Pricing must reflect flat-fee model (no hidden hourly billing — NovaMind differentiator)
- Never quote financial figures from memory — always read `Accounting/Current_Month.md` first
- Client names must not appear in social media posts without written permission
