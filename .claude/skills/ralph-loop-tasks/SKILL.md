name: ralph-loop-tasks
description: Define task templates for Ralph Wiggum autonomous loops. Use when running long-running, multi-step tasks that should iterate until completion.
version: 1.0.0
---

## What Is Ralph Wiggum?
A stop-hook pattern that keeps Claude Code iterating on a task until completion.
Claude works → tries to exit → stop hook blocks → re-feeds the prompt → Claude continues.
Named after The Simpsons character — persistent iteration despite setbacks.

## Pre-Defined Ralph Loop Tasks

### 1. Daily Morning Routine
/ralph-loop "Perform daily morning routine for AI Employee:
1. Check /Needs_Action for unprocessed items — process each one
2. Check /Approved for approved actions — execute each one
3. Check /Pending_Approval for expired items (>24h) — flag them
4. Sync Odoo accounting data to /Accounting/Current_Month.md
5. Update Dashboard.md with all current counts and status
6. Log all actions to /Logs/audit.jsonl

After completing ALL steps, verify:
- /Needs_Action has 0 unprocessed items
- Dashboard.md reflects current state
- audit.jsonl has entries for today

Output <promise>MORNING_COMPLETE</promise> when done." --max-iterations 10 --completion-promise "MORNING_COMPLETE"

### 2. Weekly CEO Briefing Generation
/ralph-loop "Generate weekly CEO Briefing:
1. Gather financial data from /Accounting/Current_Month.md and Odoo MCP
2. Count tasks completed this week from /Done folder
3. Gather social media metrics from MCP
4. Count emails processed this week from audit log
5. Identify bottlenecks (items stuck >48h)
6. Generate /Briefings/CEO_Briefing_{today's date}.md
7. Update Dashboard.md with briefing link

Output <promise>BRIEFING_DONE</promise> when complete." --max-iterations 15 --completion-promise "BRIEFING_DONE"

### 3. Social Media Content Batch
/ralph-loop "Generate social media content batch:
1. Read Business_Goals.md for context
2. Generate 1 Facebook post draft → save to /Pending_Approval
3. Generate 1 Instagram caption draft → save to /Pending_Approval
4. Generate 2 Twitter/X post drafts → save to /Pending_Approval
5. Each draft must follow Company_Handbook.md Social Media Rules
6. Log all drafts to /Logs/audit.jsonl

Output <promise>CONTENT_BATCH_DONE</promise> when all drafts created." --max-iterations 10 --completion-promise "CONTENT_BATCH_DONE"

## Safety Rules for Ralph Loops
- ALWAYS set --max-iterations (never run unbounded)
- Start with low iterations (10-15) and increase if needed
- NEVER include payment or deletion actions in Ralph loops
- Ralph loops should generate and prepare — not execute sensitive actions
- Monitor token usage — each iteration consumes API credits
- Cancel anytime with: /cancel-ralph