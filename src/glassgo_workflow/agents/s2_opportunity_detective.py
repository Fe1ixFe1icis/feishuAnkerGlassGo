"""S2 Opportunity Detective agent."""

from glassgo_workflow.agents.base import BaseAgent
from glassgo_workflow.models import (
    IntelMap,
    Opportunity,
    OpportunityList,
)
from glassgo_workflow.prompts.templates import S2_SYSTEM_PROMPT, S2_USER_PROMPT


class S2OpportunityDetective(BaseAgent):
    """Clusters intelligence and scores opportunities."""

    SCORING_DIMS = [
        "growth",
        "pain_intensity",
        "blank_space",
        "capability_match",
        "timing",
    ]

    def cluster_and_score(self, intel_map: IntelMap) -> list[Opportunity]:
        user_prompt = S2_USER_PROMPT.format(intel_summary=intel_map.summary)
        messages = self._build_messages(S2_SYSTEM_PROMPT, user_prompt)
        result = self._invoke_structured(messages, OpportunityList)
        # Ensure all scoring dimensions are present
        for opp in result.opportunities:
            for dim in self.SCORING_DIMS:
                opp.scores.setdefault(dim, 0.0)
        return sorted(result.opportunities, key=lambda x: x.total_score, reverse=True)
