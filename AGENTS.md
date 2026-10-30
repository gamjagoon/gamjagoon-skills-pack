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

## Project purpose and working brief

Use this as a general-purpose project guide. Start from the problem and intended outcome, not from a technology or a demo deadline. For substantial new work, establish the following brief in `spec/requirement.md`, and maintain its matching HTML view. Reuse answers and repository evidence instead of asking the user to fill in a form from scratch. Keep unknowns explicit; ask only about unresolved decisions that materially affect the outcome. For a small, well-understood change, record only the affected items.

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

Use the four production stages and their four reviews below within this progression; do not create a second competing process or extra agents. The requirements stage establishes the problem, constraints, target endpoint, and acceptance criteria. Architecture selects an approach and necessary experiments. Task planning turns the reviewed design into ordered, verifiable work. Development obtains evidence and, when included in the request, completes the deliverable. Reviews check evidence against the current endpoint. Reopen only affected decisions when evidence changes the plan. A PoC-only request ends with its findings and next-step recommendation; it does not authorize a full product build. Do not force a new PoC for a routine change already supported by adequate evidence; state why it is unnecessary.

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

Carry out development work in the following order. Read the skill or reviewer contract for the current stage and pass its outputs and unresolved issues to the next stage. Do not require the user to invoke each stage. If the user requests only one stage, perform only up to that stage. For simple questions and small changes, apply only the necessary stages and briefly record why any were omitted.

| Order | Skill or agent | Output |
| --- | --- | --- |
| 1 | [Requirements writing](.agents/skills/gsp-requirements/SKILL.md) | `spec/requirement.md`: source evidence, scope and completion criteria |
| 2 | [gsp-reviewer](.codex/agents/gsp-reviewer.toml), mode `requirements` | Review of omissions, contradictions, and verifiability |
| 3 | [Architecture](.agents/skills/gsp-architecture/SKILL.md) | `spec/architecture.md`: minimal structure, interfaces and verification strategy |
| 4 | [gsp-reviewer](.codex/agents/gsp-reviewer.toml), mode `architecture` | Review of requirements coverage, feasibility, and complexity |
| 5 | [Task planning](.agents/skills/gsp-tasks/SKILL.md) | `spec/tasks.md`: ordered work, dependencies, ownership and completion checks |
| 6 | [gsp-reviewer](.codex/agents/gsp-reviewer.toml), mode `tasks` | Review of coverage, actionable scope, dependencies and verification work |
| 7 | [Development](.agents/skills/gsp-development/SKILL.md) | Implementation, execution and test results recorded in `spec/tasks.md` |
| 8 | [gsp-reviewer](.codex/agents/gsp-reviewer.toml), mode `development` | Review of defects and regressions, fixes and revalidation, usage and limitations |

At the start, compare the current request with the source and unfinished items to determine whether it continues existing work or is a separate task. For the same task, continue from valid outputs; for a separate task, create a new title and record its start and any user-specified deadline. Do not reuse the PASS or time of completed work for a new request. For new substantive work, create `spec/` and use `requirement.md`, `architecture.md`, and `tasks.md` with matching HTML views as their stages are reached. Do not create future-stage placeholders or a new root-level work log. Do not migrate, rename, rewrite, or delete existing project documents merely to adopt this layout. For a continuation, reuse and link valid existing records; explicit user locations take precedence. Preserve unrelated content at the default paths; use and report a non-conflicting location if needed. Do not create work documents or a new deadline for simple questions, or start development when asked only to install. Record the following in the relevant stage document:

- Current task: the source text or its location, changes to the request, scope and budget, current stage, and next action.
- The connection from requirements → architecture → task IDs → actual verification. Keep existing records and IDs and distinguish changes.
- Each review: paths of the source and outputs read and their baseline state, review method, verdict and findings, and evidence for fixes and rechecks.

Do not seek renewed approval at each stage for work already approved. Investigate facts that can be checked with files or tools, and ask only for important user decisions that change the outcome. Continue work that does not depend on that decision or a blocking defect.

## Documents for human review

For substantive requirements, design, task planning, implementation/verification, and review deliverables, the lead produces both Markdown and HTML without requiring a separate format prompt. Use the user's requested language for the deliverables; these English instructions do not require English output. The default pairs are `spec/requirement.md` / `spec/requirement.html`, `spec/architecture.md` / `spec/architecture.html`, and `spec/tasks.md` / `spec/tasks.html`. Requirements own the problem, acceptance criteria and decisions; architecture owns the design and rationale; tasks owns the execution plan, progress and actual verification evidence. Record each review in its stage document; keep task-plan review and final implementation review separate in `tasks.md`. Cross-link stable IDs instead of duplicating authoritative content. Create only documents needed for the requested stages. Existing records may remain in place for ongoing work without automatic migration. Respect explicitly requested formats, locations, and no-write constraints. Installation alone and simple questions do not create these files. If writing is forbidden, return the permitted Markdown in conversation and state that no HTML file was generated.

Markdown is the source of truth. Update it first, then refresh the HTML from the same content at each substantive stage handoff, after recording review results or user decisions, and before final delivery. Keep stable requirement, question, and finding IDs and the same revision label in both views. Do not overwrite unrelated existing documents; preserve their content or choose a non-conflicting sibling path and report it. Multiple existing documents may keep their layout with corresponding HTML views rather than being merged into a new record.

Make both views easy to review:
- Start with the current stage, scope, outcome so far, changes since the previous revision, unresolved blockers, and decisions needed from the user. Distinguish recommendations from accepted decisions.
- Include only sections relevant to the requested scope: requirements and acceptance criteria; design rationale and alternatives; implementation tasks and dependencies; review findings; verification evidence and limitations. Do not invent completed stages, PASS verdicts, or test results to fill a template.
- Use concise headings, a table of contents, and linked IDs. Show findings in a table with blocking status, requirement ID, location, impact, suggested fix, and closure evidence. Show checks with command/input, expected and observed result, evidence type, and whether they passed, failed, or were not run. Provide source/artifact references and mark unavailable links as unavailable.
- Use portable, GitHub-compatible Markdown with working table-of-contents links. Do not assume renderer-specific heading-ID syntax works. Put literal markup and code in inline or fenced code so quoted input remains visible as text in Markdown too.
- Keep the complete evidence available in Markdown and HTML; long logs or code may be collapsed in HTML with native `details` elements. Do not omit uncertainty or unrun checks from the HTML summary.

Produce a self-contained UTF-8 HTML document with embedded CSS, semantic headings, internal navigation, readable tables and code blocks, visible status text (not color alone), responsive layout, and print styles. It must open as a local file without a server, build step, CDN, external fonts, or JavaScript. Escape source text and code before inserting it into HTML; treat quotes, logs, and user data as text rather than executable markup. Use safe links to available sources instead of embedding active content. Do not add a rendering dependency solely for this output.

The reviewer remains read-only: it returns structured findings to the lead, who updates both files. The reviewer checks consistency between both views when they are present; formatting does not replace reviewing source artifacts or running relevant checks. Before handoff, compare decisions, IDs, verdicts, and evidence between the two views, check links and local readability, and state any check not performed. End the user-facing delivery with clickable links to both documents; files and summaries alone do not count as the user answering an open question.

## Grilling in every stage

Apply [gsp-grilling](.agents/skills/gsp-grilling/SKILL.md) alongside all eight stages. Investigate facts verifiable from the source, files, or execution, and ask the user about ambiguous intent, policy, or expected behavior that changes the outcome. Ask questions whose prerequisite decisions have been made, together with recommendations, and continue to the next round according to the answers. Do not merely record questions and move on or treat recommendations as answers.

Hold only work dependent on an answer and continue independent work. The primary worker collects questions from review and work subagents and conveys them to the actual user. Reuse existing answers and resume already authorized work once the necessary answers are available. Do not require a separate question prompt or renewed approval at each stage.

## Reviews and stage transitions

Use the native `gsp-reviewer` agent for all four review stages, separate from the author. Its single definition is [.codex/agents/gsp-reviewer.toml](.codex/agents/gsp-reviewer.toml). Request agent type `gsp-reviewer` with mode `requirements`, `architecture`, `tasks`, or `development`; reuse the same reviewer conversation within a task when possible, while passing current artifacts and decisions on every handoff. Do not create separate reviewer roles for each stage. Provide the absolute project root, explicit mode and review scope, actual paths of the original text and current outputs, relevant requirement IDs, baseline state, change scope, execution evidence, and open questions with existing answers. The reviewer returns findings; the lead handles user questions, fixes, and stage progression. The reviewer does not delegate another reviewer or implement fixes. The reviewer reads the relevant files directly instead of relying only on summaries and records the baseline reviewed. Give evidence identifying the state, such as the commit and relevant working diff for Git, or the time of inspection and change history of the relevant files for non-Git work. If the subject changes during review, recheck the changed parts.

| Verdict | Meaning and primary worker's action |
| --- | --- |
| PASS | There are no blockers in the review scope and evidence supports the verdict. Pass valid outputs to the next stage. |
| WARN | There are nonblocking suggestions or review limitations. Record their impact and whether they were addressed, then proceed. |
| FAIL | A required behavior is defective, or a decision or evidence needed to advance the stage is missing. Hold subsequent work dependent on that item and the completion verdict. |

For each finding, record its ID, related requirements, location, triggering conditions, impact, and whether it is blocking. Distinguish unverified matters from confirmed defects. Do not conclude that nothing is missing or execution succeeded without the necessary source and execution evidence. If asked to review code only, limit the verdict to code review and separately state whether execution was performed.

For each significant finding, the primary worker records `fix location / recheck of the original reproduction conditions / result / verifier`. Recheck only the fix and affected parts; do not repeat the entire review by habit. If only the author revalidated, do not change the earlier review's PASS as if it represented the latest result; state that independent re-review was not performed. Do not close a finding without checks directly related to reproducing it.

If the native role is unavailable, report that it was not loaded. When independent subagents with authorized model settings are available, provide one with the same reviewer contract and explicit mode, and label it as a fallback rather than a native `gsp-reviewer` run. If independent subagents are unavailable, proceed with a self-check and explicitly state that independent review was not performed. Reading the TOML or a successful installation alone does not establish native-agent execution. The read-only review contract does not create a separate security sandbox; permissions are inherited, and checks that write files require an isolated location. If requirements or interfaces change, reopen only the affected design, task plan, implementation, verification, and review. Judge final completion by the actual evidence for current mandatory requirements and unresolved blockers. Do not declare completion based only on a review PASS or test count.

## Budget, scope, and stopping conditions

Use the user's actual deadline and resource limits; there is no default fixed-duration schedule. If a deadline exists, use an actual clock to record the start, deadline, and time zone and preserve them on resumption. Do not invent a deadline, timing measurement, budget, or spending authorization. Scale milestones to the agreed scope and risk, leaving time for meaningful verification, documentation, and handoff.

When progress or evidence invalidates the plan, identify the bottleneck, remaining mandatory outcomes, resource use, and the smallest useful next step. Defer optional features before sacrificing required correctness or verification. Obtain the user's decision before changing mandatory scope, success criteria, or an agreed budget. At a hard deadline or cost ceiling, stop affected work safely and hand off completed items, unresolved work, evidence and reproducible next steps. Without a hard deadline, reassess when evidence warrants it; do not wait out an arbitrary timebox or keep extending an unsuccessful experiment.

## Model use

The following are recommendations for selecting roles in available agent tools. The pack installs one project-local role, `gsp-reviewer`, configured for GPT-6.1 Sol (`gpt-6.1-sol`) with medium reasoning. That role file sets the review agent's model and effort; it does not change the primary model, global settings, or service tier. Preserve explicit user choices; if they conflict with the bundled role settings, resolve that conflict before invoking it rather than claiming a spawn override changed the role file's model.

| Work | Model | effort |
| --- | --- | --- |
| Narrow fact extraction and log triage | GPT-6 Luna (`gpt-6-luna`) | low |
| Research, exploration, clear implementation, and small experiments | GPT-6 Luna (`gpt-6-luna`) | medium |
| Primary work, architecture, task planning, integration, and reviews of the four stages | GPT-6.1 Sol (`gpt-6.1-sol`) | medium |
| Ambiguous debugging and risky changes | GPT-6.1 Sol (`gpt-6.1-sol`) | high |

Assign the role suited to the problem directly. Do not route sequentially from a cheaper model or set a fixed concurrency count. If model and effort selection is unavailable, work with the currently available settings and do not confuse the model actually used with the recommendation. If a specified model is unavailable, report the limitation and use only alternatives already authorized by the user. Continue primary work that is not blocked by the selection.

## Parallel work and evidence

Independent read-only investigations may share the original. Perform experiments that write files in a separate worktree or a temporary folder containing copies of only the necessary files. Before parallel work, read the development skill's [isolation procedure](.agents/skills/gsp-development/references/parallel-work.md). Specify the owned files, actual cwd, baseline state, outputs, environment, ports, and completion criteria; only one integration owner applies verified changes.

Preserve uncommitted changes in the original and other workers' edits. Distinguish actual execution, static checks, and mock results; do not mark unperformed verification as successful. Include gsp-grilling for questions in the pack, and do not add other external skills by default. Follow project and platform instructions and the scope of work authorized by the user.
<!-- GAMJAGOON-SKILLS-PACK:END -->
