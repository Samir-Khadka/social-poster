"""TikTok poster via the official Content Posting API.

Needs: a TikTok developer app (developers.tiktok.com) with the
"Content Posting API" product approved, then OAuth -> access token.
Put the token in TIKTOK_ACCESS_TOKEN. Video-only platform.

    1. Create app at developers.tiktok.com
    2. Add "Content Posting API" product, get it approved
    3. OAuth flow -> access token (see README for the one-time script)
    4. export TIKTOK_ACCESS_TOKEN=...

Upload is a 3-step flow: init -> PUT bytes to upload URL -> publish.
"""
from __future__ import annotations

import json
import os
import urllib.parse
import urllib.request
from pathlib import Path

from platforms.base import BasePoster

API = "https://open.tiktokapis.com/v2"


class TikTokPoster(BasePoster):
    name = "tiktok"

    def _token(self) -> str:
        tok = os.environ.get("TIKTOK_ACCESS_TOKEN", "").strip()
        if not tok:
            raise RuntimeError(
                "TIKTOK_ACCESS_TOKEN missing. Create a TikTok developer app with the "
                "Content Posting API and complete OAuth once (see README).")
        return tok

    def _api(self, method: str, path: str, data: dict | None = None) -> dict:
        req = urllib.request.Request(API + path, method=method)
        req.add_header("Authorization", f"Bearer {self._token()}")
        req.add_header("Content-Type", "application/json; charset=UTF-8")
        body = json.dumps(data).encode() if data is not None else None
        try:
            with urllib.request.urlopen(req, data=body, timeout=60) as r:
                return json.loads(r.read())
        except Exception as e:
            raise RuntimeError(f"TikTok API {path} failed: {e}")

    def post(self, text: str, media: list[str], cover: str | None = None,
             title: str | None = None) -> str:
        videos = [m for m in media if m.lower().endswith((".mp4", ".mov"))]
        if not videos:
            raise RuntimeError("TikTok needs a video file (.mp4/.mov).")
        video = Path(videos[0])
        size = video.stat().st_size

        # 1. init upload
        init = self._api("POST", "/post/publish/video/init/", {
            "post_info": {"title": text[:2200], "privacy_level": "SELF_ONLY"
                          if os.environ.get("TIKTOK_DRY") else "PUBLIC"},
            "source_info": {"source": "FILE_UPLOAD",
                            "video_size": size, "chunk_size": size,
                            "total_chunk_count": 1},
        })
        data = init.get("data", {})
        upload_url = data.get("upload_url")
        publish_id = data.get("publish_id")
        if not upload_url:
            raise RuntimeError(f"TikTok init failed: {init}")

        # 2. upload bytes
        put = urllib.request.Request(upload_url, method="PUT",
                                     data=video.read_bytes())
        put.add_header("Content-Type", "video/mp4")
        put.add_header("Content-Length", str(size))
        with urllib.request.urlopen(put, timeout=300):
            pass

        return (f"video uploaded OK (publish_id={publish_id}). "
                "TikTok posts in DRAFT/SELF_ONLY when TIKTOK_DRY=1; "
                "otherwise it goes PUBLIC via the API.")
