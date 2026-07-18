"""Fake LLM for end-to-end workflow testing without API keys."""

from typing import Any, List, Optional

from langchain_core.callbacks import CallbackManagerForLLMRun
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage
from langchain_core.outputs import ChatGeneration, ChatResult

from glassgo_workflow.evidence import EvidenceChain
from glassgo_workflow.models import (
    Attack,
    AttackList,
    Concept,
    ConceptList,
    IntelSource,
    Opportunity,
    OpportunityList,
    Persona,
    ProblemDef,
    Proposal,
    Review,
    ReviewList,
)


def _evidence() -> EvidenceChain:
    return EvidenceChain().add_fact(
        claim="AI glasses shipments grew rapidly in 2025",
        title="Omdia 2026 report",
        url="https://omdia.example.com",
        date="2026-03",
    )


def make_fake_instance(schema: type) -> Any:
    """Return a plausible instance for a given Pydantic schema."""
    name = schema.__name__
    if name == "ProblemDef":
        return ProblemDef(
            statement="Find a charging opportunity for AI glasses",
            category_anchor="AI glasses charging accessory",
            core_tension="fragmented charging standards vs user need for compatibility",
            capability_match="Anker has leading mobile charging expertise",
            non_goals=["become an AI glasses brand"],
            success_criteria=["ship 100k units in year one"],
            key_assumptions=["cross-brand compatibility is technically feasible"],
            evidence=_evidence(),
        )
    if name == "IntelSource":
        return IntelSource(
            channel="company",
            findings=[
                {
                    "claim": "Anker is a leading charging brand",
                    "source": {
                        "type": "fact",
                        "title": "Anker annual report",
                        "url": "https://anker.example.com",
                        "date": "2025-12",
                    },
                }
            ],
            reliability_score=0.9,
            summary="Anker has strong charging brand and supply chain.",
        )
    if name == "OpportunityList":
        return OpportunityList(
            opportunities=[
                Opportunity(
                    id="opp-1",
                    title="Cross-brand AI glasses charging case",
                    description="A universal charging case with swappable contacts",
                    scores={
                        "growth": 5.0,
                        "pain_intensity": 4.5,
                        "blank_space": 4.8,
                        "capability_match": 4.7,
                        "timing": 4.5,
                    },
                    total_score=4.7,
                    evidence=_evidence(),
                )
            ]
        )
    if name == "ConceptList":
        return ConceptList(
            concepts=[
                Concept(
                    id="c1",
                    name="GlassGo Pocket",
                    summary="Portable charging case for AI glasses",
                    tagline="Power Every Pair",
                    form_factor="pocket charging case",
                    target_user="multi-brand AI glasses users",
                    key_features=[
                        "3000mAh battery",
                        "swappable contact tongues",
                        "15min fast charge",
                    ],
                    evidence=_evidence(),
                ),
                Concept(
                    id="c2",
                    name="GlassGo Clip",
                    summary="Lightweight clip-on battery for on-the-go charging",
                    tagline="Charge while you shoot",
                    form_factor="clip-on battery",
                    target_user="heavy shooters and translators",
                    key_features=["<60g", "magnetic short cable"],
                    evidence=_evidence(),
                ),
                Concept(
                    id="c3",
                    name="GlassGo Tower",
                    summary="Desktop charging station for home",
                    tagline="Nighttime energy station",
                    form_factor="desktop dock",
                    target_user="home users",
                    key_features=["multi-device dock", "UV-C cleaning"],
                    evidence=_evidence(),
                ),
            ]
        )
    if name == "Attack":
        return Attack(
            persona=Persona(
                name="张野",
                archetype="travel vlogger",
                attack_vector="usage interruption",
                data_source="ecommerce reviews",
                aggression_level="fatal",
            ),
            target_concept_id="c1",
            statement="Putting glasses in the case stops my recording; scenery won't wait.",
            evidence_claim={
                "claim": "Charging interrupts recording",
                "source": {"type": "fact", "title": "reviews"},
            },
            suggested_fix="Add a lightweight clip-on battery for charging while using.",
            is_fatal=False,
        )
    if name == "AttackList":
        return AttackList(
            attacks=[
                Attack(
                    persona=Persona(
                        name="张野",
                        archetype="travel vlogger",
                        attack_vector="usage interruption",
                        data_source="ecommerce reviews",
                        aggression_level="fatal",
                    ),
                    target_concept_id="c1",
                    statement="Putting glasses in the case stops my recording; scenery won't wait.",
                    evidence_claim={
                        "claim": "Charging interrupts recording",
                        "source": {"type": "fact", "title": "reviews"},
                    },
                    suggested_fix="Add a lightweight clip-on battery for charging while using.",
                    is_fatal=False,
                ),
                Attack(
                    persona=Persona(
                        name="Linda",
                        archetype="business user",
                        attack_vector="compatibility anxiety",
                        data_source="crowdfunding failures",
                        aggression_level="fatal",
                    ),
                    target_concept_id="c1",
                    statement="Contacts differ across brands; how do you guarantee a good fit?",
                    evidence_claim={
                        "claim": "Contacts are not unified",
                        "source": {"type": "fact", "title": "crowdfunding cases"},
                    },
                    suggested_fix="Use swappable contact tongues plus a voting mechanism.",
                    is_fatal=False,
                ),
            ]
        )
    if name == "Review":
        return Review(
            dimension="tech",
            verdict="pass",
            score=4.5,
            reasoning="Low-voltage magnetic contacts have no protocol barriers.",
            risks=["swappable battery compatibility needs validation"],
            evidence=_evidence(),
        )
    if name == "ReviewList":
        return ReviewList(
            reviews=[
                Review(
                    dimension="tech",
                    verdict="pass",
                    score=4.5,
                    reasoning="Low-voltage magnetic contacts have no protocol barriers.",
                    risks=["swappable battery compatibility needs validation"],
                    evidence=_evidence(),
                ),
                Review(
                    dimension="supply_chain",
                    verdict="pass",
                    score=4.5,
                    reasoning="Shenzhen supply chain for magnets and small batteries is mature.",
                    risks=["mold lead time"],
                    evidence=_evidence(),
                ),
                Review(
                    dimension="compliance",
                    verdict="pass",
                    score=4.5,
                    reasoning="10Wh capacity is within airline limits.",
                    risks=["global certification matrix"],
                    evidence=_evidence(),
                ),
                Review(
                    dimension="market",
                    verdict="pass",
                    score=4.5,
                    reasoning="Accessory ecosystem lags host devices by 1-2 years.",
                    risks=["brand lock-in strategies"],
                    evidence=_evidence(),
                ),
            ]
        )
    if name == "Proposal":
        return Proposal(
            title="Anker GlassGo",
            positioning="Cross-brand energy infrastructure for AI glasses",
            core_product="GlassGo Pocket portable charging case with swappable tongues",
            product_system=[
                "GlassGo Pocket",
                "GlassGo Clip",
                "GlassGo App",
            ],
            pricing="$59.99",
            target="Crowdfunding + mass production 150k-250k units in year one",
            roadmap=[
                "P0: Kickstarter MVP",
                "P1: Mass production and ecosystem expansion",
                "P2: B2B module licensing",
            ],
            key_decisions=[
                "Reject all-in-one; choose universal case + swappable tongues"
            ],
            risk_mitigation=["Crowdfunding as stop-loss gate"],
            facts=["AI glasses shipments reached 8.7M in 2025"],
            inferences=["Accessory penetration will follow TWS curve"],
        )
    raise ValueError(f"Unsupported schema for fake LLM: {name}")


class FakeGlassGoLLM(BaseChatModel):
    """A fake chat model that returns structured outputs for testing."""

    model_name: str = "fake-glassgo"

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        return ChatResult(
            generations=[ChatGeneration(message=AIMessage(content="{}"))]
        )

    def _llm_type(self) -> str:
        return "fake-glassgo"

    def with_structured_output(self, schema, **kwargs: Any):
        class _FakeRunnable:
            def invoke(self, input, config=None, **kwargs_inner):
                return make_fake_instance(schema)

        return _FakeRunnable()
