# Installing or updating this pack

When the user asks to install or update **gamjagoon-skills-pack**, read this
repository's README and `install.sh`. Download the current repository into a
temporary source directory, preserve the user's original project path, and run
`bash install.sh --dry-run <project-path>` followed by `bash install.sh <project-path>`
when the preview succeeds. Use this script instead of manually copying files or
using the generic skill installer for individual folders. Preserve custom conflicts;
use `--overwrite` only after reviewing the differences. If Codex protects `.agents` or `.codex`,
use its normal approval flow and report a blocked installation if approval is unavailable.
After installation, read the target AGENTS, skills, and reviewer definition in the current conversation.
Reading the definition is not proof that the native agent was loaded; verify availability or report the limitation.
The script installs only the managed block below, not this source-only entrypoint.

<!-- GAMJAGOON-SKILLS-PACK:START -->
# gamjagoon-skills-pack

## Requested scope and order

The user's requested scope and order take precedence over the default GSP sequence below, including skill selection, prerequisite checks, reviews, document creation and handoffs. Use the full sequence when the requested or already agreed scope includes the full development workflow. For a specific stage or task, perform only that scope; do not interpret "only this stage" as "all stages up to this stage".

Reuse existing requirements, designs and reviews that remain valid, including artifacts from another session. A new session or a missing prerequisite document/review alone does not authorize recreating earlier stages or starting later ones. Investigate available evidence first; ask only about unresolved decisions that actually block the requested work, and hold only dependent work. Preserve applicable safety, verification, ownership and interface constraints; do not bypass a concrete blocker.

UI, screen and visual design requests are not automatically requests for GSP system architecture. Apply skills within the requested scope. Stage document and review rules below apply to the GSP stages actually being performed; they do not require unrelated stage artifacts for a scoped task. Review approval does not expand scope or authorize the next stage by itself.

## Bounded existing-code changes

For a small, well-understood change to existing code, first identify the affected behavior, acceptance criteria, relevant constraints, and existing evidence. Reuse valid artifacts and load only the stage guidance applicable to the work; briefly record why stages are omitted. Inspect the relevant code and verify the change proportionately. Load the reviewer contract when review is required or requested, and parallel-work references only when delegation or parallel work is actually needed. This route does not waive applicable safety, scope, evidence, coordination, or review requirements.

<!-- CODEGRAPH_START -->
## CodeGraph

When you need to understand or locate code, resolve the actual project root and use an existing usable CodeGraph index before grep/find or reading code files. Check `codegraph status --json "<absolute-project-root>"` for the actual index path and readiness; `.codegraph/` may be absent when a configured index exists elsewhere. Reuse an existing index rather than initializing it again; sync it when stale and confirm relevant query results before relying on it. For a bounded existing-code change, a missing or unusable index does not trigger automatic initialization: use targeted source and text inspection and report the index limitation when relevant. Outside the bounded existing-code route, if the target has no usable index, initialize it with `CODEGRAPH_TELEMETRY=0 codegraph init "<absolute-project-root>"` and wait before code investigation, following the initialization safeguards in [gsp-adopt](.agents/skills/gsp-adopt/SKILL.md). If CodeGraph is unavailable, initialization/sync/query fails, or a no-write constraint prevents required indexing, report the concrete limitation and hold dependent code investigation; continue independent document work. Do not silently substitute a full text scan.

For explicitly requested project adoption, follow the initialization and failure safeguards in [gsp-adopt](.agents/skills/gsp-adopt/SKILL.md): select manual sync if prompted, do not use `--yes` blindly, and do not install hooks or change global configuration. Adoption may initialize a missing index and holds dependent investigation if that required step fails. Installing this pack alone does not run initialization.

- **MCP tool** (when available): `codegraph_explore` answers most code questions in one call — the relevant symbols' verbatim source plus the call paths between them, including dynamic-dispatch hops grep can't follow. Name a file or symbol in the query to read its current line-numbered source. If it's listed but deferred, load it by name via tool search.
- **Shell** (when the CLI is available): run `codegraph explore "<symbol names or question>"` from the target project root to print the same output.
<!-- CODEGRAPH_END -->

## Project purpose and working brief

Use this as a general-purpose project guide. Start from the problem and intended outcome, not from a technology or a demo deadline. For substantial new work, establish the following brief in `spec/requirement.md`. Reuse answers and repository evidence instead of asking the user to fill in a form from scratch. Keep unknowns explicit; ask only about unresolved decisions that materially affect the outcome. For a small, well-understood change, record only the affected items.

| Brief section | What to establish |
| --- | --- |
| Problem and users | Who encounters which problem, in what situation, and why it matters. Link examples or evidence; distinguish an observed problem from a hypothesis. |
| Current baseline | The existing workflow, workaround, or measured behavior; explain why a change is needed and what must remain compatible. |
| Desired outcome | Observable user benefit and acceptance criteria, including measurement method and target environment. Do not invent numerical targets. |
| Scope and exclusions | Required scenarios, explicit non-goals, and the requested endpoint: investigation, PoC, or finished deliverable (PoR). |
| Constraints | Deadline if any, money/API/compute limits, available people and tools, hardware/runtime, data access, privacy/security, licenses, and external dependencies where relevant. Mark an unknown separately from no constraint. |
| Assumptions and risks | Unproven beliefs, impact if wrong, dependencies, and the next evidence needed. Prioritize risks that could invalidate the approach. |
| PoC experiment | Hypothesis, cheapest adequate test, inputs, expected observation, pass/fail criteria, cost ceiling, stop rule, and result. Existing sufficient evidence may make a new PoC unnecessary. |
| PoR completion | The agreed usable deliverable, required quality and verification evidence, delivery method, and any remaining gaps with owners or next actions. |

These are working-record fields, not values to fabricate or placeholders to declare complete. Keep durable project-specific instructions outside this pack's managed block when they belong in `AGENTS.md`, so updates preserve them. Installation creates guidance only; it does not choose a project, start experiments, or manufacture a completed brief.

## From problem to PoC to PoR

In this pack, **PoC** means a bounded proof of concept that resolves a specific uncertainty. **PoR** means the finished deliverable for the scope agreed with the user. PoR is a user-defined completion target here, not an assumed expansion of the acronym, a universal production certification, or automatic authorization to deploy.

Use the four production stages and their four reviews below within this progression; do not create a second competing process or new roles. Authorized independent workers may participate within this one workflow. The requirements stage establishes the problem, constraints, target endpoint, and acceptance criteria. Architecture selects an approach and necessary experiments. Task planning turns the reviewed design into ordered, verifiable work. Development obtains evidence and, when included in the request, completes the deliverable. Reviews check evidence against the current endpoint. Reopen only affected decisions when evidence changes the plan. A PoC-only request ends with its findings and next-step recommendation; it does not authorize a full product build. Do not force a new PoC for a routine change already supported by adequate evidence; state why it is unnecessary.

### PoC: the least costly adequate experiment

Identify the most consequential unresolved hypothesis before building. Compare the current/manual approach, a simple deterministic solution or reuse of existing tools, and a more complex option only when needed. Choose the smallest experiment that can discriminate between approaches under the relevant conditions. Low cost means reducing total effort, API/compute spend, dependencies, and rework while preserving useful evidence; it does not mean choosing a cheap model or a mock that cannot answer the question.

Before running an experiment, record its hypothesis, representative input, baseline, observable pass/fail criteria, expected resource use, allowed budget, stop condition, and resulting decision. If the environment cannot support the required check, record that limit rather than replacing it with a success claim. Use small samples or mocks only when adequate for the hypothesis, label them, and identify what later needs validation with real data or integrations.

Reuse existing assets and cached results when applicable, bound calls and retries, and avoid parallel experiments that answer the same question without a reason. Estimates and actual cost must be distinguished; record unknown cost as unknown. Do not treat an unspecified budget as unlimited or silently begin unapproved paid services, infrastructure, or external writes. When no monetary budget is specified, prefer bounded work using already-authorized resources without a new paid service or resource commitment; this is not permission to invent a zero-cost estimate. Stay within existing authorization, investigate available low-cost options, and ask only for the missing spending or scope decision. Keep independent work moving.

After the PoC, record observations, cost actually known, limitations, and a decision: proceed, revise the hypothesis/approach, or stop. A failed experiment can be useful evidence but is not a passing PoC or a finished product. If criteria fail or the budget ceiling is reached, stop the affected experiment and reassess; do not spend more or lower the success criteria silently. A successful narrow experiment does not establish overall readiness.

### PoR: the agreed finished deliverable

Before expanding a PoC, make its gaps explicit and translate them into scoped implementation and verification work. Proceed within the existing request without repeated approval when PoR was already requested; otherwise ask before expanding scope. Carry forward useful PoC evidence but retire demo shortcuts that conflict with the agreed deliverable.

Define completion proportionally to the artifact and its intended users. Check the applicable items below and justify any exclusions; do not add enterprise infrastructure to a small local tool merely to satisfy a checklist.

- Required user workflows work through the actual entry point in the agreed environment; acceptance criteria trace to observed results, not just a passing test count.
- Relevant invalid inputs, boundary cases, failures, and existing behavior are checked. Data integrity, security/privacy, performance, reliability, or accessibility have explicit criteria and evidence where they matter to the project.
- Someone else can obtain the artifact and reproduce setup and execution using documented prerequisites, versions/configuration, commands, and representative examples. Handle secrets without embedding them in code or reports.
- The applicable delivery package is complete: source/build artifact or document, setup and usage instructions, verification results, known limitations, and maintenance or handoff information. For deployed/stateful systems, include the necessary logging, recovery/rollback, migration and ownership details; omit inapplicable operational machinery with a reason.
- Blocking defects and essential decisions are resolved. Distinguish independent review from author checks, and record accepted nonblocking limitations. Passing a PoC or a review of only one part does not close unverified PoR criteria.

Report the actual state: PoC not needed, planned, in progress, passed or failed; and PoR not requested, in progress, blocked or complete, as applicable. Complete only the requested scope with supporting evidence. When essential verification cannot be run, describe what is implemented, what remains unverified, its impact, and the next action; do not label the result a finished PoR. Readiness evidence never substitutes for permission to publish, deploy, send data, or incur new costs.

## Workflow

When asked to prepare a project not previously developed with GSP for GSP-based work, use [gsp-adopt](.agents/skills/gsp-adopt/SKILL.md). It investigates existing code and scattered materials, creates or refreshes the local CodeGraph index before code investigation, and establishes linked requirements, architecture and task documents using the relevant stages below. Stop after the requested documentation and handoff. Installing this pack alone does not invoke adoption, create an index or start development.

For a full development workflow within the requested or already agreed scope, use the following order. Read the skill or reviewer contract for the current stage and pass its outputs and unresolved issues to the next authorized stage. Do not require the user to invoke each stage of an already requested full workflow. For a specific stage or task, apply Requested scope and order above and stop at its boundary. For simple questions and small changes, apply only the necessary stages and briefly record why any were omitted.

| Order | Skill or agent | Output |
| --- | --- | --- |
| 1 | [Requirements writing](.agents/skills/gsp-requirements/SKILL.md) | `spec/requirement.md`: source evidence, scope and completion criteria |
| 2 | [gsp-reviewer](.codex/agents/gsp-reviewer.toml), mode `requirements` | Review of omissions, contradictions, and verifiability |
| 3 | [Architecture](.agents/skills/gsp-architecture/SKILL.md) | `spec/architecture.md`: minimal structure, interfaces and verification strategy |
| 4 | [gsp-reviewer](.codex/agents/gsp-reviewer.toml), mode `architecture` | Review of requirements coverage, feasibility, and complexity |
| 5 | [Task planning](.agents/skills/gsp-tasks/SKILL.md) | `spec/tasks.md`: explicit DAG, dependencies, ownership, Python validation and completion checks |
| 6 | [gsp-reviewer](.codex/agents/gsp-reviewer.toml), mode `tasks` | Review of coverage, actionable scope, dependencies and verification work |
| 7 | [Development](.agents/skills/gsp-development/SKILL.md) | Implementation, execution and test results recorded in `spec/tasks.md` |
| 8 | [gsp-reviewer](.codex/agents/gsp-reviewer.toml), mode `development` | Review of defects and regressions, fixes and revalidation, usage and limitations |

At the start, compare the current request with the source and unfinished items to determine whether it continues existing work or is a separate task. For the same task, continue from valid outputs; for a separate task, create a new title and record its start and any user-specified deadline. Do not reuse the PASS or time of completed work for a new request. For new substantive GSP stage work, create `spec/` and use `requirement.md`, `architecture.md`, and `tasks.md` only as their requested stages are performed. Do not create future-stage placeholders or a new root-level work log. Do not migrate, rename, rewrite, or delete existing project documents merely to adopt this layout. For a continuation, reuse and link valid existing records; explicit user locations take precedence. Preserve unrelated content at the default paths; use and report a non-conflicting location if needed. Do not create work documents or a new deadline for simple questions, or start development when asked only to install. Record the following in the relevant stage document:

- Current task: the source text or its location, changes to the request, scope and budget, current stage, and next action.
- The connection from requirements → architecture → task IDs → actual verification. Keep existing records and IDs and distinguish changes.
- Each review: paths of the source and outputs read and their baseline state, review method, verdict and findings, and evidence for fixes and rechecks.

When creating or revising a task plan, include the [explicit DAG](.agents/skills/gsp-tasks/references/task-dag.md) in its Markdown and run the bundled Python validator. Use routing output to propose independent work within actual capacity; record real starts, verified completion and blockers, then reroute as state changes. The tool checks declared structure/scopes and suggests a batch; the lead retains agent dispatch, isolation and integration responsibility. Do not treat script success as task completion or an optimal-schedule guarantee.

Do not seek renewed approval at each stage for work already approved. Investigate facts that can be checked with files or tools, and ask only for important user decisions that change the outcome. Continue work that does not depend on that decision or a blocking defect.

## Changes during the workflow

When a request, contract, interface, test result or integration basis changes, read and apply the [common change procedure](.agents/skills/gsp-development/references/change-management.md). It owns revision history, affected-stage reopening, safe checkpoints, new modification/revalidation tasks and current acceptance bindings. Preserve old done/PASS evidence; hold only dependent work, retain running reservations until their owner confirms a safe checkpoint, and compare candidate/current baselines before integration. Use DAG v2 for declared revision/hold/revalidation/current-acceptance checks; do not mass-migrate unrelated plans.

For explicitly selected same-VM/account notifications, read [local session coordination](.agents/skills/gsp-development/references/session-control.md). It adds registered-session delivery and separate read/held/applied acknowledgements using existing Python and Codex. It does not install/start services, wake idle agents or replace work-boundary checks. Unavailable delivery stays unresolved; prior ACKs never close a new change.

## Shared session work records

Before starting or resuming project-file changes, read and apply the [session record procedure](.agents/skills/gsp-development/references/session-work.md). It owns shared-root resolution, record contents, atomic updates, peer checks and handoffs. Use one absolute `.gsp-work/` in the main checkout across linked worktrees; resolve unavailable or ambiguous access before dependent writes. Each writing session updates only its unique `sessions/<id>/work.md`; pass the shared root and record path in handoffs. Consult relevant peers before ownership/interface changes and integration, and refresh your record at meaningful changes and before stopping.

Keep `.gsp-work/` out of Git and preserve existing records. Records support coordination, not locking, notifications, synchronization or proof that another session is idle or agrees. Resolve overlapping writes through one integration owner or serialization. Authoritative requirements and acceptance stay in stage documents. Installation alone and simple questions need no session record; read-only reviewers return findings for the lead to record.

## Documents for human review

For substantive requirements, design, task planning, implementation/verification, and review deliverables, the lead produces Markdown documents only. Do not generate or refresh companion HTML as part of this workflow, and do not delete existing HTML artifacts automatically. Use the user's requested language for the deliverables; these English instructions do not require English output. The default paths are `spec/requirement.md`, `spec/architecture.md`, and `spec/tasks.md`. Requirements own the problem, acceptance criteria and decisions; architecture owns the design and rationale; tasks owns the execution plan, progress and actual verification evidence. Record each review in its stage document; keep task-plan review and final implementation review separate in `tasks.md`. Cross-link stable IDs instead of duplicating authoritative content. Create only documents needed for the requested stages. Existing records may remain in place for ongoing work without automatic migration. Respect explicitly requested formats, locations, and no-write constraints. Installation alone and simple questions do not create these files. If writing is forbidden, return the permitted Markdown in conversation.

Markdown is the source of truth. Update it at each substantive stage handoff, after recording review results or user decisions, and before final delivery. Keep stable requirement, question, and finding IDs and identify revisions. Do not overwrite unrelated existing documents; preserve their content or choose a non-conflicting sibling path and report it. Multiple existing documents may keep their layout rather than being merged into a new record.

Make the documents easy to review:
- Start with the current stage, scope, outcome so far, changes since the previous revision, unresolved blockers, and decisions needed from the user. Distinguish recommendations from accepted decisions.
- Include only sections relevant to the requested scope: requirements and acceptance criteria; design rationale and alternatives; implementation tasks and dependencies; review findings; verification evidence and limitations. Do not invent completed stages, PASS verdicts, or test results to fill a template.
- Use concise headings, a table of contents, and linked IDs. Show findings in a table with blocking status, requirement ID, location, impact, suggested fix, and closure evidence. Show checks with command/input, expected and observed result, evidence type, and whether they passed, failed, or were not run. Provide source/artifact references and mark unavailable links as unavailable.
- Use portable, GitHub-compatible Markdown with working table-of-contents links. Do not assume renderer-specific heading-ID syntax works. Put literal markup and code in inline or fenced code so quoted input remains visible as text in Markdown too.
- Keep the complete evidence available in Markdown or linked evidence files. Do not omit uncertainty or unrun checks from summaries.

The reviewer remains read-only: it returns structured findings to the lead, who updates the relevant Markdown documents. Formatting does not replace reviewing source artifacts or running relevant checks. Before handoff, check decisions, IDs, verdicts, evidence, links, and readability, and state any check not performed. End the user-facing delivery with clickable links to the relevant documents; files and summaries alone do not count as the user answering an open question.

## Grilling in every stage

At every applicable production/review stage, read and apply [gsp-grilling](.agents/skills/gsp-grilling/SKILL.md), which owns question rounds and decision recording. Investigate source/file/execution facts first; ask the actual user only about unresolved intent, policy or expected behavior that changes the outcome. The lead consolidates worker/reviewer questions with recommendations, reuses existing answers, and holds only dependent work. A recommendation, silence or elapsed time is not an answer. Do not seek renewed approval for already authorized work.

## Reviews and stage transitions

Use the native `gsp-reviewer` for reviews of the GSP stages being performed, with all four modes (`requirements`, `architecture`, `tasks`, `development`) retained, separate from the author; reuse its conversation within a task when possible. A full workflow retains all four stage reviews; a scoped task does not trigger reviews of unrequested stages. Before requesting review, read its [single contract](.codex/agents/gsp-reviewer.toml) for mode-specific checks, required handoff/report fields, baseline verification and read-only isolation. Supply the absolute project root, explicit mode/scope, actual original/current artifact paths, requirement/task IDs where present, baseline and relevant diff, execution evidence, and unresolved questions with existing answers. The reviewer reads sources directly and returns findings; the lead records them, handles user decisions and fixes, and advances only within the requested scope. The reviewer does not implement or delegate another reviewer.

| Verdict | Meaning and primary worker's action |
| --- | --- |
| PASS | No blockers in the explicit scope; evidence supports advancing valid outputs. |
| WARN | Nonblocking suggestions or review limits; record their impact and disposition, then proceed. |
| FAIL | Mandatory behavior is defective, or a required decision/evidence is missing; hold dependent work and completion. |

Record each finding's stable ID, requirement, location, trigger/reproduction, impact and blocking status. Distinguish confirmed defects from unverified concerns; code-only review does not establish execution. For significant findings record `fix location / original-condition recheck / result / verifier`; close only with relevant evidence. Recheck affected changes if the baseline changes during review. Preserve earlier verdicts/baselines and distinguish author revalidation from independent re-review. Final completion depends on current mandatory acceptance and unresolved blockers, not a narrow PASS or test count.

If the native role is unavailable, report that it was not loaded. Use an available independent subagent with authorized model settings and the same contract/mode, explicitly labeled fallback; if none is available, disclose self-check and no independent review. Reading TOML or installing files proves neither native loading nor execution. Read-only instructions inherit permissions and provide no separate security sandbox; isolate checks that write files.

## Budget, scope, and stopping conditions

Use the user's actual deadline and resource limits; there is no default fixed-duration schedule. If a deadline exists, use an actual clock to record the start, deadline, and time zone and preserve them on resumption. Do not invent a deadline, timing measurement, budget, or spending authorization. Scale milestones to the agreed scope and risk, leaving time for meaningful verification, documentation, and handoff.

When progress or evidence invalidates the plan, identify the bottleneck, remaining mandatory outcomes, resource use, and the smallest useful next step. Defer optional features before sacrificing required correctness or verification. Obtain the user's decision before changing mandatory scope, success criteria, or an agreed budget. At a hard deadline or cost ceiling, stop affected work safely and hand off completed items, unresolved work, evidence and reproducible next steps. Without a hard deadline, reassess when evidence warrants it; do not wait out an arbitrary timebox or keep extending an unsuccessful experiment.

## Model use

Use only gpt-6.1-sol and gpt-6-luna for this project unless the user explicitly chooses otherwise.

Assign models and reasoning effort according to the role table below. Explicit spawn overrides must preserve these assignments unless the task is escalated under the escalation rules.

Skills define procedures; they do not switch models or override role-based model assignments.

Use exact model IDs in assignments, configuration, and model-use reports. Do not shorten model IDs or substitute another model version without the user's explicit choice.
| Role | Model | Effort |
| --- | --- | --- |
| Lead: requirements, planning, complex implementation, integration | `gpt-6.1-sol` | high |
| Worker: research and exploration | `gpt-6-luna` | high |
| Worker: scoped implementation and test implementation | `gpt-6.1-sol` | medium |
| Triage: narrow facts and logs | `gpt-6-luna` | medium |
| Design and risky debugging | `gpt-6.1-sol` | high |
| Independent read-only reviewer: `gsp-reviewer` | `gpt-6.1-sol` | high |

Choose the suited role directly; do not impose a cheap-first sequence or fixed concurrency. Check a configured agent's actual model before invoking it; do not silently substitute another model. The bundled reviewer TOML sets its model and effort. This guide does not change the running primary model, global settings or service tier; report unavailable selections accurately.

## Parallel work and evidence

Before parallel assignments or experiments, read and apply the [isolation and integration procedure](.agents/skills/gsp-development/references/parallel-work.md). Independent read-only investigations may share the original; writing experiments use a separate worktree or temporary permitted copies. Specify objective, owned files, actual cwd, baseline, shared root/record, outputs, environment/ports and completion criteria. Only the integration owner applies verified changes; preserve other workers' files and uncommitted changes.

For concurrent PoC development and optimization, read the same reference's [optimization handoff](.agents/skills/gsp-development/references/parallel-work.md#poc-development-with-a-parallel-optimization-task). Keep the PoC lead as integration owner unless explicitly changed. Reuse valid parent requirements/design/task IDs and reviews, agree the effective baseline, preserved interface/behavior and measurement conditions, and continue independent work. Keep candidate evidence separate from combined-state revalidation and acceptance.

Distinguish actual execution, static checks and mock evidence; never mark unperformed verification successful. Include gsp-grilling in the pack and do not add other external skills by default. Follow project/platform instructions and the user's authorized scope.

<!-- GAMJAGOON-SKILLS-PACK:END -->
