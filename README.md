# Social Poster — all-in-one posting agent

One command posts your content to every monetizable social platform:

| Platform  | Status | What it needs |
|-----------|--------|---------------|
| Instagram | ✅ Works now | Meta account (already connected) |
| Facebook  | ✅ Works now | Meta account (already connected) |
| Threads   | ✅ Works now | Meta account (already connected) |
| X         | 🔑 Needs your keys | Free X developer app |
| YouTube   | 🔑 Needs your OAuth | Google Cloud project, one browser approval |
| TikTok    | 🔑 Needs your approval | TikTok developer app + Content Posting API |

## Quick start

```sh
pip install google-api-python-client google-auth-oauthlib   # only for YouTube

# Post everywhere (dry run first!)
python poster.py --text "My caption #hashtags" --media video.mp4 \
    --platforms all --dry-run

# Real post to the Meta trio
python poster.py --text "My caption" --media photo.jpg \
    --platforms instagram,facebook,threads
```

Options: `--cover` (video thumbnail), `--title` (YouTube title), `--media` (repeatable for carousels).

## Getting the API keys (one-time, ~30 min total)

**X** — developer.x.com → create app → copy API key, API secret, access token,
access token secret → `export X_API_KEY=... X_API_SECRET=... X_ACCESS_TOKEN=... X_ACCESS_SECRET=...`

**YouTube** — console.cloud.google.com → new project → enable *YouTube Data API v3* →
OAuth client (Desktop) → download `client_secret.json` next to `poster.py`.
First run opens your browser once; the token is saved for future runs.

**TikTok** — developers.tiktok.com → create app → add *Content Posting API* product
(requires approval) → OAuth → `export TIKTOK_ACCESS_TOKEN=...`.
Set `TIKTOK_DRY=1` to upload as private/draft while testing.

**Meta (Instagram/Facebook/Threads)** — nothing to do; uses the already-connected
Meta Accounts Center via the `instagram-cli`, `threads-cli`, and `facebook-cli` tools.

## Safety

- Always run `--dry-run` first.
- Publishing is per-batch: the agent shows exactly what will post where, you approve, then it runs.
- Nothing posts on a schedule unless you set one up yourself.

## TODO

- X media upload (v1.1 chunked upload) — text posts work, images pending.
- TikTok photo posts (API supports them; video flow implemented first).
