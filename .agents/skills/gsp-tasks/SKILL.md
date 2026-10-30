---
name: gsp-tasks
description: Turn reviewed requirements and architecture into ordered, independently verifiable implementation tasks. Use after architecture review or when asked to create or revise a work breakdown; stop before implementation for a planning-only request.
---

# Task planning

Read the original request, current requirements and architecture, their review findings and closure evidence, and relevant existing code. Verify the reviews cover the current artifacts. Hold tasks dependent on unresolved blockers; independent planning may continue. A missing design decision belongs in architecture, and a missing user requirement belongs in requirements; do not silently invent either in the task list.

## Check ambiguity — grilling

Read and apply [gsp-grilling](../gsp-grilling/SKILL.md). Investigate repository facts first. Ask the actual user, through the lead, only when an unresolved scope, priority, budget, or expected-behavior decision changes the plan. Reuse prior answers, include a recommendation, and hold only dependent work. Do not ask the user to approve every routine task or invent a calendar deadline.

## Build executable tasks

Write `spec/tasks.md` for new work. Follow AGENTS.md for explicit locations, continuations and preserving existing documents without migration. Link to the canonical requirements and architecture rather than duplicating them.

- Give each task a stable ID such as T1 and link it to requirement IDs and design sections. Cover all mandatory outcomes, including relevant integration, verification, documentation and handoff work. Separate optional work from required scope.
- For each task, record the concrete outcome, owned files or component boundary, prerequisites by task ID, observable completion conditions, and verification inputs/method with expected results. Use only known paths; mark proposed paths as proposed. Set the initial status to pending unless actual evidence supports a later state.
- Order work by real dependencies without cycles. Build the smallest usable flow early; include integration and final acceptance checks. Split tasks when separate ownership or completion evidence would help, not to satisfy an arbitrary size or count.
- Assign one integration owner. Mark parallel work only when dependencies and file ownership permit it; apply the development skill's [isolation procedure](../gsp-development/references/parallel-work.md) for experiments or parallel writes. Do not pretend that mentioning a worktree creates one.
- Carry PoC hypotheses, budget ceilings and stop rules into applicable experiment tasks. Include the remaining agreed PoR work only if requested. Do not invent cost estimates or turn PoC success into product completion.
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

## Human-reviewable deliverables

Follow the "Documents for human review" contract in AGENTS.md. Maintain `spec/tasks.md` and a matching self-contained `spec/tasks.html` by default, in the user's language. Include coverage, dependency order, parallel ownership where applicable, open decisions, and the task-plan review. Preserve stable IDs and prior results when revising; mark changed assumptions and affected work rather than resetting history. The lead updates both views and links both at handoff. Respect explicit format and no-write constraints. Do not create implementation results for a planning-only request.

## Completion and handoff

Request the single native `gsp-reviewer` with mode `tasks`. Pass the absolute project root, original request and requested endpoint, requirements/design/task-plan paths, requirement and task IDs, prior review results, current baseline, checks and open questions with existing answers. Use the reviewer defined in `.codex/agents/gsp-reviewer.toml`; follow AGENTS.md's disclosed fallback if unavailable. The reviewer returns findings read-only; the lead records task-plan findings separately from the later development review and resolves blockers with closure evidence.

A plan is ready when required outcomes have actionable tasks and completion checks, dependencies are feasible, and no unresolved blocker prevents the work being handed off. In a full development request, pass the reviewed plan to [gsp-development](../gsp-development/SKILL.md) without asking for repeated approval. If the user requested only task planning, stop after the plan and its review. Planning PASS never certifies implementation completion.
