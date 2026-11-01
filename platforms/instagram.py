"""Instagram poster via the Meta instagram-cli. Works today."""
from __future__ import annotations

import json
import os
import subprocess

from platforms.base import BasePoster

CLI = "/opt/hatch/bin/instagram-cli"


class InstagramPoster(BasePoster):
    name = "instagram"

    def _account_id(self) -> str:
        aid = os.environ.get("IG_ACCOUNT_ID", "").strip()
        if aid:
            return aid
        out = subprocess.run([CLI, "accounts"], capture_output=True, text=True,
                             timeout=60)
        if out.returncode != 0:
            raise RuntimeError(f"instagram-cli accounts failed: {out.stderr[:200]}")
        try:
            accounts = json.loads(out.stdout)
        except json.JSONDecodeError:
            raise RuntimeError("Could not parse instagram-cli accounts output")
        if not accounts:
            raise RuntimeError("No Instagram account linked. Connect via Meta Accounts Center.")
        # Prefer an explicitly chosen account, else the first.
        return str(accounts[0].get("id") or accounts[0].get("fbid") or accounts[0])

    def post(self, text: str, media: list[str], cover: str | None = None,
             title: str | None = None) -> str:
        if not media:
            raise RuntimeError("Instagram needs at least one image or video file.")
        cmd = [CLI, "post-feed", "--account-id", self._account_id(),
               "--retries", "0"]
        for m in media:
            cmd += ["--file", m]
        if cover:
            cmd += ["--cover", cover]
        if text.strip():
            cmd += ["--caption", text]
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        if out.returncode != 0:
            raise RuntimeError(f"Instagram post failed: {out.stderr[:300]}")
        return f"posted OK — {out.stdout.strip()[:200]}"
