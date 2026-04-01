# Agent-Harness-101 Project Instructions

## What This Project Is
An educational website + Python examples teaching Agent Harness Engineering.
The irony: this CLAUDE.md file is itself an example of Layer 4 (Persistence).

## Code Source
- Primary reference: https://github.com/instructkr/claw-code (clone to /tmp/claw-code)
- We EXTRACT 50-80 line snippets, add teaching annotations, cite source file + lines
- We do NOT copy entire files or modules
- If claw-code doesn't cover a layer, write original teaching code and label it clearly

## Tech Stack
- Frontend: Astro + vanilla CSS (dark mode, responsive)
- Examples: Python 3.11+ with anthropic SDK, pydantic, rich
- Deployment: GitHub Pages via GitHub Actions

## Code Style
- Python: Follow PEP 8, type hints required, docstrings on all public functions
- TypeScript/Astro: Standard Astro conventions
- All code comments in English
- Content in both zh-TW and en

## Key Rules
- NEVER copy entire files from claw-code — extract key snippets only (50-80 lines)
- ALWAYS add `# ←` inline annotations explaining the harness pattern
- ALWAYS cite source: `# From claw-code: src/runtime.py, lines ~45-112`
- Each example in /examples/ must be self-contained and runnable independently
- Keep /examples/ files under 200 lines (except 07_full_harness.py up to 300)
- The disclaimer MUST appear in README.md AND Footer.astro
- Use the anthropic Python SDK for LLM calls in examples

## Build & Test
- `npm run dev` — start Astro dev server
- `npm run build` — build static site to dist/
- `python examples/01_agent_loop.py` — test individual examples (needs ANTHROPIC_API_KEY or uses simulation mode)
