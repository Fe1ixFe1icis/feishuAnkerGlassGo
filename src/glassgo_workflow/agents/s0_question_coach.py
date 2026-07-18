"""S0 Question Coach agent."""

import json
from typing import Any

from glassgo_workflow.agents.base import BaseAgent
from glassgo_workflow.models import ProblemDef
from glassgo_workflow.prompts.templates import S0_SYSTEM_PROMPT, S0_USER_PROMPT


class S0QuestionCoach(BaseAgent):
    """Frames human intent into a structured problem definition."""

    def run(self, raw_input: str, constraints: dict[str, Any]) -> ProblemDef:
        user_prompt = S0_USER_PROMPT.format(
            raw_input=raw_input,
            constraints=json.dumps(constraints, ensure_ascii=False, indent=2),
        )
        messages = self._build_messages(S0_SYSTEM_PROMPT, user_prompt)
        return self._invoke_structured(messages, ProblemDef)
