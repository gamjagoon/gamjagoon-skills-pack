---
name: gsp-architecture-review
description: Review a design read-only against requirements, existing code, and experimental evidence for feasibility, missing boundaries, and excessive complexity.
---

# Architecture review

Inputs are the original requirements, current design and implementation tasks, relevant existing code, and experiment results. Open the actual design and relevant code rather than reading only the supplied summary, and compare responsibility boundaries and verification paths. Rather than repeating the requirements review, check whether the design can implement the requirements.

## Check ambiguity — grilling

At this stage, also read and apply [gsp-grilling](../gsp-grilling/SKILL.md). Ask when a design assumption lacks a basis in a user decision or a choice is needed among multiple acceptable contracts. First verify technical facts using code, documentation, or experiments.

Present questions to the actual user with a recommendation, and hold only the parts dependent on the answer. The main worker gathers and asks questions from review and work subagents. Reuse existing answers.

## Review

- Does every mandatory requirement have a responsible component, task, and verification method?
- Are data flow, inputs and outputs, error handling, and component boundaries consistent?
- Are dependencies usable in the actual environment, and is there verification evidence for risky assumptions?
- Do file ownership, baseline state, and integration order for parallel work avoid conflicts?
- Is there unnecessary structure given the remaining time, or is time for final verification missing?

## Results

Base the verdict on the review scope and required evidence. PASS means no blockers; WARN means non-blocking suggestions or limitations; FAIL means a defect affecting mandatory requirements or missing decision or evidence needed to advance the stage. Mark missing required evidence as awaiting verification and distinguish it from confirmed defects. Hold dependent work and completion decisions for a FAIL; unrelated work may continue.

Record the paths and baseline state of the original sources and deliverables actually read, checks performed, finding IDs, blocking status, and related requirements. Do not use only a previous PASS or the author's summary as review evidence. If content changes during review, recheck the changed parts.

Without modifying files, return PASS / WARN / FAIL, evidence-backed findings, and recommendations for corrections. For each finding, record the design location, related requirement ID, conditions under which the problem occurs, and its impact. Leave technical verification that was not performed marked as unverified.

For each important finding, the main worker records the correction location, the result of rechecking the relevant design condition or experiment, and the person who verified it. Hold implementation dependent on blockers until evidence of resolution exists, and confirm only user decisions that change the result. The next stage in the full workflow is `gsp-development`. If only a design review was requested, stop at the results.
