# Agent-Harness-101

> Learn Agent Harness Engineering in Python — Architecture Patterns from Claude Code

[繁體中文](#繁體中文) | [English](#english)

## English

**Agent = Model + Harness.** The Claude Code source leak (2026-03-31) revealed that ~40% of the world's most capable coding agent's performance comes not from model intelligence, but from a meticulously engineered harness. This project teaches you those patterns through 6 layers of interactive lessons with runnable Python code.

All code examples are extracted from [instructkr/claw-code](https://github.com/instructkr/claw-code), a clean-room Python/Rust reimplementation of Claude Code's architecture.

### The 6 Layers

| Layer | What It Does | Claude Code Example |
|-------|-------------|-------------------|
| 🔁 Loop | Observe → Decide → Act → Verify → Update | `queryLoop()` — a single `while(true)` |
| 🛠️ Tools | Let the agent read, write, search, execute | 40 tools, 29K lines of definitions |
| 🧠 Context | Manage what the agent sees | 4-tier compaction, static/dynamic prompt split |
| 💾 Persistence | Remember across sessions | CLAUDE.md hierarchy + session store |
| ✅ Verification | Self-review before saying "done" | Hooks, cost tracking, parity audit |
| 🛑 Constraints | Define what the agent CANNOT do | 6-layer permission engine, OS sandbox |

### Quick Start

```bash
git clone https://github.com/jack-lin-ds-ai/agent-harness-101.git
cd agent-harness-101
pip install -r examples/requirements.txt
python examples/01_agent_loop.py
```

### Live Site

Visit [https://jack-lin-ds-ai.github.io/agent-harness-101](https://jack-lin-ds-ai.github.io/agent-harness-101)

### Project Structure

```
agent-harness-101/
├── src/
│   ├── pages/          # Astro pages (landing + layer detail)
│   ├── layouts/        # HTML shell
│   ├── components/     # Header, Footer, etc.
│   ├── content/        # Bilingual content (en/ + zh-TW/)
│   ├── snippets/       # Annotated code from claw-code (50-80 lines each)
│   ├── i18n/           # UI strings (en.json + zh-TW.json)
│   └── styles/         # CSS
├── examples/           # Runnable Python files (one per layer + full integration)
│   ├── 01_agent_loop.py
│   ├── 02_tool_system.py
│   ├── 03_context_manager.py
│   ├── 04_persistence.py
│   ├── 05_verification.py
│   ├── 06_constraints.py
│   └── 07_full_harness.py
├── docs/               # Architecture, contributing, references
└── .github/workflows/  # GitHub Pages auto-deploy
```

### References

- [instructkr/claw-code](https://github.com/instructkr/claw-code) — Clean-room Python/Rust rewrite of Claude Code
- [shareAI-lab/learn-claude-code](https://github.com/shareAI-lab/learn-claude-code) — 12-step educational harness
- [LangChain: Improving Deep Agents with Harness Engineering](https://blog.langchain.com/improving-deep-agents-with-harness-engineering/)
- [Martin Fowler: Harness Engineering](https://martinfowler.com/articles/exploring-gen-ai/harness-engineering.html)
- [HumanLayer: Skill Issue — Harness Engineering for Coding Agents](https://www.humanlayer.dev/blog/skill-issue-harness-engineering-for-coding-agents)

### License

MIT

---

## 繁體中文

**Agent = 模型 + Harness（駕馭框架）。** Claude Code 原始碼洩漏事件（2026-03-31）揭示了：全球最強程式碼代理工具約 40% 的能力並非來自模型智慧，而是來自精心設計的 harness 工程。本專案透過 6 層互動式課程搭配可執行的 Python 程式碼，教你掌握這些架構模式。

所有程式碼範例均提取自 [instructkr/claw-code](https://github.com/instructkr/claw-code)，這是 Claude Code 架構的乾淨重新實作（Python/Rust）。

### 六層架構

| 層級 | 功能 | Claude Code 範例 |
|------|------|-----------------|
| 🔁 迴圈 | 觀察 → 決策 → 行動 → 驗證 → 更新 | `queryLoop()` — while(true) 迴圈 |
| 🛠️ 工具 | 讓代理讀取、寫入、搜尋、執行 | 40 個工具，29K 行定義 |
| 🧠 上下文 | 管理代理看到的內容 | 4 層壓縮，靜態/動態提示分割 |
| 💾 持久化 | 跨會話記憶 | CLAUDE.md 層級 + 會話儲存 |
| ✅ 驗證 | 完成前自我審查 | 鉤子、成本追蹤、同步審計 |
| 🛑 約束 | 定義代理不能做什麼 | 6 層權限引擎、OS 沙箱 |

### 快速開始

```bash
git clone https://github.com/jack-lin-ds-ai/agent-harness-101.git
cd agent-harness-101
pip install -r examples/requirements.txt
python examples/01_agent_loop.py
```

---

> **DISCLAIMER:** This project uses code snippets from [instructkr/claw-code](https://github.com/instructkr/claw-code), a clean-room reimplementation of Claude Code's architecture. claw-code's license status is currently ambiguous. All code excerpts are used for educational and commentary purposes under fair use principles. This project is not affiliated with Anthropic or claw-code's maintainers. If you are a rights holder and have concerns, please [open an issue](https://github.com/jack-lin-ds-ai/agent-harness-101/issues).
