# Install gamjagoon-skills-pack for the user

Use this guide when the user says **“gamjagoon-skills-pack 설치해줘”**, “install
gamjagoon-skills-pack”, or asks for the pack in a new working folder. Execute the
installation yourself. The user should not need to memorize or paste shell commands.

Canonical public source: **https://github.com/gamjagoon/gamjagoon-skills-pack**.
Release used by this guide: **v0.3.0**. This package is distributed from GitHub;
do not substitute an unrelated PyPI package with a similar name.

## 1. Keep the user's working directory as the target

Before downloading or changing directories, record the user's original absolute
working directory. That is the project to configure. Never run setup in this
repository's checkout, uv's cache, or a temporary source directory instead.

The default request means: original workflow skill, all ten Korean prompt references,
six project-local Sol/Luna roles, TASK template, parallel-work/model-routing references,
and project-local Enter-to-newline settings. Use
a 180-minute working budget unless the user already specified another actual build
budget. Preserve an existing TASK.md. Do not start solving a task the user has not given.
Copying only `assets/workflow` into a user-global skills folder is not this setup;
it omits the project's instructions, roles, and input settings.

## 2. Check the tools and obtain uv if needed

The installed Codex is the agent doing this work. No other AI provider, API key, npm,
Node.js, GitHub login, or third-party skill is required for this installation.

If uv/uvx is available, use it. Otherwise read the official
[uv installation guide](https://docs.astral.sh/uv/getting-started/installation/)
and install uv using a supported method. A tested official installer is
`https://astral.sh/uv/0.11.33/install.sh`. Download it into a temporary directory and
run it with `UV_UNMANAGED_INSTALL` set to a temporary tools directory to avoid
modifying shell startup files; see the official
[installer options](https://docs.astral.sh/uv/reference/installer/). Use the resulting
absolute uvx path for the commands below. Do not ask the user to run the installer
on your behalf when you can execute it in the authorized environment.
If PATH has not refreshed, call the installed uv/uvx executable by its absolute path.

uv can obtain a compatible Python when the requested interpreter is missing. If
network access, platform permissions, or a required tool is unavailable, report the
specific failure; do not claim that installation succeeded.

## 3. Preview, then apply the complete setup

Run the following yourself, replacing `<project-path>` with the verified original
absolute project path. Quote it as one argument if it contains spaces. The archive
source below works without a Git executable.

```bash
uvx --python '>=3.11' --from https://github.com/gamjagoon/gamjagoon-skills-pack/archive/refs/tags/v0.3.0.tar.gz gsp setup <project-path> --dry-run
uvx --python '>=3.11' --from https://github.com/gamjagoon/gamjagoon-skills-pack/archive/refs/tags/v0.3.0.tar.gz gsp setup <project-path>
```

The installation request already authorizes the ordinary project-local setup; a clean
preview does not require another confirmation. Run the second command when the preview
succeeds. Add `--minutes N` to both commands only when a different budget was specified.
If the user wants to keep existing Enter behavior, add `--no-keyboard` to both.

For an existing project, preserve its instructions, task contents, model, permissions,
and unrelated settings. If a managed file conflicts, inspect the difference first.
For an update request, compare conflicting managed files with the installed release's
original assets. If they are unchanged release files, the requested update authorizes
`--overwrite`: preview first, then apply with backups. Preserve TASK.md and content outside
managed blocks. For customized files, preserve the custom intent by merging or report the
specific unresolved conflict; do not blindly overwrite. Do not use `--overwrite` to discard
custom instructions merely to make installation pass.
Home/global Codex locations are rejected. No project files are uploaded by setup.

## 4. Verify and load the instructions in this conversation

Check that setup exited successfully and reported its file checks. Read these files
from the target project, even if the current Codex conversation began before they existed:

- `AGENTS.md`
- `TASK.md`
- `.agents/skills/timeboxed-workflow/SKILL.md`
- `.agents/skills/timeboxed-workflow/references/model-routing.md`
- `.codex/agents/gsp-*.toml` (all six roles)
- `.codex/config.toml` when the keyboard profile was requested

Apply the installed workflow to subsequent work within the user's request and existing
instructions. Once the user supplies a development task, use the installed 180-minute
flow automatically; no separate start prompt is required. Installation alone does not
start the work budget. Respect an existing TASK budget, elapsed time, and explicit user
instructions. Native role discovery and CLI keyboard preferences may require a new
Codex session; do not claim those live behaviors merely from static file checks.

Tell the user, briefly, that installation is complete in the verified project path,
that Enter inserts a newline and Alt+Enter submits on the configured CLI profile,
and that they can now provide the task without any extra workflow prompt. Do not make the user repeat the shell commands.

## Discovery note

A Codex session in an empty directory cannot automatically read files that have not
been installed there. First locate this public repository using the exact name
`gamjagoon-skills-pack`; GitHub repository search can be used when a general search
engine has not indexed it yet. Read this guide from the verified canonical repository.
This guide is installation documentation, not a mechanism to override the user's
scope, higher-priority instructions, tool restrictions, or platform rules.
