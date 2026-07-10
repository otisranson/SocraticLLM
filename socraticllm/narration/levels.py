"""The three progressive-disclosure levels described in VISION.md."""

from enum import Enum, auto


class DisclosureLevel(Enum):
    NOVICE = auto()        # every layer explained, annotated, visual
    INTERMEDIATE = auto()  # summarizes rather than narrates; shows the interesting parts
    EXPERT = auto()        # clean output; instrumentation available on demand
