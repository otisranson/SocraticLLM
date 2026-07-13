from socraticllm.curriculum import build_algebra_1
from socraticllm.curriculum.algebra_1 import CURRICULUM_ID

EXPECTED_CONCEPT_IDS = {
    "variables",
    "equality",
    "inverse-operations",
    "like-terms",
    "one-step-equations",
    "two-step-equations",
    "multi-step-equations",
    "systems-of-equations",
}


def test_builds_a_valid_graph():
    graph = build_algebra_1()

    graph.validate()  # raises ConceptGraphError on dangling refs or cycles
    assert graph.curriculum_id == CURRICULUM_ID
    assert len(graph) == len(EXPECTED_CONCEPT_IDS)


def test_contains_expected_concepts():
    graph = build_algebra_1()

    assert {concept.id for concept in graph} == EXPECTED_CONCEPT_IDS


def test_topological_order_respects_prerequisites():
    graph = build_algebra_1()
    order = graph.topological_order()

    for concept in graph:
        concept_index = order.index(concept.id)
        for prereq_id in concept.prerequisites:
            assert order.index(prereq_id) < concept_index


def test_recognition_chain_from_variables_to_systems():
    graph = build_algebra_1()

    # The core recognition ladder VISION.md describes — spot-check the chain
    # a student climbs from "what's a variable" to "what's a system".
    assert graph.get("one-step-equations").prerequisites == ["variables", "equality", "inverse-operations"]
    assert graph.get("two-step-equations").prerequisites == ["one-step-equations"]
    assert graph.get("multi-step-equations").prerequisites == ["two-step-equations", "like-terms"]
    assert graph.get("systems-of-equations").prerequisites == ["multi-step-equations"]


def test_each_call_returns_an_independent_graph():
    first = build_algebra_1()
    second = build_algebra_1()

    second.get("variables").description = "mutated"

    assert first.get("variables").description != "mutated"
