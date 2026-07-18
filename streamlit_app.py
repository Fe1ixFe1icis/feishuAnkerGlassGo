"""Streamlit human-in-the-loop interface for the GlassGo workflow."""

import json
import uuid
from typing import Any

import streamlit as st
from langgraph.types import Command

from glassgo_workflow.examples.anker_glassgo import (
    DEFAULT_CONSTRAINTS,
    DEFAULT_INPUT,
)
from glassgo_workflow.graph import WorkflowGraph
from glassgo_workflow.human_proxy import AutoHumanProxy
from glassgo_workflow.llm import get_llm


def init_state() -> None:
    if "thread_id" not in st.session_state:
        st.session_state.thread_id = str(uuid.uuid4())
    if "workflow" not in st.session_state:
        st.session_state.workflow = WorkflowGraph(
            llm=get_llm(), human_proxy=AutoHumanProxy()
        )
    if "running" not in st.session_state:
        st.session_state.running = False
    if "messages" not in st.session_state:
        st.session_state.messages = []


def render_problem_def(problem_def: dict[str, Any]) -> None:
    st.subheader("问题定义书")
    st.write(f"**陈述**：{problem_def.get('statement', '')}")
    st.write(f"**品类锚点**：{problem_def.get('category_anchor', '')}")
    st.write(f"**核心张力**：{problem_def.get('core_tension', '')}")
    st.write(f"**能力匹配**：{problem_def.get('capability_match', '')}")
    if problem_def.get("key_assumptions"):
        st.write("**关键假设**：")
        for assumption in problem_def["key_assumptions"]:
            st.write(f"- {assumption}")


def render_intel_map(intel_map: dict[str, Any]) -> None:
    st.subheader("情报地图")
    for src in intel_map.get("sources", []):
        with st.expander(f"{src.get('channel', '')} 渠道"):
            st.write(src.get("summary", ""))
            for finding in src.get("findings", []):
                st.write(f"- {finding.get('claim', '')}")


def render_opportunities(opportunities: list[dict[str, Any]]) -> str:
    st.subheader("机会评分")
    options = {
        f"{o['title']} (总分 {o.get('total_score', 0)})": o["id"]
        for o in opportunities
    }
    choice = st.radio("选择下注方向", list(options.keys()))
    return options[choice]


def render_concepts(concepts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    st.subheader("概念发散")
    enriched = []
    for c in concepts:
        with st.expander(f"{c.get('name', '')}: {c.get('summary', '')}"):
            st.write(f"形态：{c.get('form_factor', '')}")
            st.write(f"目标用户：{c.get('target_user', '')}")
            st.write("核心功能：")
            for f in c.get("key_features", []):
                st.write(f"- {f}")
            extra = st.text_area(
                f"补充场景 - {c.get('name', '')}", key=f"scenario_{c.get('id', '')}"
            )
            c_copy = c.copy()
            if extra:
                c_copy["extra_scenarios"] = extra
            enriched.append(c_copy)
    return enriched


def render_attacks(attacks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    st.subheader("红队攻击")
    decisions = []
    for a in attacks:
        persona = a.get("persona", {})
        with st.expander(
            f"[{persona.get('name', '')}] 攻击 {a.get('target_concept_id', '')}"
        ):
            st.write(f"**攻击**：{a.get('statement', '')}")
            st.write(f"**建议修正**：{a.get('suggested_fix') or '无'}")
            st.write(f"**是否致命**：{a.get('is_fatal', False)}")
            action = st.selectbox(
                "处理",
                ["接受建议修正", "自定义修正", "杀死概念", "忽略"],
                key=f"attack_action_{id(a)}",
            )
            custom_fix = st.text_input(
                "自定义修正", key=f"attack_fix_{id(a)}", value=""
            )
            if action == "接受建议修正" and a.get("suggested_fix"):
                decisions.append(
                    {
                        "concept_id": a["target_concept_id"],
                        "fix": a["suggested_fix"],
                    }
                )
            elif action == "自定义修正" and custom_fix:
                decisions.append(
                    {"concept_id": a["target_concept_id"], "fix": custom_fix}
                )
            elif action == "杀死概念":
                decisions.append(
                    {
                        "concept_id": a["target_concept_id"],
                        "killed": True,
                        "reason": a.get("statement", ""),
                    }
                )
    return decisions


def render_reviews(reviews: list[dict[str, Any]]) -> dict[str, Any]:
    st.subheader("专家评审")
    for r in reviews:
        with st.expander(f"{r.get('dimension', '')}: {r.get('verdict', '')}"):
            st.write(f"评分：{r.get('score', 0)}/5")
            st.write(f"理由：{r.get('reasoning', '')}")
    note = st.text_area("综合裁决备注")
    return {"arbitration_note": note}


def render_human_form(stage: str, payload: dict[str, Any]) -> Any:
    """Render the right form for the current human breakpoint."""
    if stage == "S0":
        render_problem_def(payload.get("problem_def", {}))
        return {"action": "continue"}
    if stage == "S1":
        render_intel_map(payload.get("intel_map", {}))
        return {"action": "continue"}
    if stage == "S2":
        selected_id = render_opportunities(payload.get("opportunities", []))
        return {"action": "continue", "selected_id": selected_id}
    if stage == "S3":
        enriched = render_concepts(payload.get("concepts", []))
        extras = [c.get("extra_scenarios", "") for c in enriched]
        return {"action": "continue", "extra_scenarios": extras}
    if stage == "S4":
        decisions = render_attacks(payload.get("attacks", []))
        return {"action": "continue", "decisions": decisions}
    if stage == "S5":
        return render_reviews(payload.get("reviews", []))
    return {"action": "continue"}


def render_proposal(state: dict[str, Any]) -> None:
    proposal = state.get("proposal")
    if not proposal:
        st.error("未生成提案")
        return
    data = proposal.model_dump() if hasattr(proposal, "model_dump") else proposal
    st.success("工作流完成！")
    st.header(data.get("title", "最终提案"))
    st.write(f"**定位**：{data.get('positioning', '')}")
    st.write(f"**核心产品**：{data.get('core_product', '')}")
    if data.get("product_system"):
        st.write("**产品系统**：")
        for item in data["product_system"]:
            st.write(f"- {item}")
    st.write(f"**定价**：{data.get('pricing', '')}")
    st.write(f"**目标**：{data.get('target', '')}")
    if data.get("roadmap"):
        st.write("**路线图**：")
        for item in data["roadmap"]:
            st.write(f"- {item}")
    if data.get("key_decisions"):
        st.write("**人类关键决策**：")
        for item in data["key_decisions"]:
            st.write(f"- {item}")


def main() -> None:
    st.set_page_config(
        page_title="GlassGo · AI 原生产品定义工作流",
        page_icon="🥽",
        layout="wide",
    )
    st.title("Anker GlassGo · AI 原生产品定义工作流")
    st.caption("六阶段 × 五角色 · 记忆隔离 · 对抗前置 · 人类裁决")

    init_state()
    workflow = st.session_state.workflow
    config = {"configurable": {"thread_id": st.session_state.thread_id}}

    # Sidebar progress
    stages = ["S0", "S1", "S2", "S3", "S4", "S5", "S6"]
    current_stage = "S0"
    if st.session_state.running and "state" in st.session_state:
        current_stage = st.session_state.state.get("current_stage", "S0")
    stage_index = stages.index(current_stage) if current_stage in stages else 0
    st.sidebar.progress((stage_index + 1) / len(stages))
    st.sidebar.write(f"当前阶段：{current_stage}")

    # Start / reset
    col1, col2 = st.columns(2)
    with col1:
        if st.button("▶ 开始运行"):
            st.session_state.running = True
            st.session_state.state = workflow.graph.invoke(
                {
                    "raw_input": DEFAULT_INPUT,
                    "constraints": DEFAULT_CONSTRAINTS,
                    "current_stage": "S0",
                    "human_decisions": [],
                },
                config,
            )
            st.rerun()
    with col2:
        if st.button("🔄 重置"):
            st.session_state.thread_id = str(uuid.uuid4())
            st.session_state.running = False
            st.session_state.pop("state", None)
            st.rerun()

    if not st.session_state.running:
        st.info("点击「开始运行」启动工作流。")
        return

    # Check for interrupt
    graph_state = workflow.graph.get_state(config)
    has_interrupt = False
    interrupt_data = None
    if graph_state and graph_state.tasks:
        for task in graph_state.tasks:
            if task.interrupts:
                has_interrupt = True
                interrupt_data = task.interrupts[0].value
                break

    if has_interrupt and interrupt_data:
        stage = interrupt_data.get("stage", "")
        payload = interrupt_data.get("payload", {})
        st.info(f"⏸ 人类断点：{stage}")
        human_response = render_human_form(stage, payload)
        if st.button("继续"):
            cmd = Command(resume=human_response)
            st.session_state.state = workflow.graph.invoke(cmd, config)
            st.rerun()
    else:
        render_proposal(st.session_state.state)


if __name__ == "__main__":
    main()
