---
name: gsp-requirements
description: Organize a user's work request into requirements supported by the original text and observable completion criteria. Use when starting a new feature or project or writing a requirements document. Do not use for reviews of design or implementation results.
---

# Writing requirements

Read the user's request, provided materials, existing project state, and existing requirements. First distinguish a continuation of existing work from a new request; do not reuse a previous completion judgment or deadline for a new request. Investigate facts that can be checked in files or tools directly, and ask only about unresolved decisions that change the outcome. Do not seek approval again for what has already been decided.

## Checking ambiguity — grilling

At this stage, also read and apply [gsp-grilling](../gsp-grilling/SKILL.md). If the goal, target users, scope, or completion criteria can be interpreted in multiple ways, ask questions and do not finalize the affected requirements before receiving answers.

Send the questions and recommendations to the actual user, and wait only on the parts that depend on the answers. The lead worker consolidates and asks questions from review and work subagents. Reuse existing answers.

## What to write

Prefer the existing document location for the work record; if none exists, use the requirements section of `TASK.md`.

- Goal, target users, inputs and outputs, required scope, and exclusions.
- Identify every mandatory item in the original text as R1, R2, and so on, and link it to its source or location in the original text.
- For each item, provide actual input or conditions → expected behavior or result → verification method. For changes to existing functionality, include existing behavior that must be preserved. Do not use “tests pass” alone as a completion criterion.
- Distinguish environment, time, and dependency constraints, confirmed facts, assumptions, and unresolved decisions.

| ID | Mandatory requirement | Original-text evidence | Completion criteria and verification method | Status |
| --- | --- | --- | --- | --- |
| R1 | Functionality based on the original text | Location in the original text | Actual input and expected result | Not implemented |

Do not arbitrarily settle implementation technology as a requirement or add functionality absent from the original text. Do not state unverifiable numbers or tolerances as facts.

## Problem, experiment, and completion scope

For substantive work, establish the project brief defined in AGENTS.md in the existing work record or `TASK.md` (with its matching HTML view): observed problem and affected users, current baseline, measurable outcome, constraints, scope/non-goals, unresolved assumptions, and whether the request ends at investigation, PoC, or the agreed finished deliverable (PoR). Distinguish unknown limits from unlimited resources. Link PoC hypotheses and PoR acceptance criteria to requirement IDs; do not require a new PoC when existing evidence is sufficient.

## Human-reviewable deliverables

Follow the "Documents for human review" contract in the project AGENTS.md. The lead maintains a Markdown source and a matching, self-contained HTML view (default `TASK.md` and `TASK.html`), using the user's language and existing document locations. Publish the requirements and acceptance criteria, original-text references, unresolved questions with recommendations, and confirmed decisions in both views. If only requirements were requested, do not fill later stages with invented results. Keep both views synchronized, preserve unrelated files, and link both in the user-facing handoff. Respect explicit format and no-write constraints; do not claim an HTML file exists if it was not created.

## Completion and handoff

Once the original text and requirement IDs are linked and the completion criteria can be verified, request the native Codex agent `gsp-reviewer` with mode `requirements`. Pass the absolute project root, requested scope, original text and requirements paths, requirement IDs, baseline state, checks performed, and unresolved questions with existing answers. Use the agent defined in `.codex/agents/gsp-reviewer.toml`; ask it to return an independent review to the lead worker, who records and resolves findings before continuing. Do not present an author's self-review as independent. If the native role or independent subagents are unavailable, follow the availability fallback in AGENTS.md and disclose the review method. If important decisions remain unresolved, mark those items and their dependent scope; do not treat all preparation as complete. For change requests, preserve existing items and decision history, and identify the changes and affected downstream stages. If the user requested only requirements writing, stop with this deliverable.
