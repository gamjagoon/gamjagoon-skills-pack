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

## Workflow

Carry out development work in the following order. Read the skill or reviewer contract for the current stage and pass its outputs and unresolved issues to the next stage. Do not require the user to invoke each stage. If the user requests only one stage, perform only up to that stage. For simple questions and small changes, apply only the necessary stages and briefly record why any were omitted.

| Order | Skill or agent | Output |
| --- | --- | --- |
| 1 | [Requirements writing](.agents/skills/gsp-requirements/SKILL.md) | Source evidence, scope, completion criteria for each requirement |
| 2 | [gsp-reviewer](.codex/agents/gsp-reviewer.toml), mode `requirements` | Review of omissions, contradictions, and verifiability |
| 3 | [Architecture](.agents/skills/gsp-architecture/SKILL.md) | Minimal structure, interfaces, implementation work and verification plan |
| 4 | [gsp-reviewer](.codex/agents/gsp-reviewer.toml), mode `architecture` | Review of requirements coverage, feasibility, and complexity |
| 5 | [Development](.agents/skills/gsp-development/SKILL.md) | Implementation, execution and test results |
| 6 | [gsp-reviewer](.codex/agents/gsp-reviewer.toml), mode `development` | Review of defects and regressions, fixes and revalidation, usage and limitations |

At the start, compare the current request with the source and unfinished items to determine whether it continues existing work or is a separate task. For the same task, continue from valid outputs; for a separate task, create a new title and start/deadline section. Do not reuse the PASS or time of completed work for a new request. Prefer the existing location for records of actual creation or development work; if none exists, collect the following in one `TASK.md`. Do not create a work record or new deadline for simple questions and answers. If asked only to install, do not start a TASK or creation work.

- Current task: the source text or its location, changes to the request, scope and budget, current stage, and next action.
- The connection from requirements → design/work → actual verification. Keep existing records and IDs and distinguish changes.
- Each review: paths of the source and outputs read and their baseline state, review method, verdict and findings, and evidence for fixes and rechecks.

Do not seek renewed approval at each stage for work already approved. Investigate facts that can be checked with files or tools, and ask only for important user decisions that change the outcome. Continue work that does not depend on that decision or a blocking defect.

## Grilling in every stage

Apply [gsp-grilling](.agents/skills/gsp-grilling/SKILL.md) alongside all six stages. Investigate facts verifiable from the source, files, or execution, and ask the user about ambiguous intent, policy, or expected behavior that changes the outcome. Ask questions whose prerequisite decisions have been made, together with recommendations, and continue to the next round according to the answers. Do not merely record questions and move on or treat recommendations as answers.

Hold only work dependent on an answer and continue independent work. The primary worker collects questions from review and work subagents and conveys them to the actual user. Reuse existing answers and resume already authorized work once the necessary answers are available. Do not require a separate question prompt or renewed approval at each stage.

## Reviews and stage transitions

Use the native `gsp-reviewer` agent for all three review stages, separate from the author. Its single definition is [.codex/agents/gsp-reviewer.toml](.codex/agents/gsp-reviewer.toml). Request agent type `gsp-reviewer` with mode `requirements`, `architecture`, or `development`; reuse the same reviewer conversation within a task when possible, while passing current artifacts and decisions on every handoff. Do not create three different reviewer roles. Provide the absolute project root, explicit mode and review scope, actual paths of the original text and current outputs, relevant requirement IDs, baseline state, change scope, execution evidence, and open questions with existing answers. The reviewer returns findings; the lead handles user questions, fixes, and stage progression. The reviewer does not delegate another reviewer or implement fixes. The reviewer reads the relevant files directly instead of relying only on summaries and records the baseline reviewed. Give evidence identifying the state, such as the commit and relevant working diff for Git, or the time of inspection and change history of the relevant files for non-Git work. If the subject changes during review, recheck the changed parts.

| Verdict | Meaning and primary worker's action |
| --- | --- |
| PASS | There are no blockers in the review scope and evidence supports the verdict. Pass valid outputs to the next stage. |
| WARN | There are nonblocking suggestions or review limitations. Record their impact and whether they were addressed, then proceed. |
| FAIL | A required behavior is defective, or a decision or evidence needed to advance the stage is missing. Hold subsequent work dependent on that item and the completion verdict. |

For each finding, record its ID, related requirements, location, triggering conditions, impact, and whether it is blocking. Distinguish unverified matters from confirmed defects. Do not conclude that nothing is missing or execution succeeded without the necessary source and execution evidence. If asked to review code only, limit the verdict to code review and separately state whether execution was performed.

For each significant finding, the primary worker records `fix location / recheck of the original reproduction conditions / result / verifier`. Recheck only the fix and affected parts; do not repeat the entire review by habit. If only the author revalidated, do not change the earlier review's PASS as if it represented the latest result; state that independent re-review was not performed. Do not close a finding without checks directly related to reproducing it.

If the native role is unavailable, report that it was not loaded. When independent subagents with authorized model settings are available, provide one with the same reviewer contract and explicit mode, and label it as a fallback rather than a native `gsp-reviewer` run. If independent subagents are unavailable, proceed with a self-check and explicitly state that independent review was not performed. Reading the TOML or a successful installation alone does not establish native-agent execution. The read-only review contract does not create a separate security sandbox; permissions are inherited, and checks that write files require an isolated location. If requirements or interfaces change, reopen only the affected design, implementation, verification, and review. Judge final completion by the actual evidence for current mandatory requirements and unresolved blockers. Do not declare completion based only on a review PASS or test count.

## Time and scope

Prioritize the user's specified budget and deadline and existing progress records. The default budget for actual development without other instructions is 180 minutes. At the start, use an actual clock to record the start, deadline, and time zone, and do not reset them on resumption. Do not invent times if the clock cannot be checked.

Under the default budget, organize requirements, architecture, and the two short reviews within the first 20 minutes. Execute the core flow by 60 minutes, focus on verification, development review, and significant fixes from 130 minutes, and reserve the final 15 minutes for final execution, usage, and handoff. Scale proportionally for a different budget. If finished early, hand off immediately without a fixed wait.

If core execution is delayed, reassess the cause of the blockage, remaining mandatory items, and smallest executable path. Defer additional features and protect verification and handoff time. Obtain the user's decision before changing mandatory scope or success criteria; do not arbitrarily remove them or substitute mock results. At a user-defined hard deadline, hand off with completed and unfinished work and reproduction instructions. The default budget without a separate hard deadline is a replanning benchmark: report any overrun and remaining work, and do not fabricate completion.

## Model use

The following are recommendations for selecting roles in available agent tools. The pack installs one project-local role, `gsp-reviewer`, configured for GPT-6.1 Sol (`gpt-6.1-sol`) with medium reasoning. That role file sets the review agent's model and effort; it does not change the primary model, global settings, or service tier. Preserve explicit user choices; if they conflict with the bundled role settings, resolve that conflict before invoking it rather than claiming a spawn override changed the role file's model.

| Work | Model | effort |
| --- | --- | --- |
| Narrow fact extraction and log triage | GPT-6 Luna (`gpt-6-luna`) | low |
| Research, exploration, clear implementation, and small experiments | GPT-6 Luna (`gpt-6-luna`) | medium |
| Primary work, architecture, integration, and reviews of the three stages | GPT-6.1 Sol (`gpt-6.1-sol`) | medium |
| Ambiguous debugging and risky changes | GPT-6.1 Sol (`gpt-6.1-sol`) | high |

Assign the role suited to the problem directly. Do not route sequentially from a cheaper model or set a fixed concurrency count. If model and effort selection is unavailable, work with the currently available settings and do not confuse the model actually used with the recommendation. If a specified model is unavailable, report the limitation and use only alternatives already authorized by the user. Continue primary work that is not blocked by the selection.

## Parallel work and evidence

Independent read-only investigations may share the original. Perform experiments that write files in a separate worktree or a temporary folder containing copies of only the necessary files. Before parallel work, read the development skill's [isolation procedure](.agents/skills/gsp-development/references/parallel-work.md). Specify the owned files, actual cwd, baseline state, outputs, environment, ports, and completion criteria; only one integration owner applies verified changes.

Preserve uncommitted changes in the original and other workers' edits. Distinguish actual execution, static checks, and mock results; do not mark unperformed verification as successful. Include gsp-grilling for questions in the pack, and do not add other external skills by default. Follow project and platform instructions and the scope of work authorized by the user.
<!-- GAMJAGOON-SKILLS-PACK:END -->
