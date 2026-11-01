"""Shared base class for platform posters."""
from __future__ import annotations


class BasePoster:
    """One platform. Subclasses implement post()."""

    name = "base"

    def post(self, text: str, media: list[str], cover: str | None = None,
             title: str | None = None) -> str:
        raise NotImplementedError

    def describe(self, text: str, media: list[str]) -> str:
        return f"would post to {self.name}: {text[:60]!r} + {len(media)} file(s)"
