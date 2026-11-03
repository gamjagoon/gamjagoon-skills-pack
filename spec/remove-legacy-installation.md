# Remove legacy installation handling

- Revision: r2
- Stage: implementation, verification and independent development review complete.
- Request: “remove old version installation codes”
- Scope: version-specific migration branches in `install.sh` and corresponding README instructions.
- Result: retired review-skill detection, retirement backup/deletion, and deleted-file restoration bookkeeping removed. Current managed-file installation and replacement protections retained.
- Blockers/user decisions: none identified. No user deadline was supplied.

## Contents

- [Requirements and implementation](#requirements-and-implementation)
- [Verification](#verification)
- [Independent review](#independent-review)
- [Scope and evidence](#scope-and-evidence)

## Requirements and implementation

| ID | Acceptance criterion | Implementation |
| --- | --- | --- |
| R1 | Remove installation handling specific to obsolete pack layouts | Removed the three retired review-skill paths, retirement loops, associated arrays, restore loop, CLI help wording and README migration instructions |
| R2 | Obsolete/unmanaged files neither block installation nor get removed by `--overwrite` | Installer checks and changes only current managed paths; README describes that boundary |
| R3 | Preserve current installation, preview, repeat-install, conflict rejection, backups and replacement rollback | Retained these paths and added focused regression tests against temporary projects |

Changed files: [install.sh](../install.sh), [README.md](../README.md), and [tests/test_install.py](../tests/test_install.py). Current CLI flags remain unchanged. Existing unmanaged files remain on disk; their presence no longer invokes migration or cleanup.

This bounded cleanup reuses the installer architecture. Separate requirements, design and task-plan stages were omitted proportionally. No new PoC is needed: the affected behavior can be checked directly with local installer fixtures. Previous review reports remain historical and unchanged.

## Verification

| Check | Expected and observed result | Evidence | Status |
| --- | --- | --- | --- |
| Before removal: `python3 tests/test_install.py InstallTests.test_legacy_and_unrelated_files_are_unmanaged -v` | Reproduced the former `Legacy review skill exists` rejection | Temporary installer execution | Expected FAIL under old behavior |
| After removal: `python3 tests/test_install.py -v` | All four tests passed | Temporary installer execution | PASS |
| Fresh preview/install/repeat | Preview creates no target; payload matches; reinstall unchanged; no runtime records/spec/HTML created | Regression test | PASS |
| Legacy/unrelated files | Default preview/install succeeds; contents and modes preserved, including after `--overwrite`; no retirement backups | Regression test | PASS |
| Current managed conflict | Default install and preview reject a customization; overwrite preview is unchanged; overwrite backs up and replaces it; reinstall unchanged | Regression test | PASS |
| Injected write failure | Already replaced AGENTS restored, newly installed files removed, unrelated files preserved, backup retained | Regression test with isolated `mv` failure shim | PASS |
| `bash -n install.sh`, `git diff --check` | No errors | Static execution | PASS |
| Active installer/README scan | No retired-path migration symbols or old cleanup instructions remain | Text inspection | PASS |

Tests require Python 3 standard library and the installer's existing Bash/Linux tools. Installation itself still requires no Python package. All fixture writes are temporary; no real target project was installed or cleaned up.

## Independent review

**PASS — R1–R3, no confirmed defects or blocking decisions.** Native `gsp-reviewer` (`gpt-6.1-sol / medium`) read the current sources, original request, scoped diff, before artifacts and execution evidence. The previous implementation PASS was not reused.

The reviewer independently ran `python3 tests/test_install.py -v` from an allowlisted temporary copy: all four tests passed. Bash syntax, working-tree diff checks and the active legacy-code scan also passed. All 13 reviewed source hashes remained unchanged during review.

The reviewer confirmed that the removed restoration loop was populated exclusively by retired-file deletion. Current managed-file rollback remains in `cleanup()` and passed the injected failure check. No correction or defect recheck was required. The lead agrees with the scoped verdict and retains the untested limits below.

| Finding ID | Blocking | Result |
| --- | --- | --- |
| None | No | No confirmed defect or pending mandatory evidence within the scope |

Full findings and checks: [independent review](../.gsp-work/sessions/session-1isulumn/reviewer.md). This report was updated by the lead after review; implementation and tests were unchanged.

## Scope and evidence

Baseline: `bd656b1eed3d7800b7162ce97ea4dec0e5081540` plus existing dirty changes at task start. Other pack guidance, previous reports, session records, `.serena/`, global settings and user projects are outside the edit scope.

[Session record](../.gsp-work/sessions/session-1isulumn/work.md), [before result](../.gsp-work/sessions/session-1isulumn/before-test.log), and [after result](../.gsp-work/sessions/session-1isulumn/after-test.log) are local Git-excluded evidence; they may be unavailable in another checkout. The regression runner is retained in the repository so the current checks can be repeated.

Actual concurrent-writer races, all failure injection points, Windows/macOS execution and separate Codex-session behavior were not tested. The result covers the stated Linux/WSL installer cleanup and observed checks. No HTML, commit, push, deployment or external installation was performed.
