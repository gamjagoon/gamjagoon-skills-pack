# Agent installation entrypoint

If the user asks to install **gamjagoon-skills-pack** into their working project,
read [INSTALL.md](INSTALL.md) and perform that setup in the user's original project
directory. This repository is the installation source, not the target project.
The user does not need to type or memorize shell commands. Keep any source checkout
in a temporary directory or uv's cache. After installation, read the installed
project instructions in the current chat. Do not begin solving a task the user has
not provided.

The instructions below apply when developing this repository itself.

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
