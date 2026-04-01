# Architecture

Agent-Harness-101 is structured as an Astro static site with bilingual content and runnable Python examples.

## Site Architecture

```
Astro Static Site (src/)
├── Pages: Landing page + 6 layer detail pages
├── Content: Markdown files in en/ and zh-TW/
├── Snippets: Annotated Python extracted from claw-code
├── Styles: Dark-mode CSS with per-layer accent colors
└── i18n: JSON-based language toggle (EN / 繁體中文)
```

## Content Architecture

Each of the 6 layers follows a consistent structure:

1. **Conceptual explanation** — What the pattern is and why it matters
2. **What Claude Code does** — The original TypeScript architecture
3. **What claw-code implements** — The Python reimplementation
4. **The universal pattern** — How this applies to any agent framework
5. **Annotated code** — 50-80 lines from claw-code with `# ←` annotations
6. **Runnable example** — Self-contained Python file in `/examples/`

## Layer → File Mapping

| Layer | Snippet | Example | Content |
|-------|---------|---------|---------|
| Loop | `01_loop.py` | `01_agent_loop.py` | `01-loop.md` |
| Tools | `02_tools.py` | `02_tool_system.py` | `02-tools.md` |
| Context | `03_context.py` | `03_context_manager.py` | `03-context.md` |
| Persistence | `04_persistence.py` | `04_persistence.py` | `04-persistence.md` |
| Verification | `05_verification.py` | `05_verification.py` | `05-verification.md` |
| Constraints | `06_constraints.py` | `06_constraints.py` | `06-constraints.md` |

## Deployment

GitHub Actions builds the Astro site on push to `main` and deploys to GitHub Pages.
See `.github/workflows/deploy.yml`.
