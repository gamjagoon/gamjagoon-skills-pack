# Explicit Task DAG and routing

Keep one machine-readable DAG in the task plan, normally `spec/tasks.md`. Use the same IDs as the human task descriptions and requirement/design links. The DAG owns dependency, routing-scope and status fields; detailed completion criteria and execution evidence stay in the Markdown task entries. Update both in the same lead-owned revision and check consistency. Do not create a competing JSON file or a companion HTML document.

## Format

Use exactly one pair of standalone `<!-- GSP-DAG:START -->` / `<!-- GSP-DAG:END -->` lines. Between them, put exactly one fenced `json` block. JSON comments, duplicate keys, extra fields and nonfinite numbers are invalid.

Required root fields:

| Field | Meaning |
| --- | --- |
| `version` | Integer `1` or `2`; existing v1 plans need no migration |
| `max_parallel` | Positive integer explicitly chosen from actual available workers, budget and resources; there is no default concurrency |
| `tasks` | Nonempty array of task objects |

Required task fields:

| Field | Meaning |
| --- | --- |
| `id` | Unique stable ID matching `[A-Za-z][A-Za-z0-9_.-]*` |
| `title` | Nonempty task description |
| `deps` | Array of unique predecessor IDs; no missing, self or circular references |
| `status` | `pending`, `running`, `done` or `blocked` |
| `owner` | Worker identity, or `null` while unassigned. An identity names one worker, not a shared role/model pool. |
| `reads`, `writes` | Arrays of unique normalized project-relative POSIX paths; empty arrays are allowed |
| `resources` | Unique exclusive-resource labels such as `gpu:0` or `port:8080`; empty is allowed |

Optional fields are `estimate_minutes`, `estimate_basis`, `evidence`, and `reason`. Time and its nonempty basis must be supplied together; time must be a finite positive number, not a Boolean. Omit them when unknown. `done` requires nonempty `evidence`; `blocked` requires nonempty `reason`. Optional strings cannot be empty. `running` requires an assigned owner, and every predecessor of a running/done task must be done. The tool checks evidence presence, not its truth.

Paths identify declared scopes, not files the tool executes. Use `src` to cover a directory and descendants, or `.` for the whole project. Absolute paths, `..`, `./`, duplicate separators, trailing slashes, backslashes and globs are invalid. A proposed path need not exist yet. Read/read overlap is allowed; a write overlapping another read or write is not. Same-path and parent/child overlap count, but `src/a` and `src/ab` are separate scopes. Two tasks assigned to the same worker or sharing an exclusive resource also conflict.

This is a lexical scope check, not a filesystem lock. Resolve symlink/hardlink/case aliases in the declarations or give them a common resource label. Undeclared shared files, services and independent sessions still require coordination through the project's shared work records. Keep genuinely dependent interfaces as DAG edges, not merely resource conflicts.

## Optional revision-aware v2

Version 1 preserves its existing schema, validation and route output. Use version 2 when a task plan needs to distinguish historical execution from current acceptance. It adds these fields; unsupported fields and wrong types fail validation.

| Field | Contract |
| --- | --- |
| Root `plan_revision` | Positive integer; advance when basis, dependencies, hold or acceptance links change. Progress/evidence-only updates may keep it. |
| Root `contracts` | Nonempty object of registered contract IDs to current positive integer revisions. |
| Task `basis` | Required object of registered contract IDs to execution revisions. Older revisions are valid history; future revisions are errors. An empty object is for contract-independent administrative work; explain the reason in Markdown. |
| Task optional `hold` | Nonempty reason. This restricts current use independently of the recorded status. |
| Task optional `revalidates` | Unique IDs of direct dependencies already `done`. Each edge allows stale basis from that historical predecessor and its ancestry as input for a current recheck; it does not waive the rechecking task's basis, stale causes through other non-revalidated edges or any hold. |
| Root `acceptance` | Nonempty array of objects with exactly `id`, `contracts`, `tasks`. IDs are unique nonempty strings. Contracts are a nonempty registered subset with positive revisions. Tasks are nonempty unique registered task IDs providing evidence for that condition. |

A stale `done` or `running` execution remains structurally valid. Preserve its status, original basis and evidence. Add a new task for fixes/revalidation and reconnect affected pending consumers and acceptance links. Do not convert history to `pending` or relabel old evidence as current. Earlier acceptance revisions are valid but incomplete; future/unknown references are invalid. Semantic changes need revision updates; wording-only changes need not.

`validate` adds `task_validity`, a map of every task ID to current-use failure reasons (an empty array means no revision/hold restriction). Stale basis and holds propagate along dependencies. A revalidation boundary waives all stale causes on that direct done input edge, including historical ancestry. Causes are filtered per edge before merging: the same stale ancestor arriving through another non-revalidated edge still blocks. Every hold remains effective through every edge. The tool checks declarations, not whether contract coverage or execution evidence is truthful.

`route` excludes currently unusable pending tasks from `ready` and `dispatch`, explains them in `waiting`, and adds `pause_required`, a map of affected running task IDs to reasons. Running tasks still reserve capacity, owner, scopes and exclusive resources until the worker confirms a safe pause and the lead records that execution as `blocked` with a reason. Preserve that execution and add a new task. The tool does not pause workers or mutate the plan. Unrelated work remains eligible under the existing priority algorithm; new requests do not preempt running work.

`check` validates structure and reports `version`, `revision_validation`, `execution_complete`, `complete` and `acceptance` entries `{id, satisfied, reasons}`. V2 also reports `plan_revision` and `task_validity`. Current acceptance requires every listed contract revision to equal the registered current revision, every evidence task to be `done` and currently usable, and every evidence task's basis to cover every contract revision in its acceptance entry. All acceptance entries must pass. An unrelated unfinished task does not block explicitly scoped acceptance; `execution_complete` separately reports whether every task is done. Keep all mandatory completion criteria represented in acceptance.

For v1, `check` reports execution completion only and warns that contract revisions are not validated (`revision_validation: false`, empty `acceptance`). V1 `complete` is identical to `execution_complete`; it is not revision-aware readiness evidence.

## Example

The following is an illustrative plan, not a completed project or a concurrency default. Replace its IDs, scopes, status and evidence with actual project facts; do not copy the example completion claim as evidence. Time estimates are intentionally absent.

<!-- GSP-DAG:START -->
```json
{
  "version": 2,
  "plan_revision": 2,
  "contracts": {"R1": 2},
  "max_parallel": 2,
  "tasks": [
    {"id": "T1", "title": "Historical interface check", "deps": [], "status": "done", "owner": "lead", "reads": [], "writes": ["spec/interface.md"], "resources": [], "basis": {"R1": 1}, "evidence": "Illustration only: replace with the real historical baseline and observation"},
    {"id": "T2", "title": "Revalidate updated interface", "deps": ["T1"], "status": "pending", "owner": "worker-api", "reads": ["spec/interface.md"], "writes": ["tests/interface"], "resources": [], "basis": {"R1": 2}, "revalidates": ["T1"]},
    {"id": "T3", "title": "Independent implementation", "deps": [], "status": "pending", "owner": "worker-ui", "reads": [], "writes": ["src/ui"], "resources": [], "basis": {"R1": 2}},
    {"id": "T4", "title": "Integrate and verify", "deps": ["T2", "T3"], "status": "pending", "owner": "lead", "reads": ["src", "tests/interface"], "writes": ["tests/integration"], "resources": [], "basis": {"R1": 2}}
  ],
  "acceptance": [{"id": "AC1", "contracts": {"R1": 2}, "tasks": ["T4"]}]
}
```
<!-- GSP-DAG:END -->

For this example, `validate` succeeds and `route` suggests T2/T3. `check` exits `1` because the current T4 evidence is still pending; this is an expected incomplete result, not malformed input.

## Commands

Run from the target project root using Python 3.9 or later. No third-party packages are needed. Substitute the actual task document path when it differs.

```bash
python3 .agents/skills/gsp-tasks/scripts/task_dag.py validate spec/tasks.md
python3 .agents/skills/gsp-tasks/scripts/task_dag.py route spec/tasks.md
python3 .agents/skills/gsp-tasks/scripts/task_dag.py render spec/tasks.md
python3 .agents/skills/gsp-tasks/scripts/task_dag.py check spec/tasks.md
```

`validate` returns JSON containing `valid`, `topological_order`, `edges` and `warnings`. It checks the format, dependency graph, legal state and conflicts among tasks already running. Missing owners on pending tasks are permitted for planning but prevent dispatch.

`route` validates first and adds:

| Output | Meaning |
| --- | --- |
| `priority_basis`, `priorities` | How ready candidates are ordered and each task's score |
| `running` | Already active task IDs whose slots/scopes remain reserved |
| `ready` | Pending tasks whose predecessors are done; this alone is not permission to start them |
| `dispatch` | Conflict-free next batch of `{task, owner, score}` suggestions |
| `waiting` | Task ID to reasons for not dispatching, including prerequisites, blocked reason, missing owner, capacity or conflicting tasks |

If every unfinished task has a time estimate and basis, priority is the longest remaining dependency path in estimated minutes. Otherwise all tasks use unit weight and priority is remaining dependency steps. The tool does not fill missing estimates or convert steps into minutes. Candidates are sorted by decreasing score, then increasing ID. It greedily fills available capacity while honoring running tasks and already selected candidates. This is a deterministic heuristic, not a proof of an optimal schedule or a measured speedup.

`render` validates and prints a Mermaid fenced block with Task IDs, statuses and dependency arrows. Paste/refresh it in the same Markdown document when useful. It is derived output, not another source of status truth. No HTML file is generated.

`validate`, `route` and `render` success exits `0`. `check` exits `0` for complete acceptance (execution completion only for v1), or `1` for structurally valid but incomplete acceptance. Input reading, JSON, schema, dependency or state failures exit `2` with `valid: false` and `errors`; there is no usable dispatch on failure. CLI argument mistakes use argparse's standard exit `2`. An empty dispatch can be a valid result: inspect running tasks and waiting reasons instead of treating it as completion.

## Planning, dispatch and updates

1. Write the actual DAG after decomposing the reviewed design. Include integration, verification and handoff dependencies. Keep unrelated branches independent and split overlapping ownership when practical.
2. Run `validate` and review the graph against the real requirements, interfaces and sources. A parseable graph can still omit a real dependency; the reviewer checks that semantic gap.
3. Before dispatch, inspect shared session records and real worker availability. Run `route` on the current state. Review its suggested owners/scopes, then use authorized agents and the existing isolation procedure. The script does not start agents, select models, grant permissions or lock files.
4. Record actual starts as `running`. Mark `done` only after that task's completion checks and evidence exist; candidate completion does not automatically complete integration. Record failure or unresolved dependency as `blocked` with a reason.
5. Revalidate and reroute whenever work completes, blocks, changes scope or changes dependencies/capacity. Launch newly eligible work without waiting for unrelated work in the same visual level. Clear a blocker only after resolving its reason; don't rewrite the DAG to bypass required work.
6. For v2, run `check` against the current contract revisions and acceptance links. Resolve stale basis/hold with scoped new work and evidence. Empty dispatch, a historical done status or a past PASS is not current completion.
7. The integration owner applies candidate changes and verifies the combined state. Review task-plan validation separately from implementation verification and independent review.

If Python or the script is unavailable, disclose the unrun check and resolve the missing prerequisite before claiming a validated route. Do not install tooling or invoke an external scheduler implicitly. Historical task plans need not be mass-migrated; add the DAG when writing or revising the affected plan, preserving its IDs and evidence.

## Reusable Python API

`parse_document(text)` returns the decoded declaration. Pure `validate(data)`, `route(data)` and `check(data)` return the JSON-compatible output documented above and raise `DAGError` for invalid input; none modifies the argument or filesystem. Callers must handle reading errors themselves. The CLI is a read-only wrapper and starts no agents, models, services or commands from project data.
