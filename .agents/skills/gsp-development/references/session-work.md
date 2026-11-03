# Shared session work records

Use `.gsp-work/` so separate sessions can inspect work in progress and completed changes. This is a file-based coordination procedure, not a daemon, notification service, source synchronization mechanism, or locking system. It applies when project files will be changed, including documentation work. Installation alone and simple questions do not create records. A read-only assignment remains read-only; its lead records returned findings.

## Resolve one shared root

Before project edits, choose and report one absolute `.gsp-work` directory for every session working on this project.

- In a normal Git checkout, use the main checkout's `.gsp-work`. Inspect `git worktree list --porcelain` to locate the main checkout and confirm the actual path. In a linked worktree, do not use that worktree's current directory as a new shared root. A worktree's ignored directories are not automatically shared with other worktrees.
- A lead may supply the absolute path as `GSP_WORK_ROOT`. Verify it refers to the agreed project and existing records before creating anything. This is a convention in this procedure, not an automatically configured Codex setting. Pass the same path explicitly to separate chats and subagents; environment variables do not automatically propagate to other sessions.
- For a non-Git project, use the original project directory's `.gsp-work` and pass its absolute path to any isolated copies. For bare repositories, inaccessible main checkouts, or an ambiguous location, resolve the shared directory with the lead/user instead of choosing a private fallback. If access is unavailable, continue independent read-only work and hold collaborative writes that depend on that information.
- Separate clones and machines do not automatically share these local records. A separately agreed shared store would be needed; do not upload or synchronize records externally as part of this procedure.

The installer adds `.gsp-work/` to `.gitignore`. Existing tracked records are not automatically untracked or deleted. Store concise work facts and evidence references, not secrets, full environment dumps or unrelated transcripts. Keep existing records when installing, updating or cleaning worktrees.

## One writer per session record

```text
<main-checkout>/.gsp-work/
└── sessions/
    ├── session-unique-a/work.md
    └── session-unique-b/work.md
```

Use a filesystem-safe unique session ID. If the actual session ID is unavailable, allocate a unique directory and record that it is a local identifier. A new independent session gets a new ID. On resumption, reuse the recorded directory only after confirming ownership; do not guess an existing session ID or take over its record.

For a new session, after setting the verified absolute `GSP_WORK_ROOT`, Bash can allocate the directory without collisions:

```bash
: "${GSP_WORK_ROOT:?Set the agreed absolute .gsp-work path first}"
case "$GSP_WORK_ROOT" in
    /*/.gsp-work) ;;
    *) printf 'Expected an absolute path ending in /.gsp-work\n' >&2; exit 1 ;;
esac
mkdir -p -- "$GSP_WORK_ROOT/sessions"
gsp_session_dir=$(mktemp -d -- "$GSP_WORK_ROOT/sessions/session-XXXXXXXX")
printf 'Session record: %s/work.md\n' "$gsp_session_dir"
```

Write only your own `work.md`. Prepare a complete update in a temporary file inside your session directory, then rename it to `work.md`; readers should see either the previous complete record or the new complete record. Keep the existing history and evidence when updating. Do not maintain a shared index that every session rewrites, append to another session's file, or delete another session's record. Coordinate a deliberate handoff before changing the writer of a record.

## Record contents

Use Markdown in the user's language. Keep the summary current and retain a timestamped history of meaningful changes. Record actual values; use `unknown`, `pending`, or `not run` where evidence is unavailable.

| Field | What to record |
| --- | --- |
| Identity | Unique record ID, actual session ID if available, owner and integration owner |
| Location and baseline | Shared root, actual cwd/worktree, branch/commit, relevant dirty changes and initial state |
| Request and scope | User request or source link, parent/related task IDs and session paths, owned files/modules and exclusions |
| State | `in_progress`, `blocked`, `paused`, `done` or `cancelled`; start/update time, current step and next action |
| Changes | Changed files, behavior, dependencies and the relevant patch/commit or content hashes; distinguish the received baseline from your added delta |
| Interfaces | Contract ID and revision, proposed/accepted status, before/after behavior, affected consumers and decision source |
| Verification | Exact tested commit plus dirty patch/hash when applicable, command/input, environment, expected/observed result and evidence type; include failed and unrun checks |
| Coordination | Related session paths, conflicts, questions, and acknowledgements identifying the specific change/version read or applied |
| Handoff | Remaining work, blockers, delivery references, candidate delivery versus integration acceptance, and exact integrated state if applicable |

Keep requirements and architecture in `spec/` or their established locations; link to their canonical IDs instead of duplicating a competing specification here. Mark `done` only for the owned task's verified completion, not merely because a turn ended. Record pauses and cancellations only when they actually occur. Old timestamps do not establish that another session stopped, surrendered ownership, or completed its work.

For a [parallel optimization task](parallel-work.md#poc-development-with-a-parallel-optimization-task), also reference the metric and comparison procedure, exact baseline/candidate measurements and controlled conditions. Keep the worker's candidate result separate from later combined-state results; copying a peer's passing result does not validate your current code.

## Read and update at work boundaries

1. At start/resumption, read the current summary and relevant history of sessions affecting your files, interfaces or dependencies. List record paths with `rg --files --hidden "$GSP_WORK_ROOT/sessions" -g work.md` when the directory exists. An absent record is not proof that an unregistered session is idle.
2. Before editing a shared file or interface, record the intended scope and check for overlapping work. A recorded claim is advisory, not a lock: two agents can claim simultaneously. Resolve overlap through the integration owner or serialize the affected edits; do not infer agreement from silence or overwrite another agent's work.
3. At a meaningful change, interface decision, test result, blocker or scope change, update your record with the actual state. Before dependent work and integration, reread relevant peers. Avoid continuous polling and do not assume peers have seen an update.
4. For interface changes, distinguish proposal from acceptance. State the affected contracts and consumers; peers acknowledge in their own records with a reference to the change/version. Acknowledgement of reading is different from applying and testing it. Hold only dependent work when a necessary decision is unresolved.
5. Share code by the agreed patch/commit and integration procedure. Reading a record does not update a worktree. The integrator verifies the combined state and records new integration results; a passing test on one worker's older snapshot does not certify the combined changes.
6. Before handoff or stopping, update status, remaining work and the next action, and return the record's absolute path. When needed, ask the lead to relay an update through an available, authorized channel. This file procedure itself does not send messages or wake idle sessions.

Concurrent readers and separate session writers are supported by directory ownership and atomic file replacement. These are cooperation rules, not an enforced security boundary or an exclusive lock on source files. Unknown ownership or missing access must remain visible as a coordination limit.

## Changed contracts and optional notification

Follow [change-management.md](change-management.md) when a requirement, interface, task or verification basis changes. Keep old execution evidence, use stable change/revision IDs, and distinguish the candidate from current integration. With explicit same-VM notification scope, follow [session-control.md](session-control.md) and register your own record/thread/tasks. The coordinator writes only its separate operational state; each work.md still has one owner. Its state lock does not lock source files or make record-only sessions receive messages.
