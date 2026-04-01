# References

## Primary Source
- [instructkr/claw-code](https://github.com/instructkr/claw-code) — Clean-room Python/Rust reimplementation of Claude Code's architecture. Our code snippets are extracted from this project.

## Educational Resources
- [shareAI-lab/learn-claude-code](https://github.com/shareAI-lab/learn-claude-code) — 12-step educational harness for learning Claude Code patterns
- [anthropics/claude-code](https://docs.anthropic.com/en/docs/claude-code) — Official Claude Code documentation

## Analysis & Commentary
- [LangChain: Improving Deep Agents with Harness Engineering](https://blog.langchain.com/improving-deep-agents-with-harness-engineering/) — Defines the "harness engineering" concept
- [Martin Fowler: Harness Engineering](https://martinfowler.com/articles/exploring-gen-ai/harness-engineering.html) — Architectural patterns for agent harnesses
- [HumanLayer: Skill Issue — Harness Engineering for Coding Agents](https://www.humanlayer.dev/blog/skill-issue-harness-engineering-for-coding-agents) — Practical harness engineering for production agents

## Concepts
- **Agent = Model + Harness**: The core insight that agent capability comes from both the LLM and the surrounding engineering
- **Harness Engineering**: The discipline of designing the scaffolding around an LLM that turns it from a text generator into a capable agent
- **The 40% Rule**: Analysis suggests ~40% of Claude Code's effectiveness comes from harness patterns, not model intelligence
