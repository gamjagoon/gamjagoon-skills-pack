---
name: gsp-tasks
description: Turn reviewed requirements and architecture into verifiable tasks with an explicit DAG, Python validation, and dependency-aware parallel routing. Use when creating or revising a work breakdown; stop before implementation for a planning-only request.
---

# Task planning

Read the original request, current requirements and architecture, their review findings and closure evidence, and relevant existing code. Verify the reviews cover the current artifacts. Hold tasks dependent on unresolved blockers; independent planning may continue. A missing design decision belongs in architecture, and a missing user requirement belongs in requirements; do not silently invent either in the task list.


For changes to existing work, apply the [common change procedure](../gsp-development/references/change-management.md). Preserve old done/PASS executions and add linked modification/revalidation tasks. Use DAG v2 for automatic revision gating, update current acceptance and pending consumer bindings, and keep affected running reservations until safe hold is acknowledged. Route independent work normally.

## Check ambiguity — grilling

Read and apply [gsp-grilling](../gsp-grilling/SKILL.md). Investigate repository facts first. Ask the actual user, through the lead, only when an unresolved scope, priority, budget, or expected-behavior decision changes the plan. Reuse prior answers, include a recommendation, and hold only dependent work. Do not ask the user to approve every routine task or invent a calendar deadline.

## Build executable tasks

Write `spec/tasks.md` for new work. Follow AGENTS.md for explicit locations, continuations and preserving existing documents without migration. Link to the canonical requirements and architecture rather than duplicating them.

- Give each task a stable ID such as T1 and link it to requirement IDs and design sections. Cover all mandatory outcomes, including relevant integration, verification, documentation and handoff work. Separate optional work from required scope.
- For each task, record the concrete outcome, owned files or component boundary, prerequisites by task ID, observable completion conditions, and verification inputs/method with expected results. Use only known paths; mark proposed paths as proposed. Set the initial status to pending unless actual evidence supports a later state.
- Order work by real dependencies without cycles. Build the smallest usable flow early; include integration and final acceptance checks. Split tasks when separate ownership or completion evidence would help, not to satisfy an arbitrary size or count.
- Assign one integration owner. Consult relevant [session work records](../gsp-development/references/session-work.md) before assigning files, and include the shared root and session record paths in handoffs. Mark parallel work only when dependencies and file ownership permit it; apply the development skill's [isolation procedure](../gsp-development/references/parallel-work.md) for experiments or parallel writes. A record is not a lock; resolve overlapping ownership before dependent writes. Do not pretend that mentioning a worktree creates one.
- Carry PoC hypotheses, budget ceilings and stop rules into applicable experiment tasks. Include the remaining agreed PoR work only if requested. Do not invent cost estimates or turn PoC success into product completion.
- For parallel optimization, link a distinct task ID to the parent PoC, its existing requirement/design IDs and both session records. Cover baseline transfer and confirmation, baseline checks/measurement, the optimization delta, functional and comparative verification, handoff, and final integration/revalidation with the responsible owners and dependencies. Apply the [optimization handoff](../gsp-development/references/parallel-work.md#poc-development-with-a-parallel-optimization-task). Schedule measurements to avoid competing load on the same constrained resources. Keep unaffected PoC work moving and reuse valid stage outputs; the optimizer need not recreate the entire plan.
- Record known blockers, assumptions and next actions. Distinguish task planning from a dated schedule; provide dates or effort estimates only when useful and supported, clearly labeling estimates. Do not introduce a fixed default duration.

A compact entry can use these fields:

```markdown
### T1. <concrete outcome>
- Requirements and design: <R IDs and design section links>
- Prerequisites: <task IDs or none>
- Ownership and change scope: <owner/role and files/components>
- Completion conditions: <observable required behavior>
- Verification: <input/check and expected result>
- Status: pending
- Evidence or blocker: not run
```

Adapt the fields to the work; do not publish scaffold placeholders as a completed plan. A list of component names or coding steps without completion checks is not an executable plan. Planning does not execute tasks or establish that checks passed.

## Explicit DAG and Python checks

Read the [DAG format and routing procedure](references/task-dag.md). Add its single JSON DAG block to the task document, using the same Task IDs and actual dependencies, statuses, owners, read/write scopes and exclusive resources. Keep routing fields authoritative in that block and link task details instead of maintaining conflicting copies. Include integration and verification nodes. Set `max_parallel` from actual available workers/resources; do not invent default concurrency or time estimates.

Run `python3 .agents/skills/gsp-tasks/scripts/task_dag.py validate <task-document>` before review and after changes. Resolve format, dependency, cycle and state errors. Use `render` to show the derived DAG in Markdown and `route` to inspect the next conflict-free batch. Record commands and actual results. Routing prioritizes the longest remaining estimated path when estimates are complete, otherwise dependency steps; it is a heuristic, not a guaranteed optimum or permission to execute tasks. Planning-only requests stop after the reviewed plan.

The reviewer still checks whether the graph matches real requirements and interfaces. A successful script result does not establish semantic completeness, valid execution evidence or implementation success. Preserve existing plans and IDs when revising; do not mass-migrate unrelated records.

## Human-reviewable deliverables

Follow the "Documents for human review" contract in AGENTS.md. Maintain a Markdown document only (default `spec/tasks.md`), in the user's language. Include coverage, dependency order, parallel ownership where applicable, open decisions, and the task-plan review. Preserve stable IDs and prior results when revising; mark changed assumptions and affected work rather than resetting history. The lead updates the document and links it at handoff. Respect explicit format and no-write constraints. Do not create implementation results for a planning-only request.

## Completion and handoff

Request the single native `gsp-reviewer` with mode `tasks`. Pass the absolute project root, original request and requested endpoint, requirements/design/task-plan paths, requirement and task IDs, prior review results, current baseline, checks and open questions with existing answers. Use the reviewer defined in `.codex/agents/gsp-reviewer.toml`; follow AGENTS.md's disclosed fallback if unavailable. The reviewer returns findings read-only; the lead records task-plan findings separately from the later development review and resolves blockers with closure evidence.

A plan is ready when required outcomes have actionable tasks and completion checks, dependencies are feasible, and no unresolved blocker prevents the work being handed off. In a full development request, pass the reviewed plan to [gsp-development](../gsp-development/SKILL.md) without asking for repeated approval. If the user requested only task planning, stop after the plan and its review. Planning PASS never certifies implementation completion.
