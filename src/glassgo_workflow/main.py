"""Command-line entry point for the workflow."""

import argparse
import json

from glassgo_workflow.graph import WorkflowGraph
from glassgo_workflow.human_proxy import CLIHumanProxy, AutoHumanProxy
from glassgo_workflow.llm import get_llm


DEFAULT_INPUT = (
    "在 AI 眼镜行业寻找安克可切入的补能机会，"
    "设计一个跨品牌的能源确定性产品系统。"
)

DEFAULT_CONSTRAINTS = {
    "brand": "Anker",
    "category": "AI glasses charging accessory",
    "price_band": "$50-80",
    "timeline": "12-18 months to market",
}


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the GlassGo workflow.")
    parser.add_argument(
        "--input",
        type=str,
        default=DEFAULT_INPUT,
        help="Raw problem statement",
    )
    parser.add_argument(
        "--constraints",
        type=str,
        default=None,
        help='JSON string of constraints, e.g. {"brand":"Anker"}',
    )
    parser.add_argument(
        "--auto",
        action="store_true",
        help="Run without human interaction using AutoHumanProxy",
    )
    args = parser.parse_args()

    constraints = DEFAULT_CONSTRAINTS.copy()
    if args.constraints:
        constraints.update(json.loads(args.constraints))

    llm = get_llm()
    human_proxy = AutoHumanProxy() if args.auto else CLIHumanProxy()
    workflow = WorkflowGraph(llm=llm, human_proxy=human_proxy)

    print("启动 GlassGo 对抗式多 Agent 工作流...")
    print(f"问题：{args.input}")

    final_state = workflow.run(raw_input=args.input, constraints=constraints)

    print("\n=== 最终提案 ===")
    proposal = final_state.get("proposal")
    if proposal:
        print(json.dumps(proposal.model_dump(), ensure_ascii=False, indent=2))
    else:
        print("未生成提案")


if __name__ == "__main__":
    main()
