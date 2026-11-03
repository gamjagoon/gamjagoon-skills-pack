---
name: gsp-adopt
description: Prepare an existing project for GSP-based development using CodeGraph and scattered documentation, then establish linked requirements, architecture, and task documents. Create a missing local code index before investigation. Use when adopting GSP in a project developed without it; not for GSP installation or feature implementation.
---

# Adopt an existing project into GSP

Recover a reliable development baseline from the existing project and organize it into three linked Markdown documents. Start from evidence already present; do not ask the user to rewrite information you can investigate. Creating or refreshing the target project's local CodeGraph index is part of this workflow. GSP installation is handled separately. This skill does not change agent/model settings, redesign the product, or implement the recovered backlog.


If adoption exposes conflicting or outdated decisions, use the [common change procedure](../gsp-development/references/change-management.md) to preserve provenance and identify the affected current contracts and verification gaps. Existing completion remains historical evidence. Adoption still stops at the requested documentation baseline and does not start the optional coordinator.

## Prepare CodeGraph before investigating code

1. Resolve the actual target project root and inspect its instructions and existing changes before indexing. Check the installed CodeGraph CLI/version and available MCP tools. Use the absolute target path on every call; do not index the home directory, workspace collection, or a different checkout by accident.
2. Run `codegraph status --json "$gsp_project_dir"`. Check the reported `projectPath` and `indexPath`, not just whether `.codegraph/` exists. A parent/worktree index is not automatically the target's index; environments may use `.codegraph-wsl/` or a configured directory. A successful status command with `initialized: false` is still an absent index.
3. If the target has no usable index, create it with `codegraph init "$gsp_project_dir"` and wait for completion before investigating its code. Missing index alone does not require another user confirmation for this requested workflow. If a sync-mode prompt appears, select manual sync. Do not use `--yes` blindly: in CodeGraph 1.6.1 it can install Git hooks when file watching is disabled. Use unattended defaults only after verifying they fit the authorized scope. Do not install hooks, change global configuration, or delete an existing index as a shortcut.
4. For an existing index with pending changes, unresolved references, or uncertain freshness, run `codegraph sync "$gsp_project_dir"`. Recheck status and the target root. Record indexing errors, partial/empty coverage, excluded files and unsupported languages; do not treat directory creation, exit 0, or a partial graph as complete coverage. Preserve existing index configuration and source files.
5. Before broad code search, run a focused `codegraph_explore` MCP query against the explicit target root, or use the CLI equivalent below. Confirm it returns relevant symbols/source and relationships. Use follow-up queries for entry points, component boundaries, callers/callees, interfaces and related tests. Let these results guide targeted source reading; avoid dumping the repository into context.

```bash
# Set gsp_project_dir to the verified absolute project root first.
CODEGRAPH_TELEMETRY=0 codegraph status --json "$gsp_project_dir"
# Only when the target index is absent; handle any prompt as described above:
CODEGRAPH_TELEMETRY=0 codegraph init "$gsp_project_dir"
CODEGRAPH_TELEMETRY=0 codegraph status --json "$gsp_project_dir"
CODEGRAPH_TELEMETRY=0 codegraph explore --path "$gsp_project_dir" --max-files 6 \
  "<entry point, symbol, or code-structure question>"
```

The environment prefix keeps these commands local without changing persistent telemetry settings. Inspect actual command help when the installed version differs. Index readiness requires usable results for the area being investigated; graph edges are static evidence, not runtime proof or approved requirements. Use file/text search afterward for documents, configuration, uncovered languages and source verification, and label gaps. If the source changes during adoption, refresh and recheck affected findings.

If CodeGraph is missing or initialization/sync/query fails, report the concrete failure and hold code investigation dependent on it. Continue independent document inventory where useful. Do not silently replace the required index step with a full text scan or claim that CodeGraph was used. Do not install tools or reconfigure MCP as part of this skill; request the missing setup or an explicit fallback decision when necessary. An explicit no-write constraint also blocks index creation; explain the conflict instead of writing anyway.

Record the actual index path, tool version, readiness/coverage, relevant queries and tested source state in the document source/method notes. Keep this indexing evidence separate from program execution and the later review verdicts.

## Establish the baseline and document paths

- Read the user's adoption scope, applicable project instructions, repository status, existing work records where applicable, and available GSP stage guidance. Preserve uncommitted changes and other workers' ownership. Record the inspected commit plus relevant dirty/untracked state, or a file snapshot when Git is unavailable.
- Locate existing requirements, architecture/design notes, ADRs, task lists, README files, API/schema documents, tests, configuration, and build/runtime entry points. Follow relevant code and callers to verify what the documents describe. Use targeted history or connected sources only when relevant and accessible; identify unavailable sources and the limits of coverage.
- Use the user's explicit destinations first. Otherwise establish `spec/requirement.md`, `spec/architecture.md`, and `spec/tasks.md`. Reuse valid same-project documents when the project already treats them as authoritative; link them rather than creating competing specifications. If a default path contains unrelated material, preserve it and choose/report a non-conflicting location. Do not move or delete old documents merely to adopt GSP.
- Inventory sources and identify which three documents will be authoritative for subsequent work. Preserve stable IDs and decision history already in use. Keep an existing requirement such as `R10` as `R10`; do not restart numbering at `R1` for a cleaner table. Allocate unused IDs only for additional items. Resolve genuine duplicate IDs with an explicit source-to-canonical mapping. A reference to an old document is not proof that its claims are current.
- Keep target-project facts separate from orchestration context. Another project's session paths, evaluation harness details or a temporary worker's permissions are not the target's architecture or permanent operating policy. Record review limitations without importing those unrelated paths as the target's coordination setup.

## Recover requirements from evidence

Write or reconcile the requirements document first. Establish the observed problem/users, existing workflows, inputs/outputs, scope, compatibility constraints and known acceptance criteria. Keep unknown goals or constraints explicit instead of fabricating a complete project brief.

For each stable requirement ID, record:

| Field | Content |
| --- | --- |
| Requirement or candidate | The intended behavior or constraint, with confirmed versus inferred status |
| Source | User decision, existing specification, issue/note, or exact code/test/configuration location; include relevant baseline/date |
| Current observation | What implementation and available execution evidence show today |
| Acceptance and verification | Observable conditions and expected results supported by the contract; mark missing decisions or checks |
| Open issue | Conflict, assumption, missing evidence, or question affecting this item |

Do not promote every implemented behavior or test assertion into an approved requirement. Current user decisions define requested intent; source code shows implementation, and tests show encoded expectations or actual execution only when run. When sources disagree, preserve both claims and their provenance. Do not silently choose code, a newer timestamp, or a passing test as the intended contract.

Investigate factual gaps first. Ask the user only about material unresolved intent, priorities, compatibility or tradeoffs, with concise options and a recommendation. Send questions to the actual user; listing them in a document is not an answer. Hold dependent decisions while documenting independent facts. Existing code does not justify inventing business goals, numerical targets, budgets or production readiness.

## Describe the actual architecture

Build the architecture document from the current code and configuration after the supported requirements are organized. Record:

- Runtime/build entry points and the core input-to-output flow.
- Components and actual file/module responsibilities, dependencies, data ownership, persistence and external integrations where present.
- Interfaces, schemas, failure/error paths, relevant consumers and compatibility boundaries.
- Requirement ID → responsible component/interface → verification method.
- Known design decisions and their evidence, discrepancies between documents and code, and unverified environmental assumptions.

Describe the current architecture before any proposed changes. Label documented rationale, inferred rationale and proposals separately. Do not invent why a historical choice was made or claim a configured service is operational without evidence. Record necessary follow-up investigation; do not add new layers, frameworks or migrations merely to make the document look complete.

Unresolved requirements do not prevent recording independent current structure, but they do block finalizing dependent target designs. Keep that boundary visible.

## Reconcile the task plan

Use the requirements and architecture to recover current progress and define actionable next work in the task document. Reuse existing task IDs where valid; otherwise assign stable T IDs. Link every in-scope task to its requirement and architecture section.

- Separate existing implemented behavior, execution/verification gaps, unfinished approved work, and optional proposals. A source file or old checked box alone is not evidence that a task is done. Preserve historical completion claims with their original baseline and identify current verification still needed.
- For each next task, record the concrete outcome, owner or unassigned status, known files/component scope, prerequisite task IDs, completion conditions, verification inputs/expected results, status, and evidence or blocker. Mark proposed paths and estimated effort as such; do not invent an owner or deadline.
- Include needed regression, integration and acceptance verification for approved work. Mark overlapping ownership and unresolved contract dependencies. Do not imply that mentioning a worktree isolates files or that a session record locks them.
- If no new development scope was requested, limit the next-work list to supported unfinished work and necessary clarification/verification gaps. Keep speculative product improvements separate and unapproved; do not turn adoption into a new feature roadmap.
- Do not execute implementation tasks while setting up this baseline. A task-plan PASS is not an implementation PASS.

When the installed Task skill provides the [DAG procedure](../gsp-tasks/references/task-dag.md), include its explicit DAG in the authoritative task document and run the Python format/dependency checks. Preserve existing IDs, mark unsupported progress claims pending, and leave unknown owners/estimates explicit. Generate a derived Markdown graph and inspect routing only for planning; adoption does not dispatch implementation agents. If the Task skill or tool is unavailable, disclose that limitation under the review fallback below instead of installing it or claiming validation.

## Review and hand off the three documents

When available, apply the installed `gsp-requirements`, `gsp-architecture`, `gsp-tasks` and `gsp-grilling` guidance to their corresponding documents. Follow project review rules: use the available `gsp-reviewer` with requirements, architecture and tasks modes, reusing its conversation where possible. Supply original adoption scope, source locations, current baseline, affected IDs and known answers. Reviewers remain read-only; the lead records findings and corrections. Do not start implementation as a stage transition in this documentation request.

If stage skills or the native reviewer are unavailable, do not install them as part of adoption. Perform the supported document work, disclose the missing capability, and use only an authorized independent fallback or clearly labeled self-check. Missing review or unresolved essential decisions remain visible; do not manufacture PASS verdicts or declare all dependent work ready.

For each document, include the scope and current outcome, source/baseline references, unresolved issues, and applicable review findings/closure evidence. Use the user's language. Create Markdown only, without companion HTML or empty future-stage placeholders. Fill each of the three documents with supported content as its inputs become available; independent current-state sections may be useful while dependent decisions remain pending.

Before handoff, check requirement → architecture → task traceability, source links, status/evidence consistency, duplicate or conflicting authority, and preservation of original files. Verify cited source paths, symbols and line numbers against the inspected state; use a verified symbol or heading when exact line numbers are unavailable. Distinguish static inspection, historical results, and checks actually run now. Run only safe, authorized checks needed for this baseline; record unrun verification without treating adoption as permission for deployment, remote writes, or new spending.

Finish with links to the three authoritative documents, what was recovered, actual verification/review coverage, remaining decisions and the first actionable GSP task. State whether the baseline is ready for the specified next work or still has blocking gaps. Stop after documentation and handoff unless the user separately authorizes further work.
