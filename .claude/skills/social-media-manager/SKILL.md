---
name: social-media-manager
description: Manage social media posting across Facebook, Instagram, and Twitter/X. Generate content, schedule posts, and create engagement summaries. All posts require HITL approval.
version: 1.0.0
---

# Social Media Manager Skill

Generates platform-specific content, routes it through HITL approval, posts via the
`social-media` MCP server, and produces weekly engagement summaries.

---

## MCP Server

**Server:** `mcp_servers/social_media_server.py`
**Registered as:** `social-media` in Claude Code local config

| Tool | Approval | Purpose |
|------|----------|---------|
| `social_media_status` | Auto | Check which platforms are live vs dry-run |
| `get_facebook_posts` | Auto | Read recent Facebook posts |
| `get_instagram_posts` | Auto | Read recent Instagram posts |
| `get_twitter_posts` | Auto | Read recent tweets |
| `post_to_facebook` | **HITL required** | Publish to Facebook Page |
| `post_to_instagram` | **HITL required** | Publish to Instagram Business |
| `post_to_twitter` | **HITL required** | Publish a tweet |
| `generate_social_summary` | Auto | Markdown engagement report |

---

## Content Generation

When asked to create social media content:

1. **Read context files**
   - `Business_Goals.md` — company value proposition, target audience, tone
   - `Company_Handbook.md` → Social Media Rules — per-platform limits and restrictions

2. **Generate platform-specific content** following these specs:

   ### Facebook
   - Style: Professional, longer-form, business updates
   - Length: 100–500 words
   - Structure: Hook → Value content (2–4 paragraphs) → CTA
   - No hashtags required (1–2 max if relevant)
   - Never post financial figures or client names without permission

   ### Instagram
   - Style: Visual-first — write the caption to accompany an image
   - Length: Max 2,200 characters
   - Include: 5–10 relevant hashtags at the end
   - Include: Image description note (what image would complement this post)
   - Never post financial details publicly

   ### Twitter/X
   - Style: Short, punchy, industry insight or thought leadership
   - Length: Max 280 characters (hard limit — count before saving)
   - 1–2 hashtags maximum
   - Can be a thread opener — mark with `[1/N]` if continuation needed

3. **Save ALL drafts to `/Pending_Approval`** — never write directly to `/Social_Media`

   File naming: `APPROVAL_social_post_{platform}_{YYYYMMDD_HHMMSS}.md`

   Required frontmatter on every approval file:
   ```yaml
   ---
   type: approval_request
   action: social_post
   platform: facebook|instagram|twitter
   created: 2026-03-02T09:00:00
   status: pending
   content_preview: "First 80 characters of the post..."
   ---
   ```

4. **Update Dashboard.md** — increment Pending Approval count

5. **STOP** — never auto-post. Wait for human to move file to `/Approved`.

---

## Posting Workflow (after human approval)

Only run this after confirming the file exists in `/Approved`:

1. **Read** the approved file from `/Approved`
2. **Confirm** frontmatter `action: social_post` and extract `platform` field
3. **Check** `social_media_status` — confirm the target platform is available
4. **Call the correct MCP tool:**
   - Facebook → `post_to_facebook(message=..., page_id=...)`
   - Instagram → `post_to_instagram(caption=..., image_url=...)`
   - Twitter → `post_to_twitter(text=...)`
5. **On success:**
   - Log to `/Logs/audit.jsonl`:
     ```json
     {"ts": "...", "action": "social_post", "platform": "...", "post_id": "...", "status": "posted"}
     ```
   - Post record is auto-saved by MCP to `/Social_Media/{Platform}/POST_{ts}.json`
   - Move approved file to `/Done` — rename with `DONE_` prefix
   - Update Dashboard.md:
     - Decrement Pending Approval count
     - Update Social Media Status table with new Last Post date
     - Add entry to Recent Activity
6. **On error (non-rate-limit):**
   - Log to `/Logs/errors.jsonl`
   - Do NOT retry automatically — report the error to the human

---

## Weekly Summary Generation

When triggered (Sunday evening, on-demand, or as part of CEO Briefing):

1. Call `generate_social_summary(platform="all", days=7)` from the MCP server
2. Supplement with any manual context from `/Social_Media/*/POST_*.json` records
3. Calculate additional metrics:
   - Total posts across all platforms
   - Average engagement rate per platform
   - Best performing post (highest likes + comments combined)
   - Platforms with zero posts (flag as inactive)
4. Save summary to `/Social_Media/weekly_summary_{YYYYMMDD}.md`
5. Update Dashboard.md → Social Media Status table
6. If part of CEO Briefing: include as a section in `/Briefings/CEO_Briefing_{date}.md`

---

## Error Handling

| Error | Action |
|-------|--------|
| `429` Rate limit | Log to `errors.jsonl`, note platform and retry-after time, do NOT retry automatically |
| `401` / `403` Auth expired | Log error, create `URGENT_social_auth_expired_{platform}_{ts}.md` in `/Needs_Action` |
| Platform unavailable / timeout | Log error, skip that platform, continue with remaining platforms |
| Post content too long | Trim to limit, re-save draft, notify human to re-approve |
| dry_run returned | Note in audit log, update Dashboard with dry-run indicator |

---

## Approval File Reference

**Location:** `/Pending_Approval/APPROVAL_social_post_{platform}_{YYYYMMDD_HHMMSS}.md`

**Full template:**
```markdown
---
type: approval_request
action: social_post
platform: twitter
created: 2026-03-02T09:00:00
status: pending
content_preview: "AI is not replacing jobs — it's eliminating..."
---

# Approval Request — Twitter Post

**Platform:** Twitter/X
**Created:** 2026-03-02 09:00:00
**Status:** ⏳ Awaiting Review

---

## Post Content

AI is not replacing jobs — it's eliminating the boring parts.
Here's what our AI Employee handled today ↓

#AI #automation #productivity

---

## Checklist

- [ ] Content aligns with Business_Goals.md
- [ ] Follows Social Media Rules (Company_Handbook.md)
- [ ] Character count within limits (Twitter: 280)
- [ ] No financial details, no client names
- [ ] Approved by human before posting

## Actions

Move this file to:
- `/Approved` → Claude will post via MCP
- `/Rejected` → Claude will archive and not retry
```

---

## Rules Summary

- **NEVER auto-post** — every post must pass through `/Pending_Approval` → `/Approved`
- **Read operations** (`get_*`, `generate_*`, `social_media_status`): auto-approved
- **Write operations** (`post_to_*`): only after file confirmed in `/Approved`
- Always log every post attempt to `/Logs/audit.jsonl` (success or dry-run)
- Always log every error to `/Logs/errors.jsonl`
- Daily limits (from `Company_Handbook.md`): Facebook 1/day, Instagram 1/day, Twitter 3/day
- Never post financial details or client names without written permission
