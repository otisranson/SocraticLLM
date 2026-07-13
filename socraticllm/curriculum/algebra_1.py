"""First-version curriculum content: hand-authored, not extracted from a textbook.

Per VISION.md's "First Version" section — one subject, one concept domain, one
student flow — this is the concept graph the dialogue engine runs against
until the curriculum ingestion pipeline exists. The recognition target at each
node is the problem *type* and the approach it calls for, matching VISION.md's
framing: "session ends when student has identified problem type and approach."
"""

from __future__ import annotations

from .concept_graph import Concept, ConceptGraph

CURRICULUM_ID = "algebra-1"


def build_algebra_1() -> ConceptGraph:
    """Return a fresh ConceptGraph for introductory linear-equation algebra.

    Returns a new instance on every call — callers get their own graph to
    mutate (e.g. via student progress tracking) without affecting others.
    """
    graph = ConceptGraph(curriculum_id=CURRICULUM_ID, title="Introductory Algebra: Linear Equations")

    graph.add(
        Concept(
            id="variables",
            name="Variables",
            domain="foundations",
            description=(
                "A symbol (like x) standing in for a number whose value isn't yet "
                "known or that can change."
            ),
        )
    )
    graph.add(
        Concept(
            id="equality",
            name="What the Equals Sign Means",
            domain="foundations",
            description=(
                "An equation asserts that the expressions on both sides represent the "
                "exact same value — whatever you do to one side, you must do to the "
                "other to keep that balance true."
            ),
        )
    )
    graph.add(
        Concept(
            id="inverse-operations",
            name="Inverse Operations",
            domain="foundations",
            description=(
                "Addition and subtraction undo each other; multiplication and division "
                "undo each other. Isolating a variable means applying the inverse of "
                "whatever operation is being done to it."
            ),
        )
    )
    graph.add(
        Concept(
            id="like-terms",
            name="Combining Like Terms",
            domain="foundations",
            description=(
                "Terms with the same variable raised to the same power can be added or "
                "subtracted together (e.g. 3x and 5x combine to 8x); terms that differ "
                "(3x and 5) cannot."
            ),
            prerequisites=["variables"],
        )
    )
    graph.add(
        Concept(
            id="one-step-equations",
            name="One-Step Equations",
            domain="linear-equations",
            description="An equation solvable by applying a single inverse operation to both sides, e.g. x + 5 = 12.",
            prerequisites=["variables", "equality", "inverse-operations"],
        )
    )
    graph.add(
        Concept(
            id="two-step-equations",
            name="Two-Step Equations",
            domain="linear-equations",
            description=(
                "An equation requiring two inverse operations applied in sequence to "
                "isolate the variable, e.g. 3x + 5 = 20."
            ),
            prerequisites=["one-step-equations"],
        )
    )
    graph.add(
        Concept(
            id="multi-step-equations",
            name="Multi-Step Equations with Like Terms",
            domain="linear-equations",
            description=(
                "An equation that requires combining like terms (possibly on both sides, "
                "or after distributing) before it reduces to a one- or two-step equation, "
                "e.g. 2(x + 3) = 3x - 1."
            ),
            prerequisites=["two-step-equations", "like-terms"],
        )
    )
    graph.add(
        Concept(
            id="systems-of-equations",
            name="Systems of Linear Equations",
            domain="systems",
            description=(
                "Two or more equations sharing the same variables, solved together by "
                "finding the values that satisfy all of them simultaneously (via "
                "substitution or elimination)."
            ),
            prerequisites=["multi-step-equations"],
        )
    )

    graph.validate()
    return graph
