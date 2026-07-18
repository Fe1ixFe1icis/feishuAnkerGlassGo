# Anker GlassGo 产品提案

> **Power Every Pair. 为每一副眼镜供电。**
> AI 眼镜的跨品牌补能系统 —— 一次「AI 原生」产品定义实验的可视化提案

一次完整的产品定义过程（市场情报 → 机会挖掘 → 概念发散 → 红队对抗 → 可行性评审 → 收敛成案）与最终产品提案。后端使用 **LangGraph** 实现六阶段 × 七角色的对抗式多 Agent 工作流，支持人类断点介入、记忆隔离与证据链追溯。

## 项目状态

- ✅ LangGraph 工作流已跑通 S0 → S6，含 6 个人类断点（S0–S5）
- ✅ 端到端测试通过：`pytest tests/` 6 项全部通过
- ✅ 支持 OpenAI / Anthropic LLM，通过 `.env` 配置 API Key
- ✅ 提供 CLI 与 Streamlit 两种人机交互入口

---


## 页面板块

| 板块 | 内容 |
|---|---|
| Hero | 核心数据：2025 年全球 AI 眼镜出货 870 万台（+322%，Omdia） |
| 市场风暴 | 出货量增长图：实际数据达机构预测 1.7 倍 |
| 断裂带 | 五品牌充电方案互不兼容矩阵；官方 ¥399–599 / 白牌 ¥46–299 / GlassGo $59.99 价格带 |
| 产品系统 | GlassGo Pocket（随身充电盒）· Clip（边充模块）· App（电量中枢） |
| AI 原生工作流 | 六阶段 × 七角色，角色隔离防止"AI 说服 AI" |
| 红队对抗 | 5 个用户替身的第一人称攻击与方案修正实录 |
| 市场测算 | 2027 年配件市场三情景：$1.1 / 1.9 / 2.8 亿美元 |
| 路线图 | P0 众筹验证 → P1 量产扩展 → P2 B2B 模组授权 |
| 方法论对比 | AI 驱动 vs 经验驱动的逐环节对照 |


## 文件结构

```
├── index.html                         # 静态展示页
├── workflow-demo.html                 # 交互式工作流演示
├── DESCRIBE.md                        # 对抗式多 Agent 工作流框架设计
├── README.md                          # 本文件
├── pyproject.toml                     # Python 项目配置
├── requirements.txt                   # Python 依赖
├── .env.example                       # API Key 模板
├── streamlit_app.py                   # Streamlit 人机界面
├── scripts/run_cli.py                 # 命令行入口包装
├── src/glassgo_workflow/              # 可运行的工作流后端
│   ├── agents/                        # S0-S6 Agent 实现
│   ├── prompts/                       # Prompt 模板
│   ├── examples/                      # 默认案例
│   ├── config.py                      # 配置读取
│   ├── evidence.py                    # 证据链工具
│   ├── models.py                      # Pydantic 数据模型
│   ├── state.py                       # LangGraph 状态
│   ├── graph.py                       # LangGraph 状态机
│   ├── human_proxy.py                 # 人类代理接口（CLI / Auto）
│   ├── llm.py                         # LLM 抽象层（OpenAI / Anthropic）
│   └── main.py                        # CLI 主入口
└── tests/                             # 单元与端到端测试
```

## 核心设计

- **六阶段 × 七角色**：S0 提问教练 → S1 情报分析师 → S2 机会侦探 → S3 概念设计师 → S4 用户替身红队 → S5 专家委员会 → S6 书记官。
- **记忆隔离**：每个 Agent 只能看到上游阶段产出的结构化结果，看不到中间推理，防止"AI 说服 AI"的同温层。
- **证据链**：`Fact` 与 `Inference` 分离，所有关键判断必须附带可核查信源或推理依据与置信度。
- **人类断点**：S0–S5 每个阶段后设置 `interrupt`，由人类做最终价值判断后再继续执行。
- **对抗前置**：红队以第一人称 persona 攻击候选概念，未回应的攻击直接触发概念修正或 kill。

## 运行方式

1. 配置环境：
   ```bash
   copy .env.example .env
   # 编辑 .env，填入 OPENAI_API_KEY 或 ANTHROPIC_API_KEY
   ```

2. 安装依赖：
   ```bash
   py -m venv .venv
   .venv\Scripts\activate
   pip install -e .
   ```

3. 命令行运行：
   ```bash
   # 交互模式：在每个阶段停下来等待人类判断
   py scripts/run_cli.py

   # 全自动模式（用于测试，使用 AutoHumanProxy 自动通过所有断点）
   py scripts/run_cli.py --auto

   # 自定义问题与约束
   py scripts/run_cli.py --input "为露营人群设计便携储能配件" --constraints '{"brand":"Anker"}' --auto
   ```

4. 直接以模块方式运行 CLI：
   ```bash
   py -m glassgo_workflow.main --auto
   ```

5. Streamlit 可视化界面：
   ```bash
   py -m streamlit run streamlit_app.py
   ```

6. 运行测试：
   ```bash
   pytest tests/
   ```

## 数据来源与声明

- 市场数据来自公开信源：Omdia、IDC、TrendForce、洛图科技、Wellsenn XR、依视路陆逊梯卡财报、安克创新 2025 年年报及公开报道
- 产品规格、渗透率、财务测算为**提案级估算假设**，非信源直接数据
- 本项目为产品方法论实验的演示材料与可运行原型，与 Anker 公司无官方关联