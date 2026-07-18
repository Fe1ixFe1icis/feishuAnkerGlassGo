"""S1 Intelligence Analyst agent with four parallel gatherers."""

from glassgo_workflow.agents.base import BaseAgent
from glassgo_workflow.models import IntelMap, IntelSource, ProblemDef
from glassgo_workflow.prompts.templates import S1_CHANNEL_PROMPT, S1_SYSTEM_PROMPT


class S1IntelligenceAnalyst(BaseAgent):
    """Gathers intelligence from four parallel sources."""

    CHANNELS = ["company", "market", "user", "competitor"]

    def gather_parallel(self, problem_def: ProblemDef) -> IntelMap:
        sources = []
        for channel in self.CHANNELS:
            source = self._gather_one(channel, problem_def)
            sources.append(source)
        summary = self._synthesize(sources)
        return IntelMap(sources=sources, summary=summary)

    def _gather_one(self, channel: str, problem_def: ProblemDef) -> IntelSource:
        user_prompt = S1_CHANNEL_PROMPT.format(
            problem_def=problem_def.model_dump_json(),
            channel=channel,
        )
        messages = self._build_messages(S1_SYSTEM_PROMPT, user_prompt)
        return self._invoke_structured(messages, IntelSource)

    def _synthesize(self, sources: list[IntelSource]) -> str:
        parts = [f"【{s.channel}】{s.summary}" for s in sources]
        return "\n".join(parts)
