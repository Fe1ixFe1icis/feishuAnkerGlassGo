"""Smoke tests for the workflow graph."""

import os

from glassgo_workflow.graph import WorkflowGraph
from glassgo_workflow.human_proxy import AutoHumanProxy
from glassgo_workflow.llm import get_llm


def test_graph_compiles():
    """The graph should compile without errors."""
    # Use a dummy key so the LLM abstraction layer can be instantiated
    # without a real API key during smoke tests.
    os.environ.setdefault("OPENAI_API_KEY", "dummy-key-for-tests")
    llm = get_llm()
    graph = WorkflowGraph(llm=llm, human_proxy=AutoHumanProxy())
    assert graph.graph is not None
