"""Tests for the social-poster agent (no network, no real posts)."""
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import poster
from platforms import PLATFORMS


class TestRegistry(unittest.TestCase):
    def test_all_six_platforms_registered(self):
        self.assertEqual(set(PLATFORMS),
                         {"instagram", "facebook", "threads", "x", "youtube", "tiktok"})

    def test_every_platform_has_post(self):
        for name, cls in PLATFORMS.items():
            self.assertTrue(callable(getattr(cls(), "post", None)), name)


class TestCLI(unittest.TestCase):
    def test_resolve_all(self):
        self.assertEqual(set(poster.resolve_platforms("all")), set(PLATFORMS))

    def test_resolve_subset(self):
        self.assertEqual(poster.resolve_platforms("instagram,threads"),
                         ["instagram", "threads"])

    def test_resolve_unknown_exits(self):
        with self.assertRaises(SystemExit):
            poster.resolve_platforms("myspace")


class TestDryRun(unittest.TestCase):
    def test_dry_run_posts_nothing(self):
        argv = ["--text", "hello", "--platforms", "threads,x", "--dry-run"]
        with patch("builtins.print"):
            rc = poster.main(argv)
        self.assertEqual(rc, 0)

    def test_missing_media_exits(self):
        argv = ["--text", "hello", "--media", "/nope.jpg", "--platforms", "instagram"]
        with self.assertRaises(SystemExit):
            poster.main(argv)


class TestKeyGating(unittest.TestCase):
    """API platforms must fail cleanly (not crash) when keys are missing."""

    def test_x_without_keys(self):
        with patch.dict("os.environ", {}, clear=False):
            for k in ("X_API_KEY", "X_API_SECRET", "X_ACCESS_TOKEN", "X_ACCESS_SECRET"):
                import os
                os.environ.pop(k, None)
            with self.assertRaises(RuntimeError):
                PLATFORMS["x"]().post("hi", [])

    def test_tiktok_without_token(self):
        import os
        import tempfile
        with patch.dict("os.environ", {}, clear=False):
            os.environ.pop("TIKTOK_ACCESS_TOKEN", None)
            with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as f:
                f.write(b"\x00" * 100)
                tmp = f.name
            try:
                with self.assertRaises(RuntimeError):
                    PLATFORMS["tiktok"]().post("hi", [tmp])
            finally:
                os.unlink(tmp)

    def test_youtube_needs_video(self):
        with self.assertRaises(RuntimeError):
            PLATFORMS["youtube"]().post("hi", [])


if __name__ == "__main__":
    unittest.main()
