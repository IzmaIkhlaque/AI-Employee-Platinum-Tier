# Social Media API Setup Guide

> Configures the `social-media` MCP server (`mcp_servers/social_media_server.py`).
> All credentials go in `AI_Employee_Vault/.env` — never commit that file.

---

## Quick Start — Dry-Run Mode (No tokens needed)

If you don't have real API access yet, the server works out of the box:

```env
# .env — no social tokens needed
SOCIAL_DRY_RUN=false   # leave false — dry-run activates automatically for missing tokens
```

Any platform missing its token automatically falls back to dry-run. You can demo all
workflows — content generation, approval routing, audit logging — without live API access.
Judges evaluate architecture and workflow, not whether you have a live Facebook token.

Verify the current state anytime:

```bash
python -c "
from mcp_servers.social_media_server import social_media_status
import json
print(json.dumps(json.loads(social_media_status()), indent=2))
"
```

---

## Facebook Page API Setup

### Prerequisites
- A Facebook account
- A **Facebook Page** (not a personal profile) — create one free at facebook.com/pages/create
- A Meta Developer account (free)

### Step 1 — Create a Meta Developer App

1. Go to https://developers.facebook.com
2. Click **My Apps → Create App**
3. Select app type: **Business**
4. Enter app name (e.g. `AI Employee`) and contact email
5. Click **Create App**

### Step 2 — Add the Pages Product

1. In your app dashboard, click **Add Product**
2. Find **Facebook Login for Business** → click **Set Up**
3. Also add **Pages API** if listed separately

### Step 3 — Generate a Page Access Token

1. In the left sidebar, go to **Tools → Graph API Explorer**
2. Top-right dropdown — select your app
3. Under **User or Page** dropdown — switch from User Token to **Page Token**
4. Select your Facebook Page from the list
5. Click **Add a Permission** and add both:
   - `pages_manage_posts`
   - `pages_read_engagement`
6. Click **Generate Access Token** — approve the dialog
7. Copy the token shown

> **Note:** Tokens from Graph API Explorer expire in ~1 hour. For production,
> use the [Token Debugger](https://developers.facebook.com/tools/debug/accesstoken/)
> to extend to a long-lived token (60 days), or set up a System User token
> for a non-expiring token.

### Step 4 — Get Your Page ID

**Option A — From your Page:**
1. Go to your Facebook Page
2. Click **About** in the left sidebar
3. Scroll to the bottom — **Page ID** is listed there

**Option B — Via Graph API Explorer:**
```
GET /me/accounts
```
Returns a list of pages you manage with their IDs.

### Step 5 — Save to .env

```env
FB_PAGE_ACCESS_TOKEN=EAABwzLixnjYBO...  (long token string)
FB_PAGE_ID=123456789012345
```

### Step 6 — Verify

```bash
python -c "
from mcp_servers.social_media_server import get_facebook_posts
import json
result = json.loads(get_facebook_posts(limit=3))
print('Status:', result['status'])
print('Posts found:', result.get('count', len(result.get('posts', []))))
"
```

A non-dry-run response with `status: ok` means Facebook is connected.

---

## Instagram Business API Setup

### Prerequisites
- An **Instagram Business** or **Creator** account (not a personal account)
- That Instagram account **linked to a Facebook Page** you manage
- The Facebook app and Page Access Token from the section above

### Step 1 — Link Instagram to Your Facebook Page
zz
1. On your Facebook Page → **Settings → Linked Accounts**
2. Select **Instagram** → follow prompts to connect your Business account
3. Confirm the link is shown as active

### Step 2 — Get Additional Permissions

1. Back in **Graph API Explorer**, regenerate your Page Access Token with these
   permissions added:
   - `instagram_basic`
   - `instagram_content_publish`
   - `pages_show_list`

### Step 3 — Find Your Instagram User ID

Run these two calls in Graph API Explorer (or curl):

**Call 1 — get your Page's numeric ID:**
```
GET /me/accounts
```
Note the `id` field for your page (same as `FB_PAGE_ID`).

**Call 2 — get the linked Instagram Business Account ID:**
```
GET /{page_id}?fields=instagram_business_account
```
The response looks like:
```json
{
  "instagram_business_account": {
    "id": "17841400000000000"
  },
  "id": "123456789012345"
}
```
The `instagram_business_account.id` value is your `IG_USER_ID`.

### Step 4 — Save to .env

```env
# FB_PAGE_ACCESS_TOKEN is shared with Facebook — same token
IG_USER_ID=17841400000000000
```

### Step 5 — Verify

```bash
python -c "
from mcp_servers.social_media_server import get_instagram_posts
import json
result = json.loads(get_instagram_posts(limit=3))
print('Status:', result['status'])
print('Posts found:', result.get('count', len(result.get('posts', []))))
"
```

### Important Notes for Instagram Posting

- `post_to_instagram` requires a **publicly accessible HTTPS image URL**
- The image must be hosted somewhere reachable from the internet (not localhost)
- For the hackathon demo, use any public image URL (e.g. from Unsplash or your CDN)
- Supported formats: JPEG only for feed posts; minimum 320×320px
- Instagram API does not support text-only posts — an image is always required

---

## Twitter / X API Setup

### Prerequisites
- A Twitter/X account
- A phone number verified on the account (required for developer access)

### Step 1 — Apply for Developer Access

1. Go to https://developer.x.com
2. Click **Sign in** → log in with your Twitter account
3. Click **Apply** for the developer portal
4. Select **Free** tier (sufficient for posting and reading)
5. Answer the use-case questions — describe the AI automation project
6. Accept the developer agreement

> Free tier allows: 1,500 tweets/month write, basic read access.

### Step 2 — Create a Project and App

1. In the developer portal → **Projects & Apps → New Project**
2. Name: `AI Employee`
3. Use case: `Making a bot` or `Automating and bot`
4. Create a new App inside the project
5. App name: `ai-employee-mcp`

### Step 3 — Set App Permissions

1. Go to your App → **Settings → App Permissions**
2. Change from `Read` to **Read and Write**
3. Save

> You MUST set Write permissions before generating tokens, or the tokens will be
> read-only and `post_to_twitter` will return a 403 error.

### Step 4 — Generate OAuth 1.0a Keys

1. Go to your App → **Keys and Tokens**
2. Under **Consumer Keys**: click **Regenerate** → copy:
   - **API Key** → `TWITTER_API_KEY`
   - **API Key Secret** → `TWITTER_API_SECRET`
3. Under **Authentication Tokens**: click **Generate** → copy:
   - **Access Token** → `TWITTER_ACCESS_TOKEN`
   - **Access Token Secret** → `TWITTER_ACCESS_SECRET`

> Save these immediately — secrets are only shown once.

### Step 5 — Save to .env

```env
TWITTER_API_KEY=xxxxxxxxxxxxxxxxxxx
TWITTER_API_SECRET=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWITTER_ACCESS_TOKEN=000000000-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWITTER_ACCESS_SECRET=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### Step 6 — Verify

```bash
python -c "
from mcp_servers.social_media_server import get_twitter_posts
import json
result = json.loads(get_twitter_posts(count=3))
print('Status:', result['status'])
print('Tweets found:', result.get('count', len(result.get('tweets', []))))
"
```

---

## Dry-Run Mode Reference

When any platform token is missing, that platform automatically operates in dry-run:

| Behaviour | Live mode | Dry-run mode |
|-----------|-----------|-------------|
| `post_to_*` | Calls real API | Logs to `audit.jsonl`, saves to `Social_Media/` |
| `get_*` | Returns real posts | Returns realistic demo data |
| `generate_social_summary` | Real engagement metrics | Demo engagement metrics |
| Audit log entry | `"dry_run": false` | `"dry_run": true` |

To force all platforms into dry-run regardless of tokens:

```env
SOCIAL_DRY_RUN=true
```

To check current mode per platform:

```bash
python -c "
from mcp_servers.social_media_server import social_media_status
import json; print(json.dumps(json.loads(social_media_status()), indent=2))
"
```

---

## Troubleshooting

### "Error 190 — Access token has expired"

Facebook Page Access tokens from Graph API Explorer expire in ~1 hour.
Options:
1. **Quick fix:** regenerate a fresh token in Graph API Explorer
2. **Proper fix:** exchange for a long-lived token (60 days):
   ```
   GET /oauth/access_token
     ?grant_type=fb_exchange_token
     &client_id={app_id}
     &client_secret={app_secret}
     &fb_exchange_token={short_lived_token}
   ```
3. **Permanent fix:** create a System User in Meta Business Suite with a
   non-expiring token

### "Error 10 — Application does not have permission"

The token was generated without the required permissions.
- Go back to Graph API Explorer
- Add `pages_manage_posts` and `pages_read_engagement`
- Regenerate the token

### "Instagram: media container creation returned no id"

Common causes:
- `image_url` is not publicly accessible (localhost URLs won't work)
- Image format is not JPEG
- Image dimensions are below 320×320px
- The Instagram account is not properly linked to the Facebook Page

### "Twitter 403 — Client Forbidden"

The app's permissions are set to Read-only. Fix:
1. Go to developer.x.com → your App → Settings → App Permissions
2. Change to **Read and Write**
3. **Regenerate** the Access Token and Secret (old tokens retain the old permissions)
4. Update `.env` with the new tokens

### "Twitter 429 — Too Many Requests"

Free tier limit reached (1,500 tweets/month or 50 requests/15 min window).
Wait 15 minutes before retrying read operations. Reduce posting frequency.

---

## Reference

| Variable | Platform | Where to find it |
|----------|----------|-----------------|
| `FB_PAGE_ACCESS_TOKEN` | Facebook + Instagram | Graph API Explorer |
| `FB_PAGE_ID` | Facebook | Page About section or `/me/accounts` |
| `IG_USER_ID` | Instagram | `GET /{page_id}?fields=instagram_business_account` |
| `TWITTER_API_KEY` | Twitter/X | App → Keys and Tokens → Consumer Keys |
| `TWITTER_API_SECRET` | Twitter/X | App → Keys and Tokens → Consumer Keys |
| `TWITTER_ACCESS_TOKEN` | Twitter/X | App → Keys and Tokens → Authentication Tokens |
| `TWITTER_ACCESS_SECRET` | Twitter/X | App → Keys and Tokens → Authentication Tokens |

**MCP server:** `mcp_servers/social_media_server.py`
**Skill:** `.claude/skills/social-media-manager/SKILL.md`
**Post records:** `/Social_Media/{Facebook|Instagram|Twitter}/POST_{ts}.json`
**Audit log:** `/Logs/audit.jsonl`
**Error log:** `/Logs/errors.jsonl`
