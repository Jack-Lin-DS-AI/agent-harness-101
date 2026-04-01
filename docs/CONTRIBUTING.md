# Contributing

Thank you for your interest in contributing to Agent-Harness-101!

## How to Contribute

### Content Improvements
- Fix typos or improve explanations in `src/content/en/` or `src/content/zh-TW/`
- Add teaching annotations to code snippets in `src/snippets/`
- Improve Chinese translations

### Code Examples
- Fix bugs in `examples/` Python files
- Add new teaching examples that demonstrate harness patterns
- Ensure all examples remain self-contained and runnable

### Site Improvements
- Improve responsive design
- Add accessibility features
- Improve syntax highlighting

## Guidelines

1. **Keep snippets 50-80 lines** — trim for teaching clarity
2. **Always cite sources** — `# From claw-code: src/filename.py, lines ~X-Y`
3. **Add `# ←` annotations** — explain the harness pattern inline
4. **Label teaching implementations** — mark code that isn't from claw-code
5. **Test Python examples** — `python examples/0X_*.py` should work independently
6. **Maintain both languages** — content changes should update both en/ and zh-TW/

## Development Setup

```bash
# Site development
npm install
npm run dev

# Python examples
pip install -r examples/requirements.txt
python examples/01_agent_loop.py
```

## Code of Conduct

Be respectful, constructive, and educational-focused. This is a teaching project.
