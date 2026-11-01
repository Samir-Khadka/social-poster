"""Threads poster via the Meta threads-cli. Works today."""
from __future__ import annotations

import json
import os
import subprocess

from platforms.base import BasePoster

CLI = "/opt/hatch/bin/threads-cli"


class ThreadsPoster(BasePoster):
    name = "threads"

    def _account_id(self) -> str:
        aid = os.environ.get("THREADS_ACCOUNT_ID", "").strip()
        if aid:
            return aid
        out = subprocess.run([CLI, "accounts"], capture_output=True, text=True,
                             timeout=60)
        if out.returncode != 0:
            raise RuntimeError(f"threads-cli accounts failed: {out.stderr[:200]}")
        try:
            accounts = json.loads(out.stdout)
        except json.JSONDecodeError:
            raise RuntimeError("Could not parse threads-cli accounts output")
        if not accounts:
            raise RuntimeError("No Threads account linked. Connect via Meta Accounts Center.")
        return str(accounts[0].get("id") or accounts[0])

    def post(self, text: str, media: list[str], cover: str | None = None,
             title: str | None = None) -> str:
        # Threads is text-first: keep it short.
        short = text if len(text) <= 500 else text[:497] + "..."
        cmd = [CLI, "publish-post", "--account-id", self._account_id(),
               "--text", short]
        for m in media:
            item = {"file": m, "alt_text": short[:100]}
            if cover and m.lower().endswith((".mp4", ".mov")):
                item["cover"] = cover
            cmd += ["--media-item", json.dumps(item)]
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        if out.returncode != 0:
            raise RuntimeError(f"Threads post failed: {out.stderr[:300]}")
        return f"posted OK — {out.stdout.strip()[:200]}"
