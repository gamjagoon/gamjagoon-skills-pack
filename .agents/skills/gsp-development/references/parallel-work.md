# Parallel work: isolation, ownership, and integration

Split only independent work, and have one parent integrate it. There is no fixed parallel count. A small task may be completed by one agent. Follow the project root `AGENTS.md` instructions for roles and models. If subagent functionality is unavailable, perform the possible work directly and record the limitation that an independent review could not be performed.

## Assignment contract

For each assignment, record the objective, required inputs and evidence, owned files/directories, prohibited scope, baseline commit and current changes, actual cwd, shared `.gsp-work` root and session record path, completion criteria, verification commands, results to return, and known blockers. Do not overlap write ownership. Tell workers that others are working and not to revert existing changes. The parent is responsible for requirements, design, integration, and the final result.

Return changed files, a patch or commit, commands actually run and their results, failure logs, and items not run. Perform reviews read-only and return defects with locations, triggering conditions, and impacts. Label speculative concerns separately.

Follow the [session record procedure](session-work.md) to share work status across isolated workspaces. Writing workers update only their own record in the common directory; this is an intentional coordination write outside their code worktree. Read-only workers return updates to the lead without writing records. Check relevant peers at work boundaries; the record directory provides neither live notifications nor an exclusive ownership lock.

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

Workers do not merge or overwrite the original project files directly. The parent compares returned changes against the baseline and checks owned files, requirements, and scope. Consult session records for pending interface changes, acknowledgements and the states actually tested. Recheck whether others changed the original, and integrate only changes to the target paths. For example, first run `git apply --check path/to/result.patch` on a reviewed result patch. If there are conflicts, adjust the affected parts directly and run relevant tests and final integration verification. Passing `--check` is not evidence of functional success. Record the integrated state and test evidence in the integrator's own session record without editing workers' histories.

After preserving failure evidence and necessary results, you may remove your own clean worktree that is no longer needed with `git -C "$repo" worktree remove "$experiment_dir"`. For a dirty worktree, first preserve and check necessary patches and logs. Do not delete another person's directories or changes, and do not use `git clean -fd`, `reset --hard`, or forced worktree removal as cleanup defaults.

## PoC development with a parallel optimization task

Treat optimization as a linked task within the agreed project scope. The PoC lead owns integration unless another owner is explicitly assigned; the optimizer owns the scoped candidate change. Both use isolated code workspaces and the same absolute session-record root. This procedure also applies when the user started the sessions independently. Reuse valid requirements, design and reviews, and reopen only affected parts. Do not create a new product workflow or promote PoC evidence to PoR merely because another agent is involved.

### Handoff before edits

Record the following in the existing task plan and reference it from both session records. The lead owns updates to the shared plan and canonical contract; workers record proposals and progress in their own histories.

| Item | Required information |
| --- | --- |
| Relationship | Parent PoC/task ID, optimization task ID, requirement/design IDs, both session paths and integration owner |
| Effective baseline | Commit plus the allowed staged/unstaged patch and required untracked files, with hashes or equivalent snapshot identity; known baseline failures and missing evidence |
| Ownership and contract | Candidate files/modules, unchanged inputs/outputs/errors and relevant side effects, contract revision, callers and shared files needing coordination |
| Improvement and limits | Metric, representative inputs, measurement method/environment, supplied target if any, functional acceptance checks, authorized resources and stop rule |
| Delivery | Candidate patch/commit relative to the received baseline, baseline/candidate evidence, limitations and integration checks |

Confirm the copied baseline using the dirty-baseline procedure above before recording comparison results. If optimization already started, preserve that work, identify its actual starting state and delta, and reconcile them with the current PoC; do not reset it or treat a guessed baseline as verified. While the optimizer works, the lead continues non-overlapping work. An overlapping file or contract change requires coordination and may hold the affected work, not the whole project.

### Measure and verify the candidate

1. Confirm the suspected bottleneck through existing evidence or bounded measurement. Record baseline correctness checks and measurements before changing the candidate. An existing failure remains an explicit limitation; a fast failing run is not a performance improvement.
2. Compare the same representative inputs and workload, environment, dependency/build configuration and measurement method. Record cache/warm-up conditions, repetitions and variability where they affect the result. Choose a proportionate method; do not impose an invented universal sample count or threshold.
3. Coordinate CPU/GPU/I/O-heavy runs on shared hardware so competing work does not confound the comparison, or record controlled load explicitly. If conditions cannot be made comparable, report the result as inconclusive rather than an established speedup. Do not stop another session's processes without authorization.
4. Check the agreed functional/interface contract and normal, error and boundary behavior alongside performance. Keep required expectations fixed; any change to allowed accuracy, semantics or compatibility follows the owner/user decision path. Check other constrained resources so a speedup does not silently violate a memory or cost limit.
5. Record exact baseline and candidate states, commands, input identities, measurements, known cost and limitations. Separate measured results from estimates. Respect the agreed scope, budget and stop rule; if the candidate fails correctness, gives inconclusive benefit or reaches the limit, report the result and reassess rather than silently expanding the experiment.

### Deliver only the candidate delta and integrate

The optimizer returns changes made after the received baseline, not a replacement copy of the whole worktree or a HEAD-relative diff that includes the lead's existing dirty changes a second time. For an uncommitted baseline, retain its snapshot or patch and derive/check the candidate delta against that state. For a commit-based handoff, identify the exact base and candidate commits. Include required new files in the reviewed handoff without copying unrelated local state.

The integrator checks current source and contract drift against that base, resolves only affected conflicts, and applies the reviewed delta. A clean textual application alone does not establish compatibility. Rerun the original PoC user flow, affected correctness/regression tests and relevant performance checks on the combined state. If necessary, compare the current integration base before/after the candidate again instead of reusing an obsolete measurement.

Record worker completion and integration acceptance separately. The worker may finish its assigned candidate and evidence while integration remains pending; the task plan and integrator record must keep that pending work visible. Report which state was tested and which acceptance criteria remain unverified. Only the integration owner's combined-state evidence supports an integrated completion claim.

Official environment documentation: [Codex subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents), [Git worktrees](https://learn.chatgpt.com/docs/environments/git-worktrees). Check installed policies and current environment feature support separately.

## Changes while workers run

Apply [change-management.md](change-management.md) at each handoff and integration. Record the received contract/plan revisions and keep old execution evidence. Only affected work pauses at a safe checkpoint; pending independent work may continue. A coordinator's delivery receipt is not a worker's held/applied confirmation. The single integrator updates authoritative contracts and current acceptance; workers never silently rewrite those contracts to match their candidate.
