"""Human-in-the-loop proxy implementations."""

import json
from abc import ABC, abstractmethod
from typing import Any

from glassgo_workflow.models import (
    Attack,
    Concept,
    IntelMap,
    Opportunity,
    ProblemDef,
    Review,
)


class HumanProxy(ABC):
    """Abstract interface for human arbitration at workflow breakpoints."""

    @abstractmethod
    def validate_problem(self, human_input: dict[str, Any]) -> dict[str, Any]:
        """S0: confirm or edit problem definition."""
        raise NotImplementedError

    @abstractmethod
    def de_noise(self, human_input: dict[str, Any]) -> dict[str, Any]:
        """S1: remove suspicious signals from intel map."""
        raise NotImplementedError

    @abstractmethod
    def select_bet(self, human_input: dict[str, Any]) -> dict[str, Any]:
        """S2: select one opportunity to bet on."""
        raise NotImplementedError

    @abstractmethod
    def enrich_scenarios(self, human_input: dict[str, Any]) -> dict[str, Any]:
        """S3: add real-world scenarios to concepts."""
        raise NotImplementedError

    @abstractmethod
    def record_unanswerable(self, human_input: dict[str, Any]) -> dict[str, Any]:
        """S4: decide which attacks are fatal and which get fixes."""
        raise NotImplementedError

    @abstractmethod
    def arbitrate(self, human_input: dict[str, Any]) -> dict[str, Any]:
        """S5: cross-dimensional arbitration."""
        raise NotImplementedError


class CLIHumanProxy(HumanProxy):
    """Command-line interactive human proxy."""

    def validate_problem(self, human_input: dict[str, Any]) -> dict[str, Any]:
        payload = human_input.get("payload", {})
        problem = ProblemDef(**payload.get("problem_def", {}))
        print("\n=== S0 问题定义书 ===")
        print(json.dumps(problem.model_dump(), ensure_ascii=False, indent=2))
        action = input("动作 [continue/edit/retry]: ").strip().lower()
        if action == "edit":
            print("输入 JSON 字段覆盖（直接回车表示无修改）：")
            edits = input("例如 {\"statement\":\"...\"}: ").strip()
            return {"action": "edit", "edits": edits or None}
        return {"action": action or "continue"}

    def de_noise(self, human_input: dict[str, Any]) -> dict[str, Any]:
        payload = human_input.get("payload", {})
        intel_map = IntelMap(**payload.get("intel_map", {}))
        print("\n=== S1 情报地图 ===")
        for src in intel_map.sources:
            print(f"[{src.channel}] {src.summary}")
        action = input("动作 [continue/mark]: ").strip().lower()
        return {"action": action or "continue"}

    def select_bet(self, human_input: dict[str, Any]) -> dict[str, Any]:
        payload = human_input.get("payload", {})
        opportunities = [
            Opportunity(**o) for o in payload.get("opportunities", [])
        ]
        print("\n=== S2 机会评分 ===")
        for idx, opp in enumerate(opportunities, 1):
            print(f"{idx}. {opp.title} (总分: {opp.total_score})")
        choice = input(f"选择下注机会编号 [1-{len(opportunities)}]: ").strip()
        try:
            idx = int(choice) - 1
            selected_id = opportunities[idx].id
        except (ValueError, IndexError):
            selected_id = opportunities[0].id
        return {"action": "continue", "selected_id": selected_id}

    def enrich_scenarios(self, human_input: dict[str, Any]) -> dict[str, Any]:
        payload = human_input.get("payload", {})
        concepts = [Concept(**c) for c in payload.get("concepts", [])]
        print("\n=== S3 概念发散 ===")
        for c in concepts:
            print(f"- {c.name}: {c.summary}")
        extra = input("补充场景（可选，直接回车跳过）：").strip()
        return {"action": "continue", "extra_scenarios": extra}

    def record_unanswerable(self, human_input: dict[str, Any]) -> dict[str, Any]:
        payload = human_input.get("payload", {})
        attacks = [Attack(**a) for a in payload.get("attacks", [])]
        print("\n=== S4 红队攻击 ===")
        decisions = []
        for attack in attacks:
            print(
                f"\n[{attack.persona.name}] -> {attack.target_concept_id}\n"
                f"  攻击：{attack.statement}\n"
                f"  建议修正：{attack.suggested_fix or '无'}\n"
                f"  是否致命：{attack.is_fatal}"
            )
            fix = input("  输入修正（直接回车表示接受建议，kill表示杀死概念）：").strip()
            if fix.lower() == "kill":
                decisions.append(
                    {
                        "concept_id": attack.target_concept_id,
                        "killed": True,
                        "reason": attack.statement,
                    }
                )
            elif fix:
                decisions.append(
                    {"concept_id": attack.target_concept_id, "fix": fix}
                )
            elif attack.suggested_fix:
                decisions.append(
                    {
                        "concept_id": attack.target_concept_id,
                        "fix": attack.suggested_fix,
                    }
                )
        return {"action": "continue", "decisions": decisions}

    def arbitrate(self, human_input: dict[str, Any]) -> dict[str, Any]:
        payload = human_input.get("payload", {})
        reviews = [Review(**r) for r in payload.get("reviews", [])]
        print("\n=== S5 专家评审 ===")
        for r in reviews:
            print(f"[{r.dimension}] {r.verdict} ({r.score}/5) - {r.reasoning}")
        note = input("综合裁决备注（可选）：").strip()
        return {"action": "continue", "arbitration_note": note}


class AutoHumanProxy(HumanProxy):
    """Non-interactive proxy that always continues with sensible defaults.

    Useful for smoke tests and automated runs.
    """

    def validate_problem(self, human_input: dict[str, Any]) -> dict[str, Any]:
        return {"action": "continue"}

    def de_noise(self, human_input: dict[str, Any]) -> dict[str, Any]:
        return {"action": "continue"}

    def select_bet(self, human_input: dict[str, Any]) -> dict[str, Any]:
        payload = human_input.get("payload", {})
        opportunities = payload.get("opportunities", [])
        selected_id = opportunities[0]["id"] if opportunities else ""
        return {"action": "continue", "selected_id": selected_id}

    def enrich_scenarios(self, human_input: dict[str, Any]) -> dict[str, Any]:
        return {"action": "continue"}

    def record_unanswerable(self, human_input: dict[str, Any]) -> dict[str, Any]:
        payload = human_input.get("payload", {})
        attacks = payload.get("attacks", [])
        decisions = []
        for attack in attacks:
            if attack.get("suggested_fix"):
                decisions.append(
                    {
                        "concept_id": attack["target_concept_id"],
                        "fix": attack["suggested_fix"],
                    }
                )
        return {"action": "continue", "decisions": decisions}

    def arbitrate(self, human_input: dict[str, Any]) -> dict[str, Any]:
        return {"action": "continue"}
