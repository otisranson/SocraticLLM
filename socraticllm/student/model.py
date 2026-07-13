"""Persistent per-student state: recognition patterns, friction, and readiness per curriculum.

A concept map's keys are not fixed — they're whatever concept ids the active ConceptGraph
defines, since curriculum is pluggable (Core Design Decision #3 in CLAUDE.md). A student may
work through more than one curriculum, so progress is scoped per curriculum id.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Literal

from socraticllm.curriculum.concept_graph import ConceptGraph

SCHEMA_VERSION = "0.2"

DEFAULT_STATE_PATH = Path("student/state.json")

Status = Literal["not_yet", "encountered", "recognized"]
Confidence = Literal["low", "medium", "high"]


@dataclass
class ConceptProgress:
    status: Status = "not_yet"
    confidence: Confidence | None = None
    notes: str | None = None
    last_seen: str | None = None


@dataclass
class CurriculumProgress:
    concept_map: dict[str, ConceptProgress] = field(default_factory=dict)
    friction_log: list[str] = field(default_factory=list)
    open_questions: list[str] = field(default_factory=list)


@dataclass
class StudentState:
    student_id: str = ""
    last_updated: str | None = None
    session_count: int = 0
    curricula: dict[str, CurriculumProgress] = field(default_factory=dict)
    preferred_explanation_style: dict[str, bool | None] = field(
        default_factory=lambda: {"analogies": None, "math": None, "code": None}
    )
    version: str = SCHEMA_VERSION

    def ensure_curriculum(self, graph: ConceptGraph) -> CurriculumProgress:
        """Register `graph`'s concepts in this student's state, without disturbing existing progress."""
        progress = self.curricula.setdefault(graph.curriculum_id, CurriculumProgress())
        for concept in graph:
            progress.concept_map.setdefault(concept.id, ConceptProgress())
        return progress


def load(path: Path = DEFAULT_STATE_PATH) -> StudentState:
    if not path.exists():
        return StudentState()

    with path.open() as f:
        raw = json.load(f)["student_state"]

    curricula = {
        curriculum_id: CurriculumProgress(
            concept_map={
                concept_id: ConceptProgress(**progress)
                for concept_id, progress in curriculum["concept_map"].items()
            },
            friction_log=curriculum["friction_log"],
            open_questions=curriculum["open_questions"],
        )
        for curriculum_id, curriculum in raw["curricula"].items()
    }

    return StudentState(
        student_id=raw["student_id"],
        last_updated=raw["last_updated"],
        session_count=raw["session_count"],
        curricula=curricula,
        preferred_explanation_style=raw["preferred_explanation_style"],
        version=raw["version"],
    )


def save(state: StudentState, path: Path = DEFAULT_STATE_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = {
        "student_state": {
            "version": state.version,
            "student_id": state.student_id,
            "last_updated": state.last_updated,
            "session_count": state.session_count,
            "curricula": {
                curriculum_id: {
                    "concept_map": {
                        concept_id: asdict(progress)
                        for concept_id, progress in curriculum.concept_map.items()
                    },
                    "friction_log": curriculum.friction_log,
                    "open_questions": curriculum.open_questions,
                }
                for curriculum_id, curriculum in state.curricula.items()
            },
            "preferred_explanation_style": state.preferred_explanation_style,
        }
    }
    with path.open("w") as f:
        json.dump(raw, f, indent=2)
        f.write("\n")
