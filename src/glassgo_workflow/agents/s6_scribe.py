"""S6 Scribe agent."""

import json

from glassgo_workflow.agents.base import BaseAgent
from glassgo_workflow.models import (
    Attack,
    Concept,
    IntelMap,
    Opportunity,
    ProblemDef,
    Proposal,
    Review,
)
from glassgo_workflow.prompts.templates import S6_SYSTEM_PROMPT, S6_USER_PROMPT


class S6Scribe(BaseAgent):
    """Converges the full chain into a final proposal."""

    def converge(
        self,
        problem_def: ProblemDef,
        opportunity: Opportunity,
        concepts: list[Concept],
        attacks: list[Attack],
        reviews: list[Review],
        human_decisions: list[dict],
        intel_map: IntelMap,
    ) -> Proposal:
        alive = [c for c in concepts if not c.killed]
        user_prompt = S6_USER_PROMPT.format(
            problem_def=problem_def.model_dump_json(),
            opportunity=opportunity.model_dump_json(),
            concepts="\n\n".join(c.model_dump_json() for c in alive),
            attacks="\n\n".join(a.model_dump_json() for a in attacks),
            reviews="\n\n".join(r.model_dump_json() for r in reviews),
            human_decisions=json.dumps(human_decisions, ensure_ascii=False),
        )
        # Inject synthesized intel context via system prompt to keep it concise
        system_prompt = (
            S6_SYSTEM_PROMPT
            + f"\n\n情报综合摘要（供参考）：\n{intel_map.summary}"
        )
        messages = self._build_messages(system_prompt, user_prompt)
        return self._invoke_structured(messages, Proposal)
