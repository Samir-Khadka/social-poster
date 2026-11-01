"""Facebook poster via the Meta facebook_cli. Works today.

The facebook_cli posts to the user's timeline or a Page they manage.
Command surface is documented in /opt/hatch/connectors/facebook_cli/CONNECTOR.md;
this module shells out to the CLI's post command.
"""
from __future__ import annotations

import os
import subprocess

from platforms.base import BasePoster

CLI = "/opt/hatch/bin/facebook-cli"


class FacebookPoster(BasePoster):
    name = "facebook"

    def post(self, text: str, media: list[str], cover: str | None = None,
             title: str | None = None) -> str:
        page_id = os.environ.get("FB_PAGE_ID", "").strip()
        cmd = [CLI, "post", "--message", text]
        if page_id:
            cmd += ["--page-id", page_id]
        for m in media:
            cmd += ["--file", m]
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        if out.returncode != 0:
            raise RuntimeError(
                "Facebook post failed — check /opt/hatch/connectors/facebook_cli/"
                f"CONNECTOR.md for the current post command. CLI said: {out.stderr[:300]}"
            )
        return f"posted OK — {out.stdout.strip()[:200]}"
