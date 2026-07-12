import pytest

from socraticllm.curriculum import Concept, ConceptGraph, ConceptGraphError


def make_graph() -> ConceptGraph:
    graph = ConceptGraph(curriculum_id="algebra-1", title="Introductory Algebra")
    graph.add(Concept(id="variables", name="Variables"))
    graph.add(Concept(id="linear-equations", name="Linear equations", prerequisites=["variables"]))
    graph.add(
        Concept(
            id="systems-of-equations",
            name="Systems of equations",
            prerequisites=["linear-equations"],
        )
    )
    return graph


def test_add_and_get():
    graph = make_graph()
    assert graph.get("variables").name == "Variables"
    assert len(graph) == 3
    assert "linear-equations" in graph


def test_add_duplicate_raises():
    graph = make_graph()
    with pytest.raises(ConceptGraphError):
        graph.add(Concept(id="variables", name="Variables again"))


def test_get_unknown_raises():
    graph = make_graph()
    with pytest.raises(ConceptGraphError):
        graph.get("quadratics")


def test_prerequisites_of():
    graph = make_graph()
    prereqs = graph.prerequisites_of("systems-of-equations")
    assert [c.id for c in prereqs] == ["linear-equations"]


def test_validate_passes_for_well_formed_graph():
    make_graph().validate()


def test_validate_raises_on_dangling_prerequisite():
    graph = ConceptGraph(curriculum_id="algebra-1")
    graph.add(Concept(id="linear-equations", name="Linear equations", prerequisites=["variables"]))
    with pytest.raises(ConceptGraphError):
        graph.validate()


def test_validate_raises_on_cycle():
    graph = ConceptGraph(curriculum_id="broken")
    graph.add(Concept(id="a", name="A", prerequisites=["b"]))
    graph.add(Concept(id="b", name="B", prerequisites=["a"]))
    with pytest.raises(ConceptGraphError):
        graph.validate()


def test_topological_order_respects_prerequisites():
    graph = make_graph()
    order = graph.topological_order()
    assert order.index("variables") < order.index("linear-equations")
    assert order.index("linear-equations") < order.index("systems-of-equations")


def test_topological_order_raises_on_cycle():
    graph = ConceptGraph(curriculum_id="broken")
    graph.add(Concept(id="a", name="A", prerequisites=["b"]))
    graph.add(Concept(id="b", name="B", prerequisites=["a"]))
    with pytest.raises(ConceptGraphError):
        graph.topological_order()
