from pathlib import Path

from socraticllm.curriculum import Concept, ConceptGraph
from socraticllm.student import ConceptProgress, StudentState, load, save


def make_graph() -> ConceptGraph:
    graph = ConceptGraph(curriculum_id="algebra-1", title="Introductory Algebra")
    graph.add(Concept(id="variables", name="Variables"))
    graph.add(Concept(id="linear-equations", name="Linear equations", prerequisites=["variables"]))
    return graph


def test_load_missing_file_returns_default_state(tmp_path: Path):
    state = load(tmp_path / "state.json")
    assert state.version == "0.2"
    assert state.curricula == {}
    assert state.session_count == 0


def test_ensure_curriculum_populates_concept_map_from_graph():
    state = StudentState()
    progress = state.ensure_curriculum(make_graph())
    assert set(progress.concept_map) == {"variables", "linear-equations"}
    assert progress.concept_map["variables"].status == "not_yet"


def test_ensure_curriculum_does_not_clobber_existing_progress():
    state = StudentState()
    progress = state.ensure_curriculum(make_graph())
    progress.concept_map["variables"].status = "recognized"
    progress.concept_map["variables"].confidence = "high"

    state.ensure_curriculum(make_graph())

    assert progress.concept_map["variables"].status == "recognized"
    assert progress.concept_map["variables"].confidence == "high"


def test_save_then_load_round_trips(tmp_path: Path):
    path = tmp_path / "state.json"
    state = StudentState(student_id="otis", session_count=3)
    progress = state.ensure_curriculum(make_graph())
    progress.concept_map["variables"] = ConceptProgress(
        status="recognized", confidence="high", notes="got it fast", last_seen="2026-07-13"
    )
    progress.friction_log.append("stalled on substitution")
    progress.open_questions.append("why does swapping sides flip the inequality?")

    save(state, path)
    loaded = load(path)

    assert loaded.student_id == "otis"
    assert loaded.session_count == 3
    assert loaded.curricula["algebra-1"].concept_map["variables"] == ConceptProgress(
        status="recognized", confidence="high", notes="got it fast", last_seen="2026-07-13"
    )
    assert loaded.curricula["algebra-1"].friction_log == ["stalled on substitution"]
    assert loaded.curricula["algebra-1"].open_questions == [
        "why does swapping sides flip the inequality?"
    ]
