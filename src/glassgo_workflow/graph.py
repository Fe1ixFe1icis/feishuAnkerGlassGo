"""LangGraph state machine for the adversarial workflow."""

import uuid
from typing import Any, Callable

from langchain_core.language_models.chat_models import BaseChatModel
from langgraph.checkpoint.memory import MemorySaver
from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt

from glassgo_workflow.agents import (
    S0QuestionCoach,
    S1IntelligenceAnalyst,
    S2OpportunityDetective,
    S3ConceptDesigner,
    S4RedTeam,
    S5ExpertCommittee,
    S6Scribe,
)
from glassgo_workflow.human_proxy import HumanProxy
from glassgo_workflow.models import Opportunity
from glassgo_workflow.state import WorkflowState


class WorkflowGraph:
    """Builds and runs the S0-S6 LangGraph workflow."""

    def __init__(self, llm: BaseChatModel, human_proxy: HumanProxy):
        self.llm = llm
        self.human = human_proxy
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        builder = StateGraph(WorkflowState)

        # Agent nodes
        builder.add_node("s0", self._make_s0_node())
        builder.add_node("s1", self._make_s1_node())
        builder.add_node("s2", self._make_s2_node())
        builder.add_node("s3", self._make_s3_node())
        builder.add_node("s4", self._make_s4_node())
        builder.add_node("s5", self._make_s5_node())
        builder.add_node("s6", self._make_s6_node())

        # Human checkpoint nodes
        builder.add_node("human_s0", self._make_human_node("S0", self.human.validate_problem))
        builder.add_node("human_s1", self._make_human_node("S1", self.human.de_noise))
        builder.add_node("human_s2", self._make_human_node("S2", self.human.select_bet))
        builder.add_node("human_s3", self._make_human_node("S3", self.human.enrich_scenarios))
        builder.add_node("human_s4", self._make_human_node("S4", self.human.record_unanswerable))
        builder.add_node("human_s5", self._make_human_node("S5", self.human.arbitrate))

        # Edges
        builder.add_edge(START, "s0")
        builder.add_edge("s0", "human_s0")
        builder.add_conditional_edges("human_s0", self._route_continue)
        builder.add_edge("s1", "human_s1")
        builder.add_conditional_edges("human_s1", self._route_continue)
        builder.add_edge("s2", "human_s2")
        builder.add_conditional_edges("human_s2", self._route_continue)
        builder.add_edge("s3", "human_s3")
        builder.add_conditional_edges("human_s3", self._route_continue)
        builder.add_edge("s4", "human_s4")
        builder.add_conditional_edges("human_s4", self._route_continue)
        builder.add_edge("s5", "human_s5")
        builder.add_conditional_edges("human_s5", self._route_continue)
        builder.add_edge("s6", END)

        # Explicitly allow our own Pydantic models in the in-memory checkpointer
        # serde so LangGraph does not emit "Deserializing unregistered type"
        # warnings on every interrupt/resume cycle.
        allowed_modules: list[tuple[str, ...]] = [
            ("glassgo_workflow.evidence", "SourceType"),
            ("glassgo_workflow.evidence", "Source"),
            ("glassgo_workflow.evidence", "EvidenceClaim"),
            ("glassgo_workflow.evidence", "EvidenceChain"),
            ("glassgo_workflow.models", "ProblemDef"),
            ("glassgo_workflow.models", "IntelSource"),
            ("glassgo_workflow.models", "IntelMap"),
            ("glassgo_workflow.models", "Opportunity"),
            ("glassgo_workflow.models", "OpportunityList"),
            ("glassgo_workflow.models", "Concept"),
            ("glassgo_workflow.models", "ConceptList"),
            ("glassgo_workflow.models", "Persona"),
            ("glassgo_workflow.models", "Attack"),
            ("glassgo_workflow.models", "AttackList"),
            ("glassgo_workflow.models", "Review"),
            ("glassgo_workflow.models", "ReviewList"),
            ("glassgo_workflow.models", "Proposal"),
        ]
        serde = JsonPlusSerializer(allowed_msgpack_modules=allowed_modules)
        return builder.compile(checkpointer=MemorySaver(serde=serde))

    # ------------------------------------------------------------------
    # Agent node factories
    # ------------------------------------------------------------------
    def _make_s0_node(self) -> Callable[[WorkflowState], WorkflowState]:
        def node(state: WorkflowState) -> WorkflowState:
            agent = S0QuestionCoach(self.llm)
            problem_def = agent.run(
                raw_input=state["raw_input"],
                constraints=state.get("constraints", {}),
            )
            state["problem_def"] = problem_def
            state["current_stage"] = "S0"
            state["human_decisions"] = state.get("human_decisions", [])
            return state

        return node

    def _make_s1_node(self) -> Callable[[WorkflowState], WorkflowState]:
        def node(state: WorkflowState) -> WorkflowState:
            agent = S1IntelligenceAnalyst(self.llm)
            intel_map = agent.gather_parallel(state["problem_def"])
            state["intel_map"] = intel_map
            state["current_stage"] = "S1"
            return state

        return node

    def _make_s2_node(self) -> Callable[[WorkflowState], WorkflowState]:
        def node(state: WorkflowState) -> WorkflowState:
            agent = S2OpportunityDetective(self.llm)
            opportunities = agent.cluster_and_score(state["intel_map"])
            state["opportunities"] = opportunities
            state["current_stage"] = "S2"
            return state

        return node

    def _make_s3_node(self) -> Callable[[WorkflowState], WorkflowState]:
        def node(state: WorkflowState) -> WorkflowState:
            selected_id = state.get("selected_opportunity_id")
            opportunity = next(
                (o for o in state["opportunities"] if o.id == selected_id),
                state["opportunities"][0],
            )
            agent = S3ConceptDesigner(self.llm)
            concepts = agent.diverge(opportunity, min_concepts=3)
            state["concepts"] = concepts
            state["current_stage"] = "S3"
            return state

        return node

    def _make_s4_node(self) -> Callable[[WorkflowState], WorkflowState]:
        def node(state: WorkflowState) -> WorkflowState:
            agent = S4RedTeam(self.llm)
            attacks = agent.attack(state["concepts"], state["intel_map"])
            state["attacks"] = attacks
            state["current_stage"] = "S4"
            return state

        return node

    def _make_s5_node(self) -> Callable[[WorkflowState], WorkflowState]:
        def node(state: WorkflowState) -> WorkflowState:
            agent = S5ExpertCommittee(self.llm)
            reviews = agent.review_parallel(
                state["concepts"], state["intel_map"]
            )
            state["reviews"] = reviews
            state["current_stage"] = "S5"
            return state

        return node

    def _make_s6_node(self) -> Callable[[WorkflowState], WorkflowState]:
        def node(state: WorkflowState) -> WorkflowState:
            selected_id = state.get("selected_opportunity_id")
            opportunity = next(
                (o for o in state["opportunities"] if o.id == selected_id),
                state["opportunities"][0],
            )
            agent = S6Scribe(self.llm)
            proposal = agent.converge(
                problem_def=state["problem_def"],
                opportunity=opportunity,
                concepts=state["concepts"],
                attacks=state["attacks"],
                reviews=state["reviews"],
                human_decisions=state.get("human_decisions", []),
                intel_map=state["intel_map"],
            )
            state["proposal"] = proposal
            state["current_stage"] = "S6"
            return state

        return node

    # ------------------------------------------------------------------
    # Human checkpoint factory
    # ------------------------------------------------------------------
    def _make_human_node(
        self, stage: str, handler: Callable[[Any], Any]
    ) -> Callable[[WorkflowState], WorkflowState]:
        def node(state: WorkflowState) -> WorkflowState:
            payload = self._build_human_payload(state, stage)
            # The value returned by interrupt() is supplied externally via
            # Command(resume=value). For the CLI run() path, _handle_interrupt
            # calls the human proxy handler once and passes the result here.
            # For Streamlit / custom callers, the UI response is passed directly
            # as the resume value, so the node must not call the handler again.
            result = interrupt({"stage": stage, "payload": payload})
            state = self._apply_human_result(state, stage, result)
            state["human_decisions"].append(
                {"stage": stage, "input": {"stage": stage, "payload": payload}, "result": result}
            )
            return state

        return node

    def _route_continue(self, state: WorkflowState) -> str:
        if state.get("error"):
            return END
        stage = state.get("current_stage")
        next_map = {
            "S0": "s1",
            "S1": "s2",
            "S2": "s3",
            "S3": "s4",
            "S4": "s5",
            "S5": "s6",
        }
        return next_map.get(stage, END)

    # ------------------------------------------------------------------
    # Helpers to serialize state for human review
    # ------------------------------------------------------------------
    def _build_human_payload(self, state: WorkflowState, stage: str) -> dict:
        if stage == "S0":
            return {"problem_def": state["problem_def"].model_dump()}
        if stage == "S1":
            return {"intel_map": state["intel_map"].model_dump()}
        if stage == "S2":
            return {
                "opportunities": [o.model_dump() for o in state["opportunities"]]
            }
        if stage == "S3":
            return {"concepts": [c.model_dump() for c in state["concepts"]]}
        if stage == "S4":
            return {"attacks": [a.model_dump() for a in state["attacks"]]}
        if stage == "S5":
            return {"reviews": [r.model_dump() for r in state["reviews"]]}
        return {}

    def _apply_human_result(
        self, state: WorkflowState, stage: str, result: Any
    ) -> WorkflowState:
        if stage == "S2":
            selected_id = None
            if isinstance(result, Opportunity):
                selected_id = result.id
            elif isinstance(result, str):
                selected_id = result
            elif isinstance(result, dict):
                selected_id = result.get("selected_id")
            if selected_id:
                state["selected_opportunity_id"] = selected_id
        elif stage == "S3" and isinstance(result, list):
            state["concepts"] = result
        elif stage == "S4":
            decisions = result
            if isinstance(result, dict):
                decisions = result.get("decisions", [])
            if isinstance(decisions, list):
                self._apply_red_team_fixes(state, decisions)
        elif stage == "S5":
            if isinstance(result, list):
                state["reviews"] = result
            elif isinstance(result, dict) and result.get("arbitration_note"):
                # Preserve the note as metadata for downstream auditing.
                state["arbitration_note"] = result["arbitration_note"]
        return state

    def _apply_red_team_fixes(
        self, state: WorkflowState, decisions: list[dict]
    ) -> None:
        """Apply fixes or kill concepts based on human red-team decisions."""
        concepts_by_id = {c.id: c for c in state["concepts"]}
        for decision in decisions:
            concept_id = decision.get("concept_id")
            fix = decision.get("fix")
            killed = decision.get("killed", False)
            if concept_id and concept_id in concepts_by_id:
                concept = concepts_by_id[concept_id]
                if killed:
                    concept.mark_killed(decision.get("reason", "Killed by red team"))
                elif fix:
                    concept.apply_fix(fix)

    def _handle_interrupt(self, interrupt_data: dict[str, Any]) -> dict[str, Any]:
        """Route an interrupt payload to the right human proxy method."""
        stage = interrupt_data["stage"]
        handler = {
            "S0": self.human.validate_problem,
            "S1": self.human.de_noise,
            "S2": self.human.select_bet,
            "S3": self.human.enrich_scenarios,
            "S4": self.human.record_unanswerable,
            "S5": self.human.arbitrate,
        }[stage]
        return handler(interrupt_data)

    def run(
        self,
        raw_input: str,
        constraints: dict[str, Any] | None = None,
        config: dict[str, Any] | None = None,
    ) -> WorkflowState:
        """Run the full workflow, pausing and resuming at human breakpoints."""
        if config is None:
            config = {"configurable": {"thread_id": str(uuid.uuid4())}}

        state: WorkflowState = {
            "raw_input": raw_input,
            "constraints": constraints or {},
            "current_stage": "S0",
            "human_decisions": [],
        }

        # Initial invocation runs up to the first human breakpoint.
        state = self.graph.invoke(state, config)

        for _ in range(30):
            if state.get("proposal") is not None:
                break

            graph_state = self.graph.get_state(config)
            interrupt_data = None
            if graph_state and graph_state.tasks:
                for task in graph_state.tasks:
                    if task.interrupts:
                        interrupt_data = task.interrupts[0].value
                        break

            if interrupt_data is None:
                break

            human_response = self._handle_interrupt(interrupt_data)
            # Resume from the breakpoint. This single invocation processes the
            # human node, routes to the next agent, and runs until the next
            # interrupt or END. We must not call graph.invoke(state, config)
            # again afterwards, or LangGraph will replay from the previous
            # checkpoint and loop forever.
            state = self.graph.invoke(Command(resume=human_response), config)

        return state
