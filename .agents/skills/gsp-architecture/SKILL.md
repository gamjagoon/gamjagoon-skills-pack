---
name: gsp-architecture
description: Turn reviewed requirements into a minimal structure, interfaces, implementation tasks, and verification plan. Use when creating or changing a design to meet requirements.
---

# Architecture design

Read the current requirements, requirements review results, existing code structure, and execution environment. Check whether the previous review covered the current requirements, and do not finalize the design of areas with remaining blockers. Do not arbitrarily finalize a design that depends on unresolved required decisions. First use the existing project's structure.

## Check ambiguity — grilling

At this stage, also read and apply [gsp-grilling](../gsp-grilling/SKILL.md). Ask when choices about storage, deployment, external integration, security, or compatibility produce different outcomes for the user. Do not finalize structures or interfaces that depend on an answer.

Present questions to the actual user with a recommendation, and hold only the parts dependent on the answer. The main worker gathers and asks questions from review and work subagents. Reuse existing answers.

## What to document

Briefly record the following in an existing design document or the design section of `TASK.md`:

1. The core flow from input to result and the required components.
2. Each component's responsibilities, data, function, and API boundaries, and error handling.
3. Requirement ID → responsible file or component → implementation task → method of confirming completion. Also link existing behavior and affected callers and integration paths.
4. Risky assumptions and the smallest experiment to check them.
5. Test and execution methods, required dependencies, scopes that can be split for parallel work, and the integration owner.

For important choices, record the rationale and alternatives to actually consider. Do not add unnecessary layers, services, or frameworks to a small task. Do not guarantee performance, security, or compatibility without code or execution evidence. Follow the development skill's isolation rules for experiments with uncertain dependencies.

## Human-reviewable deliverables

Follow the "Documents for human review" contract in the project AGENTS.md. The lead maintains a Markdown source and a matching, self-contained HTML view (default `TASK.md` and `TASK.html`), using the user's language and existing document locations. Publish the design rationale, alternatives, interfaces, requirement-to-task mapping, dependencies, and verification plan in both views. Make choices needing user input and their consequences easy to locate. Keep both views synchronized, preserve unrelated files, and link both in the user-facing handoff. Respect explicit format and no-write constraints; do not claim an HTML file exists if it was not created.

## Completion and handoff

The design is complete when every mandatory requirement is linked to an implementation location and verification method, and the tasks ready to start and their dependencies are clear. For each task, record its scope, prerequisites, completion check, and integration owner. For assumptions requiring experiments, also hand off the verification results or the reason they remain unverified and the affected scope. In the full workflow, request the native Codex agent `gsp-reviewer` with mode `architecture`. Pass the absolute project root, requested scope, original requirements and design paths, relevant code and task locations, requirement IDs, baseline state, experimental evidence, checks performed, and unresolved questions with existing answers. Use the agent defined in `.codex/agents/gsp-reviewer.toml`; ask it to return an independent review to the lead worker, who records and resolves findings before continuing. Do not present an author's self-review as independent. If the native role or independent subagents are unavailable, follow the availability fallback in AGENTS.md and disclose the review method. If only a design was requested, do not implement it.
