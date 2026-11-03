---
name: gsp-requirements
description: Organize a user's work request into requirements supported by the original text and observable completion criteria. Use when starting a new feature or project or writing a requirements document. Do not use for reviews of design or implementation results.
---

# Writing requirements

Read the user's request, provided materials, existing project state, and existing requirements. First distinguish a continuation of existing work from a new request; do not reuse a previous completion judgment or deadline for a new request. Investigate facts that can be checked in files or tools directly, and ask only about unresolved decisions that change the outcome. Do not seek approval again for what has already been decided.


When the request changes, use the [common change procedure](../gsp-development/references/change-management.md). Keep the source decision and prior requirement revision, identify affected acceptance/design/task links, and reopen only those parts. A new request without explicit priority preserves running work and enters the existing routing policy.

## Checking ambiguity — grilling

At this stage, also read and apply [gsp-grilling](../gsp-grilling/SKILL.md). If the goal, target users, scope, or completion criteria can be interpreted in multiple ways, ask questions and do not finalize the affected requirements before receiving answers.

Send the questions and recommendations to the actual user, and wait only on the parts that depend on the answers. The lead worker consolidates and asks questions from review and work subagents. Reuse existing answers.

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

Follow the "Documents for human review" contract in the project AGENTS.md. The lead maintains a Markdown document only (default `spec/requirement.md`), using the user's language. Preserve existing project documents without automatic migration; explicit locations and continuation records follow AGENTS.md. Record the requirements and acceptance criteria, original-text references, unresolved questions with recommendations, and confirmed decisions. If only requirements were requested, do not fill later stages with invented results. Preserve unrelated files and link the document in the user-facing handoff. Respect explicit format and no-write constraints.

## Completion and handoff

Once the original text and requirement IDs are linked and the completion criteria can be verified, request the native Codex agent `gsp-reviewer` with mode `requirements`. Pass the absolute project root, requested scope, original text and requirements paths, requirement IDs, baseline state, checks performed, and unresolved questions with existing answers. Use the agent defined in `.codex/agents/gsp-reviewer.toml`; ask it to return an independent review to the lead worker, who records and resolves findings before continuing. Do not present an author's self-review as independent. If the native role or independent subagents are unavailable, follow the availability fallback in AGENTS.md and disclose the review method. If important decisions remain unresolved, mark those items and their dependent scope; do not treat all preparation as complete. For change requests, preserve existing items and decision history, and identify the changes and affected downstream stages. If the user requested only requirements writing, stop with this deliverable.
