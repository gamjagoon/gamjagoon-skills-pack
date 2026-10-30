---
name: gsp-architecture
description: Turn reviewed requirements into a minimal structure, interfaces, and verification strategy. Use when creating or changing a design to meet requirements.
---

# Architecture design

Read the current requirements, requirements review results, existing code structure, and execution environment. Check whether the previous review covered the current requirements, and do not finalize the design of areas with remaining blockers. Do not arbitrarily finalize a design that depends on unresolved required decisions. First use the existing project's structure.

## Check ambiguity — grilling

At this stage, also read and apply [gsp-grilling](../gsp-grilling/SKILL.md). Ask when choices about storage, deployment, external integration, security, or compatibility produce different outcomes for the user. Do not finalize structures or interfaces that depend on an answer.

Present questions to the actual user with a recommendation, and hold only the parts dependent on the answer. The main worker gathers and asks questions from review and work subagents. Reuse existing answers.

## What to document

Write the following in `spec/architecture.md` for new work, or retain the valid continuation record under AGENTS.md:

1. The core flow from input to result and the required components.
2. Each component's responsibilities, data, function, and API boundaries, and error handling.
3. Requirement ID → responsible file or component → method of confirming completion. Also link existing behavior and affected callers and integration paths.
4. Risky assumptions and the smallest experiment to check them.
5. Test and execution methods, required dependencies, scopes that can be split for parallel work, and the integration owner.

For important choices, record the rationale and alternatives to actually consider. Do not add unnecessary layers, services, or frameworks to a small task. Do not guarantee performance, security, or compatibility without code or execution evidence. Follow the development skill's isolation rules for experiments with uncertain dependencies.

## Problem, experiment, and completion scope

Follow the project brief and PoC/PoR contract in AGENTS.md. Compare the current approach, reuse or a simple deterministic option, and additional complexity only when justified. If uncertainty warrants an experiment, define the cheapest adequate PoC with representative inputs, baseline, pass/fail evidence, a budget ceiling and stop rule. Explain its limitations and the gaps to the agreed finished deliverable (PoR), with proportionate implementation and verification needs. Keep PoC-only requests within their scope.

## Human-reviewable deliverables

Follow the "Documents for human review" contract in the project AGENTS.md. The lead maintains a Markdown source and a matching, self-contained HTML view (default `spec/architecture.md` and `spec/architecture.html`), using the user's language. Preserve existing project documents without automatic migration; explicit locations and continuation records follow AGENTS.md. Publish the design rationale, alternatives, interfaces, requirement-to-component mapping, dependencies, and verification plan in both views. Make choices needing user input and their consequences easy to locate. Keep both views synchronized, preserve unrelated files, and link both in the user-facing handoff. Respect explicit format and no-write constraints; do not claim an HTML file exists if it was not created.

## Completion and handoff

The design is complete when every mandatory requirement is linked to a responsible component and verification strategy, interfaces are coherent, and important risks and constraints are explicit. Hand off design boundaries and dependency constraints to gsp-tasks; the detailed task list and its review belong to that next stage, not this one. Do not require a completed tasks.md to finish architecture review. For assumptions requiring experiments, also hand off the verification results or the reason they remain unverified and the affected scope. In the full workflow, request the native Codex agent `gsp-reviewer` with mode `architecture`. Pass the absolute project root, requested scope, original requirements and design paths, relevant code locations, requirement IDs, baseline state, experimental evidence, checks performed, and unresolved questions with existing answers. Use the agent defined in `.codex/agents/gsp-reviewer.toml`; ask it to return an independent review to the lead worker, who records and resolves findings before continuing. Do not present an author's self-review as independent. If the native role or independent subagents are unavailable, follow the availability fallback in AGENTS.md and disclose the review method. After resolving architecture-review blockers, continue with [gsp-tasks](../gsp-tasks/SKILL.md) within the requested scope. If only a design was requested, stop without task planning or implementation.
