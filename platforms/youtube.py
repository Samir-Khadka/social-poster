"""YouTube uploader via the official YouTube Data API v3.

Needs: a Google Cloud project with the YouTube Data API v3 enabled,
OAuth 2.0 client (Desktop app) -> download client_secret.json ->
first run opens a browser to authorize -> token saved to
~/.config/social-poster/youtube-token.json.

    pip install google-api-python-client google-auth-oauthlib
"""
from __future__ import annotations

import os
from pathlib import Path

from platforms.base import BasePoster

TOKEN_PATH = Path.home() / ".config" / "social-poster" / "youtube-token.json"
CLIENT_SECRET = Path(os.environ.get("YOUTUBE_CLIENT_SECRET",
                                    "client_secret.json")).expanduser()


class YouTubePoster(BasePoster):
    name = "youtube"

    def _service(self):
        try:
            from googleapiclient.discovery import build
            from googleapiclient.http import MediaFileUpload
            from google.auth.transport.requests import Request
            from google.oauth2.credentials import Credentials
            from google_auth_oauthlib.flow import InstalledAppFlow
        except ImportError:
            raise RuntimeError("pip install google-api-python-client google-auth-oauthlib")
        self._MediaFileUpload = MediaFileUpload
        scopes = ["https://www.googleapis.com/auth/youtube.upload"]
        creds = None
        if TOKEN_PATH.exists():
            creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), scopes)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not CLIENT_SECRET.is_file():
                    raise RuntimeError(
                        "YouTube client_secret.json missing. Create an OAuth client in "
                        "Google Cloud Console (YouTube Data API v3 enabled) and save it as "
                        "client_secret.json (see README).")
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(CLIENT_SECRET), scopes)
                creds = flow.run_local_server(port=0)
            TOKEN_PATH.parent.mkdir(parents=True, exist_ok=True)
            TOKEN_PATH.write_text(creds.to_json())
        return build("youtube", "v3", credentials=creds)

    def post(self, text: str, media: list[str], cover: str | None = None,
             title: str | None = None) -> str:
        videos = [m for m in media if m.lower().endswith((".mp4", ".mov", ".avi", ".mkv"))]
        if not videos:
            raise RuntimeError("YouTube needs a video file (.mp4/.mov).")
        video = videos[0]
        yt = self._service()
        body = {
            "snippet": {
                "title": (title or text[:90] or "Untitled")[:100],
                "description": text,
                "categoryId": "22",  # People & Blogs
            },
            "status": {"privacyStatus": "public", "selfDeclaredMadeForKids": False},
        }
        req = yt.videos().insert(
            part="snippet,status",
            body=body,
            media_body=self._MediaFileUpload(video, resumable=True),
        )
        resp = None
        while resp is None:
            status, resp = req.next_chunk()
        vid = resp.get("id", "?")
        # Optional thumbnail
        if cover and Path(cover).is_file():
            from googleapiclient.http import MediaFileUpload as MFU
            yt.thumbnails().set(videoId=vid,
                                media_body=MFU(cover)).execute()
        return f"uploaded OK — https://youtu.be/{vid}"
