"""S4 Red Team agent with five data-driven personas."""

from glassgo_workflow.agents.base import BaseAgent
from glassgo_workflow.models import (
    Attack,
    AttackList,
    Concept,
    IntelMap,
    Persona,
)
from glassgo_workflow.prompts.templates import S4_ATTACK_PROMPT, S4_SYSTEM_PROMPT


class S4RedTeam(BaseAgent):
    """Attacks concepts with first-person personas."""

    DEFAULT_PERSONAS = [
        Persona(
            name="张野",
            archetype="旅行 Vlogger，双机党，重度拍摄者",
            attack_vector="使用中断",
            data_source="电商差评与论坛：充电=拍摄中断",
            aggression_level="致命",
        ),
        Persona(
            name="Linda",
            archetype="外贸创始人，商务用户，会议翻译场景",
            attack_vector="兼容焦虑",
            data_source="众筹失败案例：触点不统一",
            aggression_level="致命",
        ),
        Persona(
            name="阿凯",
            archetype="数码尝鲜党，眼镜已退货",
            attack_vector="需求虚假",
            data_source="退货原因统计：高退货率",
            aggression_level="致命",
        ),
        Persona(
            name="王姐",
            archetype="教师，近视+处方镜片用户",
            attack_vector="佩戴中断",
            data_source="用户访谈与社媒：充电时无法使用",
            aggression_level="严重",
        ),
        Persona(
            name="陆工",
            archetype="硬件 PM，手持 Meta 二代",
            attack_vector="趋势否定",
            data_source="竞品发布会与评测：原厂续航提升",
            aggression_level="致命",
        ),
    ]

    def attack(self, concepts: list[Concept], intel_map: IntelMap) -> list[Attack]:
        all_attacks = []
        intel_summary = intel_map.summary
        for concept in concepts:
            if concept.killed:
                continue
            for persona in self.DEFAULT_PERSONAS:
                attack = self._attack_one(concept, persona, intel_summary)
                all_attacks.append(attack)
        return all_attacks

    def _attack_one(
        self, concept: Concept, persona: Persona, intel_summary: str
    ) -> Attack:
        user_prompt = S4_ATTACK_PROMPT.format(
            persona_name=persona.name,
            persona_archetype=persona.archetype,
            attack_vector=persona.attack_vector,
            data_source=persona.data_source,
            concept_name=concept.name,
            concept_summary=concept.summary,
            key_features="\n".join(f"- {f}" for f in concept.key_features),
            intel_summary=intel_summary,
        )
        messages = self._build_messages(S4_SYSTEM_PROMPT, user_prompt)
        return self._invoke_structured(messages, Attack)
