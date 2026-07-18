"""S5 Expert Committee agent with four parallel reviewers."""

from glassgo_workflow.agents.base import BaseAgent
from glassgo_workflow.models import (
    Concept,
    IntelMap,
    Review,
    ReviewList,
)
from glassgo_workflow.prompts.templates import S5_REVIEW_PROMPT, S5_SYSTEM_PROMPT


class S5ExpertCommittee(BaseAgent):
    """Reviews surviving concepts across four independent dimensions."""

    DIMENSIONS = ["tech", "supply_chain", "compliance", "market"]

    def review_parallel(
        self, concepts: list[Concept], intel_map: IntelMap
    ) -> list[Review]:
        alive = [c for c in concepts if not c.killed]
        concepts_summary = "\n\n".join(
            f"{c.name}: {c.summary}\nFeatures: {', '.join(c.key_features)}"
            for c in alive
        )
        reviews = []
        for dimension in self.DIMENSIONS:
            review = self._review_one(dimension, concepts_summary, intel_map.summary)
            reviews.append(review)
        return reviews

    def _review_one(
        self, dimension: str, concepts_summary: str, intel_summary: str
    ) -> Review:
        system_prompt = S5_SYSTEM_PROMPT.format(dimension=dimension)
        user_prompt = S5_REVIEW_PROMPT.format(
            dimension=dimension,
            concepts_summary=concepts_summary,
            intel_summary=intel_summary,
        )
        messages = self._build_messages(system_prompt, user_prompt)
        return self._invoke_structured(messages, Review)
