# Development instructions

- Requirements live in `docs/requirements.md`; implementation choices live in `docs/design.md`.
- Keep the CLI installable with uv and free of runtime third-party Python dependencies.
- Do not call an LLM, change model/permission settings, or send project contents over the network.
- Only `skills add` may download an explicitly selected third-party skill.
- Preserve existing project content. Preview changes, preflight conflicts, and back up replacements.
- Keep prompt assets self-contained, with inherited agent model and reasoning settings.
- Keep tests focused on installer behavior, packaging, CLI outcomes, and download integrity.
- Validate with `uv run pytest`, `uv run ruff check .`, `uv run ruff format --check .`, and `uv build`.
- Smoke-test the built wheel with `uv tool install` in temporary tool/bin directories.
- Distinguish static config checks, isolated installs, live downloads, and live Codex execution.
- Other workers may be editing the repository; preserve their changes and stay within assigned files.
