<div align="center">

<img src="./public/platform.svg" alt="OpenFinAgent platform diagram" width="100%" />

# OpenFinAgent

**开源金融 Agent 工作台——自带数据源也好，接入 [QVeris](https://qveris.ai) 一键满血也好。**

用多智能体团队组合投研、尽调和量化研究工作流，在免费公开数据、私有数据源、QVeris 1 万+ 经过验证的能力之间自由路由——只需一套 SDK、CLI、MCP 接口和（即将推出的）Web UI。

[English](./README.md) · [快速开始](#快速开始) · [数据源说明](./docs/providers/overview.md) · [路线图](#路线图) · [更新日志](./CHANGELOG.md)

[![License](https://img.shields.io/badge/license-Apache%202.0-064E3B?style=flat-square)](./LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-064E3B?style=flat-square)](https://www.python.org)
[![Status](https://img.shields.io/badge/status-v0.2%20rc-D97706?style=flat-square)](#路线图)
[![Built on QVeris](https://img.shields.io/badge/built%20on-QVeris-064E3B?style=flat-square)](https://qveris.ai)

</div>

> [!NOTE]
> **v0.2 release candidate。** 核心 `DataProvider` 协议、CLI、MCP server、离线 demo、doctor 诊断和示例工作流都已可用，但 API 在 v1.0 之前可能会有破坏性变更。欢迎试用、反馈、贡献——以生产负载为准请等到 v0.5 之后。

---

## 一句话说明

构建可用的金融 AI Agent 通常意味着把一堆破碎的部件拼起来：数据厂商 SDK、易碎的爬虫、手写 tool 定义、没有审计、没有成本上限、无法分享给同事。OpenFinAgent 用三个支柱来解决这个问题：

- **可插拔的数据层**——一套 `DataProvider` 协议同时覆盖免费公开源（FRED、yfinance、SEC EDGAR）、QVeris 的 1 万+ 经过验证的能力，以及任何你自己接入的私有数据（Bloomberg、Refinitiv、内部数据库）。一份 YAML 即可叠加或切换。
- **QVeris 作为推荐能力层**——覆盖最广、零配置、一个 API key 即可获得生产级数据。可选，绝不强制。
- **专为金融场景的 Agent 运行时**——YAML 工作流、角色化 LLM 步骤、审计日志、成本守卫，以及规划中的 Skill 注册中心和 Web workbench。

> **它不是什么：** 不是交易机器人、智能投顾或 ChatGPT 套壳。它是一个*研究和工作流*平台——服务于不想花两万美元订 Bloomberg 又要生产级工具链的分析师、PM、Fintech 工程师和独立研究者。

---

## 实际跑起来什么样

一条命令、免费数据源、一份完整备忘——实时 LLM 步骤只需要一个兼容 OpenAI 的 key。想先验证运行时，可以直接跑 `finagent demo NVDA`，完全离线、无网络、无数据源 key。

```console
$ finagent run earnings-deep-dive --input ticker=NVDA

╭─────────────────────────────────────────────────╮
│ Running earnings-deep-dive.yaml                 │
│ inputs   = {'ticker': 'NVDA'}                   │
│ providers = ['yfinance', 'sec_edgar']           │
╰─────────────────────────────────────────────────╯
→ fetch  profile…
✓ profile                   0.42s · $0.0000
→ fetch  quote…
✓ quote                     0.31s · $0.0000
→ fetch  filings…
✓ filings                   0.88s · $0.0000
→ agent  thesis…
✓ thesis                    6.10s · $0.0021
→ report report…
✓ report                    0.01s · $0.0000

╭─────────────────────────────────────────────╮
│ done · 7.7s · $0.0021                       │
│ report: reports/NVDA-2026-04-29.md          │
╰─────────────────────────────────────────────╯
```

每一步都被**追踪、缓存、按预算管控**。完整的审计日志在 `audit.jsonl`（每一次 Discover / Inspect / Call / LLM 事件占一行 JSON）。

想看实际产出长什么样？直接打开 [`examples/sample-report-NVDA.md`](./examples/sample-report-NVDA.md)。

---

## 当前 main 已发布功能

- **可插拔数据层**——三层供给（免费公开 / QVeris / 自带私有），一套统一协议。详见 [数据源](./docs/providers/overview.md)。
- **工作流 DSL**——用纯 YAML 描述研究流水线，可版本化、可分享、可复现。
- **MCP server**——`finagent mcp serve` 把整个 registry 暴露给 Claude Code、Cursor、Codex 等任何 MCP 客户端，仅通过三个元工具（discover / inspect / call）即可驱动。
- **成本与审计内建**——每次 Discover → Inspect → Call 都被追踪和按预算管控。开箱即用的 JSONL 审计日志。
- **CLI + Python API**——终端用 `finagent doctor`、`finagent demo`、`finagent init`、`finagent run`，Notebook 里 10 行代码驱动同一个 Runner。

**即将推出**（详见[路线图](#路线图)）：PyPI 发布、更多旗舰 workflow、Skill 注册中心（`finagent skill install ...`）、Web UI workbench。

---

## 快速开始

> 今天就能跑，要求 Python 3.10+。下面这条路径就是 CI 里在跑的同一条。

### 1. 安装

```bash
# 源码安装，当前可用：
git clone https://github.com/Leon-Drq/openfinagent.git
cd openfinagent
pip install -e .

# v0.2 PyPI 发布后：
# pip install openfinagent
```

### 2. 先检查环境

`doctor` 会告诉你当前环境哪些已经就绪，哪些是 live workflow 才需要补的配置。

```bash
finagent doctor --no-network
```

去掉 `--no-network` 会额外探测 SEC EDGAR、Yahoo Finance 和 PyPI 是否可达。

### 3. 先跑离线 demo

这一步不需要网络、不需要 OpenAI key、不需要任何数据源 key，用内置 sample provider 验证 workflow runner、provider 路由、报告输出和审计日志。

```bash
finagent demo NVDA
```

你也可以先初始化一个独立项目目录：

```bash
finagent init my-research-workspace
cd my-research-workspace
finagent doctor --no-network
finagent demo NVDA
```

### 4. 配置 OpenAI key

预置工作流里的 `agent` 步骤需要一次 LLM 调用，任何兼容 OpenAI Chat Completions 协议的服务都可以（真 OpenAI、Vercel AI Gateway、Azure、Groq、本地 llama.cpp 等）。

```bash
cp .env.example .env
# 编辑 .env 填入：
OPENAI_API_KEY=sk-...
# 可选：OPENAI_BASE_URL=https://gateway.ai.vercel.com/v1/openai
```

默认的两个 provider —— `yfinance` 和 `sec_edgar` —— **完全不需要 API key**。

### 5. 跑通实时预置工作流

```bash
finagent run earnings-deep-dive --input ticker=NVDA
```

会看到流式步骤输出，runner 会拉取 quote + profile + filings，调用 `gpt-4o-mini` 写一份备忘录，结果落到 `reports/NVDA-<date>.md`。普通笔记本上整个流程 5–10 秒、约 $0.002。

### 6. 从 Python 调用

```python
import asyncio
from finagent import ProviderRegistry, Runner
from finagent.providers.builtin import YFinanceProvider, SecEdgarProvider
from finagent.runtime.llm import LLMClient

async def main():
    registry = ProviderRegistry()
    registry.add(YFinanceProvider(), priority=1)
    registry.add(SecEdgarProvider(), priority=1)

    runner = Runner(registry, llm=LLMClient(), audit_path="audit.jsonl")
    result = await runner.run(
        "workflows/earnings-deep-dive.yaml",
        inputs={"ticker": "NVDA"},
    )
    print(result.report_path, f"${result.total_cost_usd:.4f}")
    await registry.teardown()

asyncio.run(main())
```

完整自包含脚本见 [`examples/quickstart.py`](./examples/quickstart.py)。

### 7. 接入 QVeris 或自有 provider

在工作流旁边放一个 `config.yaml`（模板见 [`config.example.yaml`](./config.example.yaml)）：

```yaml
providers:
  - { name: yfinance,  type: builtin.yfinance,  priority: 1 }
  - { name: sec_edgar, type: builtin.sec_edgar, priority: 1 }
  - { name: qveris,    type: builtin.qveris,    priority: 2,
      api_key: ${QVERIS_API_KEY}, budget_usd_per_run: 5.00 }
```

查看当前加载了哪些 provider：

```bash
finagent providers
```

自带 provider（Bloomberg / Refinitiv / 内部 API）的写法相同——继承 [`DataProvider`](./finagent/providers/base.py) 写 50–100 行子类，用 `type:` 引用即可。详见 [`docs/providers/overview.md`](./docs/providers/overview.md)。

### 8. 作为 MCP server 使用

```bash
pip install -e ".[mcp]"
```

```jsonc
// ~/.config/Claude/claude_desktop_config.json 或 Cursor settings.json
{
  "mcpServers": {
    "finagent": {
      "command": "finagent",
      "args": ["mcp", "serve"]
    }
  }
}
```

### 当前 v0.2 还没有的功能

`finagent auth login`、`finagent skill install`、Web UI 等都在[路线图](#路线图)上但还没发布。Star 仓库即可第一时间收到通知。

维护者发布 PyPI 包时可按 [`docs/release.md`](./docs/release.md) 执行 TestPyPI、PyPI Trusted Publishing 和 wheel 验证流程。

---

## 数据源

> **一套协议，任意组合，零厂商绑定。**

| 层级 | 示例 | 适用场景 |
|---|---|---|
| **免费公开源** | FRED · yfinance · SEC EDGAR · CoinGecko · Alpha Vantage | 原型、教学、个人研究。零成本，多数无需 API key。 |
| **QVeris**（推荐） | 1 万+ 经过验证的能力——股票、固收、另类、公告、新闻、基本面 | 生产级研究、广覆盖、不想自己签 30 份数据合同。 |
| **自带私有源** | Bloomberg · Refinitiv · FactSet · S&P · 内部数据库 · 私有 CSV | 机构用户、合规敏感工作流、已经付过钱的数据。 |

详见 [`docs/providers/overview.md`](./docs/providers/overview.md)。

---

## 路线图

- [x] **v0.2 rc** —— `DataProvider` 协议、5 个内置 provider（sample / yfinance / sec_edgar / fred / qveris）、工作流 YAML DSL、`finagent` CLI、`finagent init`、`finagent demo`、`finagent doctor`、兼容 OpenAI 协议的 LLM 步骤、审计日志、成本守卫、MCP server、release workflow、包验证。
- [ ] **v0.3** —— PyPI 发布收尾、更丰富示例、workflow catalog。
- [ ] **v0.4** —— Skill 注册中心（`finagent skill install ...`）、更丰富的 provider 目录、工作流模板。
- [ ] **v0.5** —— Web UI workbench（Next.js）、运行控制台、报告预览、审计时间线、Langfuse 追踪。
- [ ] **v0.6** —— 多租户部署、RBAC、自托管 Docker compose。
- [ ] **v1.0** —— 生产 SLA、企业 SSO、私有化 QVeris 桥接。

参见 [`CHANGELOG.md`](./CHANGELOG.md) 已发布功能详情。

---

## 参与共建

欢迎 PR。最快的贡献方式：

1. **加一个数据 provider**——你常用的免费源（Polygon / Tiingo / FMP / AKShare 等）还没支持？继承 [`DataProvider`](./finagent/providers/base.py) 写 50–100 行，参考 [`yfinance_provider.py`](./finagent/providers/builtin/yfinance_provider.py) 的写法。
2. **加一个工作流**——把你每周都做的分析放到 `workflows/<name>.yaml` 提 PR。
3. **完善运行时**——缓存、结构化输出、流式、重试——都可以做。

详见 [`CONTRIBUTING.md`](./CONTRIBUTING.md)。

---

## 免责声明

OpenFinAgent 是研究工具。输出可能错误、不完整或过时。本项目中任何内容都不构成投资、法律或税务建议。你需要为使用本工具做出的任何决策自行负责。

---

## 许可

Apache License 2.0 —— 详见 [`LICENSE`](./LICENSE)。
