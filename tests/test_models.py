"""Tests for Pydantic data models."""

from glassgo_workflow.evidence import EvidenceChain, SourceType
from glassgo_workflow.models import Concept, Opportunity, ProblemDef


def test_evidence_chain():
    chain = EvidenceChain()
    chain.add_fact(
        claim="2025 AI glasses shipments reached 8.7M units",
        title="Omdia report",
        url="https://omdia.example.com",
        date="2026-03",
    )
    chain.add_inference(
        claim="Accessory penetration will follow TWS curve",
        basis="Analogous category behavior",
        confidence=0.6,
    )
    assert len(chain.claims) == 2
    assert len(chain.facts()) == 1
    assert len(chain.inferences()) == 1
    assert chain.inferences()[0].source.type == SourceType.INFERENCE


def test_concept_apply_fix_and_kill():
    concept = Concept(
        id="c1",
        name="PocketDock",
        summary="Portable charging case",
        form_factor="charging case",
        target_user="AI glasses users",
    )
    concept.apply_fix("add swappable contact tongue")
    assert len(concept.fixes) == 1
    concept.mark_killed("fatally attacked by red team")
    assert concept.killed
    assert concept.kill_reason == "fatally attacked by red team"


def test_problem_def_has_evidence():
    problem = ProblemDef(
        statement="Find a charging opportunity",
        category_anchor="AI glasses",
        core_tension="fragmented charging standards",
        capability_match="Anker charging expertise",
    )
    assert problem.evidence is not None


def test_opportunity_scoring():
    opp = Opportunity(
        id="o1",
        title="Cross-brand charging",
        description="A universal charging accessory",
        scores={"growth": 5.0, "pain_intensity": 4.5},
        total_score=4.7,
    )
    assert opp.total_score == 4.7
    assert opp.scores["growth"] == 5.0
