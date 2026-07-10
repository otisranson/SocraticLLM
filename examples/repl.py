"""Minimal terminal REPL for exercising the model before an artifact/UI layer exists.

Run with: python examples/repl.py
"""

from socraticllm.narration import DisclosureLevel, Narrator


def main() -> None:
    narrator = Narrator(level=DisclosureLevel.NOVICE)
    raise NotImplementedError


if __name__ == "__main__":
    main()
