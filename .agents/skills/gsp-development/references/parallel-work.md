# Parallel work: isolation, ownership, and integration

Split only independent work, and have one parent integrate it. There is no fixed parallel count. A small task may be completed by one agent. Follow the project root `AGENTS.md` instructions for roles and models. If subagent functionality is unavailable, perform the possible work directly and record the limitation that an independent review could not be performed.

## Assignment contract

For each assignment, record the objective, required inputs and evidence, owned files/directories, prohibited scope, baseline commit and current changes, actual cwd, completion criteria, verification commands, results to return, and known blockers. Do not overlap write ownership. Tell workers that others are working and not to revert existing changes. The parent is responsible for requirements, design, integration, and the final result.

Return changed files, a patch or commit, commands actually run and their results, failure logs, and items not run. Perform reviews read-only and return defects with locations, triggering conditions, and impacts. Label speculative concerns separately.

## Read-only work

Log triage, exploration, research, and review may read the shared repository. Include file modification, formatters, package installation, and test cache or snapshot writes in the prohibited scope. If verification that causes writes is needed, perform it in an isolated directory. For example, explicitly specify the repository path to read status and differences.

```sh
repo=/absolute/path/to/project
git -C "$repo" status --short
git -C "$repo" diff --stat
```

## Write work: Git worktree

A separate worktree is the default choice when the Git repository has a valid HEAD. First check the repository's current changes and baseline. The checks and HEAD worktree creation below are possible even if the original is dirty, but uncommitted changes are not transferred. If clean, assign immediately; if dirty, complete the current-change transfer procedure below before assigning.

```sh
repo=/absolute/path/to/project
git -C "$repo" rev-parse --show-toplevel
git -C "$repo" rev-parse --verify HEAD
git -C "$repo" status --short
```

After confirming a valid HEAD, create a detached worktree under a new temporary parent directory you own. Even with a dirty original, run this creation command first to prepare `experiment_root` and `experiment_dir`. Automatic commit or stash is unnecessary.

```sh
experiment_root=$(mktemp -d "${TMPDIR:-/tmp}/gsp-work.XXXXXX")
experiment_dir="$experiment_root/worker-a"
git -C "$repo" worktree add --detach "$experiment_dir" HEAD
git -C "$experiment_dir" rev-parse --show-toplevel
git -C "$experiment_dir" rev-parse HEAD
```

Give the worker the actual absolute path of `experiment_dir` and have them check cwd and baseline in their first command. Do not assume that a change to the parent's shell cwd automatically propagates to agents or other tools. Ordinary subagent calls do not automatically isolate cwd or sandbox. If the spawn tool lacks cwd isolation, verify that each tool follows the assigned absolute path and cwd/workdir. If this cannot be guaranteed, do not write concurrently in the shared original; perform write tasks sequentially. Specify cwd/workdir for each execution tool. A shell example follows:

```sh
(cd "$experiment_dir" && pwd && git status --short)
```

A worktree helps separate file changes but is not a security boundary. Credentials, network, home directory, and shared Git metadata remain accessible. It does not automatically create a container. Separately design the environment and permissions for work that needs additional security isolation.

## Dirty baseline, no HEAD, and non-Git projects

A HEAD worktree does not include the original's uncommitted changes. If the current work must be tested, record the baseline and transfer **only allowed files reviewed directly**. Create path-specific patches for tracked file changes, and copy only explicit untracked files whose contents, secrets, and size have been checked. Do not bulk-copy the entire project, home, `.env`, credentials, caches, or all untracked files. Do not automatically commit or stash to clean up the original.

For example, suppose only `src/feature.py` and `tests/test_feature.py` are needed from the current changes. Review the patch for sensitive content and keep it in a private working path.

```sh
umask 077
git -C "$repo" diff --binary HEAD -- src/feature.py tests/test_feature.py > "$experiment_root/baseline.patch"
git -C "$experiment_dir" apply --check "$experiment_root/baseline.patch"
git -C "$experiment_dir" apply "$experiment_root/baseline.patch"
git -C "$experiment_dir" diff --stat
```

This patch compares the final tracked file state, including staged and unstaged changes, against HEAD. The parent checks that no required current changes are missing. The worker separately retains the received baseline diff to distinguish it from their own result. Untracked files are not included in the patch above.

If Git or HEAD is absent, copy a reviewed allowlist into a new temporary folder. The paths below are examples; replace them with necessary files that actually exist. Do not inadvertently add hidden files or entire directories.

```sh
copy_root=$(mktemp -d "${TMPDIR:-/tmp}/gsp-copy.XXXXXX")
mkdir -p "$copy_root/project/src" "$copy_root/project/tests"
cp -- "$repo/pyproject.toml" "$copy_root/project/pyproject.toml"
cp -- "$repo/src/feature.py" "$copy_root/project/src/feature.py"
cp -- "$repo/tests/test_feature.py" "$copy_root/project/tests/test_feature.py"
```

Record the copy list, observed original changes, baseline and hashes, missing dependencies, and limitations of the copy. Compare the allowed files in the original and the copy to check that current changes are reflected. If baseline transfer is incomplete, do not report the result as overall integration success.

## Output and execution environment

Each worker has separate output and log paths, virtual environments/caches, and necessary ports. In an environment with `uv` and local Python, place the virtual environment, uv cache, temporary files, and output under the experiment as follows. Explicitly specify this virtual environment and cache for actual dependency installation too. The example below checks output separation only and does not replace project verification.

```sh
mkdir -p "$experiment_root/cache" "$experiment_root/tmp" "$experiment_root/output"
UV_CACHE_DIR="$experiment_root/cache" uv venv --python python3 "$experiment_root/venv"
(cd "$experiment_dir" && TMPDIR="$experiment_root/tmp" "$experiment_root/venv/bin/python" -c 'from pathlib import Path; import sys; print(Path.cwd()); Path(sys.argv[1]).write_text("isolated output\n")' "$experiment_root/output/smoke.txt")
```

First check whether resources such as shared databases, development servers, external services, and build caches conflict. If the server supports it, prefer binding to port 0 and reading the OS-assigned port. If a fixed port is needed, check its availability, but a pre-check does not reserve it, so also handle actual bind failures. Record the actual assigned value and process owner. Separating worktrees alone does not isolate execution environments. Terminate only processes belonging to your own work.

## Parent integration and cleanup

Workers do not merge or overwrite the original directly. The parent compares returned changes against the baseline and checks owned files, requirements, and scope. Recheck whether others changed the original, and integrate only changes to the target paths. For example, first run `git apply --check path/to/result.patch` on a reviewed result patch. If there are conflicts, adjust the affected parts directly and run relevant tests and final integration verification. Passing `--check` is not evidence of functional success.

After preserving failure evidence and necessary results, you may remove your own clean worktree that is no longer needed with `git -C "$repo" worktree remove "$experiment_dir"`. For a dirty worktree, first preserve and check necessary patches and logs. Do not delete another person's directories or changes, and do not use `git clean -fd`, `reset --hard`, or forced worktree removal as cleanup defaults.

Official environment documentation: [Codex subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents), [Git worktrees](https://learn.chatgpt.com/docs/environments/git-worktrees). Check installed policies and current environment feature support separately.
