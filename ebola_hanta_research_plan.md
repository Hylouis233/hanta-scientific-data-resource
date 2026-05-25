# Ebola 与 Hanta 自动化科研项目建设计划

生成日期：2026-05-25  
目标目录：`~/d/autoresearch/`

## 1. 总体目标

在 `~/d/autoresearch/` 下建设两个相互独立、可复现、可由 AI agent 长期协作推进的病毒研究项目：

```text
~/d/autoresearch/
├── ebola/
└── hanta/
```

两个项目均参考当前 `~/d/nipah` 的病毒流行病学研究框架，同时吸收本机 ResearchOps 配置的硬约束：固定数据版本、固定评估入口、固定实验记录、固定可复现流程。

核心原则：

1. **ResearchOps 作底座**：DVC 管理数据版本，Snakemake 管理流程，MLflow 记录实验，`evaluation/evaluate.sh` 作为统一评估入口。
2. **Nipah 作领域模板**：继承 `outbreaks/`、`genomic_data/`、`params/`、`scripts/`、`results/`、`manuscripts/`、`docs/` 等目录思想。
3. **科研诚信优先**：清晰标注真实数据、文献参数、模型推断、模拟数据；禁止 agent 为了改善结果而改动锁定数据、评估指标或基线。
4. **两个病毒分开建仓式管理**：Ebola 和 Hanta 不混入 Nipah 仓库，也不彼此混放，避免数据、论文、图表和实验版本纠缠。

## 2. 建议目录结构

### 2.1 顶层结构

```text
~/d/autoresearch/
├── README.md
├── ebola/
│   ├── AGENTS.md
│   ├── CLAUDE.md
│   ├── README.md
│   ├── pyproject.toml
│   ├── params.yaml
│   ├── dvc.yaml
│   ├── Snakefile
│   ├── configs/
│   ├── data/
│   ├── outbreaks/
│   ├── genomic_data/
│   ├── protein_data/
│   ├── params/
│   ├── scripts/
│   ├── evaluation/
│   ├── reports/
│   ├── results/
│   ├── docs/
│   └── manuscripts/
└── hanta/
    ├── AGENTS.md
    ├── CLAUDE.md
    ├── README.md
    ├── pyproject.toml
    ├── params.yaml
    ├── dvc.yaml
    ├── Snakefile
    ├── configs/
    ├── data/
    ├── outbreaks/
    ├── host_data/
    ├── environment/
    ├── genomic_data/
    ├── params/
    ├── scripts/
    ├── evaluation/
    ├── reports/
    ├── results/
    ├── docs/
    └── manuscripts/
```

### 2.2 共同目录含义

| 目录 | 用途 |
|---|---|
| `data/` | 原始或规范化核心数据，进入 DVC 管理，默认只读 |
| `outbreaks/` | 暴发级数据集、病例时间序列、linelist、README 和来源说明 |
| `genomic_data/` | GenBank/NCBI/Nextstrain 等来源的基因组、metadata、alignment |
| `params/` | 建模参数、文献参数表、CFR/R0/潜伏期等 |
| `scripts/` | 数据生成、建模、可视化、系统发育、地图脚本 |
| `evaluation/` | 固定评估协议，含锁定指标和运行入口 |
| `reports/` | 当前实验指标、审计报告、数据真实性报告、执行记录 |
| `results/` | 图表、模型输出、中间分析结果、投稿候选图 |
| `docs/` | 数据源说明、会议记录、项目组织、复现说明 |
| `manuscripts/` | LaTeX/Markdown 论文草稿、补充材料、图表清单 |

## 3. Ebola 项目计划

### 3.1 研究定位

建议标题方向：

> Ebola virus disease transmission heterogeneity, outbreak control, and genomic epidemiology across Central and West Africa

Ebola 项目应以“多次大型暴发的人际传播、干预效果和分子流行病学”为主线。它比 Nipah 更适合做传播动力学和干预建模，因为 Ebola 有更大规模的暴发数据，尤其是 2013–2016 西非疫情。

### 3.2 核心研究问题

1. 不同 Ebola 暴发中的 R0/Rt、CFR、潜伏期、序列间隔有何差异？
2. 葬礼传播、院内传播、家庭传播、社区传播在不同阶段的相对贡献是什么？
3. 接触者追踪、隔离、疫苗、环形疫苗接种、入境筛查等干预措施如何改变疫情轨迹？
4. West Africa 2013–2016 是否可作为主数据集构建可推广的传播模型？
5. EBOV、SUDV、BDBV 等 Ebolavirus 物种在传播动力学和病死率上有何差异？
6. 基因组系统发育能否重建跨地区、跨国传播路径？

### 3.3 建议 outbreaks 子目录

```text
ebola/outbreaks/
├── Yambuku_DRC_1976/
├── Kikwit_DRC_1995/
├── Gulu_Uganda_2000/
├── West_Africa_2013_2016/
├── DRC_Equateur_2018/
├── North_Kivu_DRC_2018_2020/
├── Uganda_Sudan_ebolavirus_2022/
└── Global_Data/
```

每个暴发目录建议包含：

```text
README.md
cases_timeseries.csv
linelist.csv              # 如果公开可得
metadata.yaml
sources.bib
source_notes.md
```

### 3.4 数据源优先级

P0 数据源：

- WHO Ebola situation reports
- CDC Ebola outbreak summaries
- peer-reviewed linelist / time-series papers
- GenBank Ebola virus genomes
- Nextstrain Ebola builds and metadata, if available

P1 数据源：

- HDX / humanitarian data portals
- national ministry of health reports
- published supplementary tables
- Our World in Data or curated public repositories, if source-traceable

数据引入规则：

1. 所有病例数据必须记录来源、下载日期、字段定义和清洗步骤。
2. 原始数据保存在 `data/raw/` 或 outbreak 目录的 `raw/`，不得覆盖。
3. 清洗数据放入 `data/processed/` 或 outbreak 目录的 `processed/`。
4. 若数据为人工整理，应在 `source_notes.md` 说明逐项来源。

### 3.5 分析模块

建议脚本模块：

```text
ebola/scripts/
├── data_generation/
│   ├── build_outbreak_timeseries.py
│   ├── extract_linelist.py
│   └── validate_sources.py
├── transmission_modeling/
│   ├── estimate_rt.py
│   ├── seir_model.py
│   ├── branching_process.py
│   └── superspreading_analysis.py
├── intervention_simulation/
│   ├── isolation_scenarios.py
│   ├── vaccination_scenarios.py
│   └── contact_tracing_scenarios.py
├── genomics/
│   ├── download_genomes.py
│   ├── filter_metadata.py
│   └── build_alignment.py
├── phylogenetics/
│   ├── prepare_beast_xml.py
│   ├── parse_tree.py
│   └── phylogeography.py
└── visualization/
    ├── plot_epidemic_curves.py
    ├── plot_rt.py
    ├── plot_intervention.py
    └── plot_phylogeography.py
```

### 3.6 预期结果目录

```text
ebola/results/
├── figures/
├── reports/
├── transmission_tracing/
├── rt_estimation/
├── intervention_simulation/
├── phylogeography/
├── sensitivity_analysis/
└── submission_bundle/
```

### 3.7 论文图表候选

1. 全球 Ebola 暴发时间线与地理分布图。
2. 主要暴发的 epidemic curves 对比图。
3. R0/Rt 与干预时间点叠加图。
4. 葬礼、医院、社区传播贡献分解图。
5. West Africa 2013–2016 干预模拟图。
6. Ebolavirus 物种 CFR/R0 对比图。
7. Genomic phylogeography / cross-border spread 图。
8. 敏感性分析 tornado plot 或 PRCC 图。

## 4. Hanta 项目计划

### 4.1 研究定位

建议标题方向：

> Hantavirus host ecology, environmental drivers, and spatial spillover risk across Eurasia and the Americas

Hanta 项目不应完全套用 Ebola/Nipah 的人际传播链框架。汉坦病毒的核心问题更偏向“宿主啮齿动物—环境—人类暴露—空间溢出风险”，只有 Andes virus 等少数场景适合做人际传播子模块。

### 4.2 核心研究问题

1. 不同 Hantavirus 物种与宿主啮齿动物之间的对应关系是否稳定？
2. 环境变量，如温度、降水、NDVI、土地利用、海拔、人类密度，如何解释 HFRS/HCPS 风险？
3. 旧大陆 HFRS 与新大陆 HCPS 的空间生态驱动是否不同？
4. Andes virus 的人际传播与其他汉坦病毒相比有何特殊性？
5. S/M/L 三节段基因组的系统发育是否提示 reassortment 或宿主转换？
6. 中国、韩国、欧洲、美洲的数据能否形成跨区域风险预测框架？

### 4.3 建议 outbreaks / regions 子目录

```text
hanta/outbreaks/
├── Four_Corners_USA_1993/
├── Andes_Virus_Argentina_Chile/
├── Europe_PUUV_SEOV_DOBV/
├── China_HFRS_Longitudinal/
├── Korea_Hantaan_Classic/
└── Global_Data/
```

### 4.4 Hanta 专属目录

```text
hanta/host_data/
├── rodent_occurrences/
├── host_trait_table.csv
├── reservoir_species_index.csv
└── sources.md

hanta/environment/
├── climate/
├── landcover/
├── elevation/
├── ndvi/
├── human_population/
└── environmental_covariates.csv

hanta/genomic_data/
├── segment_S/
├── segment_M/
├── segment_L/
├── metadata/
└── alignments/
```

### 4.5 数据源优先级

P0 数据源：

- GenBank Hantavirus S/M/L segment sequences
- GBIF rodent occurrence records
- WHO/CDC/ECDC hantavirus surveillance summaries
- 中国 HFRS 长期监测相关文献和公开统计资料
- peer-reviewed HCPS/HFRS outbreak reports

P1 数据源：

- WorldClim / CHELSA climate variables
- MODIS NDVI or other vegetation indices
- ESA/GlobCover/Copernicus land cover
- SRTM elevation
- WorldPop or GPW human population density

数据引入规则：

1. 宿主分布与病例数据必须分开存储，避免把宿主出现点误当成人类病例。
2. HFRS 和 HCPS 必须在数据表中明确标注。
3. 病毒物种、宿主物种、地理区域、基因片段必须使用标准化字段。
4. 所有环境栅格需要记录分辨率、坐标系、下载日期和裁剪范围。

### 4.6 分析模块

建议脚本模块：

```text
hanta/scripts/
├── data_generation/
│   ├── build_case_dataset.py
│   ├── build_host_occurrence_dataset.py
│   └── validate_sources.py
├── host_ecology/
│   ├── host_virus_network.py
│   ├── host_trait_analysis.py
│   └── reservoir_overlap.py
├── landscape_epidemiology/
│   ├── extract_environmental_covariates.py
│   ├── risk_model.py
│   ├── spatial_cv.py
│   └── risk_mapping.py
├── genomics/
│   ├── download_segments.py
│   ├── filter_segments.py
│   └── align_segments.py
├── reassortment_analysis/
│   ├── compare_segment_trees.py
│   └── detect_reassortment_candidates.py
└── visualization/
    ├── plot_host_network.py
    ├── plot_risk_maps.py
    ├── plot_environment_effects.py
    └── plot_segment_phylogenies.py
```

### 4.7 预期结果目录

```text
hanta/results/
├── figures/
├── reports/
├── risk_maps/
├── host_virus_association/
├── landscape_epidemiology/
├── segment_phylogeny/
├── reassortment_analysis/
├── sensitivity_analysis/
└── submission_bundle/
```

### 4.8 论文图表候选

1. 全球 HFRS/HCPS 分布与病毒物种地图。
2. 宿主啮齿动物—病毒网络图。
3. 环境变量对溢出风险的贡献图。
4. 中国/欧洲/美洲重点区域风险地图。
5. 旧大陆 vs 新大陆 Hantavirus 比较图。
6. S/M/L 三节段系统发育树对比图。
7. reassortment candidate summary 图。
8. 空间交叉验证性能图。

## 5. 共同 ResearchOps 规范

### 5.1 固定评估入口

每个项目都应保留：

```bash
bash evaluation/evaluate.sh configs/experiment.yaml
```

该命令应输出：

```text
reports/current_metrics.json
reports/tables/main_results.csv
```

### 5.2 DVC 规范

每个项目单独初始化 DVC：

```bash
cd ~/d/autoresearch/ebola
dvc init
dvc remote add -d research-s3 s3://dvc-store/ebola
dvc remote modify research-s3 endpointurl http://127.0.0.1:9000

dvc remote modify --local research-s3 access_key_id research_admin
dvc remote modify --local research-s3 secret_access_key '<MINIO_ROOT_PASSWORD>'
```

Hanta 同理：

```bash
cd ~/d/autoresearch/hanta
dvc init
dvc remote add -d research-s3 s3://dvc-store/hanta
dvc remote modify research-s3 endpointurl http://127.0.0.1:9000
```

注意：本计划不写入密钥，密钥只进入 `.dvc/config.local`。

### 5.3 Snakemake 规范

初始 `Snakefile` 至少包含：

```text
rule all:
    input:
        "reports/current_metrics.json",
        "reports/tables/main_results.csv"

rule evaluate:
    output:
        "reports/current_metrics.json"
    shell:
        "bash evaluation/evaluate.sh configs/experiment.yaml"
```

后续再逐步扩展数据下载、清洗、建模、绘图、论文图表生成规则。

### 5.4 MLflow 规范

每次正式实验记录：

- Git commit hash
- DVC data version
- params.yaml
- configs/experiment.yaml
- metrics
- figures/artifacts
- runtime environment
- random seed

### 5.5 Agent 约束

每个项目的 `AGENTS.md` 应至少包含：

```text
Never modify without explicit approval:
- data/
- evaluation/locked_metrics.py
- evaluation/locked_splits.py
- evaluation/run_protocol.py
- reports/baseline/
- dvc.yaml
- .dvc/

After changing model or analysis code:
1. Run unit tests if available.
2. Run bash evaluation/evaluate.sh configs/experiment.yaml.
3. Report all metrics, not only the best metric.
4. Do not change random seeds unless explicitly instructed.

Scientific integrity:
- Do not tune on the final test set.
- Do not remove hard cases.
- Do not weaken baselines.
- Do not change metric formulas.
- Do not report only the best seed.
```

## 6. 数据真实性分级

建议两个项目共同采用以下标记：

| 标记 | 含义 | 是否可用于正式论文 |
|---|---|---|
| 🟢 真实数据 | 来自 WHO/CDC/NCBI/GBIF/公开数据库/同行评审文献 | 可以 |
| 🟡 文献参数 | 来自文献的 R0、CFR、潜伏期、宿主参数等 | 可以，需引用 |
| 🟠 模型推断 | 基于真实数据拟合或估计 | 可以，需说明方法和不确定性 |
| 🔵 模拟数据 | 用于方法验证或演示 | 不可冒充真实结果 |
| 🔴 未核实数据 | 来源不完整或未追溯 | 不进入正式分析 |

每个数据集 README 应包含：

```text
Data authenticity: 🟢/🟡/🟠/🔵/🔴
Source:
Download date:
Processing script:
Known limitations:
Use in manuscript: yes/no/conditional
```

## 7. 第一阶段执行清单

### Phase 1: 建立骨架

- [ ] 创建 `~/d/autoresearch/README.md`
- [ ] 创建 `~/d/autoresearch/ebola/`
- [ ] 创建 `~/d/autoresearch/hanta/`
- [ ] 从 ResearchOps 模板复制基础文件
- [ ] 写入两个项目的 `CLAUDE.md`
- [ ] 写入两个项目的 `AGENTS.md`
- [ ] 写入两个项目的 `README.md`
- [ ] 创建标准目录树

### Phase 2: 数据源规划

- [ ] Ebola 数据源清单：WHO、CDC、GenBank、Nextstrain、文献
- [ ] Hanta 数据源清单：GenBank、GBIF、CDC/ECDC/WHO、中国 HFRS 文献、环境数据
- [ ] 为每个 P0 数据源写 `docs/data_sources.md`
- [ ] 为每个项目写 `docs/data_authenticity_policy.md`

### Phase 3: 最小可复现流程

- [ ] 创建 `configs/experiment.yaml`
- [ ] 创建 `evaluation/evaluate.sh`
- [ ] 创建 `evaluation/run_protocol.py`
- [ ] 创建 `evaluation/locked_metrics.py`
- [ ] 创建 `reports/current_metrics.json` 的最小输出逻辑
- [ ] 创建 `Snakefile`
- [ ] 创建 `dvc.yaml`

### Phase 4: 初始研究数据集

Ebola：

- [ ] 先整理 West Africa 2013–2016 周/月病例时间序列
- [ ] 再整理 North Kivu 2018–2020
- [ ] 建立 Global_Data 汇总表

Hanta：

- [ ] 先整理全球 virus-host-region 索引表
- [ ] 再整理 GBIF rodent occurrence 数据方案
- [ ] 建立 China HFRS / Four Corners / Andes virus 三个重点数据分支

### Phase 5: 初始图表和报告

Ebola：

- [ ] 暴发时间线
- [ ] epidemic curves
- [ ] R0/Rt 参数综述图
- [ ] 干预情景框架图

Hanta：

- [ ] 全球病毒类型分布图
- [ ] 宿主—病毒网络图
- [ ] 环境变量数据覆盖图
- [ ] S/M/L 片段数据可用性图

## 8. 下一步建议

切换到工作路径后，建议先执行：

```bash
cd ~/d/autoresearch
```

然后按以下顺序继续：

1. 创建 `README.md`，说明 `ebola/` 与 `hanta/` 的关系。
2. 复制 ResearchOps 模板到两个项目。
3. 写两个项目的 `CLAUDE.md` 和 `AGENTS.md`。
4. 初始化 Git/DVC 前先确认是否希望两个项目分别为 Git 仓库，还是 `autoresearch` 作为一个 monorepo。
5. 暂时不要下载数据，先把数据源清单和真实性策略写清楚。

## 9. 关键决策点

正式执行前需要确认：

1. **仓库结构**：`autoresearch` 一个 monorepo，还是 `ebola` / `hanta` 两个独立 Git 仓库？
2. **DVC remote**：是否使用本机 MinIO 的 `s3://dvc-store/ebola` 和 `s3://dvc-store/hanta`？
3. **论文目标**：两个项目是否都以可投稿论文为目标，还是先做研究资产库？
4. **优先级**：先做 Ebola，先做 Hanta，还是两个骨架并行？

我的默认建议：

- 用 `~/d/autoresearch` 作为 monorepo。
- `ebola` 和 `hanta` 各自有独立 DVC remote。
- 先并行建立骨架，再优先推进 Ebola，因为 Ebola 数据更适合快速形成传播动力学结果。
- Hanta 前期多花时间做数据源和本体结构，避免把宿主、病例、环境和基因片段混成一张不可解释的大表。
