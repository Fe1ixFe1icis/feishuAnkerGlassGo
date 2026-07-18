"""S3 Concept Designer agent."""

from glassgo_workflow.agents.base import BaseAgent
from glassgo_workflow.models import Concept, ConceptList, Opportunity
from glassgo_workflow.prompts.templates import S3_SYSTEM_PROMPT, S3_USER_PROMPT


class S3ConceptDesigner(BaseAgent):
    """Diverges multiple concept candidates from a selected opportunity."""

    def diverge(
        self, opportunity: Opportunity, min_concepts: int = 3
    ) -> list[Concept]:
        evidence_summary = "\n".join(
            f"- {c.claim} [{c.source.title}]" for c in opportunity.evidence.claims
        )
        user_prompt = S3_USER_PROMPT.format(
            opportunity_title=opportunity.title,
            opportunity_description=opportunity.description,
            evidence_summary=evidence_summary,
            min_concepts=min_concepts,
        )
        system_prompt = S3_SYSTEM_PROMPT.format(min_concepts=min_concepts)
        messages = self._build_messages(system_prompt, user_prompt)
        result = self._invoke_structured(messages, ConceptList)
        return result.concepts
