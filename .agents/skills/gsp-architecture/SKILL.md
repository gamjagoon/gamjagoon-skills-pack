---
name: gsp-architecture
description: Create or change system structure, interfaces and verification strategy when architecture work is requested or belongs to an agreed full GSP workflow. Do not treat UI, screen or visual design alone as a request for system architecture.
---

# Architecture design

Apply [requested scope and order](../../../AGENTS.md#requested-scope-and-order) before starting this stage. Reuse valid existing artifacts; missing prerequisite documents or reviews alone do not authorize earlier stages. Perform this stage and its review only when included in the requested or already agreed scope, and hand off to later stages only within that scope. Investigate actual blockers without expanding the task.

Read the current requirements, requirements review results, existing code structure, and execution environment. Check whether the previous review covered the current requirements, and do not finalize the design of areas with remaining blockers. Do not arbitrarily finalize a design that depends on unresolved required decisions. First use the existing project's structure.

For a changed requirement, interface or failed experiment, use the [common change procedure](../gsp-development/references/change-management.md). Record the changed contract revision and inspect actual consumers; keep compatible design decisions and prior evidence. Hand off affected and unknown boundaries plus required revalidation, not a blanket restart.

## Check ambiguity — grilling

At this stage, also read and apply [gsp-grilling](../gsp-grilling/SKILL.md). Ask when choices about storage, deployment, external integration, security, or compatibility produce different outcomes for the user. Do not finalize structures or interfaces that depend on an answer.

Follow that skill’s question rounds, lead/user routing and answer-reuse rules.

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

For a PoC with a parallel optimization task, define the smallest implementation boundary that preserves the agreed inputs, outputs and relevant error/side-effect behavior. Identify the contract and specification owner, affected callers, and files the PoC lead and optimizer may each change. Follow the [optimization handoff](../gsp-development/references/parallel-work.md#poc-development-with-a-parallel-optimization-task) for the baseline, comparison environment and integration evidence. Workers propose contract changes through their records and handoff; the owner updates the canonical design. Reuse unaffected design decisions and reviews. Hold only work dependent on an unresolved interface or policy change.

## Human-reviewable deliverables

Read and follow the [project document contract](../../../AGENTS.md#documents-for-human-review), including Markdown-only output, language, retained/explicit paths, stable IDs, evidence and handoff links. Default: `spec/architecture.md`. Record design rationale, alternatives, interfaces, requirement-to-component mapping, dependencies, and verification plan; make user decisions and their consequences easy to locate. Respect stage-only requests and explicit format/no-write constraints.

## Completion and handoff

The design is complete when every mandatory requirement in scope is linked to a responsible component and verification strategy, interfaces are coherent, and important risks and constraints are explicit. Hand off design boundaries and dependency constraints to gsp-tasks only if task planning is included in the requested scope; the detailed task list and its review belong to that next stage, not this one. Do not require a completed tasks.md to finish architecture review. For assumptions requiring experiments, also hand off the verification results or the reason they remain unverified and the affected scope. When reviewing this GSP stage, request the native Codex agent `gsp-reviewer` with mode `architecture`. Pass the absolute project root, requested scope, original requirements and design paths, relevant code locations, requirement IDs where present, baseline state, experimental evidence, checks performed, and unresolved questions with existing answers. Read the [reviewer contract](../../../.codex/agents/gsp-reviewer.toml) for this mode and follow the [review/fallback rules](../../../AGENTS.md#reviews-and-stage-transitions). The lead records findings and resolves blockers before dependent work. After resolving architecture-review blockers, continue with [gsp-tasks](../gsp-tasks/SKILL.md) only when included in the requested scope. If only system architecture was requested, stop without task planning or implementation.
