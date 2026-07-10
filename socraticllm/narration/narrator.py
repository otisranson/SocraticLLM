"""Shared hook that model/tokenizer components call into to report what they're doing.

Each component receives a Narrator and calls `narrator.report(...)` at points worth
explaining. The Narrator decides, based on the current DisclosureLevel, whether and how
much to surface -- so components stay free of level-specific branching.
"""

from typing import Any

from .levels import DisclosureLevel


class Narrator:
    def __init__(self, level: DisclosureLevel = DisclosureLevel.EXPERT):
        self.level = level

    def report(self, component: str, event: str, detail: Any = None) -> None:
        raise NotImplementedError
