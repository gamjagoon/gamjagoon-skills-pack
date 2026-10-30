---
name: gsp-grilling
description: Resolve ambiguities requiring user decisions through question rounds during requirements, architecture, development, and their reviews. Use when unresolved decisions would change the outcome; do not ask again about facts to investigate or decisions already answered.
---

# Grilling — asking about ambiguous decisions

This is a supporting skill shared by the six work stages. Apply grilling's question rounds by dependency to this pack's stage progression and independent reviews. It is not a separate seventh work stage and does not require an external grilling installation.

## Distinguish first

- Distinguish facts verifiable from the original text, existing answers, files, or execution from intentions, preferences, and policies that only the user can decide. Investigate facts first. Delegate independent investigation to read-only subagents when possible; check directly if they are unavailable.
- Ask when the same request can have multiple interpretations that change the scope, expected behavior, data handling, external integrations, or completion criteria. Do not settle an unresolved decision merely by recording it as an assumption.
- Do not repeatedly ask about already decided matters or routine internal implementation choices within that scope. If the user has delegated a choice, decide within the delegated scope and record the reason.

## Question rounds

1. Connect unresolved decisions to prerequisite decisions. Ask together in this round the questions whose prerequisite answers and investigation are complete. Defer follow-up questions whose meaning depends on the answers to the next round. If there are many items, split them into readable groups without bringing dependent questions forward.
2. Give each question a number such as Q1, what is unclear, its effect on the outcome, options, and a recommendation with its reason. If options are difficult to express, use a short free-response question.
3. Do not merely write the list of questions in a document and move on; send it to the actual user. Use an available question tool, or ask in conversation if none is available. A recommendation is not the user's answer.
4. Wait on the parts that need answers and work that depends on them. Investigation and implementation unrelated to the answers may continue. Do not treat no response, elapsed time, or insufficient budget as consent.
5. After receiving answers, briefly confirm the decisions and your understanding, and revisit dependencies. Ask about partial answers, contradictions, and new ambiguities in the next round. Once the unresolved decisions for a part are resolved, resume within the existing authorized scope without adding separate approval at every stage.

Example question:

> ❓ Q1 — If an output file with the same name exists, should it be overwritten or should execution stop with an error?
> ➡️ Recommendation: Stop with an error. This preserves the existing result.

## Review, recording, and resumption

- Review subagents send the lead worker their questions, options, reasons for recommendations, and affected requirements. The lead worker removes duplicates, asks the actual user, and conveys the answers to the relevant worker. When reviewing directly without a lead worker, ask directly.
- Distinguish ambiguities requiring user judgment from reproduced implementation defects. Do not seek renewed approval to fix a bug that violates an already clear contract. Do not assume an ambiguous expected value is correct and produce a PASS or confirmed defect.
- The lead worker records the question ID, related requirements, answer or waiting status, decision, and affected stages in the existing work record. Reuse answers to questions with the same meaning in later stages; ask only about changed parts when conditions change. Do not create a new record file for simple questions and answers.
- If answers change requirements, interfaces, or completion criteria, update only the affected design, code, verification, and reviews. If a mandatory decision remains unresolved, do not declare that part complete.
