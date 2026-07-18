"""End-to-end workflow test using a fake LLM."""

from glassgo_workflow.graph import WorkflowGraph
from glassgo_workflow.human_proxy import AutoHumanProxy
from tests.fake_llm import FakeGlassGoLLM


def test_e2e_auto_run():
    """Run the full S0-S6 workflow with a fake LLM and auto human proxy."""
    llm = FakeGlassGoLLM()
    workflow = WorkflowGraph(llm=llm, human_proxy=AutoHumanProxy())

    final_state = workflow.run(
        raw_input="Find a charging opportunity for AI glasses for Anker",
        constraints={"brand": "Anker"},
    )

    assert final_state.get("proposal") is not None
    assert final_state["proposal"].title == "Anker GlassGo"
    assert len(final_state["human_decisions"]) == 6
    assert len(final_state["concepts"]) == 3
    assert len(final_state["attacks"]) > 0
    assert len(final_state["reviews"]) == 4