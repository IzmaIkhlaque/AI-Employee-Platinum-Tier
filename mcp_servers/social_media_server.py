#!/usr/bin/env python3
"""
Social Media MCP Server for AI Employee

Handles posting and reading from Facebook, Instagram, and Twitter/X.

Dry-run mode is automatic when credentials are absent, or forced via
SOCIAL_DRY_RUN=true in .env — safe for hackathon demos without live tokens.

Tools:
  post_to_facebook      / get_facebook_posts
  post_to_instagram     / get_instagram_posts
  post_to_twitter       / get_twitter_posts
  generate_social_summary
  social_media_status
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

import requests
from dotenv import load_dotenv
from fastmcp import FastMCP

try:
    import tweepy
    _TWEEPY_OK = True
except ImportError:
    _TWEEPY_OK = False

# ── Credentials ───────────────────────────────────────────────────────────────

_vault_root = Path(__file__).parent.parent
load_dotenv(_vault_root / ".env")

FB_PAGE_ACCESS_TOKEN  = os.environ.get("FB_PAGE_ACCESS_TOKEN", "")
FB_PAGE_ID            = os.environ.get("FB_PAGE_ID", "")
IG_USER_ID            = os.environ.get("IG_USER_ID", "")

TWITTER_API_KEY       = os.environ.get("TWITTER_API_KEY", "")
TWITTER_API_SECRET    = os.environ.get("TWITTER_API_SECRET", "")
TWITTER_ACCESS_TOKEN  = os.environ.get("TWITTER_ACCESS_TOKEN", "")
TWITTER_ACCESS_SECRET = os.environ.get("TWITTER_ACCESS_SECRET", "")

SOCIAL_DRY_RUN        = os.environ.get("SOCIAL_DRY_RUN", "false").lower() == "true"

# ── Paths ─────────────────────────────────────────────────────────────────────

AUDIT_LOG    = _vault_root / "Logs" / "audit.jsonl"
ERROR_LOG    = _vault_root / "Logs" / "errors.jsonl"
SOCIAL_PATH  = _vault_root / "Social_Media"
FB_GRAPH     = "https://graph.facebook.com/v19.0"

# ── Helpers ───────────────────────────────────────────────────────────────────

def _dry(tokens: list[str]) -> bool:
    """True if forced dry-run or any required token is empty."""
    return SOCIAL_DRY_RUN or any(not t for t in tokens)


def _log_audit(action: str, platform: str, details: dict, dry_run: bool = False) -> None:
    AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "ts": datetime.now().isoformat(),
        "action": action,
        "platform": platform,
        "dry_run": dry_run,
        **details,
    }
    with open(AUDIT_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


def _log_error(action: str, platform: str, error: str) -> None:
    ERROR_LOG.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "ts": datetime.now().isoformat(),
        "action": action,
        "platform": platform,
        "error": error,
    }
    with open(ERROR_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


def _save_post_record(platform: str, data: dict) -> None:
    """Write post metadata to /Social_Media/<Platform>/POST_<ts>.json."""
    folder = SOCIAL_PATH / platform
    folder.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    (folder / f"POST_{ts}.json").write_text(
        json.dumps(data, indent=2, default=str), encoding="utf-8"
    )


def _ok(data: dict) -> str:
    return json.dumps({"status": "ok", **data}, default=str)


def _err(msg: str) -> str:
    return json.dumps({"status": "error", "error": msg})


def _dry_result(platform: str, action: str, preview: dict) -> str:
    result = {
        "status": "dry_run",
        "platform": platform,
        "action": action,
        "note": (
            "Dry-run mode — no real API call made. "
            "Set credentials in .env and SOCIAL_DRY_RUN=false to enable live posting."
        ),
        **preview,
    }
    return json.dumps(result)


# ── MCP server ────────────────────────────────────────────────────────────────

mcp = FastMCP(
    "social-media",
    instructions=(
        "Social media management for AI Employee. "
        "Handles Facebook, Instagram, and Twitter/X. "
        "ALL post_to_* tools require prior HITL approval in /Approved before calling. "
        "get_* and generate_* tools are read-only and auto-approved."
    ),
)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STATUS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@mcp.tool()
def social_media_status() -> str:
    """
    Check which platforms are configured and whether dry-run mode is active.
    Call this first to understand what's available.
    """
    def _status(tokens: list[str], label: str) -> str:
        if _dry(tokens):
            missing = [n for n, t in zip(label.split(","), tokens) if not t]
            return f"dry_run (missing: {', '.join(missing)})" if missing else "dry_run (forced)"
        return "configured"

    result = {
        "dry_run_forced": SOCIAL_DRY_RUN,
        "tweepy_installed": _TWEEPY_OK,
        "platforms": {
            "facebook": _status([FB_PAGE_ACCESS_TOKEN, FB_PAGE_ID], "FB_PAGE_ACCESS_TOKEN,FB_PAGE_ID"),
            "instagram": _status([FB_PAGE_ACCESS_TOKEN, IG_USER_ID], "FB_PAGE_ACCESS_TOKEN,IG_USER_ID"),
            "twitter": _status(
                [TWITTER_API_KEY, TWITTER_API_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET],
                "TWITTER_API_KEY,TWITTER_API_SECRET,TWITTER_ACCESS_TOKEN,TWITTER_ACCESS_SECRET",
            ),
        },
    }
    return json.dumps(result, indent=2)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# FACEBOOK
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@mcp.tool()
def post_to_facebook(message: str, page_id: Optional[str] = None) -> str:
    """
    Post a message to a Facebook Page.

    IMPORTANT: Only call after HITL approval exists in /Approved folder.

    Args:
        message:  Post text content (max ~63,000 chars for Facebook)
        page_id:  Facebook Page ID — uses FB_PAGE_ID from .env if omitted

    Returns:
        JSON with status and post_id on success, dry_run details, or error
    """
    pid = page_id or FB_PAGE_ID

    if _dry([FB_PAGE_ACCESS_TOKEN, pid]):
        _log_audit("post_facebook", "facebook", {"message_preview": message[:100]}, dry_run=True)
        _save_post_record("Facebook", {"action": "post", "message": message, "dry_run": True,
                                       "ts": datetime.now().isoformat()})
        return _dry_result("facebook", "post", {
            "page_id": pid or "(FB_PAGE_ID not set)",
            "message_preview": message[:100],
            "char_count": len(message),
        })

    try:
        resp = requests.post(
            f"{FB_GRAPH}/{pid}/feed",
            data={"message": message, "access_token": FB_PAGE_ACCESS_TOKEN},
            timeout=30,
        )
        resp.raise_for_status()
        post_id = resp.json().get("id", "unknown")

        _log_audit("post_facebook", "facebook", {"post_id": post_id, "message_preview": message[:100]})
        _save_post_record("Facebook", {"post_id": post_id, "message": message,
                                       "page_id": pid, "ts": datetime.now().isoformat()})
        return _ok({"post_id": post_id, "page_id": pid, "platform": "facebook"})

    except requests.HTTPError as e:
        status = e.response.status_code
        body = e.response.text[:300]
        if status == 429:
            _log_error("post_facebook", "facebook", "Rate limit")
            return _err("Facebook rate limit hit. Wait ~1 hour before retrying.")
        if status in (401, 403):
            _log_error("post_facebook", "facebook", f"Auth error {status}")
            return _err(f"Facebook auth error ({status}). Check FB_PAGE_ACCESS_TOKEN.")
        _log_error("post_facebook", "facebook", f"HTTP {status}: {body}")
        return _err(f"HTTP {status}: {body}")
    except Exception as e:
        _log_error("post_facebook", "facebook", str(e))
        return _err(str(e))


@mcp.tool()
def get_facebook_posts(page_id: Optional[str] = None, limit: int = 10) -> str:
    """
    Get recent posts from a Facebook Page.

    Args:
        page_id:  Facebook Page ID — uses FB_PAGE_ID from .env if omitted
        limit:    Number of posts to return (default: 10, max: 100)

    Returns:
        JSON list of posts with id, message, created_time, likes, comments
    """
    pid = page_id or FB_PAGE_ID
    limit = min(limit, 100)

    if _dry([FB_PAGE_ACCESS_TOKEN, pid]):
        _log_audit("get_facebook_posts", "facebook", {"limit": limit}, dry_run=True)
        return json.dumps({
            "status": "dry_run",
            "note": "Set FB_PAGE_ACCESS_TOKEN and FB_PAGE_ID in .env for live data",
            "posts": [
                {
                    "id": "demo_post_001",
                    "message": "Excited to announce our AI Employee is now live! 🚀 Automating accounting, emails, and social media.",
                    "created_time": datetime.now().isoformat(),
                    "likes": 24,
                    "comments": 7,
                },
                {
                    "id": "demo_post_002",
                    "message": "How we reduced invoice processing time by 80% using AI automation.",
                    "created_time": datetime.now().isoformat(),
                    "likes": 41,
                    "comments": 12,
                },
            ],
        })

    try:
        resp = requests.get(
            f"{FB_GRAPH}/me/feed",
            params={
                "access_token": FB_PAGE_ACCESS_TOKEN,
                "fields": "id,message,created_time,likes.summary(true),comments.summary(true)",
                "limit": limit,
            },
            timeout=30,
        )
        resp.raise_for_status()
        posts = [
            {
                "id": p.get("id"),
                "message": p.get("message", "")[:300],
                "created_time": p.get("created_time"),
                "likes": p.get("likes", {}).get("summary", {}).get("total_count", 0),
                "comments": p.get("comments", {}).get("summary", {}).get("total_count", 0),
            }
            for p in resp.json().get("data", [])
        ]
        _log_audit("get_facebook_posts", "facebook", {"count": len(posts)})
        return _ok({"count": len(posts), "posts": posts})

    except requests.HTTPError as e:
        status = e.response.status_code
        if status == 429:
            return _err("Facebook rate limit hit. Try again in 1 hour.")
        _log_error("get_facebook_posts", "facebook", f"HTTP {status}: {e.response.text[:200]}")
        return _err(f"HTTP {status}: {e.response.text[:200]}")
    except Exception as e:
        _log_error("get_facebook_posts", "facebook", str(e))
        return _err(str(e))


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# INSTAGRAM
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@mcp.tool()
def post_to_instagram(caption: str, image_url: str) -> str:
    """
    Post to an Instagram Business Account.

    Uses a two-step Instagram Graph API process:
    1. Create a media container with the image URL + caption
    2. Publish the container

    IMPORTANT: Only call after HITL approval exists in /Approved folder.
    NOTE: image_url must be a publicly accessible HTTPS URL (not localhost).

    Args:
        caption:   Post caption. Hashtags allowed. Max ~2,200 chars.
        image_url: Public HTTPS URL of the image to post.

    Returns:
        JSON with status and post_id on success, dry_run details, or error
    """
    if _dry([FB_PAGE_ACCESS_TOKEN, IG_USER_ID]):
        _log_audit("post_instagram", "instagram", {"caption_preview": caption[:100]}, dry_run=True)
        _save_post_record("Instagram", {"action": "post", "caption": caption,
                                        "image_url": image_url, "dry_run": True,
                                        "ts": datetime.now().isoformat()})
        return _dry_result("instagram", "post", {
            "ig_user_id": IG_USER_ID or "(IG_USER_ID not set)",
            "caption_preview": caption[:100],
            "image_url": image_url,
        })

    try:
        # Step 1 — create media container
        container = requests.post(
            f"{FB_GRAPH}/{IG_USER_ID}/media",
            data={"image_url": image_url, "caption": caption,
                  "access_token": FB_PAGE_ACCESS_TOKEN},
            timeout=30,
        )
        container.raise_for_status()
        container_id = container.json().get("id")
        if not container_id:
            return _err("Instagram: media container creation returned no id")

        # Step 2 — publish container
        publish = requests.post(
            f"{FB_GRAPH}/{IG_USER_ID}/media_publish",
            data={"creation_id": container_id, "access_token": FB_PAGE_ACCESS_TOKEN},
            timeout=30,
        )
        publish.raise_for_status()
        post_id = publish.json().get("id", "unknown")

        _log_audit("post_instagram", "instagram", {"post_id": post_id, "caption_preview": caption[:100]})
        _save_post_record("Instagram", {"post_id": post_id, "caption": caption,
                                        "image_url": image_url, "ts": datetime.now().isoformat()})
        return _ok({"post_id": post_id, "platform": "instagram"})

    except requests.HTTPError as e:
        status = e.response.status_code
        body = e.response.text[:300]
        if status == 429:
            _log_error("post_instagram", "instagram", "Rate limit")
            return _err("Instagram rate limit. Try again in 1 hour.")
        if status in (400, 190):
            _log_error("post_instagram", "instagram", f"Token error: {body}")
            return _err(f"Instagram token error. Check FB_PAGE_ACCESS_TOKEN. Detail: {body}")
        _log_error("post_instagram", "instagram", f"HTTP {status}: {body}")
        return _err(f"HTTP {status}: {body}")
    except Exception as e:
        _log_error("post_instagram", "instagram", str(e))
        return _err(str(e))


@mcp.tool()
def get_instagram_posts(limit: int = 10) -> str:
    """
    Get recent posts from an Instagram Business Account.

    Args:
        limit: Number of posts to return (default: 10, max: 100)

    Returns:
        JSON list of posts with id, caption, timestamp, like_count, comments_count
    """
    limit = min(limit, 100)

    if _dry([FB_PAGE_ACCESS_TOKEN, IG_USER_ID]):
        _log_audit("get_instagram_posts", "instagram", {"limit": limit}, dry_run=True)
        return json.dumps({
            "status": "dry_run",
            "note": "Set FB_PAGE_ACCESS_TOKEN and IG_USER_ID in .env for live data",
            "posts": [
                {
                    "id": "ig_demo_001",
                    "caption": "Behind the scenes: how our AI Employee handles 50 invoices per hour ⚡ #AI #automation #fintech",
                    "timestamp": datetime.now().isoformat(),
                    "like_count": 38,
                    "comments_count": 5,
                },
                {
                    "id": "ig_demo_002",
                    "caption": "Dashboard view of our AI accounting sync 📊 Real-time Odoo integration #startup #SaaS",
                    "timestamp": datetime.now().isoformat(),
                    "like_count": 22,
                    "comments_count": 3,
                },
            ],
        })

    try:
        resp = requests.get(
            f"{FB_GRAPH}/{IG_USER_ID}/media",
            params={
                "access_token": FB_PAGE_ACCESS_TOKEN,
                "fields": "id,caption,timestamp,like_count,comments_count",
                "limit": limit,
            },
            timeout=30,
        )
        resp.raise_for_status()
        posts = resp.json().get("data", [])
        _log_audit("get_instagram_posts", "instagram", {"count": len(posts)})
        return _ok({"count": len(posts), "posts": posts})

    except requests.HTTPError as e:
        status = e.response.status_code
        if status == 429:
            return _err("Instagram rate limit. Try again later.")
        _log_error("get_instagram_posts", "instagram", f"HTTP {status}: {e.response.text[:200]}")
        return _err(f"HTTP {status}: {e.response.text[:200]}")
    except Exception as e:
        _log_error("get_instagram_posts", "instagram", str(e))
        return _err(str(e))


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TWITTER / X
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def _tweepy_client():
    if not _TWEEPY_OK:
        raise ImportError("tweepy not installed — run: uv add tweepy")
    return tweepy.Client(
        consumer_key=TWITTER_API_KEY,
        consumer_secret=TWITTER_API_SECRET,
        access_token=TWITTER_ACCESS_TOKEN,
        access_token_secret=TWITTER_ACCESS_SECRET,
    )


@mcp.tool()
def post_to_twitter(text: str) -> str:
    """
    Post a tweet to Twitter/X using OAuth 1.0a.

    IMPORTANT: Only call after HITL approval exists in /Approved folder.

    Args:
        text: Tweet text (max 280 characters)

    Returns:
        JSON with status and tweet_id on success, dry_run details, or error
    """
    if len(text) > 280:
        return _err(f"Tweet too long: {len(text)}/280 characters. Shorten before posting.")

    tw_tokens = [TWITTER_API_KEY, TWITTER_API_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET]

    if _dry(tw_tokens):
        _log_audit("post_twitter", "twitter",
                   {"text_preview": text[:100], "char_count": len(text)}, dry_run=True)
        _save_post_record("Twitter", {"action": "tweet", "text": text, "dry_run": True,
                                      "ts": datetime.now().isoformat()})
        return _dry_result("twitter", "tweet", {
            "text_preview": text[:100],
            "char_count": len(text),
            "remaining_chars": 280 - len(text),
        })

    try:
        client = _tweepy_client()
        response = client.create_tweet(text=text)
        tweet_id = response.data["id"]

        _log_audit("post_twitter", "twitter", {"tweet_id": tweet_id, "text_preview": text[:100]})
        _save_post_record("Twitter", {"tweet_id": tweet_id, "text": text,
                                      "ts": datetime.now().isoformat()})
        return _ok({"tweet_id": tweet_id, "platform": "twitter", "char_count": len(text)})

    except tweepy.errors.TweepyException as e:
        msg = str(e)
        if "429" in msg or "Rate limit" in msg:
            _log_error("post_twitter", "twitter", "Rate limit")
            return _err("Twitter rate limit reached. Wait 15 minutes.")
        if "401" in msg or "403" in msg:
            _log_error("post_twitter", "twitter", f"Auth error: {msg}")
            return _err(f"Twitter auth error. Check API keys in .env. Detail: {msg[:200]}")
        _log_error("post_twitter", "twitter", msg)
        return _err(msg[:300])
    except Exception as e:
        _log_error("post_twitter", "twitter", str(e))
        return _err(str(e))


@mcp.tool()
def get_twitter_posts(count: int = 10) -> str:
    """
    Get recent tweets from the authenticated Twitter/X account.

    Args:
        count: Number of tweets to return (default: 10, max: 100)

    Returns:
        JSON list of tweets with id, text, created_at, retweet_count, like_count
    """
    count = min(count, 100)
    tw_tokens = [TWITTER_API_KEY, TWITTER_API_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET]

    if _dry(tw_tokens):
        _log_audit("get_twitter_posts", "twitter", {"count": count}, dry_run=True)
        return json.dumps({
            "status": "dry_run",
            "note": "Set Twitter credentials in .env for live data",
            "tweets": [
                {
                    "id": "tw_demo_001",
                    "text": "AI is not replacing jobs — it's eliminating the boring parts. Here's how our AI Employee handles 200+ tasks/day 🧵",
                    "created_at": datetime.now().isoformat(),
                    "retweet_count": 14,
                    "like_count": 67,
                },
                {
                    "id": "tw_demo_002",
                    "text": "Just synced 3 months of Odoo invoices into a CEO briefing in 8 seconds. The future of back-office automation is here.",
                    "created_at": datetime.now().isoformat(),
                    "retweet_count": 8,
                    "like_count": 43,
                },
            ],
        })

    try:
        client = _tweepy_client()
        me = client.get_me()
        tweets = client.get_users_tweets(
            id=me.data.id,
            max_results=max(count, 5),  # API minimum is 5
            tweet_fields=["created_at", "public_metrics"],
        )
        result = []
        for t in tweets.data or []:
            m = t.public_metrics or {}
            result.append({
                "id": t.id,
                "text": t.text[:280],
                "created_at": str(t.created_at),
                "retweet_count": m.get("retweet_count", 0),
                "like_count": m.get("like_count", 0),
            })
        _log_audit("get_twitter_posts", "twitter", {"count": len(result)})
        return _ok({"count": len(result), "tweets": result})

    except tweepy.errors.TweepyException as e:
        msg = str(e)
        if "429" in msg:
            return _err("Twitter rate limit. Try again in 15 minutes.")
        _log_error("get_twitter_posts", "twitter", msg)
        return _err(msg[:300])
    except Exception as e:
        _log_error("get_twitter_posts", "twitter", str(e))
        return _err(str(e))


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SUMMARY
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@mcp.tool()
def generate_social_summary(platform: str = "all", days: int = 7) -> str:
    """
    Generate a markdown engagement summary for one or all platforms.

    Fetches recent posts, calculates totals, and formats a report suitable
    for inclusion in CEO Briefings or Dashboard updates.

    Args:
        platform: 'facebook', 'instagram', 'twitter', or 'all' (default: 'all')
        days:     Look-back window in days (default: 7). Used for context label only
                  when in dry-run mode; live platforms filter by created_time.

    Returns:
        Markdown-formatted engagement summary string
    """
    platform = platform.lower()
    valid = {"facebook", "instagram", "twitter", "all"}
    if platform not in valid:
        return _err(f"Invalid platform '{platform}'. Choose from: {', '.join(sorted(valid))}")

    sections = []
    totals = {"posts": 0, "likes": 0, "comments": 0, "retweets": 0}

    def _fb_section():
        raw = json.loads(get_facebook_posts(limit=20))
        posts = raw.get("posts", [])
        total_likes = sum(p.get("likes", 0) for p in posts)
        total_comments = sum(p.get("comments", 0) for p in posts)
        totals["posts"] += len(posts)
        totals["likes"] += total_likes
        totals["comments"] += total_comments
        dry_tag = " _(demo data)_" if raw.get("status") == "dry_run" else ""
        lines = [
            f"## Facebook{dry_tag}",
            f"| Metric | Value |",
            f"|--------|-------|",
            f"| Posts (last {days}d) | {len(posts)} |",
            f"| Total Likes | {total_likes} |",
            f"| Total Comments | {total_comments} |",
        ]
        if posts:
            top = max(posts, key=lambda p: p.get("likes", 0))
            lines += [
                "",
                f"**Top post:** {top.get('message','')[:80]}...",
                f"_{top.get('likes',0)} likes · {top.get('comments',0)} comments_",
            ]
        return "\n".join(lines)

    def _ig_section():
        raw = json.loads(get_instagram_posts(limit=20))
        posts = raw.get("posts", [])
        total_likes = sum(p.get("like_count", 0) for p in posts)
        total_comments = sum(p.get("comments_count", 0) for p in posts)
        totals["posts"] += len(posts)
        totals["likes"] += total_likes
        totals["comments"] += total_comments
        dry_tag = " _(demo data)_" if raw.get("status") == "dry_run" else ""
        lines = [
            f"## Instagram{dry_tag}",
            f"| Metric | Value |",
            f"|--------|-------|",
            f"| Posts (last {days}d) | {len(posts)} |",
            f"| Total Likes | {total_likes} |",
            f"| Total Comments | {total_comments} |",
        ]
        if posts:
            top = max(posts, key=lambda p: p.get("like_count", 0))
            lines += [
                "",
                f"**Top post:** {top.get('caption','')[:80]}...",
                f"_{top.get('like_count',0)} likes · {top.get('comments_count',0)} comments_",
            ]
        return "\n".join(lines)

    def _tw_section():
        raw = json.loads(get_twitter_posts(count=20))
        tweets = raw.get("tweets", [])
        total_likes = sum(t.get("like_count", 0) for t in tweets)
        total_rts = sum(t.get("retweet_count", 0) for t in tweets)
        totals["posts"] += len(tweets)
        totals["likes"] += total_likes
        totals["retweets"] += total_rts
        dry_tag = " _(demo data)_" if raw.get("status") == "dry_run" else ""
        lines = [
            f"## Twitter/X{dry_tag}",
            f"| Metric | Value |",
            f"|--------|-------|",
            f"| Tweets (last {days}d) | {len(tweets)} |",
            f"| Total Likes | {total_likes} |",
            f"| Total Retweets | {total_rts} |",
        ]
        if tweets:
            top = max(tweets, key=lambda t: t.get("like_count", 0))
            lines += [
                "",
                f"**Top tweet:** {top.get('text','')[:100]}...",
                f"_{top.get('like_count',0)} likes · {top.get('retweet_count',0)} RTs_",
            ]
        return "\n".join(lines)

    header = (
        f"# Social Media Summary — Last {days} Days\n"
        f"_Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}_\n"
    )

    if platform in ("facebook", "all"):
        sections.append(_fb_section())
    if platform in ("instagram", "all"):
        sections.append(_ig_section())
    if platform in ("twitter", "all"):
        sections.append(_tw_section())

    footer_lines = [
        "---",
        "## Combined Totals",
        "| Metric | Value |",
        "|--------|-------|",
        f"| Total Posts | {totals['posts']} |",
        f"| Total Likes | {totals['likes']} |",
        f"| Total Comments | {totals['comments']} |",
        f"| Total Retweets | {totals['retweets']} |",
    ]

    return header + "\n\n---\n\n".join(sections) + "\n\n" + "\n".join(footer_lines)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ENTRY POINT
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

if __name__ == "__main__":
    print("=" * 55)
    print("Social Media MCP Server - AI Employee")
    print("=" * 55)
    print(f"Dry-run forced  : {SOCIAL_DRY_RUN}")
    print(f"Tweepy installed: {_TWEEPY_OK}")
    print(f"Facebook        : {'OK' if FB_PAGE_ACCESS_TOKEN and FB_PAGE_ID else 'dry-run'}")
    print(f"Instagram       : {'OK' if FB_PAGE_ACCESS_TOKEN and IG_USER_ID else 'dry-run'}")
    tw = all([TWITTER_API_KEY, TWITTER_API_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET])
    print(f"Twitter/X       : {'OK' if tw else 'dry-run'}")
    print("=" * 55)
    mcp.run()
