---
name: gsp-requirements
description: Write or revise requirements supported by original text and observable completion criteria when requirements work is requested or belongs to an agreed full GSP workflow. Do not restart requirements for a scoped design or implementation task, or use for reviews of design or implementation results.
---

# Writing requirements

Apply [requested scope and order](../../../AGENTS.md#requested-scope-and-order) before starting this stage. Reuse valid existing artifacts; missing prerequisite documents or reviews alone do not authorize earlier stages. Perform this stage and its review only when included in the requested or already agreed scope, and hand off to later stages only within that scope. Investigate actual blockers without expanding the task.

Read the user's request, provided materials, existing project state, and existing requirements. First distinguish a continuation of existing work from a new request; do not reuse a previous completion judgment or deadline for a new request. Investigate facts that can be checked in files or tools directly, and ask only about unresolved decisions that change the outcome. Do not seek approval again for what has already been decided.

When the request changes, use the [common change procedure](../gsp-development/references/change-management.md). Keep the source decision and prior requirement revision, identify affected acceptance/design/task links, and reopen only those parts. A new request without explicit priority preserves running work and enters the existing routing policy.

## Checking ambiguity — grilling

At this stage, also read and apply [gsp-grilling](../gsp-grilling/SKILL.md). If the goal, target users, scope, or completion criteria can be interpreted in multiple ways, ask questions and do not finalize the affected requirements before receiving answers.

Follow that skill’s question rounds, lead/user routing and answer-reuse rules.

## What to write

Write `spec/requirement.md` for new work. Preserve valid existing records for a continuation and respect explicit document locations; do not migrate old documents just to adopt this layout.

- Goal, target users, inputs and outputs, required scope, and exclusions.
- Identify every mandatory item in the original text as R1, R2, and so on, and link it to its source or location in the original text.
- For each item, provide actual input or conditions → expected behavior or result → verification method. For changes to existing functionality, include existing behavior that must be preserved. Do not use “tests pass” alone as a completion criterion.
- Distinguish environment, time, and dependency constraints, confirmed facts, assumptions, and unresolved decisions.

| ID | Mandatory requirement | Original-text evidence | Completion criteria and verification method | Status |
| --- | --- | --- | --- | --- |
| R1 | Functionality based on the original text | Location in the original text | Actual input and expected result | Not implemented |

Do not arbitrarily settle implementation technology as a requirement or add functionality absent from the original text. Do not state unverifiable numbers or tolerances as facts.

## Problem, experiment, and completion scope

For substantive work, establish the project brief defined in AGENTS.md in `spec/requirement.md` (or the retained continuation record): observed problem and affected users, current baseline, measurable outcome, constraints, scope/non-goals, unresolved assumptions, and whether the request ends at investigation, PoC, or the agreed finished deliverable (PoR). Distinguish unknown limits from unlimited resources. Link PoC hypotheses and PoR acceptance criteria to requirement IDs; do not require a new PoC when existing evidence is sufficient.

For optimization of an existing PoC, reuse its requirements and identify the affected IDs. State the behavior and interface that must remain compatible, the metric to improve, representative inputs, and whether performance is required for PoC acceptance or is a follow-up improvement. Record user-specified targets and constraints without inventing numerical thresholds. If no numeric target was given, a bounded before/after comparison can report observed improvement and limits; do not claim an unspecified target was met. Investigate missing baseline measurements as work, and ask only about unresolved priorities or allowed tradeoffs that change the outcome. Do not expand a PoC optimization into PoR by default.

## Human-reviewable deliverables

Read and follow the [project document contract](../../../AGENTS.md#documents-for-human-review), including Markdown-only output, language, retained/explicit paths, stable IDs, evidence and handoff links. Default: `spec/requirement.md`. Record requirements and acceptance criteria, original-text references, unresolved questions with recommendations, and confirmed decisions. Respect stage-only requests and explicit format/no-write constraints.

## Completion and handoff

Once the original text and requirement IDs are linked and the completion criteria can be verified, request the native Codex agent `gsp-reviewer` with mode `requirements`. Pass the absolute project root, requested scope, original text and requirements paths, requirement IDs, baseline state, checks performed, and unresolved questions with existing answers. Read the [reviewer contract](../../../.codex/agents/gsp-reviewer.toml) for this mode and follow the [review/fallback rules](../../../AGENTS.md#reviews-and-stage-transitions). The lead records findings and resolves blockers before dependent work. If important decisions remain unresolved, mark those items and their dependent scope; do not treat all preparation as complete. For change requests, preserve existing items and decision history, and identify the changes and affected downstream stages. If the user requested only requirements writing, stop with this deliverable.
