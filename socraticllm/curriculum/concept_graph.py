"""The concept graph: the data model a curriculum's dialogue and student model run against.

One ConceptGraph corresponds to one curriculum (e.g. one uploaded textbook). Concepts are nodes;
prerequisites are directed edges pointing at the concept(s) that must come first. Extracting a
graph automatically from source text is a separate, later step (curriculum ingestion) — this
module only defines the shape and validates it.
"""

from __future__ import annotations

from dataclasses import dataclass, field


class ConceptGraphError(Exception):
    """Raised when a concept graph is structurally invalid (dangling reference or cycle)."""


@dataclass
class Concept:
    """A single recognizable unit within a curriculum.

    `domain` is a free-text grouping label (e.g. "linear-equations" within an "algebra-1"
    curriculum) for the dialogue engine to classify problems against — distinct from
    `prerequisites`, which drive sequencing rather than classification.
    """

    id: str
    name: str
    description: str = ""
    domain: str | None = None
    prerequisites: list[str] = field(default_factory=list)


class ConceptGraph:
    """A curriculum's concepts and their prerequisite relationships."""

    def __init__(self, curriculum_id: str, title: str = "") -> None:
        self.curriculum_id = curriculum_id
        self.title = title
        self._concepts: dict[str, Concept] = {}

    def add(self, concept: Concept) -> None:
        if concept.id in self._concepts:
            raise ConceptGraphError(f"concept '{concept.id}' already exists")
        self._concepts[concept.id] = concept

    def get(self, concept_id: str) -> Concept:
        try:
            return self._concepts[concept_id]
        except KeyError:
            raise ConceptGraphError(f"unknown concept '{concept_id}'") from None

    def __contains__(self, concept_id: str) -> bool:
        return concept_id in self._concepts

    def __iter__(self):
        return iter(self._concepts.values())

    def __len__(self) -> int:
        return len(self._concepts)

    def prerequisites_of(self, concept_id: str) -> list[Concept]:
        return [self.get(prereq_id) for prereq_id in self.get(concept_id).prerequisites]

    def validate(self) -> None:
        """Raise ConceptGraphError if any prerequisite is dangling or the graph has a cycle."""
        for concept in self._concepts.values():
            for prereq_id in concept.prerequisites:
                if prereq_id not in self._concepts:
                    raise ConceptGraphError(
                        f"concept '{concept.id}' references unknown prerequisite '{prereq_id}'"
                    )
        self._check_acyclic()

    def _check_acyclic(self) -> None:
        UNVISITED, IN_PROGRESS, DONE = 0, 1, 2
        state = {concept_id: UNVISITED for concept_id in self._concepts}

        def visit(concept_id: str, path: list[str]) -> None:
            state[concept_id] = IN_PROGRESS
            for prereq_id in self._concepts[concept_id].prerequisites:
                if state[prereq_id] == IN_PROGRESS:
                    cycle = " -> ".join([*path, prereq_id])
                    raise ConceptGraphError(f"cycle in prerequisites: {cycle}")
                if state[prereq_id] == UNVISITED:
                    visit(prereq_id, [*path, prereq_id])
            state[concept_id] = DONE

        for concept_id in self._concepts:
            if state[concept_id] == UNVISITED:
                visit(concept_id, [concept_id])

    def topological_order(self) -> list[str]:
        """Concept ids ordered so every concept follows all of its prerequisites."""
        self.validate()
        order: list[str] = []
        visited: set[str] = set()

        def visit(concept_id: str) -> None:
            if concept_id in visited:
                return
            visited.add(concept_id)
            for prereq_id in self._concepts[concept_id].prerequisites:
                visit(prereq_id)
            order.append(concept_id)

        for concept_id in self._concepts:
            visit(concept_id)
        return order
