---
name: gsp-development
description: Implement features according to reviewed requirements and architecture, and verify them through actual execution. Isolate workspaces for independent investigations and experiments, and preserve existing changes.
---

# Development

Check the original requirements, current design and task list, both review results, and existing changes. Confirm that the reviews concern the current artifacts, and do not start implementation that depends on unresolved blockers. Within the approved scope, implement the core flow first and execute it in small units. Handle simple changes in proportion to their size and do not add unnecessary planning documents.

## Check ambiguity — grilling

At this stage, also read and apply [gsp-grilling](../gsp-grilling/SKILL.md). Ask when implementation reveals undecided boundary behavior, data handling policy, or conflicts with existing behavior. Before an answer, do not arbitrarily implement that behavior or fix it as a test expectation.

Bring questions to the actual user with a recommendation, and wait only on the parts that depend on the answer. The main worker collects and asks questions from review and work subagents. Reuse existing answers.

## Implementation and verification

In an existing project, first find usage instructions, build and test commands, and relevant existing checks. If needed, run them before changes to record existing failures and distinguish them from new regressions. If there is no test system, prepare execution cases appropriate to the size of the work and do not add a new framework by default.

- First, execute the minimum user-observable functionality end to end.
- Connect each change to a requirement ID and check normal, error, and boundary cases against expectations established by the original text and existing contracts. Do not take the implementation result itself as the expectation.
- Verify the actual flow through the user entry point and affected existing regression and integration paths. Record the reason and impact for required checks that could not be run because of the external environment, and do not mark them complete.
- Fix issues based on confirmed causes of failure. If the same localized repair fails, hand the attempt, reproduction, and error evidence to the appropriate role.
- Once relevant checks pass, do not repeat the same checks without a reason.
- Preserve existing user changes and other workers' files. Do not remove scope or required functionality without approval.

## Parallel investigation and experiments

Parallelize only independent work. Share investigation and fact extraction as read-only work, and conduct experiments that write files in a separate worktree or a directory containing only permitted copied files. When starting parallel work, read the [isolation, environment, and integration procedure](references/parallel-work.md).

For each assignment, specify the objective, input evidence, owned files, actual cwd, completion criteria, and results to return. Also isolate outputs, virtual environments, caches, and ports. A worktree is not a security boundary, and do not assume subagents automatically have an independent cwd. The main worker integrates only verified changes and reruns relevant checks.

## Human-reviewable deliverables

Follow the "Documents for human review" contract in the project AGENTS.md. The lead maintains a Markdown source and a matching, self-contained HTML view (default `TASK.md` and `TASK.html`), using the user's language and existing document locations. Publish the implementation summary, changed files, actual commands and results, unresolved findings, and unrun checks in both views. After the review, the lead adds its findings and fix/recheck evidence and refreshes the HTML. Keep both views synchronized, preserve unrelated files, and link both in the user-facing handoff. Respect explicit format and no-write constraints; do not claim an HTML file exists if it was not created.

## Completion and handoff

In the current work record, connect each requirement to actual inputs, expected results, observed results, commands run, changed files, and unrun verification. If the implementation differs from the design, record the reason and impact and recheck only the relevant reviews. Once implementation and verification of the functionality are complete, request the native Codex agent `gsp-reviewer` with mode `development`. Pass the absolute project root, requested scope, original text, requirements and design paths, requirement IDs, changed files and affected callers, baseline state, actual execution evidence, checks performed, and unresolved questions with existing answers. Use the agent defined in `.codex/agents/gsp-reviewer.toml`; ask it to return an independent review to the lead worker, who records and resolves findings and distinguishes independent re-review from author revalidation. Do not present an author's self-review as independent. If the native role or independent subagents are unavailable, follow the availability fallback in AGENTS.md and disclose the review method. Do not treat passing tests as proof of success in the user's environment.
