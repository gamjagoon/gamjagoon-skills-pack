# Changes throughout the GSP workflow

Use this procedure when a new request or evidence changes requirements, architecture, tasks, implementation, verification, review, or integration. Keep the existing eight stages. Reopen the affected parts; do not restart all stages or create a new workflow for every edit.

## Capture and assess

1. Check the current source, applicable decisions, unfinished tasks and [shared session records](session-work.md). Identify the integration owner and exact code/document baseline. A stale conversation summary is not the current contract.
2. Record a stable change ID such as `C1` in the earliest affected authoritative stage document. Include the request/failure evidence, old/new contract revisions, affected and unknown scope, owner, decision, follow-up Task IDs and closure evidence. Other documents link the ID rather than copying its authority. No separate root change log or HTML is required.
3. Trace requirements → design/interfaces → actual consumers → tasks → tests/reviews. The Task DAG and file scopes identify candidates; inspect the code and contracts to determine semantic impact. Missing links mean unknown impact, not no impact. An unaffected boundary needs a reason supported by evidence.
4. Reuse accepted user decisions and existing authorization. Ask only about changed mandatory scope, acceptance criteria, budget or an unresolved behavioral choice. Continue independent work while awaiting that answer. A recommendation is not acceptance.

| Trigger | Reopen and preserve |
| --- | --- |
| Wording/link change with unchanged meaning | Check the edited document; keep semantic revision and valid prior evidence |
| Internal implementation bug | Fix/reproduce the affected implementation and regressions; reuse unchanged requirements/design |
| Interface/design change | Recheck affected consumers, design, tasks and verification; reuse unaffected requirements |
| Requirement/acceptance change | Update that requirement and its connected design, execution and evidence |
| Test failure | Distinguish product defect, environment failure and unclear expectation before changing the contract |
| New task | Preserve running work and put new work into the same routing policy unless priority was explicitly changed |
| Cancellation/resource/owner change | Record the disposition, affected obligations and handoff; never label cancellation as successful completion |

## Preserve history, update current obligations

Use semantic revisions such as `R1@2` and `D1@3`. Exact file hashes identify a tested snapshot; they do not decide whether meaning changed. Keep IDs stable and preserve the old meaning/evidence in linked history when revising a contract.

- An old `done` or `PASS` says what was verified under its recorded baseline. Do not erase it or silently make it certify a new requirement.
- Add new, unused Task IDs for modification, revalidation and current integration. Link the old execution in Markdown. Revalidation may reuse an artifact without repeating its implementation.
- Update current acceptance bindings and pending consumer dependencies to the new evidence. Adding a new task while the final gate still references old evidence leaves the change incomplete.
- With [DAG v2](../../gsp-tasks/references/task-dag.md), update current `contracts`, per-task `basis`, `hold`, explicit `revalidates` boundaries and `acceptance`. Increment `plan_revision` for semantic plan/hold/dependency changes. Do not insert v2 fields into a v1 document or migrate unrelated old plans.
- Preserve an affected running execution and request a safe checkpoint. Until the worker confirms that results are saved and writing has stopped, keep its running reservation. After confirmation, record the unfinished old execution as `blocked` with its reason and create the needed successor task. A stopped partial execution is not `done`; a `revalidates` edge is only for a completed historical input.
- Do not modify a running worker's basis or deps to pretend it already follows the new contract. A worker returns its received baseline and actual delta; the integrator reconciles them.

## Update and verify at work boundaries (A)

The integration owner serializes authoritative document changes. Before changing several related documents, mark the affected tasks held in the current plan. Publish a coherent revision and run `validate`, `route`, and v2 `check` after updating the related contract/acceptance records. Do not dispatch from a half-updated plan. Confirmed independent branches may continue.

At start/resumption, before dependent work or a stage transition, and before integration:

1. Read the current relevant contract/plan revisions, peers' records and any outstanding change requests.
2. Compare the incoming candidate's basis and exact source state with the current one. Investigate drift and rebase/reverify affected parts before integrating. This precheck is not a source-file lock.
3. Re-run the affected original failure/acceptance conditions against the combined state. Keep candidate results separate from integrated results.
4. Request only the affected stage review. Preserve the old review's baseline and verdict; record who rechecked each significant fix and whether independent re-review occurred.
5. Close the change only when current mandatory acceptance and unresolved coordination requests are satisfied. Empty dispatch, old PASS, a delivered message, or test count alone cannot close it.

For v1 plans, record revisions and current acceptance in Markdown and make the manual limitation explicit. For changed work requiring automatic revision gating, author the affected plan as v2 and validate it. The tool checks declarations and evidence presence, not the truth of semantic impact or test results.

## Optional local notifications (B)

Use [session-control.md](session-control.md) only for an explicitly selected local coordination run. The requirements for B are an existing compatible Codex server, Python 3.9+, the same Linux VM/account, a shared accessible `.gsp-work`, and explicit session registration. A remains the common workflow when B is off or unavailable.

The bundled coordinator records and delivers a change to registered active threads and tracks separate read/held/applied acknowledgements. It does not install/start a server, wake idle agents, choose models, force interruption, modify source files, or synchronize worktrees. Only the user's authorized task and registered scope may be communicated. An unavailable thread remains unresolved; no notification or silence counts as consent.

Before publishing a hold request, declare its affected tasks in the current v2 plan using `hold` or the changed contract basis. Include the current change ID and revision in every acknowledgement. Record saved results before `held`; record applied basis and actual verification before `applied`. Follow the CLI's current-plan checks for resolve/supersede, preserving prior events and never copying ACKs to a new change.

When automatic delivery fails, inspect status and continue A's manual boundary checks. Do not clear a hold or approve integration merely because the process stopped. A file-based record or cooperative ACK is not a security boundary against other processes using the same account.
