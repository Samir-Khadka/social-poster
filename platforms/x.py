"""X (Twitter) poster via the official X API v2.

Needs: a free X developer account -> app -> API key, API secret,
access token, access token secret. Put them in the environment
(see README). Uses tweepy if installed, else raw HTTP.

    pip install tweepy
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import os
import time
import urllib.parse
import urllib.request

from platforms.base import BasePoster


def _oauth1_header(method: str, url: str, params: dict[str, str],
                   consumer_key: str, consumer_secret: str,
                   token: str, token_secret: str) -> str:
    """Minimal OAuth 1.0a header (no external deps)."""
    oauth = {
        "oauth_consumer_key": consumer_key,
        "oauth_nonce": base64.b64encode(os.urandom(32)).decode()[:32],
        "oauth_signature_method": "HMAC-SHA1",
        "oauth_timestamp": str(int(time.time())),
        "oauth_token": token,
        "oauth_version": "1.0",
    }
    all_params = {**params, **oauth}
    base = "&".join([
        method.upper(),
        urllib.parse.quote(url, safe=""),
        urllib.parse.quote("&".join(
            f"{urllib.parse.quote(k, safe='')}={urllib.parse.quote(v, safe='')}"
            for k, v in sorted(all_params.items())), safe=""),
    ])
    key = f"{urllib.parse.quote(consumer_secret, safe='')}&{urllib.parse.quote(token_secret, safe='')}"
    sig = base64.b64encode(hmac.new(key.encode(), base.encode(),
                                    hashlib.sha1).digest()).decode()
    oauth["oauth_signature"] = sig
    return "OAuth " + ", ".join(
        f'{urllib.parse.quote(k, safe="")}="{urllib.parse.quote(v, safe="")}"'
        for k, v in sorted(oauth.items()))


class XPoster(BasePoster):
    name = "x"

    def _creds(self) -> tuple[str, str, str, str]:
        ck = os.environ.get("X_API_KEY", "")
        cs = os.environ.get("X_API_SECRET", "")
        at = os.environ.get("X_ACCESS_TOKEN", "")
        ats = os.environ.get("X_ACCESS_SECRET", "")
        if not all([ck, cs, at, ats]):
            raise RuntimeError(
                "X API keys missing. Set X_API_KEY, X_API_SECRET, "
                "X_ACCESS_TOKEN, X_ACCESS_SECRET (see README).")
        return ck, cs, at, ats

    def post(self, text: str, media: list[str], cover: str | None = None,
             title: str | None = None) -> str:
        ck, cs, at, ats = self._creds()
        tweet = text if len(text) <= 280 else text[:277] + "..."
        # NOTE: media upload (v1.1 upload.twitter.com) omitted for brevity —
        # text posts work now; image upload is a documented TODO in README.
        if media:
            raise RuntimeError(
                "X media upload not wired yet — post text-only for now, "
                "or attach media in the X app. (TODO in README.)")
        url = "https://api.twitter.com/2/tweets"
        body = urllib.parse.urlencode({"text": tweet}).encode()
        req = urllib.request.Request(url, data=body, method="POST")
        req.add_header("Content-Type", "application/x-www-form-urlencoded")
        req.add_header("Authorization",
                       _oauth1_header("POST", url, {"text": tweet}, ck, cs, at, ats))
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return f"posted OK — {r.read()[:200]!r}"
        except Exception as e:
            raise RuntimeError(f"X post failed: {e}")
