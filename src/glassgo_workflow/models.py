"""Pydantic data models for the adversarial workflow."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from glassgo_workflow.evidence import EvidenceChain


class ProblemDef(BaseModel):
    """Structured problem definition produced by S0."""

    statement: str = Field(..., description="Clear problem statement")
    category_anchor: str = Field(..., description="Category anchor point")
    core_tension: str = Field(..., description="Core market tension")
    capability_match: str = Field(..., description="Why we are qualified")
    non_goals: List[str] = Field(default_factory=list, description="Explicit non-goals")
    success_criteria: List[str] = Field(
        default_factory=list, description="Success criteria"
    )
    key_assumptions: List[str] = Field(
        default_factory=list,
        description="Key assumptions that need human confirmation",
    )
    evidence: EvidenceChain = Field(default_factory=EvidenceChain)


class IntelSource(BaseModel):
    """Findings from a single intelligence channel."""

    channel: str = Field(
        ..., description="One of: company, market, user, competitor"
    )
    findings: List[Any] = Field(
        default_factory=list, description="List of evidence claims"
    )
    reliability_score: float = Field(
        0.8, ge=0.0, le=1.0, description="Reliability score of this source"
    )
    summary: str = Field("", description="Short summary of this channel")


class IntelMap(BaseModel):
    """Aggregated intelligence map produced by S1."""

    sources: List[IntelSource] = Field(default_factory=list)
    summary: str = Field("", description="Cross-source synthesis")

    def get_channel(self, channel: str) -> Optional[IntelSource]:
        for src in self.sources:
            if src.channel == channel:
                return src
        return None


class Opportunity(BaseModel):
    """A scored opportunity produced by S2."""

    id: str = Field(..., description="Unique opportunity ID")
    title: str = Field(..., description="Short title")
    description: str = Field(..., description="Detailed description")
    scores: Dict[str, float] = Field(
        default_factory=dict,
        description="Scores per dimension: growth, pain_intensity, blank_space, capability_match, timing",
    )
    total_score: float = Field(0.0, description="Weighted total score 0-5")
    evidence: EvidenceChain = Field(default_factory=EvidenceChain)


class Concept(BaseModel):
    """A product concept produced by S3."""

    id: str = Field(..., description="Unique concept ID")
    name: str = Field(..., description="Concept name")
    summary: str = Field(..., description="One-line summary")
    tagline: str = Field("", description="Marketing tagline")
    form_factor: str = Field(..., description="Physical form factor")
    target_user: str = Field(..., description="Target user segment")
    key_features: List[str] = Field(default_factory=list)
    killed: bool = Field(False, description="Whether the concept was killed")
    kill_reason: Optional[str] = Field(None, description="Why it was killed")
    fixes: List[str] = Field(default_factory=list, description="Applied fixes")
    evidence: EvidenceChain = Field(default_factory=EvidenceChain)

    def apply_fix(self, fix: str) -> None:
        self.fixes.append(fix)

    def mark_killed(self, reason: str) -> None:
        self.killed = True
        self.kill_reason = reason


class Persona(BaseModel):
    """A red-team persona."""

    name: str = Field(..., description="Persona name")
    archetype: str = Field(..., description="User archetype")
    attack_vector: str = Field(..., description="Primary attack vector")
    data_source: str = Field(..., description="Real data source grounding the persona")
    aggression_level: str = Field(
        ..., description="Severity: fatal / severe / moderate"
    )


class Attack(BaseModel):
    """A first-person attack from a red-team persona."""

    persona: Persona = Field(..., description="Attacking persona")
    target_concept_id: str = Field(..., description="Target concept ID")
    statement: str = Field(
        ..., description="First-person attack statement with emotion"
    )
    evidence_claim: Dict[str, Any] = Field(
        default_factory=dict, description="Cited evidence claim"
    )
    suggested_fix: Optional[str] = Field(None, description="Suggested fix")
    is_fatal: bool = Field(False, description="Whether this attack is fatal")


class Review(BaseModel):
    """A review from a single expert committee dimension."""

    dimension: str = Field(
        ..., description="One of: tech, supply_chain, compliance, market"
    )
    verdict: str = Field(
        ..., description="One of: pass / concern / block"
    )
    score: float = Field(..., ge=0.0, le=5.0, description="Score 0-5")
    reasoning: str = Field(..., description="Review reasoning")
    risks: List[str] = Field(default_factory=list)
    evidence: EvidenceChain = Field(default_factory=EvidenceChain)


class Proposal(BaseModel):
    """Final proposal produced by S6."""

    title: str = Field(..., description="Proposal title")
    positioning: str = Field(..., description="Market positioning")
    core_product: str = Field(..., description="Core product description")
    product_system: List[str] = Field(default_factory=list)
    pricing: str = Field(..., description="Pricing strategy")
    target: str = Field(..., description="Target segment and first-year goal")
    roadmap: List[str] = Field(default_factory=list)
    key_decisions: List[str] = Field(
        default_factory=list, description="Human key decisions recorded"
    )
    risk_mitigation: List[str] = Field(default_factory=list)
    facts: List[str] = Field(default_factory=list)
    inferences: List[str] = Field(default_factory=list)


# Wrapper models for structured LLM output
class OpportunityList(BaseModel):
    """Wrapper for S2 structured output."""

    opportunities: List[Opportunity] = Field(
        default_factory=list, description="Scored opportunities"
    )


class ConceptList(BaseModel):
    """Wrapper for S3 structured output."""

    concepts: List[Concept] = Field(
        default_factory=list, description="Diverged concepts"
    )


class AttackList(BaseModel):
    """Wrapper for S4 structured output."""

    attacks: List[Attack] = Field(default_factory=list, description="Attacks")


class ReviewList(BaseModel):
    """Wrapper for S5 structured output."""

    reviews: List[Review] = Field(default_factory=list, description="Reviews")
