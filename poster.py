"""All-in-one social media posting agent.

One command posts Samir's content to every monetizable platform:
Instagram, Facebook, Threads (via Meta CLIs — work today) and
X, YouTube, TikTok (via official APIs — need his keys, see README).

Usage:
    python poster.py --text "caption" --media photo.jpg --platforms instagram,facebook,threads
    python poster.py --text "caption" --media video.mp4 --platforms all --dry-run
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from platforms import PLATFORMS  # noqa: E402


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="All-in-one social media posting agent")
    p.add_argument("--text", required=True, help="Post caption / text")
    p.add_argument("--media", action="append", default=[],
                   help="Media file path (repeatable for carousels)")
    p.add_argument("--cover", default=None,
                   help="Cover image for video posts (Instagram reel / Threads video)")
    p.add_argument("--platforms", default="all",
                   help="Comma list or 'all'. Choices: " + ", ".join(sorted(PLATFORMS)))
    p.add_argument("--title", default=None, help="Video title (YouTube)")
    p.add_argument("--dry-run", action="store_true",
                   help="Show what would be posted without posting")
    return p.parse_args(argv)


def resolve_platforms(spec: str) -> list[str]:
    if spec.strip().lower() == "all":
        return sorted(PLATFORMS)
    names = [s.strip().lower() for s in spec.split(",") if s.strip()]
    unknown = [n for n in names if n not in PLATFORMS]
    if unknown:
        raise SystemExit(f"Unknown platform(s): {', '.join(unknown)}. "
                         f"Choices: {', '.join(sorted(PLATFORMS))}")
    return names


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    names = resolve_platforms(args.platforms)

    media = [str(Path(m).expanduser().resolve()) for m in args.media]
    for m in media:
        if not Path(m).is_file():
            raise SystemExit(f"Media file not found: {m}")

    results: dict[str, str] = {}
    for name in names:
        poster = PLATFORMS[name]()
        try:
            if args.dry_run:
                results[name] = f"DRY-RUN: {poster.describe(args.text, media)}"
            else:
                results[name] = poster.post(
                    text=args.text, media=media, cover=args.cover, title=args.title)
        except Exception as e:  # noqa: BLE001 — report per-platform, keep going
            results[name] = f"FAILED: {e}"

    print("\n==== Results ====")
    for name in names:
        print(f"[{name}] {results[name]}")
    failed = [n for n in names if results[n].startswith("FAILED")]
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
