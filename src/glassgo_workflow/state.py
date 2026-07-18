"""LangGraph state schema for the adversarial workflow."""

from typing import Any, Dict, List, Optional

from typing_extensions import TypedDict

from glassgo_workflow.models import (
    Attack,
    Concept,
    IntelMap,
    Opportunity,
    ProblemDef,
    Proposal,
    Review,
)


class WorkflowState(TypedDict, total=False):
    """Shared state across LangGraph nodes.

    Each node reads only the fields it needs to enforce memory isolation.
    """

    # Inputs
    raw_input: str
    constraints: Dict[str, Any]

    # Stage outputs
    problem_def: ProblemDef
    intel_map: IntelMap
    opportunities: List[Opportunity]
    selected_opportunity_id: str
    concepts: List[Concept]
    attacks: List[Attack]
    reviews: List[Review]
    proposal: Proposal

    # Human decisions log
    human_decisions: List[Dict[str, Any]]

    # Control
    current_stage: str
    next_stage: str
    error: Optional[str]
