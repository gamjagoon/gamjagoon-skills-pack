---
name: gsp-requirements-review
description: Compare the original text with the written requirements in a read-only review for omissions, contradictions, and unverifiable completion criteria. Use when reviewing a requirements draft or a scope change.
---

# Requirements review

Inputs are the user's original text, provided materials, current requirements, and list of unresolved decisions. Do not judge that there are no omissions without the original text. If it is unavailable, mark comparison with it as pending verification and distinguish it from any internal consistency review that can be performed. Do not start design or implementation in its place.

## Checking ambiguity — grilling

At this stage, also read and apply [gsp-grilling](../gsp-grilling/SKILL.md). Ask questions if investigation cannot resolve conflicts between the original text and requirements, or missing policies or expected behavior. Do not treat an arbitrary answer as correct for an unresolved decision.

Send the questions and recommendations to the actual user, and wait only on the parts that depend on the answers. The lead worker consolidates and asks questions from review and work subagents. Reuse existing answers.

## Review

- Check whether mandatory items in the original text are linked to requirements.
- Find unnecessary scope expansion, mutually contradictory conditions, and missing error or boundary conditions.
- Check whether completion criteria can actually be observed and verified.
- Check that assumptions have not been presented as facts or user decisions.
- Check the evidence that the mandatory scope can be performed with the remaining time and environment.

## Results

Base the verdict on the review scope and required evidence. PASS means no blockers; WARN means nonblocking suggestions or limitations exist; FAIL means a defect affecting mandatory requirements exists or a decision or evidence needed to proceed to the next stage is missing. Mark missing mandatory evidence as pending verification and distinguish it from a confirmed defect. Hold work and completion judgments dependent on a FAIL; unrelated work may continue.

Record the paths of the original text and deliverables actually read, their baseline state, checks performed, finding IDs, whether each is blocking, and related requirements. Do not rely only on a previous PASS or the author's summary as review evidence. If content changes during review, recheck the changed parts.

A read-only review returns PASS / WARN / FAIL and findings without modifying the original documents. For each finding, include the requirement ID and original-text location, problem conditions, impact, and suggested correction. Distinguish unverified concerns from defects. Do not invent unsupported scores or repetitive formatting criticisms.

The lead worker records the correction location, result of rechecking against the original text, and verifier for each important finding. Hold designs dependent on unresolved blockers, and pass portions to the next stage as evidence of resolution becomes available. Ask only about issues requiring user decisions; do not wait for approval after every review. The next stage in the overall flow is `gsp-architecture`. If asked only for a review, return the result and stop.
