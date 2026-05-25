# AutoResearch 病毒研究工作区

本 monorepo 用于建设可复现、可审计、可由 AI agent 长期协作推进的病毒科研项目。

当前项目：

- `ebola/`：Ebola 暴发传播动力学、干预模拟与分子流行病学。当前优先推进。
- `hanta/`：Hantavirus 宿主生态、环境驱动与空间溢出风险。

共同 ResearchOps 约束：

- DVC 管理数据版本，真实数据必须保留来源、下载日期和处理脚本。
- Snakemake 管理流程，`evaluation/evaluate.sh configs/experiment.yaml` 是固定评估入口。
- MLflow 或等价实验记录应记录 Git commit、DVC data version、配置、指标、产物和随机种子。
- 数据真实性分级必须区分真实数据、文献参数、模型推断、模拟数据和未核实数据。
- 当前阶段不下载数据，不声称任何占位结果为真实科学发现。

详细计划见：[`ebola_hanta_research_plan.md`](./ebola_hanta_research_plan.md)。
