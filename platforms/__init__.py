"""Platform registry."""
from __future__ import annotations

from platforms.base import BasePoster  # noqa: F401  (re-exported)
from platforms.facebook import FacebookPoster
from platforms.instagram import InstagramPoster
from platforms.threads import ThreadsPoster
from platforms.tiktok import TikTokPoster
from platforms.x import XPoster
from platforms.youtube import YouTubePoster

PLATFORMS: dict[str, type[BasePoster]] = {
    "instagram": InstagramPoster,
    "facebook": FacebookPoster,
    "threads": ThreadsPoster,
    "x": XPoster,
    "youtube": YouTubePoster,
    "tiktok": TikTokPoster,
}
