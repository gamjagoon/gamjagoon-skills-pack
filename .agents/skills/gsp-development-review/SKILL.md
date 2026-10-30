---
name: gsp-development-review
description: Review defects and regressions read-only by comparing implementation results with the original requirements, design, and evidence from actual execution. Use when judging completion after implementation or requesting a code review.
---

# Development review

Inputs are the original text, requirements and design, changed files, and actual verification results. Check affected callers and completion criteria as well as the diff. The review itself is read-only. If tests write files, use a separate isolated space.

## Check ambiguity — grilling

At this stage, also read and apply [gsp-grilling](../gsp-grilling/SKILL.md). Ask when expected behavior is ambiguous or a proposed fix requires the user to choose a policy. Report clear contract violations as defects, and do not ask for approval again to fix them.

Bring questions to the actual user with a recommendation, and wait only on the parts that depend on the answer. The main worker collects and asks questions from review and work subagents. Reuse existing answers.

## Review

- Check whether mandatory requirements and normal, error, and boundary behavior are actually implemented.
- Check the reasons for and effects of departures from the design.
- Prioritize reproducible defects, regressions in existing behavior, and data loss or boundary-handling problems.
- Establish expectations first from the original text and existing contracts, and compare tests written alongside the implementation against those expectations too. Passing tests can repeat the same misunderstanding.
- Check the actual user entry point and affected existing regression and integration paths. Record what was run and why items were not run, and distinguish mocked results, static checks, and actual execution.

## Results and fixes

Base the verdict on the review scope and required evidence. PASS means no blockers; WARN means there are non-blocking suggestions or limitations; FAIL means there is a defect affecting mandatory requirements or a decision or evidence needed to proceed to the next stage is missing. Mark missing required evidence as pending verification and distinguish it from a confirmed defect. Hold work dependent on a FAIL and the completion verdict; unrelated work may continue.

Record the paths and baseline state of the original text and artifacts actually read, checks performed, finding IDs, whether each is blocking, and related requirements. Do not use only an earlier PASS or the author's summary as review evidence. If content changes during review, recheck the changed parts.

Return PASS / WARN / FAIL and findings. For each defect, record the file and location, reproduction conditions or method, user impact, and recommended fix. Do not present speculative concerns as confirmed defects. If there are no defects, record that fact, the review scope, and items not run.

For each significant finding, the main worker records the fix location, results of rerunning the original failing input or reproduction conditions and affected regression checks, and the person who verified them. Do not close a defect merely because normal-path tests pass. If there is no independent re-review after a fix, communicate this separately from author revalidation. Do not repeat the entire review by inertia if no new risk has arisen. Tell the user the final execution instructions, completed items, actual verification results, and remaining limitations. Deploy, transmit externally, or push only within the scope authorized by the user for that task.

Judge a request to review only code within that scope and do not claim successful execution. Separately check actual evidence for the current mandatory completion criteria and unresolved blockers when judging completion of the entire task.
